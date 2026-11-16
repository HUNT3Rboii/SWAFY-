"""classify(image) -> ClassificationResult with fail-closed behaviour.

Public entry point for the vision worker. It loads config, picks a provider,
classifies the image and validates the provider output against schema.json.

Fail closed: ANY doubt, exception, misconfiguration or invalid model output
becomes "unavailable" - which is never treated as safe. A broken checker must
never approve a photo. classify() itself never raises.
"""

from __future__ import annotations

from .config import Config
from .log_setup import logger
from .providers import Provider
from .providers.stub import StubProvider
from .result import ClassificationResult, validate_dict


class ProviderConfigError(Exception):
    """The configured provider cannot be built (bad mode, missing key, ...)."""


def build_provider(cfg: Config) -> Provider:
    """Pick the provider from config.

    Raises ProviderConfigError when the config cannot give a working provider.
    It never falls back to a stub that could return "safe": a missing key on a
    real provider must not approve photos.
    """
    if cfg.use_stub:
        try:
            return StubProvider(mode=cfg.stub_mode)
        except ValueError as exc:
            raise ProviderConfigError(str(exc)) from exc

    if cfg.provider == "gemini":
        if not cfg.gemini_api_key:
            raise ProviderConfigError("VISION_PROVIDER=gemini but GEMINI_API_KEY is empty")
        raise ProviderConfigError("gemini provider not implemented yet (AI-2)")

    if cfg.provider == "groq":
        if not cfg.groq_api_key:
            raise ProviderConfigError("VISION_PROVIDER=groq but GROQ_API_KEY is empty")
        raise ProviderConfigError("groq provider not implemented yet (AI-3)")

    raise ProviderConfigError(f"unknown VISION_PROVIDER: {cfg.provider!r}")


def classify(image_path: str, provider: Provider | None = None) -> ClassificationResult:
    """Classify the image at image_path.

    Never raises: any exception becomes ClassificationResult(outcome=unavailable).
    Invalid model output counts as failure -> unavailable.
    """
    try:
        if provider is None:
            provider = build_provider(Config.from_env())
    except Exception as exc:  # noqa: BLE001 - fail closed: bad config -> unavailable
        logger.error("cannot build provider: %s", exc)
        return _unavailable("provider not configured", provider="none")

    name = getattr(provider, "name", None) or type(provider).__name__

    try:
        payload = dict(provider.classify(image_path))
    except Exception as exc:  # noqa: BLE001 - fail closed: any provider crash -> unavailable
        logger.exception("provider %s raised during classify: %s", name, exc)
        return _unavailable("provider failed", provider=name)

    # The worker, not the model, says which provider answered.
    payload["provider"] = name

    # Model output is untrusted: validate it against the schema.
    try:
        result = validate_dict(payload)
    except Exception as exc:  # noqa: BLE001 - invalid output -> unavailable
        logger.error("provider %s returned invalid output: %s", name, exc)
        return _unavailable("invalid model output", provider=name)

    # Every decision is logged (result + provider) for later evaluation.
    logger.info(
        "classified | provider=%s outcome=%s category=%s confidence=%s",
        result.provider,
        result.outcome,
        result.category,
        result.confidence,
    )
    return result


def _unavailable(reason: str, provider: str) -> ClassificationResult:
    """Build an unavailable result. unavailable is never treated as safe.

    BE-1 rule: unavailable always has category unknown and confidence null.
    """
    return ClassificationResult(
        outcome="unavailable",
        category="unknown",
        confidence=None,
        reason=reason,
        provider=provider,
    )
