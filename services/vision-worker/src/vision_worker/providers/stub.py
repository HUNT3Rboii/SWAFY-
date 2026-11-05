"""Stub provider with canned results, selectable by STUB_MODE.

Used for local development, CI, and tests when no real API key is set.
STUB_MODE=safe|unsafe|unavailable|error.

The stub shares the Provider interface so providers are swappable.
"""

from __future__ import annotations

from typing import Any

from . import Provider

# Canned results, one per STUB_MODE value. category "unknown" is a worker-only
# value meaning "the model could not decide" - it is never stored in the DB.
_STUB_RESULTS: dict[str, dict[str, Any]] = {
    "safe": {
        "status": "safe",
        "category": "pothole",
        "confidence": 0.98,
        "reason": "Stub canned result: street scene with a damaged road.",
    },
    "unsafe": {
        "status": "unsafe",
        "category": "other",
        "confidence": 0.99,
        "reason": "Stub canned result: explicit content rejected.",
    },
    "unavailable": {
        "status": "unavailable",
        "category": "unknown",
        "confidence": 0.0,
        "reason": "Stub canned result: provider could not decide.",
    },
}


class StubProvider(Provider):
    """Returns canned results. In 'error' mode it raises before returning."""

    def __init__(self, mode: str = "safe") -> None:
        if mode not in {"safe", "unsafe", "unavailable", "error"}:
            raise ValueError(f"unknown STUB_MODE: {mode!r}")
        self.mode = mode

    def classify(self, image_path: str) -> dict[str, Any]:
        if self.mode == "error":
            raise RuntimeError("stub provider injected failure")
        return dict(_STUB_RESULTS[self.mode])