from typing import List, Optional, Literal

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.appraisal.repositories.appraisal_section import appraisal_section_actions as appraisal_section_repo
from domains.appraisal.schemas.appraisal_section import (
    AppraisalSectionSchema,
    AppraisalSectionUpdate,
    AppraisalSectionCreate
)


class AppraisalSectionService:

    def __init__(self):
        self.repo = appraisal_section_repo

    def list_appraisal_sections(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            cycle_id: UUID4 = None,
    ) -> List[AppraisalSectionSchema]:
        appraisal_sections = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction,
            cycle_id=cycle_id
        )
        return appraisal_sections

    def create_appraisal_section(
            self, db: Session, *, data: AppraisalSectionCreate, validate_unique=True
    ) -> AppraisalSectionSchema:
        # validate unique field 'name' but only unique to the associated cycle
        if validate_unique and self.repo.get_by_filters(db=db, appraisal_cycle_id=data.appraisal_cycle_id, name=data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"'name' for {data.name} already exists")

        appraisal_section = self.repo.create(db=db, data=data)
        return appraisal_section

    def update_appraisal_section(
            self, db: Session, *, id: UUID4, data: AppraisalSectionUpdate
    ) -> AppraisalSectionSchema:
        appraisal_section = self.repo.get_by_id(db=db, id=id)
        appraisal_section = self.repo.update(db=db, db_obj=appraisal_section, data=data)
        return appraisal_section

    def get_appraisal_section(self, db: Session, *, id: UUID4, silent=False) -> AppraisalSectionSchema:
        appraisal_section = self.repo.get_by_id(db=db, id=id, silent=silent)
        return appraisal_section

    def delete_appraisal_section(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_appraisal_section_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSectionSchema]:
        appraisal_sections = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_sections

    def search_appraisal_sections(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSectionSchema]:
        appraisal_sections = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_sections


appraisal_section_service = AppraisalSectionService()
