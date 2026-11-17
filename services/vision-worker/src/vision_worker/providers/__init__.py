"""Vision providers share one interface and are swappable.

classify(image_path: str) -> dict with outcome, category, confidence, reason.
classify() in vision_worker.classify adds the "provider" field itself (from
Provider.name) so a model can never claim to be another provider.
The chain (gemini then groq) is assembled in Phase 3; Phase 1 only has the stub.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """A hosted vision LLM that classifies a single photo."""

    #: Identifier sent to the API as `provider` (stub, gemini, groq).
    name: str = "unknown"

    @abstractmethod
    def classify(self, image_path: str) -> dict[str, Any]:
        """Classify the image at image_path.

        Return outcome, category, confidence and reason (see schema.json).
        """
        raise NotImplementedError
