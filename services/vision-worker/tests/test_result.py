"""Tests for the result type and schema validation.

Every classify() result must validate against schema.json. Invalid output
counts as a failure (unavailable), never as a guess.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from vision_worker.result import ClassificationResult, validate_dict

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.json"


def test_schema_is_committed():
    """The JSON schema lives in this service, not docs/."""
    assert SCHEMA_PATH.is_file()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["status"]["enum"] == ["safe", "unsafe", "unavailable"]


def test_valid_results_validate():
    """The three real statuses and the frozen categories all pass."""
    for status in ("safe", "unsafe", "unavailable"):
        for category in ("pothole", "trash", "graffiti", "broken_light", "other", "unknown"):
            r = ClassificationResult(status, category, 0.5, "ok")
            r.validate()  # must not raise


def test_invalid_status_rejected():
    """A status outside the three is invalid - never a guess."""
    with pytest.raises(jsonschema.ValidationError):
        ClassificationResult("maybe", "pothole", 0.5, "ok").validate()


def test_unknown_category_is_allowed_only_in_worker():
    """'unknown' is a worker-only value that is never stored."""
    r = ClassificationResult("unavailable", "unknown", 0.0, "could not decide")
    r.validate()


def test_confidence_out_of_range_rejected():
    with pytest.raises(jsonschema.ValidationError):
        ClassificationResult("safe", "pothole", 1.5, "ok").validate()


def test_validate_dict_builds_result():
    r = validate_dict({"status": "unsafe", "category": "graffiti", "confidence": 0.9, "reason": "x"})
    assert r.status == "unsafe"
    assert r.category == "graffiti"
    assert r.confidence == 0.9
    assert r.reason == "x"


def test_validate_dict_rejects_garbage():
    with pytest.raises(jsonschema.ValidationError):
        validate_dict({"status": "safe"})  # missing required fields


def test_as_dict_matches_schema():
    r = ClassificationResult("safe", "pothole", 0.98, "damaged road")
    jsonschema.validate(r.as_dict(), json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))