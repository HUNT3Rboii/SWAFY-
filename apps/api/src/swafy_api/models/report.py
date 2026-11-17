from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from swafy_api.db import Base
from swafy_api.models.enums import LabelSource, PhotoState, ReportCategory, ReportStatus
from swafy_api.models.types import (
    LABEL_SOURCE_DB,
    PHOTO_STATE_DB,
    REPORT_CATEGORY_DB,
    REPORT_STATUS_DB,
)


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_location_gist", "location", postgresql_using="gist"),
        Index("ix_reports_owner_created", "owner_id", "created_at"),
        Index("ix_reports_photo_state_status", "photo_state", "status"),
        CheckConstraint(
            "ai_confidence IS NULL OR (ai_confidence >= 0 AND ai_confidence <= 1)",
            name="ck_reports_ai_confidence_range",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[ReportCategory] = mapped_column(REPORT_CATEGORY_DB, nullable=False)
    suggested_category: Mapped[ReportCategory | None] = mapped_column(
        REPORT_CATEGORY_DB, nullable=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        REPORT_STATUS_DB,
        nullable=False,
        default=ReportStatus.SUBMITTED,
        server_default=ReportStatus.SUBMITTED.value,
    )
    photo_state: Mapped[PhotoState] = mapped_column(
        PHOTO_STATE_DB,
        nullable=False,
        default=PhotoState.PENDING_CHECK,
        server_default=PhotoState.PENDING_CHECK.value,
    )
    label_source: Mapped[LabelSource] = mapped_column(
        LABEL_SOURCE_DB,
        nullable=False,
        default=LabelSource.MANUAL,
        server_default=LabelSource.MANUAL.value,
    )
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Coordinates are stored as a WGS84 POINT (longitude, latitude).
    location: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )

    # Storage object keys are private implementation details and must never be
    # serialized into public API responses. BE-3/BE-4 own upload and promotion.
    quarantine_photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    public_photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    photo_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    photo_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="reports")
    status_history = relationship(
        "StatusHistory",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="StatusHistory.changed_at",
    )
    confirmations = relationship(
        "Confirmation", back_populates="report", cascade="all, delete-orphan"
    )


class StatusHistory(Base):
    __tablename__ = "status_history"
    __table_args__ = (Index("ix_status_history_report_changed", "report_id", "changed_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    from_status: Mapped[ReportStatus | None] = mapped_column(
        REPORT_STATUS_DB,
        nullable=True,
    )
    to_status: Mapped[ReportStatus] = mapped_column(
        REPORT_STATUS_DB,
        nullable=False,
    )
    changed_by_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    report = relationship("Report", back_populates="status_history")


class Confirmation(Base):
    __tablename__ = "confirmations"
    __table_args__ = (
        # One confirmation per citizen per report; BE-5 can safely make this idempotent.
        UniqueConstraint("report_id", "user_id", name="uq_confirmations_report_user"),
        Index("ix_confirmations_user_created", "user_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="confirmations")
