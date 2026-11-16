"""Tests for the stub provider and the fail-closed classify() behaviour.

- stub safe / unsafe / unavailable -> valid results
- provider crash -> unavailable (never raises, never safe)
- every result validates against the schema
"""

from __future__ import annotations

import pytest

from vision_worker.classify import classify
from vision_worker.providers.stub import StubProvider


def test_stub_safe_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="safe"))
    assert r.outcome == "safe"
    assert r.category == "pothole"
    assert 0 <= r.confidence <= 1
    assert r.provider == "stub"
    r.validate()


def test_stub_unsafe_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="unsafe"))
    assert r.outcome == "unsafe"
    assert r.category == "unknown"
    assert r.provider == "stub"
    r.validate()


def test_stub_unavailable_is_valid(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="unavailable"))
    assert r.outcome == "unavailable"
    assert r.category == "unknown"
    assert r.confidence is None
    r.validate()


def test_provider_crash_gives_unavailable(tmp_image: str):
    """Fail closed: a crashing provider must never raise and never return safe."""
    r = classify(tmp_image, provider=StubProvider(mode="error"))
    assert r.outcome == "unavailable"
    assert r.category == "unknown"
    assert r.confidence is None
    assert r.provider == "stub"
    r.validate()


def test_unknown_stub_mode_raises_during_construction():
    with pytest.raises(ValueError):
        StubProvider(mode="bogus")


def test_classify_with_garbage_path_never_raises():
    """The stub ignores the file; classify still returns a valid result."""
    r = classify("/no/such/file.png", provider=StubProvider(mode="safe"))
    assert r.outcome == "safe"
    r.validate()


@pytest.mark.parametrize("mode", ["safe", "unsafe", "unavailable", "error"])
def test_every_stub_mode_validates(tmp_image: str, mode: str):
    classify(tmp_image, provider=StubProvider(mode=mode)).validate()


def test_unavailable_is_never_treated_as_safe(tmp_image: str):
    r = classify(tmp_image, provider=StubProvider(mode="unavailable"))
    assert r.outcome != "safe"


def test_model_cannot_claim_another_provider(tmp_image: str):
    """The worker stamps `provider` itself; a value from the model is overwritten."""

    class Liar(StubProvider):
        def classify(self, image_path):
            return super().classify(image_path) | {"provider": "gemini"}

    r = classify(tmp_image, provider=Liar(mode="safe"))
    assert r.provider == "stub"
