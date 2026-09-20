from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import (
    blank_to_none,
    normalize_email,
    normalize_optional_email,
    require_non_blank,
)


class UserBase(BaseModel):
    employee_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    team: str | None = None
    lead_name: str | None = None
    lead_email: EmailStr | None = None
    manager_name: str | None = None
    manager_email: EmailStr | None = None
    active: bool = True

    @field_validator("employee_id", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return require_non_blank(value)
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_required_email(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_email(value)
        return value

    @field_validator("team", "lead_name", "manager_name", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            return blank_to_none(value)
        return value

    @field_validator("lead_email", "manager_email", mode="before")
    @classmethod
    def normalize_optional_emails(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_optional_email(value)
        return value


class UserCreate(UserBase):
    pass


class UserReplace(UserBase):
    """Full replacement payload for PUT /api/users/{user_id}."""


class UserUpdate(BaseModel):
    employee_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    team: str | None = None
    lead_name: str | None = None
    lead_email: EmailStr | None = None
    manager_name: str | None = None
    manager_email: EmailStr | None = None
    active: bool | None = None

    @field_validator("employee_id", "name", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return require_non_blank(value)
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_required_email(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_email(value)
        return value

    @field_validator("team", "lead_name", "manager_name", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            return blank_to_none(value)
        return value

    @field_validator("lead_email", "manager_email", mode="before")
    @classmethod
    def normalize_optional_emails(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_optional_email(value)
        return value


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
