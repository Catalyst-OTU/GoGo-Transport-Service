from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status, Header
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.driver.schemas import appraisal as schemas
from domains.driver.services.appraisal import appraisal_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_router = APIRouter(prefix="/forms")


@appraisal_router.get(
    "",
    response_model=List[schemas.AppraisalSchema],
)
def list_appraisals(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        
) -> Any:
    appraisals = actions.list_appraisals(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return appraisals


@appraisal_router.post(
    "",
    response_model=schemas.AppraisalSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_in: schemas.AppraisalCreate,
        
) -> Any:
    appraisal = actions.create_appraisal(db=db, appraisal_in=appraisal_in)
    return appraisal


@appraisal_router.put(
    "/{id}",
    response_model=schemas.AppraisalSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_in: schemas.AppraisalUpdate,
) -> Any:
    appraisal = actions.update_appraisal(db=db, id=id, appraisal_in=appraisal_in)
    return appraisal


@appraisal_router.get(
    "/{id}",
    response_model=schemas.AppraisalSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> Any:
    appraisal = actions.get_appraisal(db=db, id=id)
    return appraisal


@appraisal_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_appraisal(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> None:
    actions.delete_appraisal(db=db, id=id)
