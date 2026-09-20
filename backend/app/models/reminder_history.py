from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.access_record import AccessRecord


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReminderHistory(Base):
    __tablename__ = "reminder_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    access_record_id: Mapped[int] = mapped_column(
        ForeignKey("access_records.id"),
        nullable=False,
        index=True,
    )
    reminder_type: Mapped[str] = mapped_column(String(64), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)

    access_record: Mapped["AccessRecord"] = relationship(
        "AccessRecord",
        back_populates="reminder_history",
    )
