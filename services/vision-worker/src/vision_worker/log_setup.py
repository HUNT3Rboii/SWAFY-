"""Structured logging setup for the vision worker.

Configures Python's standard logging module once, at service start. The log
level comes from LOG_LEVEL (default: info). Logs go to stdout so they are
captured by Docker / systemd / cloud logging.
"""

from __future__ import annotations

import logging
import sys


def setup(level: str = "info") -> None:
    """Configure the root logger.

    Called once at startup. Safe to call multiple times; later calls are
    ignored once logging is configured.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [vision-worker] %(message)s",
        stream=sys.stdout,
        force=True,
    )


logger = logging.getLogger("vision-worker")