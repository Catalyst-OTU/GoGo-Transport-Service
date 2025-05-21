from datetime import datetime
from typing import List, Optional, Literal

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from domains.appraisal.models.appraisal_section import AppraisalSection
from domains.appraisal.repositories.appraisal_cycle import appraisal_cycle_actions as appraisal_cycle_repo
from domains.appraisal.schemas.appraisal_cycle import AppraisalCycleSchema, AppraisalCycleUpdate, AppraisalCycleCreate
from domains.appraisal.schemas.appraisal_cycle import (
    AppraisalCycleWithSections
)
from domains.appraisal.schemas.appraisal_section import AppraisalSectionCreate
from domains.appraisal.services.appraisal_section import appraisal_section_service


class AppraisalCycleService:

    def __init__(self):
        self.repo = appraisal_cycle_repo

    def list_appraisal_cycles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalCycleSchema]:
        appraisal_cycles = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return appraisal_cycles

    def create_appraisal_cycle(self, db: Session, *, data: AppraisalCycleCreate) -> AppraisalCycleSchema:
        date = datetime.now()
        current_year = str(date.year)

        # data.name = data.name.value  # convert enum to string
        data.year = current_year
        appraisal_cycle = self.repo.create(db=db, data=data, unique_fields=['name'])
        return appraisal_cycle

    def update_appraisal_cycle(
            self, db: Session, *, id: UUID4, data: AppraisalCycleUpdate
    ) -> AppraisalCycleWithSections:
        """
        Update Appraisal Cycle and its related sections in one shot.
        """
        # remove sections from payload since they are handled manually
        sections = data.appraisal_sections
        data.appraisal_sections = None

        appraisal_cycle = self.repo.get_by_id(db=db, id=id)
        appraisal_cycle = self.repo.update(db=db, data=data, db_obj=appraisal_cycle, id=id, unique_fields=['name'])

        if sections is not None:
            # ensure all sections for this cycle are unique
            names_with_possible_duplicates = [section.name for section in sections]
            names_with_no_duplicates = set(names_with_possible_duplicates)

            if len(names_with_no_duplicates) != len(names_with_possible_duplicates): raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate sections found: {' ,'.join(names_with_possible_duplicates)}"
            )
            # delete old sections and create new sections in the order they arrived
            appraisal_section_service.repo.bulk_hard_delete(
                db=db, ids=[section.id for section in appraisal_cycle.appraisal_sections]
            )

            for section in sections:
                section_to_create = AppraisalSectionCreate(
                    name=section.name,
                    description=section.description,
                    appraisal_cycle_id=id
                )
                appraisal_section_service.create_appraisal_section(db=db, data=section_to_create, validate_unique=False)
            db.refresh(appraisal_cycle)

        return appraisal_cycle

    def get_appraisal_cycle(self, db: Session, *, id: UUID4) -> AppraisalCycleWithSections:
        appraisal_cycle = self.repo.get_by_id(db=db, id=id)
        return appraisal_cycle

    def delete_appraisal_cycle(self, db: Session, *, id: UUID4) -> None:
        # Check if the appraisal cycle has AppraisalSection
        appraisal_section_query = select(AppraisalSection).where(AppraisalSection.appraisal_cycle_id == id)
        result = db.execute(appraisal_section_query)
        appraisal_section = result.scalars().first()
        if appraisal_section:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete Appraisal Cycle. Appraisal Sections are assigned to this Cycle."
            )

        self.repo.delete(db=db, id=id, soft=False)

    def get_appraisal_cycle_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalCycleSchema]:
        appraisal_cycles = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_cycles

    def search_appraisal_cycles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalCycleSchema]:
        appraisal_cycles = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_cycles


appraisal_cycle_service = AppraisalCycleService()
