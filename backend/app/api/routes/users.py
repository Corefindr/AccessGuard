from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserRead, UserReplace, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserRead],
    summary="List users",
    description="Return users with optional active, team, and search filters. Search matches name, employee_id, and email.",
)
def list_users(
    active: bool | None = Query(default=None),
    team: str | None = Query(default=None),
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    return user_service.list_users(
        db,
        active=active,
        team=team,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user",
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    return user_service.get_user(db, user_id)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    return user_service.create_user(db, payload)


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Replace user",
)
def replace_user(user_id: int, payload: UserReplace, db: Session = Depends(get_db)) -> UserRead:
    return user_service.replace_user(db, user_id, payload)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update user",
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> UserRead:
    return user_service.update_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    response_model=UserRead,
    summary="Deactivate user",
    description="Soft-deletes the user by setting active=false. The row is retained for audit history.",
)
def deactivate_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    return user_service.soft_delete_user(db, user_id)
