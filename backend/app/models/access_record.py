from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ComplianceStatus
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.reminder_history import ReminderHistory
    from app.models.user import User


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AccessRecord(Base):
    __tablename__ = "access_records"
    __table_args__ = (
        UniqueConstraint("user_id", "application_id", name="uq_access_record_user_application"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False, index=True)
    last_login_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_validated_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    compliance_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ComplianceStatus.UNKNOWN.value,
        server_default=ComplianceStatus.UNKNOWN.value,
    )
    action_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )

    user: Mapped["User"] = relationship("User", back_populates="access_records")
    application: Mapped["Application"] = relationship("Application", back_populates="access_records")
    reminder_history: Mapped[list["ReminderHistory"]] = relationship(
        "ReminderHistory",
        back_populates="access_record",
    )
