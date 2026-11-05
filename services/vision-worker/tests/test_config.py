"""Tests for config: env vars with fail-safe defaults, no keys = stub."""

from __future__ import annotations

from vision_worker.config import Config


def test_defaults_use_stub():
    cfg = Config.from_env({})
    assert cfg.provider == "stub"
    assert cfg.stub_mode == "safe"
    assert cfg.use_stub is True


def test_no_keys_means_stub():
    cfg = Config.from_env({"GEMINI_API_KEY": "", "GROQ_API_KEY": ""})
    assert cfg.use_stub is True


def test_stub_mode_selectable():
    cfg = Config.from_env({"STUB_MODE": "unsafe"})
    assert cfg.stub_mode == "unsafe"


def test_provider_set_with_key_is_not_stub():
    cfg = Config.from_env({"VISION_PROVIDER": "gemini", "GEMINI_API_KEY": "abc"})
    assert cfg.use_stub is False