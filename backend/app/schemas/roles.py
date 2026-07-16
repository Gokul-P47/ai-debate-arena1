"""Shared debate enums."""

from enum import Enum


class SpeakerRole(str, Enum):
    """Who is speaking in the talk show.

    Guests: support / opposition / guest3 / guest4 (participantCount selects first N).
    Host is always present and is not counted as a participant.
    """

    HOST = "host"
    SUPPORT = "support"
    OPPOSITION = "opposition"
    GUEST3 = "guest3"
    GUEST4 = "guest4"


class HostSegment(str, Enum):
    """Which hosting duty the Host Agent is performing."""

    OPENING = "opening"
    ROUND = "round"
    CLOSING = "closing"
