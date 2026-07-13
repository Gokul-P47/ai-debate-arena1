"""Reusable, dynamic prompt templates for debate agents."""

from string import Template

from app.schemas.debate_request import DebateMood
from app.services.agent_context import AgentContext

MOOD_STYLE: dict[DebateMood, str] = {
    DebateMood.SERIOUS: (
        "Use a serious, formal debating tone. Prefer evidence, logic, and clear structure."
    ),
    DebateMood.FUN: (
        "Use a witty, energetic tone. Keep arguments playful but still substantive."
    ),
    DebateMood.MIXED: (
        "Blend serious reasoning with light wit. Stay persuasive and engaging."
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


def mood_instruction(mood: DebateMood) -> str:
    """Return style guidance for the selected debate mood."""
    return MOOD_STYLE.get(mood, MOOD_STYLE[DebateMood.SERIOUS])


class DynamicPromptTemplate:
    """Simple named template that renders with ``$placeholders``."""

    def __init__(self, template: str) -> None:
        self._template = Template(template)

    def render(self, **values: str) -> str:
        return self._template.safe_substitute(**values).strip()


SUPPORT_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
You are the Support agent in a structured debate.

Core directives:
- Support the debate topic with logical reasoning.
- Your ONLY context is topic, mood, language, claim memories, latest opponent response, and round.
- Never use or invent a full conversation transcript.
- Never merely repeat already-used claims unless you are explicitly defending a CONTRADICTED claim.
- If a claim is CONTRADICTED: defend it, refine it, or introduce something new.
- Advance the debate each round with meaningful progress.
- Respect the selected language: write entirely in $language_label.
- Respect the selected mood: $mood_style
- Do not invent citations or fabricated statistics.
- Respond with the argument only — no preamble, titles, or role labels.
""".strip()
)

OPPOSITION_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
You are the Opposition agent in a structured debate.

Core directives:
- Oppose the debate topic with logical reasoning.
- Your ONLY context is topic, mood, language, claim memories, latest opponent response, and round.
- Never use or invent a full conversation transcript.
- Directly counter the opponent's latest response and their ACTIVE claims.
- Never merely repeat already-used counterclaims unless defending a CONTRADICTED claim of your own.
- If your own claim is CONTRADICTED: defend/refine it or open a new line of attack.
- Respect the selected language: write entirely in $language_label.
- Respect the selected mood: $mood_style
- Do not invent citations or fabricated statistics.
- Respond with the counterargument only — no preamble, titles, or role labels.
""".strip()
)

SUPPORT_USER_TEMPLATE = DynamicPromptTemplate(
    """
Debate topic: $topic
Agent role: Support
Current round: $round_number of $total_rounds
Language: $language_label
Mood: $mood_name — $mood_style

Your claim memory (Support Memory):
$own_memory

Opponent claim memory (Opposition Memory):
$opponent_memory

Already used by you (do NOT repeat unless defending):
$already_used

Contradicted claims to defend or refine:
$defend_or_refine

Latest opponent response:
$opponent_latest

Strategy guidance:
$guidance

Task:
Produce ONE progressive supporting argument for this round.
Choose exactly one path: defend a contradicted claim, refine a challenged idea, or introduce a new claim.
""".strip()
)

OPPOSITION_USER_TEMPLATE = DynamicPromptTemplate(
    """
Debate topic: $topic
Agent role: Opposition
Current round: $round_number of $total_rounds
Language: $language_label
Mood: $mood_name — $mood_style

Your claim memory (Opposition Memory):
$own_memory

Opponent claim memory (Support Memory):
$opponent_memory

Already used by you (do NOT repeat unless defending):
$already_used

Contradicted claims to defend or refine:
$defend_or_refine

Latest opponent response (counter this):
$opponent_latest

Strategy guidance:
$guidance

Task:
Produce ONE progressive counterargument for this round.
Choose exactly one path: challenge an ACTIVE opponent claim, defend your contradicted claim, or introduce a new attack line.
""".strip()
)


def render_support_system_prompt(context: AgentContext) -> str:
    return SUPPORT_SYSTEM_TEMPLATE.render(
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
    )


def render_opposition_system_prompt(context: AgentContext) -> str:
    return OPPOSITION_SYSTEM_TEMPLATE.render(
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
    )


def _common_user_values(context: AgentContext) -> dict[str, str]:
    return {
        "topic": context.topic,
        "round_number": str(context.round_number),
        "total_rounds": str(context.total_rounds),
        "language_label": language_label(context.language),
        "mood_name": context.mood.value,
        "mood_style": mood_instruction(context.mood),
        "own_memory": context.own_memory,
        "opponent_memory": context.opponent_memory,
        "already_used": context.already_used,
        "defend_or_refine": context.defend_or_refine,
        "opponent_latest": context.opponent_latest,
        "guidance": context.guidance,
    }


def render_support_user_prompt(context: AgentContext) -> str:
    return SUPPORT_USER_TEMPLATE.render(**_common_user_values(context))


def render_opposition_user_prompt(context: AgentContext) -> str:
    return OPPOSITION_USER_TEMPLATE.render(**_common_user_values(context))
