"""Talk-show guest catalog — Host is separate; these are counting participants."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.roles import SpeakerRole


@dataclass(frozen=True)
class GuestSpec:
    """One configurable talk-show guest."""

    role: SpeakerRole
    name: str
    label: str
    stance: str
    stance_instructions: str
    theme: str  # frontend theme key


# Fixed roster order; participantCount=N takes the first N guests.
GUEST_ROSTER: tuple[GuestSpec, ...] = (
    GuestSpec(
        role=SpeakerRole.SUPPORT,
        name="Dave",
        label="Dave",
        stance="enthusiast",
        stance_instructions=(
            "You are Dave. Be warm, hyper-enthusiastic, and completely hilarious. "
            "You love the topic and think it is the absolute greatest idea ever conceived. "
            "Defend it using wild, over-the-top analogies, funny everyday examples, "
            "and a contagiously positive vibe."
        ),
        theme="teal",
    ),
    GuestSpec(
        role=SpeakerRole.OPPOSITION,
        name="Sarah",
        label="Sarah",
        stance="skeptic",
        stance_instructions=(
            "You are Sarah. Be a witty, sarcastic skeptic. You are highly skeptical "
            "of the topic but express it through dry humor, playful sarcasm, and "
            "self-deprecating jokes. Never be mean or aggressive; instead, raise "
            "hilarious doubts and highlight funny downsides or absurd consequences."
        ),
        theme="rose",
    ),
    GuestSpec(
        role=SpeakerRole.GUEST3,
        name="Winston",
        label="Winston",
        stance="realist",
        stance_instructions=(
            "You are Winston. You are a dry, drama-loving pragmatist who filters "
            "everything through daily life frustrations (like missing the bus, bad WiFi, "
            "or losing a sock). Argue from a funny, down-to-earth perspective: "
            "caution where it's a hassle, support where it makes life lazier."
        ),
        theme="sky",
    ),
    GuestSpec(
        role=SpeakerRole.GUEST4,
        name="Chloe",
        label="Chloe",
        stance="tangent_generator",
        stance_instructions=(
            "You are Chloe. You are a completely unpredictable wild card who brings "
            "hilarious, absurd, or bizarrely specific hypothetical scenarios. Stay friendly, "
            "but derail the conversation slightly with comedic tangents that somehow loop "
            "back to the topic."
        ),
        theme="violet",
    ),
)


def guests_for_count(count: int) -> list[GuestSpec]:
    """Return the first ``count`` guests (2–4)."""
    n = max(2, min(4, int(count)))
    return list(GUEST_ROSTER[:n])


def guest_by_role(role: SpeakerRole) -> GuestSpec | None:
    for guest in GUEST_ROSTER:
        if guest.role == role:
            return guest
    return None


def is_guest_role(role: SpeakerRole) -> bool:
    return role in {
        SpeakerRole.SUPPORT,
        SpeakerRole.OPPOSITION,
        SpeakerRole.GUEST3,
        SpeakerRole.GUEST4,
    }


def guest_public_meta(count: int) -> list[dict[str, str]]:
    """JSON-friendly participant list for SSE / frontend."""
    return [
        {
            "role": g.role.value,
            "name": g.name,
            "label": g.label,
            "stance": g.stance,
            "theme": g.theme,
        }
        for g in guests_for_count(count)
    ]
