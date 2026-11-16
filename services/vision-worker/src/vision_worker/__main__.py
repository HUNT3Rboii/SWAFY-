"""Let `python -m vision_worker` start the service.

Phase 1: the container only needs to start, read its config, print log lines,
and stay alive. It does NOT poll any backend (that depends on BE-4).
"""

from __future__ import annotations

import sys
import time

from .classify import ProviderConfigError, build_provider
from .config import Config
from .log_setup import logger, setup


def main() -> int:
    cfg = Config.from_env()
    setup(level=cfg.log_level)
    logger.info(
        "vision worker starting | provider=%s stub_mode=%s log_level=%s",
        cfg.provider,
        cfg.stub_mode if cfg.use_stub else "-",
        cfg.log_level,
    )

    # Check the config once at startup so a mistake shows up in the logs right
    # away. We still stay alive: classify() will answer "unavailable" (fail
    # closed) until the config is fixed.
    try:
        build_provider(cfg)
    except ProviderConfigError as exc:
        logger.error("provider misconfigured, every photo will be 'unavailable': %s", exc)
    else:
        if cfg.use_stub:
            logger.warning(
                "STUB provider active (STUB_MODE=%s): photos are NOT really checked. "
                "Never use this in production.",
                cfg.stub_mode,
            )

    # Stay alive so orchestration (docker compose) keeps the service up.
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("vision worker stopping")
        return 0


if __name__ == "__main__":
    sys.exit(main())
