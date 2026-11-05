"""Vision providers share one interface and are swappable.

classify(image_path: str) -> dict
Each provider returns a dict matching schema.json. The chain (gemini then groq)
is assembled in Phase 3; Phase 1 only has the stub.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """A hosted vision LLM that classifies a single photo."""

    @abstractmethod
    def classify(self, image_path: str) -> dict[str, Any]:
        """Classify the image at image_path. Return a dict matching schema.json."""
        raise NotImplementedError