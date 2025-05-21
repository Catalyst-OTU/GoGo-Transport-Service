from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.driver.schemas import appraisal_cycle as schemas
from domains.driver.services.appraisal_cycle import appraisal_cycle_service as actions
from utils.rbac import get_current_user, require_permissions
from utils.schemas import HTTPError

appraisal_cycle_router = APIRouter(prefix="/cycles")


@appraisal_cycle_router.get(
    "",
    response_model=List[schemas.AppraisalCycleSchema],
    # dependencies=[Depends(require_permissions("readAppraisalCycle"))]
)
async def list_appraisal_cycles(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc'
) -> Any:
    appraisal_cycles = actions.list_appraisal_cycles(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return appraisal_cycles


@appraisal_cycle_router.post(
    "",
    response_model=schemas.AppraisalCycleSchema,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permissions("createAppraisalCycle"))]
)
async def create_appraisal_cycle(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.AppraisalCycleCreate
) -> Any:
    appraisal_cycle = actions.create_appraisal_cycle(db=db, data=data)
    return appraisal_cycle


@appraisal_cycle_router.put(
    "/{id}",
    response_model=schemas.AppraisalCycleWithSections,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("updateAppraisalCycle"))]
)
async def update_appraisal_cycle(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.AppraisalCycleUpdate,
) -> Any:
    appraisal_cycle = actions.update_appraisal_cycle(db=db, id=id, data=data)
    return appraisal_cycle


@appraisal_cycle_router.get(
    "/{id}",
    response_model=schemas.AppraisalCycleWithSections,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("getAppraisalCycleByID"))]
)
async def get_appraisal_cycle(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_cycle = actions.get_appraisal_cycle(db=db, id=id)
    return appraisal_cycle


@appraisal_cycle_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("deleteAppraisalCycle"))]
)
async def delete_appraisal_cycle(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    actions.delete_appraisal_cycle(db=db, id=id)












@appraisal_cycle_router.get(
    "/cycle_id/{id}",
    response_model=schemas.AppraisalCycleWithSections,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("getAppraisalCycleByID"))]
)
async def get_appraisal_sections_by_cycle_id(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_cycle = actions.get_appraisal_sections_by_cycle_id(db=db, id=id)
    return appraisal_cycle