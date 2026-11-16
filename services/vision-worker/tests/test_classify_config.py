"""classify() built from env config: never raises, never approves by accident.

These cover the cases where the provider comes from environment variables
(no provider injected), as it will inside the container.
"""

from __future__ import annotations

import pytest

from vision_worker.classify import ProviderConfigError, build_provider, classify
from vision_worker.config import Config


def test_default_env_uses_stub_safe(isolated_env, tmp_image: str):
    """No env at all -> stub, safe mode: backend/mobile can integrate."""
    r = classify(tmp_image)
    assert r.status == "safe"
    r.validate()


@pytest.mark.parametrize("mode", ["safe", "unsafe", "unavailable"])
def test_stub_mode_from_env(isolated_env, tmp_image: str, mode: str):
    isolated_env.setenv("VISION_PROVIDER", "stub")
    isolated_env.setenv("STUB_MODE", mode)
    r = classify(tmp_image)
    assert r.status == mode
    r.validate()


def test_stub_error_mode_from_env_gives_unavailable(isolated_env, tmp_image: str):
    isolated_env.setenv("STUB_MODE", "error")
    r = classify(tmp_image)
    assert r.status == "unavailable"
    r.validate()


def test_bad_stub_mode_gives_unavailable_not_exception(isolated_env, tmp_image: str):
    isolated_env.setenv("STUB_MODE", "bogus")
    r = classify(tmp_image)
    assert r.status == "unavailable"
    r.validate()


@pytest.mark.parametrize("provider", ["gemini", "groq"])
def test_real_provider_without_key_never_falls_back_to_safe(isolated_env, tmp_image: str, provider: str):
    """A missing key must NOT silently use the stub (which would approve photos)."""
    isolated_env.setenv("VISION_PROVIDER", provider)
    r = classify(tmp_image)
    assert r.status == "unavailable"
    r.validate()


@pytest.mark.parametrize("provider", ["gemini", "groq"])
def test_real_provider_not_implemented_yet_gives_unavailable(isolated_env, tmp_image: str, provider: str):
    """Until AI-2/AI-3 land, a real provider with a key is still unavailable."""
    isolated_env.setenv("VISION_PROVIDER", provider)
    isolated_env.setenv(f"{provider.upper()}_API_KEY", "fake-key")
    r = classify(tmp_image)
    assert r.status == "unavailable"


def test_unknown_provider_gives_unavailable(isolated_env, tmp_image: str):
    isolated_env.setenv("VISION_PROVIDER", "openai")
    r = classify(tmp_image)
    assert r.status == "unavailable"


def test_build_provider_raises_config_error_for_bad_config():
    with pytest.raises(ProviderConfigError):
        build_provider(Config.from_env({"VISION_PROVIDER": "gemini"}))


def test_invalid_provider_output_gives_unavailable(tmp_image: str):
    """Model output is untrusted: garbage must become unavailable, not a guess."""

    class Garbage:
        def classify(self, image_path):
            return {"status": "safe", "category": "cat_picture", "confidence": 2, "reason": ""}

    r = classify(tmp_image, provider=Garbage())
    assert r.status == "unavailable"
    r.validate()


def test_boolean_safe_is_rejected(tmp_image: str):
    """A model answering safe=true (a boolean) is not one of the three statuses."""

    class BoolProvider:
        def classify(self, image_path):
            return {"status": True, "category": "pothole", "confidence": 0.9, "reason": "x"}

    r = classify(tmp_image, provider=BoolProvider())
    assert r.status == "unavailable"
