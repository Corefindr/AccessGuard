from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.enums import ApplicationCriticality
from app.schemas.common import (
    blank_to_none,
    normalize_optional_email,
    require_non_blank,
)


class ApplicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    application_owner: str | None = None
    owner_email: EmailStr | None = None
    criticality: ApplicationCriticality | None = None
    dormancy_threshold_days: int | None = Field(default=None, ge=0)
    reminder_before_days: int | None = Field(default=None, ge=0)
    active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        if isinstance(value, str):
            return require_non_blank(value)
        return value

    @field_validator("description", "application_owner", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            return blank_to_none(value)
        return value

    @field_validator("owner_email", mode="before")
    @classmethod
    def normalize_owner_email(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_optional_email(value)
        return value


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationReplace(ApplicationBase):
    """Full replacement payload for PUT /api/applications/{application_id}."""


class ApplicationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    application_owner: str | None = None
    owner_email: EmailStr | None = None
    criticality: ApplicationCriticality | None = None
    dormancy_threshold_days: int | None = Field(default=None, ge=0)
    reminder_before_days: int | None = Field(default=None, ge=0)
    active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        if isinstance(value, str):
            return require_non_blank(value)
        return value

    @field_validator("description", "application_owner", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            return blank_to_none(value)
        return value

    @field_validator("owner_email", mode="before")
    @classmethod
    def normalize_owner_email(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_optional_email(value)
        return value


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
