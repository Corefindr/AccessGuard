from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.enums import ApplicationCriticality
from app.database.session import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationReplace,
    ApplicationUpdate,
)
from app.services import application_service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get(
    "",
    response_model=list[ApplicationRead],
    summary="List applications",
    description="Return applications with optional active, criticality, and search filters. Search matches name, description, and application_owner.",
)
def list_applications(
    active: bool | None = Query(default=None),
    criticality: ApplicationCriticality | None = Query(default=None),
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ApplicationRead]:
    return application_service.list_applications(
        db,
        active=active,
        criticality=criticality,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationRead,
    summary="Get application",
)
def get_application(application_id: int, db: Session = Depends(get_db)) -> ApplicationRead:
    return application_service.get_application(db, application_id)


@router.post(
    "",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create application",
)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
) -> ApplicationRead:
    return application_service.create_application(db, payload)


@router.put(
    "/{application_id}",
    response_model=ApplicationRead,
    summary="Replace application",
)
def replace_application(
    application_id: int,
    payload: ApplicationReplace,
    db: Session = Depends(get_db),
) -> ApplicationRead:
    return application_service.replace_application(db, application_id, payload)


@router.patch(
    "/{application_id}",
    response_model=ApplicationRead,
    summary="Update application",
)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
) -> ApplicationRead:
    return application_service.update_application(db, application_id, payload)


@router.delete(
    "/{application_id}",
    response_model=ApplicationRead,
    summary="Deactivate application",
    description="Soft-deletes the application by setting active=false. The row is retained for audit history.",
)
def deactivate_application(
    application_id: int,
    db: Session = Depends(get_db),
) -> ApplicationRead:
    return application_service.soft_delete_application(db, application_id)
