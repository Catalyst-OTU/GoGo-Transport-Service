from datetime import datetime
from typing import Any, List, Optional, Literal

from fastapi import APIRouter, Depends, status, Header
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.driver.schemas import appraisal_input as schemas
from domains.driver.services.appraisal_input import appraisal_input_service as actions
from domains.auth.models.users import User
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_input_router = APIRouter(prefix='/inputs')


@appraisal_input_router.get(
    "",
    response_model=List[schemas.AppraisalInputSchema],

)
def list_appraisal_inputs(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        appraisal_id: Optional[UUID4] = None,
        staff_id: Optional[UUID4] = None,
        appraisal_year: Optional[int] = None,
        cycle: Optional[str] = None,
        department_id: Optional[UUID4] = None,
        is_global: Optional[bool] = None,
        is_active: Optional[bool] = None,
        date_from: datetime = None,
        date_to: datetime = None,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        
) -> Any:
    appraisal_inputs = actions.list_appraisal_inputs(
        db=db, skip=skip, limit=limit,
        appraisal_id=appraisal_id,
        staff_id=staff_id,
        appraisal_year=appraisal_year,
        cycle=cycle,
        department_id=department_id,
        is_global=is_global,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
        order_by=order_by,
        order_direction=order_direction
    )
    return appraisal_inputs


@appraisal_input_router.post(
    "",
    response_model=schemas.AppraisalInputSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_input_in: schemas.AppraisalInputCreate,
        
) -> Any:
    appraisal_input = actions.create_appraisal_input(db=db, appraisal_input_in=appraisal_input_in)
    return appraisal_input


@appraisal_input_router.put(
    "/{id}",
    response_model=schemas.AppraisalInputSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_input_in: schemas.AppraisalInputUpdate,
        
) -> Any:
    appraisal_input = actions.update_appraisal_input(db=db, id=id, appraisal_input_in=appraisal_input_in)
    return appraisal_input


@appraisal_input_router.get(
    "/{id}",
    response_model=schemas.AppraisalInputSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> Any:
    appraisal_input = actions.get_appraisal_input(db=db, id=id)
    return appraisal_input


@appraisal_input_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_appraisal_input(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> None:
    actions.delete_appraisal_input(db=db, id=id)






@appraisal_input_router.get(
    "/section_id/{id}",
    response_model=schemas.AppraisalInputSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal_input_by_section_id(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        section_id: UUID4,
        
) -> Any:
    appraisal_input = actions.get_appraisal_input_by_section_id(db=db, section_id=section_id)
    return appraisal_input
