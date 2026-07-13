"""Shared debate enums."""

from enum import Enum


class SpeakerRole(str, Enum):
    """Which side of the debate is speaking."""

    SUPPORT = "support"
    OPPOSITION = "opposition"
