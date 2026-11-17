# ruff: noqa: UP042
from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    MUNICIPAL_ADMIN = "municipal_admin"


class ReportCategory(str, Enum):
    POTHOLE = "pothole"
    TRASH = "trash"
    GRAFFITI = "graffiti"
    BROKEN_LIGHT = "broken_light"
    OTHER = "other"


class ReportStatus(str, Enum):
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class PhotoState(str, Enum):
    PENDING_CHECK = "pending_check"
    APPROVED = "approved"
    REJECTED = "rejected"


class LabelSource(str, Enum):
    MANUAL = "manual"
    AI = "ai"
    AI_CORRECTED = "ai_corrected"
