"""Vision worker: classifies report photos with hosted vision LLMs.

The worker never returns a boolean. classify(image) returns one of three
statuses: safe (publish the photo), unsafe (reject it) or unavailable
(leave it pending, ask a human). Fail closed: any error or invalid model
output becomes unavailable, never safe.
"""

from .classify import classify
from .result import ClassificationResult

__all__ = ["classify", "ClassificationResult"]