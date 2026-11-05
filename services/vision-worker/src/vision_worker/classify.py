"""classify(image) -> ClassificationResult with fail-closed behaviour.

Public entry point for the vision worker. It loads config, picks a provider,
classifies the image, validates the provider output against schema.json, and
maps category unknown / status unavailable into the right backend outcome.

Fail closed: ANY doubt, exception, or invalid model output becomes
unavailable - which is never treated as safe. A broken checker must never
approve a photo.
"""

from __future__ import annotations

from typing import Any

from .config import Config
from .log_setup import logger
from .providers import Provider
from .providers.stub import StubProvider
from .result import ClassificationResult, validate_dict


def _build_provider(cfg: Config) -> Provider:
    """Pick the provider based on config. Falls back to stub with no keys."""
    if cfg.use_stub:
        return StubProvider(mode=cfg.stub_mode)
    if cfg.provider == "gemini":
        from .providers.gemini import GeminiProvider  # noqa: WPS433 (deferred import)

        return GeminiProvider(api_key=cfg.gemini_api_key)
    if cfg.provider == "groq":
        from .providers.groq import GroqProvider  # noqa: WPS433 (deferred import)

        return GroqProvider(api_key=cfg.groq_api_key)
    # Unknown provider -> fail closed: use stub unavailable rather than crash.
    logger.warning("unknown provider %r; falling back to stub(unavailable)", cfg.provider)
    return StubProvider(mode="unavailable")


def classify(image_path: str, provider: Provider | None = None) -> ClassificationResult:
    """Classify the image at image_path.

    Never raises: any exception becomes ClassificationResult(status=unavailable).
    Invalid model output counts as failure -> unavailable.
    """
    # Build config lazily so a caller can still classify with an injected provider
    # without env vars present.
    cfg = Config.from_env()

    if provider is None:
        provider = _build_provider(cfg)

    try:
        payload = provider.classify(image_path)
    except Exception as exc:  # noqa: BLE001 - fail closed: any provider crash -> unavailable
        logger.exception("provider %s raised during classify: %s", type(provider).__name__, exc)
        return _unavailable("provider failed")

    # Model output is untrusted: validate it against the schema.
    try:
        return validate_dict(payload)
    except Exception as exc:  # noqa: BLE001 - invalid output -> unavailable
        logger.exception("provider %s returned invalid output: %s", type(provider).__name__, exc)
        return _unavailable("invalid model output")


def _unavailable(reason: str) -> ClassificationResult:
    """Build an unavailable result. unavailable is never treated as safe."""
    return ClassificationResult(
        status="unavailable",
        category="unknown",
        confidence=0.0,
        reason=reason,
    )