"""Configuration from environment variables.

All values come from the environment with fail-safe defaults. The service
starts cleanly with no API key set: it simply falls back to the stub provider.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    provider: str = ""
    stub_mode: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    log_level: str = "info"

    @classmethod
    def from_env(cls, env: dict | None = None) -> "Config":
        """Build Config from os.environ (or a dict for tests)."""
        env = env if env is not None else os.environ
        return cls(
            provider=str(env.get("VISION_PROVIDER", "")).strip().lower(),
            stub_mode=str(env.get("STUB_MODE", "")).strip().lower(),
            gemini_api_key=str(env.get("GEMINI_API_KEY", "")),
            groq_api_key=str(env.get("GROQ_API_KEY", "")),
            log_level=str(env.get("LOG_LEVEL", "info")).strip().lower(),
        )

    @property
    def use_stub(self) -> bool:
        return self.provider == "stub"