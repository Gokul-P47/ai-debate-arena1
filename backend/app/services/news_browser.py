"""Browse related topic information — private knowledge for conversation, not news scripts."""

from __future__ import annotations

import asyncio

from app.providers.base_provider import BaseProvider
from app.utils.logger import get_logger
from app.utils.news import fetch_latest_news

logger = get_logger(__name__)

_RESEARCH_SYSTEM = """
You prepare PRIVATE show notes for TV guests. Guests will NOT read these aloud as news.

Stay strictly on the given Topic. Drop any snippet that is not clearly about that topic.

Given a topic + search snippets, write a compact knowledge pack:

1) First line exactly: CONTROVERSIAL: yes   OR   CONTROVERSIAL: no
   (yes = people genuinely disagree; politics, ethics, identity, policy fights, etc.)

2) Then these sections with short bullet lines starting with "- ":

KNOWLEDGE
- Useful background people should understand about the topic (not headline dumps)

LIVED ANGLES
- Everyday situations where this topic shows up (people, places, choices) — varied

FOR
- 3–5 honest arguments someone who leans supportive might make

AGAINST
- 3–5 honest arguments someone who leans critical might make

TALK HOOKS
- 4–6 short chat sparks guests can riff on (questions, tensions, contrasts)

Rules:
- Every bullet must be about the Topic. No side subjects.
- Use the search snippets for freshness when useful; also add clear general knowledge of the topic.
- Do NOT invent fake statistics or fake named events.
- Do NOT write "according to" / source names / "headline".
- Keep language simple.
- Write in the requested language.
""".strip()


async def _fetch_related_snippets(topic: str, max_per_query: int = 4) -> list[dict[str, str]]:
    """Fetch related search/news snippets with a few topic-shaped queries."""
    base = topic.strip()
    queries = [
        base,
        f"{base} debate",
        f"{base} impact",
        f"{base} opinion",
    ]
    seen: set[str] = set()
    merged: list[dict[str, str]] = []

    results = await asyncio.gather(
        *[fetch_latest_news(q, max_results=max_per_query) for q in queries],
        return_exceptions=True,
    )
    for batch in results:
        if isinstance(batch, Exception):
            logger.warning("Related fetch failed: %s", batch)
            continue
        for article in batch:
            title = (article.get("title") or "").strip()
            key = title.lower()
            if not title or key in seen:
                continue
            seen.add(key)
            merged.append(article)
    return merged[:14]


def _format_snippets(articles: list[dict[str, str]]) -> str:
    if not articles:
        return "(No live snippets found — rely on clear general knowledge of the topic.)"
    lines = []
    for i, article in enumerate(articles, start=1):
        title = (article.get("title") or "").strip()
        if title:
            lines.append(f"{i}. {title}")
    return "\n".join(lines) if lines else "(No live snippets found.)"


async def browse_topic_news(
    *,
    topic: str,
    language: str,
    provider: BaseProvider,
    max_results: int = 10,
) -> tuple[list[dict[str, str]], str]:
    """Browse related topic info and build a private knowledge pack for guests.

    Returns (raw_articles_for_api, knowledge_pack_for_prompts).
    The pack is reference knowledge — not a script of news to recite.
    """
    del max_results  # related fetch uses its own per-query limits
    articles = await _fetch_related_snippets(topic)
    snippets = _format_snippets(articles)

    user_prompt = (
        f'SHOW TOPIC (mandatory): "{topic}"\n'
        f"Language: {language}\n\n"
        f"Related search/news snippets (keep only what is about this topic):\n{snippets}\n\n"
        "Build the private knowledge pack now — every bullet about this topic only."
    )

    try:
        pack = (await provider.generate(user_prompt, _RESEARCH_SYSTEM)).strip()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Topic research pack failed: %s", exc)
        fallback_lines = [
            "CONTROVERSIAL: no",
            "",
            "KNOWLEDGE",
            f"- The show is about: {topic}",
            "",
            "LIVED ANGLES",
            f"- How {topic} shows up in daily choices",
            f"- Who feels helped or hurt by {topic}",
            "",
            "FOR",
            f"- There may be real upsides to {topic}",
            "",
            "AGAINST",
            f"- There may be real worries about {topic}",
            "",
            "TALK HOOKS",
            f"- What should ordinary people do about {topic}?",
        ]
        for article in articles[:5]:
            title = (article.get("title") or "").strip()
            if title:
                fallback_lines.append(f"- {title}")
        pack = "\n".join(fallback_lines)

    prompt_block = (
        "PRIVATE TOPIC KNOWLEDGE (for you only — gain understanding; "
        "do NOT recite as a news bulletin; never cite sources):\n"
        f"{pack}"
    )

    logger.info(
        "Built topic knowledge pack for %r from %d snippets",
        topic,
        len(articles),
    )
    return articles, prompt_block


def is_controversial_pack(pack: str) -> bool:
    """Detect CONTROVERSIAL: yes marker from the knowledge pack."""
    for line in (pack or "").splitlines()[:24]:
        lower = line.strip().lower()
        if "controversial:" in lower:
            return "yes" in lower.split("controversial:", 1)[1]
    return False


def extract_section_bullets(pack: str, section: str) -> list[str]:
    """Pull '- ' bullets under a named section header."""
    lines = (pack or "").splitlines()
    collecting = False
    bullets: list[str] = []
    target = section.strip().upper()
    for raw in lines:
        line = raw.strip()
        if not line:
            if collecting and bullets:
                break
            continue
        upper = line.upper()
        if upper in {
            "KNOWLEDGE",
            "LIVED ANGLES",
            "FOR",
            "AGAINST",
            "TALK HOOKS",
        } or upper.startswith("CONTROVERSIAL:"):
            collecting = upper == target
            continue
        if collecting:
            if line.startswith("-"):
                bullets.append(line.lstrip("-").strip())
            elif not line[0].isspace() and bullets:
                break
    return bullets
