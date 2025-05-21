from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.driver.schemas import appraisal_template as schemas
from domains.driver.services.appraisal_template import appraisal_template_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_template_router = APIRouter(prefix="/templates")


@appraisal_template_router.get(
    "",
    response_model=List[schemas.AppraisalTemplateSchema],
)
def list_appraisal_templates(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    appraisal_templates = actions.list_appraisal_templates(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return appraisal_templates


@appraisal_template_router.post(
    "",
    response_model=schemas.AppraisalTemplateSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_appraisal_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_template_in: schemas.AppraisalTemplateCreate
) -> Any:
    appraisal_template = actions.create_appraisal_template(db=db, appraisal_template_in=appraisal_template_in)
    return appraisal_template


@appraisal_template_router.put(
    "/{id}",
    response_model=schemas.AppraisalTemplateSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_appraisal_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_template_in: schemas.AppraisalTemplateUpdate,
) -> Any:
    appraisal_template = actions.update_appraisal_template(db=db, id=id, appraisal_template_in=appraisal_template_in)
    return appraisal_template


@appraisal_template_router.get(
    "/{id}",
    response_model=schemas.AppraisalTemplateSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_template = actions.get_appraisal_template(db=db, id=id)
    return appraisal_template


@appraisal_template_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_appraisal_template(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    actions.delete_appraisal_template(db=db, id=id)
