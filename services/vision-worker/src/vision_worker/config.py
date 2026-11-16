"""Configuration from environment variables.

All values come from the environment with defaults. The service starts cleanly
with no API key set: by default it uses the stub provider in "safe" mode so
backend and mobile can integrate before the real LLM exists.

Fail closed: asking for a real provider (gemini / groq) WITHOUT its key does
NOT silently fall back to the stub (that would approve every photo). classify()
turns that case into "unavailable" instead.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_PROVIDER = "stub"
DEFAULT_STUB_MODE = "safe"


def _clean(env, key: str, default: str) -> str:
    """Read env var, strip it, lowercase it; blank means 'use the default'."""
    value = str(env.get(key, "") or "").strip().lower()
    return value or default


@dataclass(frozen=True)
class Config:
    provider: str = DEFAULT_PROVIDER
    stub_mode: str = DEFAULT_STUB_MODE
    gemini_api_key: str = ""
    groq_api_key: str = ""
    log_level: str = "info"

    @classmethod
    def from_env(cls, env: dict | None = None) -> "Config":
        """Build Config from os.environ (or a dict for tests)."""
        env = env if env is not None else os.environ
        return cls(
            provider=_clean(env, "VISION_PROVIDER", DEFAULT_PROVIDER),
            stub_mode=_clean(env, "STUB_MODE", DEFAULT_STUB_MODE),
            gemini_api_key=str(env.get("GEMINI_API_KEY", "") or "").strip(),
            groq_api_key=str(env.get("GROQ_API_KEY", "") or "").strip(),
            log_level=_clean(env, "LOG_LEVEL", "info"),
        )

    @property
    def use_stub(self) -> bool:
        return self.provider == "stub"
