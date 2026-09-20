from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReminderHistoryBase(BaseModel):
    reminder_type: str = Field(min_length=1, max_length=64)
    recipient: str = Field(min_length=1, max_length=255)
    sent_at: datetime | None = None
    status: str | None = Field(default=None, max_length=32)


class ReminderHistoryCreate(ReminderHistoryBase):
    access_record_id: int


class ReminderHistoryRead(ReminderHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    access_record_id: int
    sent_at: datetime
    created_at: datetime
