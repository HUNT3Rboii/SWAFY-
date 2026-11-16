"""Classification result type and JSON-schema validation.

Every classify() result validates against services/vision-worker/schema.json,
which matches the decision fields of PhotoCheckResultRequest in
docs/contracts/openapi.yaml (BE-1). Invalid output counts as a failure
(unavailable), never as a guess.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema

# Load the committed schema once so the worker and the tests share one source
# of truth.
_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schema.json"

with open(_SCHEMA_PATH, "r", encoding="utf-8") as _fh:
    _SCHEMA: Dict[str, Any] = json.load(_fh)


class ClassificationResult:
    """Result of classifying a single photo.

    outcome    : "safe" | "unsafe" | "unavailable"
    category   : one of the five frozen categories, or "unknown" (worker-only)
    confidence : 0.0 to 1.0, or None when outcome is "unavailable"
    reason     : short human-readable explanation
    provider   : "stub" | "gemini" | "groq" | "none"
    """

    __slots__ = ("outcome", "category", "confidence", "reason", "provider")

    def __init__(
        self,
        outcome: str,
        category: str,
        confidence: Optional[float],
        reason: str,
        provider: str,
    ) -> None:
        self.outcome = outcome
        self.category = category
        self.confidence = confidence
        self.reason = reason
        self.provider = provider

    def __repr__(self) -> str:
        return (
            f"ClassificationResult(outcome={self.outcome!r}, category={self.category!r}, "
            f"confidence={self.confidence!r}, reason={self.reason!r}, provider={self.provider!r})"
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome,
            "category": self.category,
            "confidence": self.confidence,
            "reason": self.reason,
            "provider": self.provider,
        }

    def validate(self) -> None:
        """Validate against schema.json. Raises jsonschema.ValidationError on failure."""
        jsonschema.validate(self.as_dict(), _SCHEMA)


def validate_dict(payload: Dict[str, Any]) -> ClassificationResult:
    """Validate a raw dict (e.g. from a model) against the schema and build a result.

    Raises jsonschema.ValidationError if the payload does not conform.
    """
    jsonschema.validate(payload, _SCHEMA)
    confidence = payload["confidence"]
    return ClassificationResult(
        outcome=payload["outcome"],
        category=payload["category"],
        confidence=None if confidence is None else float(confidence),
        reason=str(payload["reason"]),
        provider=str(payload["provider"]),
    )
