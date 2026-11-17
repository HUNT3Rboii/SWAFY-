"""Tests for the result type and schema validation.

Every classify() result must validate against schema.json, which matches the
decision fields of PhotoCheckResultRequest in docs/contracts/openapi.yaml.
Invalid output counts as a failure (unavailable), never as a guess.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from vision_worker.result import ClassificationResult, validate_dict

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.json"
FROZEN = ("pothole", "trash", "graffiti", "broken_light", "other")


def _r(outcome, category, confidence, reason="ok", provider="stub"):
    return ClassificationResult(outcome, category, confidence, reason, provider)


def test_schema_is_committed():
    assert SCHEMA_PATH.is_file()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["outcome"]["enum"] == ["safe", "unsafe", "unavailable"]
    assert schema["properties"]["category"]["enum"] == [*FROZEN, "unknown"]


@pytest.mark.parametrize("category", [*FROZEN, "unknown"])
def test_safe_accepts_any_category(category):
    _r("safe", category, 0.5).validate()


def test_unsafe_valid_shape():
    _r("unsafe", "unknown", 0.9).validate()


def test_unavailable_valid_shape():
    _r("unavailable", "unknown", None).validate()


@pytest.mark.parametrize("category", FROZEN)
def test_unsafe_must_use_unknown_category(category):
    """BE-1: an unsafe photo gets no category."""
    with pytest.raises(jsonschema.ValidationError):
        _r("unsafe", category, 0.9).validate()


def test_unavailable_must_have_null_confidence():
    with pytest.raises(jsonschema.ValidationError):
        _r("unavailable", "unknown", 0.0).validate()


def test_unavailable_must_use_unknown_category():
    with pytest.raises(jsonschema.ValidationError):
        _r("unavailable", "pothole", None).validate()


@pytest.mark.parametrize("outcome", ["safe", "unsafe"])
def test_completed_decision_needs_a_confidence(outcome):
    with pytest.raises(jsonschema.ValidationError):
        _r(outcome, "unknown", None).validate()


def test_invalid_outcome_rejected():
    with pytest.raises(jsonschema.ValidationError):
        _r("maybe", "pothole", 0.5).validate()


def test_boolean_outcome_rejected():
    with pytest.raises(jsonschema.ValidationError):
        _r(True, "pothole", 0.5).validate()


@pytest.mark.parametrize("confidence", [-0.1, 1.5])
def test_confidence_out_of_range_rejected(confidence):
    with pytest.raises(jsonschema.ValidationError):
        _r("safe", "pothole", confidence).validate()


def test_empty_reason_or_provider_rejected():
    with pytest.raises(jsonschema.ValidationError):
        _r("safe", "pothole", 0.5, reason="").validate()
    with pytest.raises(jsonschema.ValidationError):
        _r("safe", "pothole", 0.5, provider="").validate()


def test_too_long_reason_rejected():
    with pytest.raises(jsonschema.ValidationError):
        _r("safe", "pothole", 0.5, reason="x" * 2001).validate()


def test_extra_field_rejected():
    payload = _r("safe", "pothole", 0.5).as_dict() | {"lease_token": "x" * 40}
    with pytest.raises(jsonschema.ValidationError):
        validate_dict(payload)


def test_validate_dict_builds_result():
    r = validate_dict(
        {"outcome": "safe", "category": "graffiti", "confidence": 0.9, "reason": "x", "provider": "stub"}
    )
    assert (r.outcome, r.category, r.confidence, r.reason, r.provider) == ("safe", "graffiti", 0.9, "x", "stub")


def test_validate_dict_keeps_null_confidence():
    r = validate_dict(
        {"outcome": "unavailable", "category": "unknown", "confidence": None, "reason": "x", "provider": "none"}
    )
    assert r.confidence is None


def test_validate_dict_rejects_garbage():
    with pytest.raises(jsonschema.ValidationError):
        validate_dict({"outcome": "safe"})
