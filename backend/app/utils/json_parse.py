"""Helpers for parsing structured JSON from LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL | re.IGNORECASE)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


def parse_json_payload(text: str) -> Any:
    """Extract and parse a JSON object/array from model output.

    Raises:
        ValueError: If no valid JSON can be parsed.
    """
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Empty LLM response")

    candidates: list[str] = [cleaned]
    fence = _JSON_FENCE_RE.search(cleaned)
    if fence:
        candidates.insert(0, fence.group(1))
    obj = _JSON_OBJECT_RE.search(cleaned)
    if obj:
        candidates.append(obj.group(0))
    arr = _JSON_ARRAY_RE.search(cleaned)
    if arr:
        candidates.append(arr.group(0))

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
    raise ValueError(f"Could not parse JSON from LLM response: {last_error}")
