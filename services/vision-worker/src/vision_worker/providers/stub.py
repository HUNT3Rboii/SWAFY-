"""Stub provider with canned results, selectable by STUB_MODE.

Used for local development, CI, and tests when no real API key is set, so
backend and mobile can integrate before the real LLM exists.
STUB_MODE=safe|unsafe|unavailable|error.

The stub shares the Provider interface so providers are swappable.
"""

from __future__ import annotations

from typing import Any

from . import Provider

# Canned results, one per STUB_MODE value. They follow the BE-1 rules:
# unsafe -> category unknown; unavailable -> category unknown, confidence null.
_STUB_RESULTS: dict[str, dict[str, Any]] = {
    "safe": {
        "outcome": "safe",
        "category": "pothole",
        "confidence": 0.98,
        "reason": "Stub canned result: street scene with a damaged road.",
    },
    "unsafe": {
        "outcome": "unsafe",
        "category": "unknown",
        "confidence": 0.99,
        "reason": "Stub canned result: explicit content rejected.",
    },
    "unavailable": {
        "outcome": "unavailable",
        "category": "unknown",
        "confidence": None,
        "reason": "Stub canned result: provider could not decide.",
    },
}

STUB_MODES = frozenset({*_STUB_RESULTS, "error"})


class StubProvider(Provider):
    """Returns canned results. In 'error' mode it raises before returning."""

    name = "stub"

    def __init__(self, mode: str = "safe") -> None:
        if mode not in STUB_MODES:
            raise ValueError(f"unknown STUB_MODE: {mode!r}")
        self.mode = mode

    def classify(self, image_path: str) -> dict[str, Any]:
        if self.mode == "error":
            raise RuntimeError("stub provider injected failure")
        return dict(_STUB_RESULTS[self.mode])
