"""Prompt helpers — re-exports dynamic templates for convenience."""

from app.core.prompt_templates import (
    MOOD_STYLE,
    language_label,
    mood_instruction,
    render_opposition_system_prompt,
    render_opposition_user_prompt,
    render_support_system_prompt,
    render_support_user_prompt,
)

__all__ = [
    "MOOD_STYLE",
    "language_label",
    "mood_instruction",
    "render_opposition_system_prompt",
    "render_opposition_user_prompt",
    "render_support_system_prompt",
    "render_support_user_prompt",
]
