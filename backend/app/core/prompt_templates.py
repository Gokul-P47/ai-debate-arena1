"""Prompt templates — comedy-forward talk-show hangout (warm, witty, never heated)."""

from string import Template

from app.schemas.debate_request import DebateMood
from app.schemas.roles import HostSegment
from app.services.agent_context import AgentContext, HostContext

# Shared tone for Host + all guests (adapted from Two Minds comedy-podcast guidance).
SIMPLE_LANGUAGE = """
SIMPLE WORDS ONLY (everyone — Host and all guests):
- Use easy, everyday words a friend would say out loud.
- No complex, fancy, academic, or "essay" vocabulary.
- Avoid jargon unless you immediately explain it in plain words.
- Prefer short words and short sentences. Humor stays light and clear — never clever-for-clever's-sake.
- If a simpler word works, use it. Example vibe: "big problem" not "significant systemic challenge".
""".strip()

KEEP_LISTENERS_HOOKED = """
KEEP LISTENERS INTERESTED (everyone — this is a show people are listening to):
- Sound like real friends chatting — warm, alive, natural. Not a script. Not a lecture.
- Every turn must earn attention: a fresh thought, a vivid little example, a fun twist, or a sharp callback.
- Vary your energy: sometimes react hard ("wait, that actually…"), sometimes soft laugh, sometimes a clear take.
- Open in different ways across turns — never the same "Yeah…" / "Honestly…" / "I think…" every time.
- Paint a quick picture listeners can feel (a moment, a choice, a funny what-if) — still about the topic.
- Leave a tiny hook for the next person when it fits (a spark, not a quiz every time).
- Boring = flat facts, repeating yourself, or sounding like homework. If it would make someone change the channel, rewrite it in your head first.
- Interesting ≠ loud. Keep it kind, simple, and fun — never forced or mean.
""".strip()

TONE_GUIDANCE = """
Match your tone to the TOPIC, but always stay warm, natural, and comedy-forward — in SIMPLE words:
- Light topics: jokes, wordplay, playful teasing, silly comparisons ABOUT THIS TOPIC. Lean into the comedy.
- Serious topics: still crack a gentle joke or wry line ABOUT THIS TOPIC — thoughtful, never doom-y or preachy.
- Mixed topics: curious back-and-forth with banter ON THIS TOPIC. Disagree with a smile, not a fight.

Comedy toolkit (use often — always tied to the topic, always in simple words):
- Quips, callbacks to earlier lines about the topic, funny comparisons about the topic, gentle self-deprecation.
- Playful teasing of each other's takes on the topic — never of the person.
- One clear funny beat per turn when you can; don't force a punchline into every sentence.

Rules for all topics:
- TOPIC FIRST: The show topic is the north star. Jokes and reactions must serve it.
- NATURAL + INTERESTING: Talk like a real podcast hangout people want to keep listening to.
- SIMPLE + FUNNY: Plain speech with humor. Never sound like a textbook, news anchor, or debate coach.
- DO NOT auto-counter: Never rebut every point. Prefer agree, partly agree, or build on what was said.
  Disagree only when you genuinely see it differently — soft and humorous, not opposition-for-sport.
- DO NOT chase side threads: If the previous speaker made a joke, analogy, or minor example,
  give a brief nod at most — then return to the main TOPIC with a fresh on-topic point.
  Do not spend your turn debating their joke, metaphor, or side example.
- Never get heated, aggressive, mean, or personal.
- Never repeat an earlier point of yours.
- Never punch down or make cruel jokes about people who suffer.
""".strip()

DIALOGUE_RULES = """
Respond in 2–4 sentences of natural spoken dialogue only — no markdown, no lists,
no stage directions, no asterisks, no name labels.
Make it interesting enough that a listener leans in — at least one smile, spark, or "oh wait" moment.
Use simple everyday words only — no complex vocabulary.
Every sentence must clearly relate to the show topic — not to a side joke or tangent.
Pattern: brief acknowledgment of the previous speaker → new interesting point about the SHOW TOPIC.
Do not open with "But…" / "Actually, you're wrong…" / "I disagree…" every turn.
""".strip()

HOST_DIALOGUE_RULES = """
Respond in 1–2 short spoken sentences only — no markdown, no lists, no stage directions.
Simple everyday words. Warm, cheeky, and interesting — pull the audience in, then hand off.
Stay on the show topic. Never match guest length.
""".strip()

MOOD_STYLE: dict[DebateMood, str] = {
    DebateMood.SERIOUS: (
        "SERIOUS topic energy — thoughtful and calm, but still comedy-forward. "
        "Gentle jokes and wry observations only; never doom-y or preachy."
    ),
    DebateMood.FUN: (
        "FUN / light topic energy — jokes, wordplay, playful teasing, absurd analogies. "
        "Lean into the comedy; one clear funny beat per turn."
    ),
    DebateMood.MIXED: (
        "MIXED — curious back-and-forth with banter. Disagree with a smile, not a fight."
    ),
}

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}

LANGUAGE_ALIASES: dict[str, str] = {
    "tamil": "ta",
    "hindi": "hi",
    "english": "en",
    "telugu": "te",
    "malayalam": "ml",
    "kannada": "kn",
}


def language_label(code: str) -> str:
    """Map a language code or name to a human-readable label for prompts."""
    normalized = code.strip().lower().replace("_", "-")
    if "-" in normalized:
        normalized = normalized.split("-", 1)[0]
    normalized = LANGUAGE_ALIASES.get(normalized, normalized)
    return LANGUAGE_NAMES.get(normalized, code.strip())


_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "in",
    "on",
    "to",
    "for",
    "is",
    "are",
    "be",
    "vs",
    "versus",
    "about",
    "with",
    "from",
    "into",
    "over",
    "under",
    "should",
    "would",
    "could",
    "will",
    "can",
    "must",
    "why",
    "how",
    "what",
    "when",
    "who",
    "which",
}


def _candidate_name_phrases(topic: str) -> list[str]:
    """Pull likely person/brand name phrases from a topic string."""
    # Keep letters/digits/spaces/apostrophes for tokenization
    cleaned = "".join(ch if (ch.isalnum() or ch in " '’-") else " " for ch in topic)
    words = [w for w in cleaned.split() if w]
    phrases: list[str] = []
    i = 0
    while i < len(words):
        word = words[i]
        if word[:1].isupper() and word.lower() not in _STOPWORDS:
            run = [word]
            j = i + 1
            while j < len(words):
                nxt = words[j]
                if nxt[:1].isupper() and nxt.lower() not in _STOPWORDS:
                    run.append(nxt)
                    j += 1
                else:
                    break
            if len(run) >= 2:
                phrases.append(" ".join(run))
            elif len(run) == 1 and len(run[0]) > 2:
                phrases.append(run[0])
            i = j
        else:
            i += 1
    # Dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for phrase in phrases:
        key = phrase.lower()
        if key not in seen:
            seen.add(key)
            out.append(phrase)
    return out


def topic_shorthand_context(topic: str) -> str:
    """Build nickname / short-form + desi hangout flavor for the topic."""
    topic = (topic or "").strip()
    if not topic:
        return "No special nicknames — still stay warm and funny on the topic."

    lines = [
        f'Full topic: "{topic}"',
        "Treat this as ONE shared context for the whole show.",
        "You may use natural short forms and nicknames for names in the topic:",
    ]

    names = _candidate_name_phrases(topic)
    if names:
        for name in names[:4]:
            parts = [p for p in name.replace("-", " ").split() if p]
            initials = "".join(p[0].upper() for p in parts if p)
            last = parts[-1] if parts else name
            first = parts[0] if parts else name
            shorts = [s for s in [initials, last, first] if s and s.lower() != name.lower()]
            # unique shorts
            uniq: list[str] = []
            for s in shorts:
                if s not in uniq:
                    uniq.append(s)
            if uniq:
                lines.append(
                    f'- "{name}" → also say {", ".join(repr(s) for s in uniq)} '
                    "(mix them naturally; don't explain the nickname)."
                )
            else:
                lines.append(f'- "{name}" — use casually when it fits.')
    else:
        lines.append(
            "- If the topic has a long name/title, invent a friendly short form once "
            "(initials or last word) and reuse it."
        )

    lines.extend(
        [
            "Desi hangout flavor (light, warm — sprinkle, don't dump):",
            '- Casual bits like: "arre yaar", "hai na", "bas", "yaar", "matlab", '
            '"seriously yaar", "ok suno", "bilkul".',
            "- Match language setting: if speaking English, keep desi words as light seasoning; "
            "if speaking Hindi/Tamil/etc., lean into natural local hangout speech.",
            "- Never force every sentence to be slang; never mock accents or punch down.",
        ]
    )
    return "\n".join(lines)


def mood_instruction(mood: DebateMood) -> str:
    """Return style guidance for the selected conversation mood."""
    return MOOD_STYLE.get(mood, MOOD_STYLE[DebateMood.SERIOUS])


WORDS_PER_MINUTE = 140


def word_target_for_seconds(seconds: int) -> tuple[int, int, int]:
    """Return (target, soft_min, hard_max) word counts for a spoken duration."""
    target = max(28, round(seconds * WORDS_PER_MINUTE / 60))
    soft_min = max(18, round(target * 0.5))
    hard_max = round(target * 1.0)
    return target, soft_min, hard_max


def agent_length_instruction(turn_seconds: int) -> str:
    """Length guidance: prefer short spoken turns within the time budget."""
    target, soft_min, hard_max = word_target_for_seconds(turn_seconds)
    return (
        f"Prefer 2–4 spoken sentences. Hard MAX {hard_max} words (~{turn_seconds}s); "
        f"usually {soft_min}-{target}. Never pad."
    )


def host_length_instruction(turn_seconds: int, segment: HostSegment) -> str:
    """Much shorter Host remarks than guest turns."""
    guest_target, _, _ = word_target_for_seconds(turn_seconds)
    if segment == HostSegment.OPENING:
        target = max(16, round(guest_target * 0.18))
        prefer = "1–2 short spoken sentences"
    elif segment == HostSegment.CLOSING:
        target = max(14, round(guest_target * 0.15))
        prefer = "1–2 short spoken sentences"
    else:
        target = max(10, round(guest_target * 0.1))
        prefer = "ONE short bridge sentence (two max)"
    hard_max = max(target + 4, round(target * 1.15))
    return (
        f"{prefer}. Hard MAX {hard_max} words — far shorter than guests. "
        "Never match guest length. No padding."
    )


def round_focus_instruction(round_number: int, total_rounds: int) -> str:
    """How this segment should progress the conversation."""
    if total_rounds <= 1:
        return "Share your take on the show topic with a smile, then stop."
    if round_number <= 1:
        return "Open with your angle on the show topic — warm, funny; leave room for others."
    if round_number >= total_rounds:
        return (
            "Closing beat — reflect on the show topic with a light joke; "
            "do not rehash or rebut earlier points."
        )
    if total_rounds == 2:
        return (
            "Add a fresh angle on the show topic. Acknowledge the last speaker briefly; "
            "prefer building on them over contradicting them."
        )
    progress = (round_number - 1) / max(1, total_rounds - 1)
    if progress < 0.4:
        return (
            "Deepen the show topic. Agree or partly agree when fair; "
            "add something new — do not auto-counter."
        )
    if progress < 0.7:
        return (
            "Bring a concrete on-topic example. Brief nod to the last speaker only — "
            "do not chase their side joke or metaphor."
        )
    return "Talk implications of the show topic lightly — advance, stay warm, avoid rebuttals."


def controversy_instruction(controversial: bool) -> str:
    if controversial:
        return (
            "People can see this topic differently — still prefer agreement and building. "
            "Do NOT rebut every point. Soft humorous disagreement only when you truly differ. "
            "Never turn the chat into point-by-point opposition."
        )
    return (
        "Friendly hangout energy. Agree often, build on good points, "
        "and add a new on-topic angle. Do not invent disagreements."
    )


class DynamicPromptTemplate:
    """Simple named template that renders with ``$placeholders``."""

    def __init__(self, template: str) -> None:
        self._template = Template(template)

    def render(self, **values: str) -> str:
        return self._template.safe_substitute(**values).strip()


GUEST_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
TOPIC LOCK: You are talking ONLY about "$topic". Do not change the subject.

You are $speaker_name, a co-host on a witty talk show — more comedy podcast hangout than heated debate.

Primary goal: keep listeners hooked with a believable, warm, funny chat ABOUT "$topic" —
natural podcast energy, not a script, not a debate, not auto-countering, not chasing side threads.
If your line would make someone lose interest, make it fresher and more human.

Other guests:
$guest_roster

Who you are:
$personality

Your lean (subtle — NOT a mandate to oppose others):
$viewpoint

Mood dial for tonight:
$mood_style

$controversy_mode

$simple_language

$keep_listeners_hooked

$tone_guidance

$dialogue_rules

Shared topic nicknames / hangout flavor:
$topic_shorthand

Hard behaviour:
- Speak in $language_label. Every joke/analogy must serve "$topic".
- Listening: briefly acknowledge the previous speaker, then add a NEW interesting point about "$topic".
- Prefer: "Fair point…" / "Yeah…" / "I like that…" then advance the topic with something fresh.
- Forbidden as a habit: rebutting every claim, debating their joke/metaphor, following a tangent
  that leaves "$topic", or sounding flat / repetitive / lecture-y.
- Topic notes are optional context for "$topic" only — never recite headlines or cite sources.
- Ignore any hint, news line, or previous side-bit that is not about "$topic".
- Never repeat an earlier point of yours.
- $length_instruction
""".strip()
)

GUEST_USER_TEMPLATE = DynamicPromptTemplate(
    """
SHOW TOPIC (mandatory — stay here): "$topic"

Round: $round_number / $total_rounds — $round_focus
You: $speaker_name

Previous speaker (brief nod only — then return to "$topic"; do NOT rebut point-by-point;
do NOT chase their joke/analogy/side example):
$reply_to

Conversation so far (about "$topic"):
$conversation_transcript

Optional supporting notes for "$topic" only (ignore if off-topic):
$news_context

Optional soft angle — only if it clearly relates to "$topic" (not a rebuttal script):
$scenario_seed

Optional lean notes — use to enrich "$topic", NOT to contradict the last speaker every turn:
$opinion_brief

Other on-topic angles later (do not dump now):
$unused_angles

Speak as $speaker_name about "$topic" — warm, natural, comedy-forward, 2–4 sentences.
Make it interesting for listeners. Agree or build when you can. Then stop.
""".strip()
)

HOST_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
TOPIC LOCK: This show is ONLY about "$topic". Keep every guest on that topic.

You are the host of a witty talk show — more comedy podcast hangout than heated debate.
Stay neutral, warm, and a little cheeky. Don't take a side.

Guests:
$guest_roster

Mood dial: $mood_style
Language: $language_label

$simple_language

$keep_listeners_hooked

$tone_guidance

$dialogue_rules

Shared topic nicknames / hangout flavor:
$topic_shorthand

Never say "Round N begins" or sound robotic.
Never ask guests to quote news or sources.
If a guest drifts off "$topic", gently pull them back — keep the show fun to listen to.
$length_instruction
No "Host:" label.
""".strip()
)

HOST_USER_TEMPLATE = DynamicPromptTemplate(
    """
SHOW TOPIC (mandatory): "$topic"
Segment: $segment
Round: $round_number / $total_rounds
Mood: $mood_name

Guests:
$guest_roster

Conversation so far (about "$topic"):
$conversation_transcript

Focus: $round_focus

Do this now (stay on "$topic"):
$segment_instructions
""".strip()
)


def render_guest_system_prompt(context: AgentContext) -> str:
    return GUEST_SYSTEM_TEMPLATE.render(
        speaker_name=context.speaker_name,
        guest_roster=context.guest_roster,
        personality=context.personality,
        viewpoint=context.viewpoint,
        topic=context.topic,
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
        length_instruction=agent_length_instruction(context.turn_seconds),
        controversy_mode=controversy_instruction(context.controversial),
        simple_language=SIMPLE_LANGUAGE,
        keep_listeners_hooked=KEEP_LISTENERS_HOOKED,
        tone_guidance=TONE_GUIDANCE,
        dialogue_rules=DIALOGUE_RULES,
        topic_shorthand=topic_shorthand_context(context.topic),
    )


def render_guest_user_prompt(context: AgentContext) -> str:
    reply_to = (context.reply_to or "").strip() or (
        "(You open — share a warm, witty take on the show topic.)"
    )
    seed = (context.scenario_seed or "").strip() or "(None — stay concrete and funny on the topic.)"
    return GUEST_USER_TEMPLATE.render(
        topic=context.topic,
        speaker_name=context.speaker_name,
        round_number=str(context.round_number),
        total_rounds=str(context.total_rounds),
        round_focus=context.round_focus,
        conversation_transcript=context.conversation_transcript,
        reply_to=reply_to,
        scenario_seed=seed,
        unused_angles=context.unused_angles or "(Keep exploring fresh sides when needed.)",
        opinion_brief=context.opinion_brief or "(Use your personality lean.)",
        news_context=context.news_context
        or "(No notes — personal or hypothetical takes with a smile are fine.)",
    )


def render_support_system_prompt(context: AgentContext) -> str:
    return render_guest_system_prompt(context)


def render_opposition_system_prompt(context: AgentContext) -> str:
    return render_guest_system_prompt(context)


def render_support_user_prompt(context: AgentContext) -> str:
    return render_guest_user_prompt(context)


def render_opposition_user_prompt(context: AgentContext) -> str:
    return render_guest_user_prompt(context)


def render_host_system_prompt(context: HostContext) -> str:
    return HOST_SYSTEM_TEMPLATE.render(
        topic=context.topic,
        guest_roster=context.guest_roster,
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
        length_instruction=host_length_instruction(
            context.turn_seconds, context.segment
        ),
        tone_guidance=TONE_GUIDANCE,
        dialogue_rules=HOST_DIALOGUE_RULES,
        simple_language=SIMPLE_LANGUAGE,
        keep_listeners_hooked=KEEP_LISTENERS_HOOKED,
        topic_shorthand=topic_shorthand_context(context.topic),
    )


def _host_segment_instructions(context: HostContext) -> str:
    first_guest = "the first guest"
    guest_names: list[str] = []
    if context.guest_roster:
        for line in context.guest_roster.strip().splitlines():
            if not line.startswith("- "):
                continue
            name = line[2:].split("(", 1)[0].strip()
            if name:
                guest_names.append(name)
        if guest_names:
            first_guest = guest_names[0]
    guests_thanks = ", ".join(guest_names) if guest_names else "the guests"

    if context.segment == HostSegment.OPENING:
        return (
            f"ONE short welcome (1–2 sentences). Name \"{context.topic}\" with a witty hook, "
            f"hand straight to {first_guest}. No second intro. Don't take a side."
        )
    if context.segment == HostSegment.ROUND:
        if context.round_number >= context.total_rounds:
            return (
                "ONE short cue for a closing reflection — smile, no countdown language."
            )
        return (
            "ONE short bridge — nod, steer to the show topic, name a guest. "
            "Never force a fight. Never say \"Round N begins.\""
        )
    return (
        f'ONE short wrap about "{context.topic}" (1–2 sentences). '
        f"Thank {guests_thanks} + audience, witty closer, hangout vibe."
    )


def render_host_user_prompt(context: HostContext) -> str:
    return HOST_USER_TEMPLATE.render(
        segment=context.segment.value,
        topic=context.topic,
        language_label=language_label(context.language),
        mood_name=context.mood.value,
        round_number=str(context.round_number),
        total_rounds=str(context.total_rounds),
        guest_roster=context.guest_roster,
        conversation_transcript=context.conversation_transcript,
        round_focus=context.round_focus,
        segment_instructions=_host_segment_instructions(context),
    )
