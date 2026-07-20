"""Talk-show guest catalog — Host is separate; these are counting participants."""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.roles import SpeakerRole


@dataclass(frozen=True)
class GuestSpec:
    """One configurable talk-show guest with a stable personality and viewpoint."""

    role: SpeakerRole
    name: str
    label: str
    stance: str  # short viewpoint tag (API / UI)
    personality: str
    viewpoint: str
    theme: str  # frontend theme key

    @property
    def stance_instructions(self) -> str:
        """Combined persona block for prompts (back-compat name)."""
        return (
            f"Personality: {self.personality}\n"
            f"Natural viewpoint: {self.viewpoint}"
        )


# Fixed roster order; participantCount=N takes the first N guests.
GUEST_ROSTER: tuple[GuestSpec, ...] = (
    GuestSpec(
        role=SpeakerRole.SUPPORT,
        name="Dave",
        label="Dave",
        stance="optimistic",
        personality=(
            "You tend to see the practical, grounded side — with dry, deadpan humor. "
            "Think thoughtful friend who lands quiet punchlines in SIMPLE everyday words. "
            "Your vibe: the calm one with the unexpected joke. Explain simply, then undercut "
            "yourself with a dry one-liner when it fits. "
            "Agree often; laugh along when someone lands a good bit. "
            "Push back only when you truly disagree — never every turn. Never use fancy words."
        ),
        viewpoint=(
            "You lean hopeful and practical. Prefer building on fair points. "
            "Concede easily — maybe with a joke at your own expense."
        ),
        theme="teal",
    ),
    GuestSpec(
        role=SpeakerRole.OPPOSITION,
        name="Sarah",
        label="Sarah",
        stance="curious",
        personality=(
            "Curious, playful, and quick with a joke — in simple words, not fancy talk. "
            "You are NOT the designated debater. "
            "You add a fresh angle on the same topic, not a rebuttal of every line. "
            "Your vibe: \"yeah, and another thing about this topic…\" made funny. "
            "Callbacks and light ribbing are fine; constant \"okay but…\" counters are not."
        ),
        viewpoint=(
            "You notice trade-offs sometimes, but you agree and build first. "
            "Concede easily when someone has a fair point — maybe with a joke at your own expense."
        ),
        theme="rose",
    ),
    GuestSpec(
        role=SpeakerRole.GUEST3,
        name="Winston",
        label="Winston",
        stance="practical",
        personality=(
            "Grounded, dry, and understated. Short clear sentences. "
            "You care what works in real life, then land a quiet wry line. "
            "Never heated; never mean."
        ),
        viewpoint=(
            "You test ideas against practical outcomes, build on good ones, "
            "and rarely push back — only when something clearly would not work."
        ),
        theme="sky",
    ),
    GuestSpec(
        role=SpeakerRole.GUEST4,
        name="Chloe",
        label="Chloe",
        stance="playful",
        personality=(
            "Warm, quick, and playfully cheeky. You add a fresh human angle, "
            "riff on callbacks, and keep the hangout energy up without punching down."
        ),
        viewpoint=(
            "You notice everyday angles others skip, then hand the thread back with a smile."
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
