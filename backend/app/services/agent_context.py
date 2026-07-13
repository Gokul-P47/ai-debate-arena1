"""Shared agent prompt/context dataclasses."""

from dataclasses import dataclass

from app.schemas.debate_request import DebateMood
from app.schemas.debate_response import SpeakerRole


@dataclass(frozen=True)
class AgentPrompt:
    """Fully built prompts — the only LLM input for an agent turn."""

    system_prompt: str
    user_prompt: str
    round_number: int
    side: SpeakerRole


@dataclass(frozen=True)
class AgentContext:
    """Structured context used to render agent prompts."""

    topic: str
    mood: DebateMood
    language: str
    round_number: int
    total_rounds: int
    side: SpeakerRole
    own_memory: str
    opponent_memory: str
    opponent_latest: str
    already_used: str
    defend_or_refine: str
    guidance: str
