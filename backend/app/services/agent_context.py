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


@dataclass(frozen=True)
class AgentContext:
    """Structured context used to render guest prompts."""

    topic: str
    mood: DebateMood
    language: str
    round_number: int
    total_rounds: int
    turn_seconds: int
    side: SpeakerRole
    speaker_name: str
    stance_instructions: str
    own_memory: str
    peers_memory: str
    peer_latest: str
    already_used: str
    defend_or_refine: str
    guidance: str
    guest_roster: str
    news_context: str = ""


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
    claim_overview: str
    news_context: str = ""
