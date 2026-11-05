"""Tests for the stub provider and the fail-closed classify() behaviour.

- stub safe -> validates against the schema
- stub unsafe -> validates against the schema
- provider crash -> unavailable (never raises, never safe)
- every result validates against the schema
"""

from __future__ import annotations

import pytest

from vision_worker.classify import classify
from vision_worker.providers.stub import StubProvider


def test_stub_safe_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="safe"))
    assert r.status == "safe"
    assert r.category == "pothole"
    assert 0 <= r.confidence <= 1
    r.validate()  # must not raise


def test_stub_unsafe_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="unsafe"))
    assert r.status == "unsafe"
    assert r.category == "other"
    r.validate()


def test_stub_unavailable_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="unavailable"))
    assert r.status == "unavailable"
    assert r.category == "unknown"
    r.validate()


def test_provider_crash_gives_unavailable(tmp_image: str):
    """Fail closed: a crashing provider must never raise and never return safe."""
    r = classify(tmp_image, provider=StubProvider(mode="error"))
    assert r.status == "unavailable"
    assert r.category == "unknown"
    assert r.confidence == 0.0
    r.validate()


def test_unknown_stub_mode_raises_during_construction():
    """Bad STUB_MODE fails at construction, not at classify time."""
    with pytest.raises(ValueError):
        StubProvider(mode="bogus")


def test_classify_with_garbage_path_returns_safe_from_stub(tmp_image: str):
    """The stub returns canned results regardless of the file path; classify
    with a garbage path still returns a valid result (never raises)."""
    r = classify("/no/such/file.png", provider=StubProvider(mode="safe"))
    assert r.status == "safe"
    r.validate()


def test_unavailable_is_never_treated_as_safe(tmp_image: str):
    """The contract: unavailable must not map to approved."""
    r = classify(tmp_image, provider=StubProvider(mode="unavailable"))
    assert r.status != "safe"