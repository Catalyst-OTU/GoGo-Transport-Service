from typing import Any, List, Literal

from fastapi import APIRouter, Depends, status, Header
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.driver.schemas import department_group as schemas
from domains.driver.services.department_group import department_group_service as actions
from utils.rbac import get_current_user
from utils.schemas import HTTPError

department_group_router = APIRouter(prefix="/department_groups")


@department_group_router.get(
    "",
    response_model=List[schemas.DepartmentGroupSchema],
)
def list_department_groups(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        
) -> Any:
    department_groups = actions.list_department_groups(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return department_groups


@department_group_router.post(
    "",
    response_model=schemas.DepartmentGroupSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        department_group_in: schemas.DepartmentGroupCreate,
        
) -> Any:
    department_group = actions.create_department_group(db=db, department_group_in=department_group_in)
    return department_group


@department_group_router.put(
    "/{id}",
    response_model=schemas.DepartmentGroupSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        department_group_in: schemas.DepartmentGroupUpdate,
        
) -> Any:
    department_group = actions.update_department_group(db=db, id=id, department_group_in=department_group_in)
    return department_group


@department_group_router.get(
    "/{id}",
    response_model=schemas.DepartmentGroupSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> Any:
    department_group = actions.get_department_group(db=db, id=id)
    return department_group


@department_group_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_department_group(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> None:
    actions.delete_department_group(db=db, id=id)
