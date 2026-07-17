"""Shared agent prompt/context dataclasses."""

from dataclasses import dataclass

from app.schemas.debate_request import DebateMood
from app.schemas.debate_response import SpeakerRole
from app.schemas.roles import HostSegment


@dataclass(frozen=True)
class AgentPrompt:
    """Fully built prompts — the only LLM input for an agent turn."""

    system_prompt: str
    user_prompt: str
    round_number: int
    side: SpeakerRole
    # Always carried so every LLM call can re-assert the topic lock.
    topic: str = ""


def topic_locked_prompts(prompt: AgentPrompt) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) with the topic forced into both.

    Guarantees every provider call sees the show topic at the top of both
    system and user messages — even if a template is thin or comedy riffs wander.
    """
    topic = (prompt.topic or "").strip() or "(unspecified topic)"
    lock = (
        f'TOPIC LOCK — The only subject of this turn is: "{topic}". '
        "Every sentence must clearly relate to this topic. "
        "Use simple everyday words with light humor — no complex vocabulary. "
        "Keep it natural and interesting so listeners do not lose interest. "
        "Jokes, analogies, and reactions must be about this topic — never a side subject. "
        "Do NOT auto-counter the previous speaker. "
        "Do NOT chase their joke, metaphor, or side example away from the topic. "
        "Brief acknowledgment → new point on the show topic."
    )
    system = f"{lock}\n\n{prompt.system_prompt}".strip()
    user = (
        f'SHOW TOPIC (mandatory): "{topic}"\n'
        "Stay on this topic for the entire reply.\n"
        "Do not rebut every prior point. Do not divert onto a prior speaker's side bit.\n\n"
        f"{prompt.user_prompt}"
    ).strip()
    return system, user


@dataclass(frozen=True)
class AgentContext:
    """Structured context used to render guest prompts (natural conversation)."""

    topic: str
    mood: DebateMood
    language: str
    round_number: int
    total_rounds: int
    turn_seconds: int
    side: SpeakerRole
    speaker_name: str
    personality: str
    viewpoint: str
    conversation_transcript: str
    round_focus: str
    guest_roster: str
    news_context: str = ""
    # Previous guest's last turn — continue this thread in-round.
    reply_to: str = ""
    # Soft conversation angle for this turn (hint, not a news script).
    scenario_seed: str = ""
    # Other unused angles so the show keeps covering fresh content.
    unused_angles: str = ""
    # Controversial topics get clearer mixed opinions / debate energy.
    controversial: bool = False
    # Side-leaning brief for this guest (FOR/AGAINST).
    opinion_brief: str = ""


@dataclass(frozen=True)
class HostContext:
    """Context for Host Agent segments (opening / round / closing)."""

    topic: str
    mood: DebateMood
    language: str
    round_number: int
    total_rounds: int
    turn_seconds: int
    segment: HostSegment
    guest_roster: str
    conversation_transcript: str
    round_focus: str
    news_context: str = ""
    controversial: bool = False
