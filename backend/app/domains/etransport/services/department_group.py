from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from pydantic import UUID4
from domains.appraisal.repositories.department_group import department_group_actions as department_group_repo
from domains.appraisal.schemas.department_group import DepartmentGroupSchema, DepartmentGroupUpdate, DepartmentGroupCreate


class DepartmentGroupService:

    def __init__(self):
        self.repo = department_group_repo

    def list_department_groups(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[DepartmentGroupSchema]:
        department_groups = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return department_groups

    def create_department_group(self, db: Session, *, department_group_in: DepartmentGroupCreate) -> DepartmentGroupSchema:
        department_group = self.repo.create(db=db, data=department_group_in)
        return department_group

    def update_department_group(self, db: Session, *, id: UUID4, department_group_in: DepartmentGroupUpdate) -> DepartmentGroupSchema:
        department_group = self.repo.get_by_id(db=db, id=id)
        department_group = self.repo.update(db=db, db_obj=department_group, data=department_group_in)
        return department_group

    def get_department_group(self, db: Session, *, id: UUID4) -> DepartmentGroupSchema:
        department_group = self.repo.get_by_id(db=db, id=id)
        return department_group

    def delete_department_group(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_department_group_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DepartmentGroupSchema]:
        department_groups = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return department_groups

    def search_department_groups(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DepartmentGroupSchema]:
        department_groups = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return department_groups


department_group_service = DepartmentGroupService()
