import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApplicationCriticality, ComplianceStatus
from app.models import AccessRecord, Application, ReminderHistory, User
from app.schemas.user import UserCreate, UserRead


def test_database_connection(db_session: Session) -> None:
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


def test_migration_creates_core_tables(db_session: Session) -> None:
    inspector = inspect(db_session.get_bind())
    assert set(inspector.get_table_names()) >= {
        "users",
        "applications",
        "access_records",
        "reminder_history",
        "alembic_version",
    }


def test_unique_employee_id(db_session: Session) -> None:
    db_session.add(User(employee_id="EMP-1", name="Pat Lee", email="pat.lee@example.com"))
    db_session.add(User(employee_id="EMP-1", name="Pat Duplicate", email="pat.dup@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_unique_application_name(db_session: Session) -> None:
    db_session.add(Application(name="ServiceNow", criticality=ApplicationCriticality.HIGH.value))
    db_session.add(Application(name="ServiceNow", criticality=ApplicationCriticality.LOW.value))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_unique_user_application_access_record(db_session: Session) -> None:
    user = User(employee_id="EMP-2", name="Quinn Reed", email="quinn.reed@example.com")
    application = Application(name="CyberArk")
    db_session.add_all([user, application])
    db_session.flush()

    db_session.add(AccessRecord(user_id=user.id, application_id=application.id))
    db_session.add(AccessRecord(user_id=user.id, application_id=application.id))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_relationships_and_default_compliance_status(db_session: Session) -> None:
    user = User(employee_id="EMP-3", name="Jamie Cole", email="jamie.cole@example.com")
    application = Application(name="Microsoft 365")
    db_session.add_all([user, application])
    db_session.flush()

    record = AccessRecord(user_id=user.id, application_id=application.id)
    db_session.add(record)
    db_session.flush()

    reminder = ReminderHistory(
        access_record_id=record.id,
        reminder_type="validation_due",
        recipient="jamie.cole@example.com",
        status="recorded",
    )
    db_session.add(reminder)
    db_session.commit()

    stored_user = db_session.scalar(select(User).where(User.employee_id == "EMP-3"))
    assert stored_user is not None
    assert len(stored_user.access_records) == 1
    assert stored_user.access_records[0].application.name == "Microsoft 365"
    assert stored_user.access_records[0].compliance_status == ComplianceStatus.UNKNOWN.value
    assert stored_user.access_records[0].reminder_history[0].recipient == "jamie.cole@example.com"
    assert reminder.access_record.user.email == "jamie.cole@example.com"


def test_user_read_schema_from_orm(db_session: Session) -> None:
    payload = UserCreate(
        employee_id="EMP-4",
        name="Taylor Kim",
        email="taylor.kim@example.com",
        team="Service Desk",
    )
    user = User(**payload.model_dump())
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    read = UserRead.model_validate(user)
    assert read.employee_id == "EMP-4"
    assert read.active is True
