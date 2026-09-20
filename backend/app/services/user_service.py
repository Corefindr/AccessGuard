from datetime import datetime, timezone

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models import User
from app.schemas.user import UserCreate, UserReplace, UserUpdate


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("The requested change conflicts with an existing user.") from exc


def _ensure_unique(
    db: Session,
    *,
    employee_id: str,
    email: str,
    exclude_user_id: int | None = None,
) -> None:
    employee_stmt: Select[tuple[User]] = select(User).where(User.employee_id == employee_id)
    email_stmt: Select[tuple[User]] = select(User).where(User.email == email)
    if exclude_user_id is not None:
        employee_stmt = employee_stmt.where(User.id != exclude_user_id)
        email_stmt = email_stmt.where(User.id != exclude_user_id)
    if db.scalar(employee_stmt) is not None:
        raise ConflictError("A user with this employee_id already exists.")
    if db.scalar(email_stmt) is not None:
        raise ConflictError("A user with this email already exists.")


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")
    return user


def list_users(
    db: Session,
    *,
    active: bool | None = None,
    team: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[User]:
    stmt = select(User).order_by(User.id)
    if active is not None:
        stmt = stmt.where(User.active.is_(active))
    if team:
        stmt = stmt.where(func.lower(User.team) == team.strip().lower())
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.name.ilike(term),
                User.employee_id.ilike(term),
                User.email.ilike(term),
            )
        )
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create_user(db: Session, payload: UserCreate) -> User:
    _ensure_unique(db, employee_id=payload.employee_id, email=payload.email)
    user = User(**payload.model_dump())
    db.add(user)
    _commit(db)
    db.refresh(user)
    return user


def replace_user(db: Session, user_id: int, payload: UserReplace) -> User:
    user = get_user(db, user_id)
    _ensure_unique(
        db,
        employee_id=payload.employee_id,
        email=payload.email,
        exclude_user_id=user.id,
    )
    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    user.updated_at = _utc_now()
    _commit(db)
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    changes = payload.model_dump(exclude_unset=True)
    employee_id = changes.get("employee_id", user.employee_id)
    email = changes.get("email", user.email)
    _ensure_unique(db, employee_id=employee_id, email=email, exclude_user_id=user.id)
    for field, value in changes.items():
        setattr(user, field, value)
    user.updated_at = _utc_now()
    _commit(db)
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    user.active = False
    user.updated_at = _utc_now()
    _commit(db)
    db.refresh(user)
    return user
