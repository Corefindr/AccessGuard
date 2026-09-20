from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ApplicationCriticality, ComplianceStatus
from app.database.session import SessionLocal
from app.models import AccessRecord, Application, ReminderHistory, User

DEMO_USERS = [
    {
        "employee_id": "EMP-1001",
        "name": "Avery Chen",
        "email": "avery.chen@example.com",
        "team": "Identity Operations",
        "lead_name": "Priya Raman",
        "lead_email": "priya.raman@example.com",
        "manager_name": "Dana Brooks",
        "manager_email": "dana.brooks@example.com",
    },
    {
        "employee_id": "EMP-1002",
        "name": "Jordan Patel",
        "email": "jordan.patel@example.com",
        "team": "Service Desk",
        "lead_name": "Chris Alvarez",
        "lead_email": "chris.alvarez@example.com",
        "manager_name": "Dana Brooks",
        "manager_email": "dana.brooks@example.com",
    },
    {
        "employee_id": "EMP-1003",
        "name": "Riley Nguyen",
        "email": "riley.nguyen@example.com",
        "team": "Privileged Access",
        "lead_name": "Priya Raman",
        "lead_email": "priya.raman@example.com",
        "manager_name": "Morgan Hale",
        "manager_email": "morgan.hale@example.com",
    },
    {
        "employee_id": "EMP-1004",
        "name": "Sam Okonkwo",
        "email": "sam.okonkwo@example.com",
        "team": "End User Computing",
        "lead_name": "Chris Alvarez",
        "lead_email": "chris.alvarez@example.com",
        "manager_name": "Dana Brooks",
        "manager_email": "dana.brooks@example.com",
    },
    {
        "employee_id": "EMP-1005",
        "name": "Casey Ellis",
        "email": "casey.ellis@example.com",
        "team": "Mainframe Support",
        "lead_name": "Lee Fontaine",
        "lead_email": "lee.fontaine@example.com",
        "manager_name": "Morgan Hale",
        "manager_email": "morgan.hale@example.com",
        "active": False,
    },
]

DEMO_APPLICATIONS = [
    {
        "name": "ServiceNow",
        "description": "ITSM platform used for incidents, requests, and change records.",
        "application_owner": "Alex Rivera",
        "owner_email": "alex.rivera@example.com",
        "criticality": ApplicationCriticality.HIGH.value,
        "dormancy_threshold_days": 45,
        "reminder_before_days": 14,
    },
    {
        "name": "CyberArk",
        "description": "Privileged access management vault and session control.",
        "application_owner": "Priya Raman",
        "owner_email": "priya.raman@example.com",
        "criticality": ApplicationCriticality.CRITICAL.value,
        "dormancy_threshold_days": 30,
        "reminder_before_days": 7,
    },
    {
        "name": "Microsoft 365",
        "description": "Productivity suite including mailbox, Teams, and SharePoint access.",
        "application_owner": "Chris Alvarez",
        "owner_email": "chris.alvarez@example.com",
        "criticality": ApplicationCriticality.MEDIUM.value,
        "dormancy_threshold_days": 90,
        "reminder_before_days": 21,
    },
    {
        "name": "Mainframe Access",
        "description": "TN3270 access to core banking batch and CICS environments.",
        "application_owner": "Lee Fontaine",
        "owner_email": "lee.fontaine@example.com",
        "criticality": ApplicationCriticality.HIGH.value,
        "dormancy_threshold_days": 21,
        "reminder_before_days": 7,
    },
]


def _get_or_create_user(db: Session, payload: dict) -> User:
    user = db.scalar(select(User).where(User.employee_id == payload["employee_id"]))
    if user:
        return user
    user = User(**payload)
    db.add(user)
    db.flush()
    return user


def _get_or_create_application(db: Session, payload: dict) -> Application:
    application = db.scalar(select(Application).where(Application.name == payload["name"]))
    if application:
        return application
    application = Application(**payload)
    db.add(application)
    db.flush()
    return application


def _get_or_create_access(
    db: Session,
    user: User,
    application: Application,
    **fields,
) -> AccessRecord:
    record = db.scalar(
        select(AccessRecord).where(
            AccessRecord.user_id == user.id,
            AccessRecord.application_id == application.id,
        )
    )
    if record:
        return record
    record = AccessRecord(
        user_id=user.id,
        application_id=application.id,
        compliance_status=ComplianceStatus.UNKNOWN.value,
        **fields,
    )
    db.add(record)
    db.flush()
    return record


def seed(db: Session) -> None:
    now = datetime.now(timezone.utc)
    users = {item["employee_id"]: _get_or_create_user(db, item) for item in DEMO_USERS}
    apps = {item["name"]: _get_or_create_application(db, item) for item in DEMO_APPLICATIONS}

    access_pairs = [
        (
            "EMP-1001",
            "ServiceNow",
            {
                "last_login_date": now - timedelta(days=3),
                "last_validated_date": now - timedelta(days=20),
                "expiry_date": now + timedelta(days=180),
            },
        ),
        (
            "EMP-1001",
            "Microsoft 365",
            {
                "last_login_date": now - timedelta(days=1),
                "last_validated_date": now - timedelta(days=40),
                "expiry_date": now + timedelta(days=365),
            },
        ),
        (
            "EMP-1002",
            "ServiceNow",
            {
                "last_login_date": now - timedelta(days=12),
                "last_validated_date": now - timedelta(days=12),
                "expiry_date": now + timedelta(days=90),
            },
        ),
        (
            "EMP-1003",
            "CyberArk",
            {
                "last_login_date": now - timedelta(days=2),
                "last_validated_date": now - timedelta(days=5),
                "expiry_date": now + timedelta(days=60),
                "notes": "Emergency break-glass group membership pending recertification.",
            },
        ),
        (
            "EMP-1003",
            "Microsoft 365",
            {
                "last_login_date": now - timedelta(days=8),
                "last_validated_date": now - timedelta(days=90),
            },
        ),
        (
            "EMP-1004",
            "Microsoft 365",
            {
                "last_login_date": now - timedelta(days=18),
                "last_validated_date": now - timedelta(days=18),
                "expiry_date": now + timedelta(days=200),
            },
        ),
        (
            "EMP-1005",
            "Mainframe Access",
            {
                "last_login_date": now - timedelta(days=120),
                "last_validated_date": now - timedelta(days=200),
                "expiry_date": now - timedelta(days=5),
                "action_required": True,
                "notes": "Former contractor account retained for knowledge transfer.",
            },
        ),
    ]

    records = [
        _get_or_create_access(db, users[employee_id], apps[app_name], **fields)
        for employee_id, app_name, fields in access_pairs
    ]

    cyberark_access = next(
        record for record in records if record.application_id == apps["CyberArk"].id
    )
    existing_reminder = db.scalar(
        select(ReminderHistory).where(ReminderHistory.access_record_id == cyberark_access.id)
    )
    if existing_reminder is None:
        db.add(
            ReminderHistory(
                access_record_id=cyberark_access.id,
                reminder_type="validation_due",
                recipient="priya.raman@example.com",
                sent_at=now - timedelta(days=2),
                status="recorded",
            )
        )

    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
        print("Development seed data is in place.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
