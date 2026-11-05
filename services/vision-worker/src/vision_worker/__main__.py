"""Let `python -m vision_worker` start the service.

Phase 1: the container only needs to start, read its config, print a log line,
and stay alive. It does NOT poll any backend (that depends on BE-4).
"""

from __future__ import annotations

import sys
import time

from .config import Config
from .log_setup import setup
from .log_setup import logger


def main() -> int:
    cfg = Config.from_env()
    setup(level=cfg.log_level)
    logger.info(
        "vision worker starting | provider=%s stub_mode=%s log_level=%s",
        cfg.provider,
        cfg.stub_mode,
        cfg.log_level,
    )
    # Stay alive so orchestration (docker compose, systemd, k8s) can probe.
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("vision worker stopping")
        return 0


if __name__ == "__main__":
    sys.exit(main())