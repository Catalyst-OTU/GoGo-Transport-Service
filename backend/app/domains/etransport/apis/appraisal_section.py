from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.driver.schemas import appraisal_section as schemas
from domains.driver.services.appraisal_section import appraisal_section_service as actions
from utils.rbac import get_current_user, require_permissions
from utils.schemas import HTTPError

appraisal_section_router = APIRouter(prefix="/sections")


@appraisal_section_router.get(
    "",
    response_model=List[schemas.AppraisalSectionSchema],
    # dependencies=[Depends(require_permissions("readAppraisalSection"))]
)
async def list_appraisal_sections(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        cycle_id: UUID4 = None,
) -> Any:
    appraisal_sections = actions.list_appraisal_sections(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction,
        cycle_id=cycle_id
    )
    return appraisal_sections


@appraisal_section_router.post(
    "",
    response_model=schemas.AppraisalSectionSchema,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permissions("createAppraisalSection"))]
)
async def create_appraisal_section(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        data: schemas.AppraisalSectionCreate
) -> Any:
    appraisal_section = actions.create_appraisal_section(db=db, data=data)
    return appraisal_section


@appraisal_section_router.put(
    "/{id}",
    response_model=schemas.AppraisalSectionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("updateAppraisalSection"))]
)
async def update_appraisal_section(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.AppraisalSectionUpdate,
) -> Any:
    appraisal_section = actions.update_appraisal_section(db=db, id=id, data=data)
    return appraisal_section


@appraisal_section_router.get(
    "/{id}",
    response_model=schemas.AppraisalSectionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("getAppraisalSectionByID"))]
)
async def get_appraisal_section(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> Any:
    appraisal_section = actions.get_appraisal_section(db=db, id=id)
    return appraisal_section


@appraisal_section_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    # dependencies=[Depends(require_permissions("deleteAppraisalSection"))]
)
async def delete_appraisal_section(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    actions.delete_appraisal_section(db=db, id=id)
