"""Classification result type and JSON-schema validation.

Every classify() result validates against services/vision-worker/schema.json.
Invalid output counts as a failure (unavailable), never as a guess.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import jsonschema

_STATUS = {"safe", "unsafe", "unavailable"}
_CATEGORY = {"pothole", "trash", "graffiti", "broken_light", "other", "unknown"}

# Load the committed schema once so the worker and the tests share one source
# of truth. The schema lives in this service (not docs/) and stays here.
_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schema.json"

with open(_SCHEMA_PATH, "r", encoding="utf-8") as _fh:
    _SCHEMA: Dict[str, Any] = json.load(_fh)


class ClassificationResult:
    """Result of classifying a single photo.

    status   : "safe" | "unsafe" | "unavailable"
    category : one of the five frozen categories, or "unknown" (worker-only)
    confidence: 0.0 to 1.0
    reason   : short human-readable explanation
    """

    __slots__ = ("status", "category", "confidence", "reason")

    def __init__(self, status: str, category: str, confidence: float, reason: str) -> None:
        self.status = status
        self.category = category
        self.confidence = confidence
        self.reason = reason

    def __repr__(self) -> str:
        return (
            f"ClassificationResult(status={self.status!r}, category={self.category!r}, "
            f"confidence={self.confidence!r}, reason={self.reason!r})"
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "category": self.category,
            "confidence": self.confidence,
            "reason": self.reason,
        }

    def validate(self) -> None:
        """Validate this result against schema.json. Raises jsonschema.ValidationError on failure."""
        jsonschema.validate(self.as_dict(), _SCHEMA)


def validate_dict(payload: Dict[str, Any]) -> ClassificationResult:
    """Validate a raw dict (e.g. from a model) against the schema and build a result.

    Raises jsonschema.ValidationError if the payload does not conform.
    """
    jsonschema.validate(payload, _SCHEMA)
    return ClassificationResult(
        status=payload["status"],
        category=payload["category"],
        confidence=float(payload["confidence"]),
        reason=str(payload["reason"]),
    )