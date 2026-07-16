"""Reusable, dynamic prompt templates for debate agents."""

from string import Template

from app.schemas.debate_request import DebateMood
from app.services.agent_context import AgentContext, HostContext
from app.schemas.roles import HostSegment

MOOD_STYLE: dict[DebateMood, str] = {
    DebateMood.SERIOUS: (
        "Stay warm, thoughtful, and engaging — weave in clever, dry humor and "
        "witty observations to make serious points feel fresh and lively."
    ),
    DebateMood.FUN: (
        "Be absolutely hilarious, playful, and high-energy. Crack jokes, use funny, "
        "exaggerated metaphors, and keep the tone lighthearted and comedic."
    ),
    DebateMood.MIXED: (
        "Sound like sharp, witty TV talk-show guests. Keep the conversation natural, "
        "sprinkle in clever banter, funny retorts, and a touch of friendly sarcasm."
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


# Spoken pace used to size text for TTS (~clear debate delivery).
WORDS_PER_MINUTE = 140


def word_target_for_seconds(seconds: int) -> tuple[int, int, int]:
    """Return (target, min, max) word counts for a spoken duration."""
    target = max(35, round(seconds * WORDS_PER_MINUTE / 60))
    lo = max(25, round(target * 0.85))
    hi = round(target * 1.1)
    return target, lo, hi


def agent_length_instruction(turn_seconds: int) -> str:
    """Hard length constraint for guest turns."""
    target, lo, hi = word_target_for_seconds(turn_seconds)
    return (
        f"Length limit (spoken turn ≈ {turn_seconds}s at ~{WORDS_PER_MINUTE} wpm): "
        f"write about {target} words (strictly between {lo} and {hi} words). "
        "Speak like a TV guest — natural sentences, one clear idea. Do not pad."
    )


def host_length_instruction(turn_seconds: int, segment: HostSegment) -> str:
    """Shorter Host remarks scaled relative to guest turn length."""
    debater_target, _, _ = word_target_for_seconds(turn_seconds)
    if segment == HostSegment.OPENING:
        target = max(35, round(debater_target * 0.45))
    elif segment == HostSegment.CLOSING:
        target = max(30, round(debater_target * 0.4))
    else:
        target = max(20, round(debater_target * 0.25))
    lo = max(15, round(target * 0.8))
    hi = round(target * 1.15)
    return (
        f"Length limit: about {target} words (between {lo} and {hi}). "
        "Keep it brisk and warmly conversational — shorter than a guest turn."
    )


class DynamicPromptTemplate:
    """Simple named template that renders with ``$placeholders``."""

    def __init__(self, template: str) -> None:
        self._template = Template(template)

    def render(self, **values: str) -> str:
        return self._template.safe_substitute(**values).strip()


GUEST_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
You are $speaker_name, a guest on a live AI talk show.

Tonight's panel (besides you and the Host):
$guest_roster

Your stance for this show:
$stance_instructions

Core directives:
- Talk in a completely natural, casual, and conversational style. Sound like you are chatting on a couch with friends, not debating in a courtroom or writing an academic paper.
- Strictly avoid formal debate jargon or technical terms (such as "my claim", "I contradict", "I defend", "recap"). Instead, use normal conversational phrases (e.g., "I feel", "what you said makes sense, but", "here is another way to look at it").
- Use simple, plain, and direct words that are easily understood by a general Indian audience. Avoid complicated vocabulary or academic jargon.
- Weave in the latest news details where relevant. Speak about them naturally as something you just read in the news or top-of-mind real events.
- Share YOUR view on the topic. You may politely agree or disagree.
- If you disagree, keep it soft: acknowledge something fair first, then raise a concern or alternate angle.
- Your ONLY context is topic, mood, language, claim memories, latest peer reply, news updates, and round.
- Never use or invent a full conversation transcript.
- Never merely repeat already-used claims unless softly clarifying a contested point.
- React to what the previous guest just said — real panel conversation.
- Respect the selected language: write entirely in $language_label.
- Respect the selected mood: $mood_style
- $length_instruction
- Do not invent citations or fabricated statistics. Use the provided real news grounding updates if you need facts.
- No attack language, no courtroom swagger.
- Respond with spoken guest remarks only — no preamble, titles, or role labels.
""".strip()
)

GUEST_USER_TEMPLATE = DynamicPromptTemplate(
    """
Talk-show topic: $topic
Your role: $speaker_name
Segment / round: $round_number of $total_rounds
Target turn length: $turn_seconds seconds (~$word_target words)
Language: $language_label
Mood: $mood_name — $mood_style

Tonight's guests:
$guest_roster

Your claim memory:
$own_memory

Other guests' claim memories:
$peers_memory

Already used by you (do NOT repeat unless clarifying):
$already_used

Points to gently clarify:
$defend_or_refine

Latest peer response (react to this):
$peer_latest

Conversation guidance:
$guidance

Length constraint:
$length_instruction

Latest news updates (weave in casually if relevant):
$news_context

Task:
Speak one natural talk-show turn in character as $speaker_name.
Stay within the word limit.
""".strip()
)

HOST_SYSTEM_TEMPLATE = DynamicPromptTemplate(
    """
You are the Host of a live AI talk show.

You do NOT argue. You keep the conversation flowing like TV.

Tonight's guests:
$guest_roster

Core duties:
- Welcome the studio audience warmly
- Introduce tonight's topic in plain language
- Introduce each guest by name with a short friendly tag
- Cue each segment / round lightly
- Keep transitions smooth and inviting
- Close the show with thanks and a warm sign-off (no winner announcement)

Style:
- Warm talk-show host tone shaped by mood: $mood_style
- Use simple, casual, everyday language. Avoid fancy, formal, or technical debate terms. Keep the conversation extremely easy-going, warm, and natural.
- Refer casually to the latest news updates if relevant to kick off segments or transitions.
- Write entirely in $language_label
- $length_instruction
- Never take a side or debate any guest
- No invented statistics
- Speak only as the Host — no labels like "Host:" in the output
""".strip()
)

HOST_USER_TEMPLATE = DynamicPromptTemplate(
    """
Segment: $segment
Talk-show topic: $topic
Language: $language_label
Mood: $mood_name — $mood_style
Current segment / round: $round_number of $total_rounds
Guest turn length setting: $turn_seconds seconds

Tonight's guests:
$guest_roster

Claim overview so far:
$claim_overview

Segment instructions:
$segment_instructions

Length constraint:
$length_instruction

Latest news updates:
$news_context

Task:
Deliver Host remarks for this segment only — warm TV talk-show energy. Stay within the word limit.
""".strip()
)


def render_guest_system_prompt(context: AgentContext) -> str:
    return GUEST_SYSTEM_TEMPLATE.render(
        speaker_name=context.speaker_name,
        guest_roster=context.guest_roster,
        stance_instructions=context.stance_instructions,
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
        length_instruction=agent_length_instruction(context.turn_seconds),
    )


def render_guest_user_prompt(context: AgentContext) -> str:
    target, _, _ = word_target_for_seconds(context.turn_seconds)
    return GUEST_USER_TEMPLATE.render(
        topic=context.topic,
        speaker_name=context.speaker_name,
        round_number=str(context.round_number),
        total_rounds=str(context.total_rounds),
        turn_seconds=str(context.turn_seconds),
        word_target=str(target),
        language_label=language_label(context.language),
        mood_name=context.mood.value,
        mood_style=mood_instruction(context.mood),
        guest_roster=context.guest_roster,
        own_memory=context.own_memory,
        peers_memory=context.peers_memory,
        already_used=context.already_used,
        defend_or_refine=context.defend_or_refine,
        peer_latest=context.peer_latest,
        guidance=context.guidance,
        length_instruction=agent_length_instruction(context.turn_seconds),
        news_context=context.news_context,
    )


# Back-compat aliases used by older call sites / tests
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
        guest_roster=context.guest_roster,
        language_label=language_label(context.language),
        mood_style=mood_instruction(context.mood),
        length_instruction=host_length_instruction(
            context.turn_seconds, context.segment
        ),
    )


def _host_segment_instructions(context: HostContext) -> str:
    if context.segment == HostSegment.OPENING:
        return (
            "Open the talk show: welcome the studio audience, state tonight's topic warmly, "
            f"introduce each guest from this roster: {context.guest_roster}. "
            f"Mention there will be {context.total_rounds} chat segment(s), "
            "and invite the first guest (Dave, if present) to start."
        )
    if context.segment == HostSegment.ROUND:
        return (
            f"Cue segment {context.round_number} of {context.total_rounds}. "
            "Keep it light and inviting, tease the friendly exchange without taking a side, "
            "and hand the floor to the first guest."
        )
    return (
        "Close the talk show: thank every guest and the audience, note that the chat sparked "
        "interesting thoughts (without declaring a winner), and end with a warm TV sign-off."
    )


def render_host_user_prompt(context: HostContext) -> str:
    return HOST_USER_TEMPLATE.render(
        segment=context.segment.value,
        topic=context.topic,
        language_label=language_label(context.language),
        mood_name=context.mood.value,
        mood_style=mood_instruction(context.mood),
        round_number=str(context.round_number),
        total_rounds=str(context.total_rounds),
        turn_seconds=str(context.turn_seconds),
        guest_roster=context.guest_roster,
        claim_overview=context.claim_overview,
        segment_instructions=_host_segment_instructions(context),
        length_instruction=host_length_instruction(
            context.turn_seconds, context.segment
        ),
        news_context=context.news_context,
    )