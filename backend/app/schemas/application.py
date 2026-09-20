from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ApplicationCriticality


class ApplicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    application_owner: str | None = None
    owner_email: str | None = None
    criticality: ApplicationCriticality | None = None
    dormancy_threshold_days: int | None = Field(default=None, ge=0)
    reminder_before_days: int | None = Field(default=None, ge=0)
    active: bool = True


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
