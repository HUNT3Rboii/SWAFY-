"""Shared test fixtures.

Tests generate their own images with Pillow instead of committing files, so
the sensitive evaluation folder stays out of git and no test image is
tracked.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def tmp_image(tmp_path: Path) -> str:
    """A tiny PNG generated in the test temp dir. Never committed."""
    path = tmp_path / "test.png"
    Image.new("RGB", (8, 8), (120, 80, 40)).save(path)
    return str(path)


@pytest.fixture
def isolated_env(monkeypatch):
    """An environment with only the vision worker's known keys set."""
    for key in ("VISION_PROVIDER", "STUB_MODE", "GEMINI_API_KEY", "GROQ_API_KEY", "LOG_LEVEL"):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch