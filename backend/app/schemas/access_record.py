from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ComplianceStatus


class AccessRecordBase(BaseModel):
    last_login_date: datetime | None = None
    last_validated_date: datetime | None = None
    expiry_date: datetime | None = None
    compliance_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    action_required: bool = False
    notes: str | None = None


class AccessRecordCreate(AccessRecordBase):
    user_id: int
    application_id: int


class AccessRecordRead(AccessRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    application_id: int
    created_at: datetime
    updated_at: datetime
