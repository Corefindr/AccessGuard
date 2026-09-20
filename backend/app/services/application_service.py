from datetime import datetime, timezone

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApplicationCriticality
from app.core.exceptions import ConflictError, NotFoundError
from app.models import Application
from app.schemas.application import ApplicationCreate, ApplicationReplace, ApplicationUpdate


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("The requested change conflicts with an existing application.") from exc


def _ensure_unique_name(
    db: Session,
    name: str,
    *,
    exclude_application_id: int | None = None,
) -> None:
    stmt: Select[tuple[Application]] = select(Application).where(Application.name == name)
    if exclude_application_id is not None:
        stmt = stmt.where(Application.id != exclude_application_id)
    if db.scalar(stmt) is not None:
        raise ConflictError("An application with this name already exists.")


def get_application(db: Session, application_id: int) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise NotFoundError("Application not found.")
    return application


def list_applications(
    db: Session,
    *,
    active: bool | None = None,
    criticality: ApplicationCriticality | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Application]:
    stmt = select(Application).order_by(Application.id)
    if active is not None:
        stmt = stmt.where(Application.active.is_(active))
    if criticality is not None:
        stmt = stmt.where(Application.criticality == criticality.value)
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Application.name.ilike(term),
                Application.description.ilike(term),
                Application.application_owner.ilike(term),
            )
        )
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create_application(db: Session, payload: ApplicationCreate) -> Application:
    _ensure_unique_name(db, payload.name)
    application = Application(**payload.model_dump())
    db.add(application)
    _commit(db)
    db.refresh(application)
    return application


def replace_application(
    db: Session,
    application_id: int,
    payload: ApplicationReplace,
) -> Application:
    application = get_application(db, application_id)
    _ensure_unique_name(db, payload.name, exclude_application_id=application.id)
    for field, value in payload.model_dump().items():
        setattr(application, field, value.value if isinstance(value, ApplicationCriticality) else value)
    application.updated_at = _utc_now()
    _commit(db)
    db.refresh(application)
    return application


def update_application(
    db: Session,
    application_id: int,
    payload: ApplicationUpdate,
) -> Application:
    application = get_application(db, application_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        _ensure_unique_name(db, changes["name"], exclude_application_id=application.id)
    for field, value in changes.items():
        setattr(application, field, value.value if isinstance(value, ApplicationCriticality) else value)
    application.updated_at = _utc_now()
    _commit(db)
    db.refresh(application)
    return application


def soft_delete_application(db: Session, application_id: int) -> Application:
    application = get_application(db, application_id)
    application.active = False
    application.updated_at = _utc_now()
    _commit(db)
    db.refresh(application)
    return application
