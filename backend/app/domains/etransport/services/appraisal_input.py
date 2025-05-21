from datetime import datetime
from typing import List, Optional, Literal
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from domains.appraisal.models.appraisal_input import AppraisalInput
from uuid import UUID as UUIDType
from domains.appraisal.repositories.appraisal import appraisal_actions
from domains.appraisal.repositories.appraisal_section import appraisal_section_actions
from domains.appraisal.repositories.appraisal_input import appraisal_input_actions as appraisal_input_repo
from domains.appraisal.repositories.department_group import department_group_actions
from domains.appraisal.schemas.appraisal_input import (
    AppraisalInputSchema, AppraisalInputUpdate, AppraisalInputCreate
)
from domains.organization.repositories.department import department_actions


class AppraisalInputService:

    def __init__(self):
        self.repo = appraisal_input_repo

    def list_appraisal_inputs(
            self, *,
            db: Session,
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
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalInputSchema]:
        appraisal_inputs = self.repo.list_appraisal_input_for_staff(
            db=db, skip=skip, limit=limit,
            is_global=is_global,
            appraisal_id=appraisal_id,
            staff_id=staff_id,
            appraisal_year=appraisal_year,
            cycle=cycle,
            department_id=department_id,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
            order_by=order_by,
            order_direction=order_direction
        )
        if not appraisal_inputs: return []
        appraisal_ids = {
            input.appraisal_id for input in appraisal_inputs if input.appraisal_id is not None
        }
        department_group_ids = {
            input.department_group_id for input in appraisal_inputs if
            input.department_group_id is not None
        }

        department_ids = {
            id for input in appraisal_inputs
            if input.department_ids is not None
            for id in input.department_ids
            if id is not None
        }

        appraisals_map = {
            str(a.id): a for a in appraisal_actions.get_all_by_ids_silently(db=db, ids=list(appraisal_ids))
        } if appraisal_ids else dict()

        department_groups_map = {
            str(d.id): d for d in
            department_group_actions.get_all_by_ids_silently(db=db, ids=list(department_group_ids))
        } if department_group_ids else dict()

        departments_map = {
            str(d.id): d for d in department_actions.get_all_by_ids_silently(db=db, ids=list(department_ids))
        } if department_ids else dict()

        return [
            AppraisalInputSchema(
                **{k: v for k, v in input.__dict__.items() if k != '_sa_instance_state'},
                departments=[
                    departments_map.get(id)
                    for id in (input.department_ids or [])
                    if id is not None and id in departments_map
                ],
                appraisal=appraisals_map.get(str(input.appraisal_id)) if input.appraisal_id is not None else None,
                department_group=department_groups_map.get(
                    str(input.department_group_id)) if input.department_group_id is not None else None
            )
            for input in appraisal_inputs
        ]

    # def create_appraisal_input(
    #         self, db: Session, *,appraisal_input_in: AppraisalInputCreate
    # ) -> AppraisalInputSchema:
    #     appraisal_input = self.repo.create(db=db, data=appraisal_input_in)
    #     return appraisal_input
    


    def create_appraisal_input(self, db: Session, *, appraisal_input_in: AppraisalInputCreate) -> AppraisalInputSchema:
        existing = db.query(AppraisalInput).filter_by(appraisal_section_id=appraisal_input_in.appraisal_section_id).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="An appraisal input with this appraisal section already exists.",
            )

        data = appraisal_input_in.dict()

        if data.get("department_ids"):
            data["department_ids"] = [str(d) if isinstance(d, UUIDType) else d for d in data["department_ids"]]

        appraisal_input = self.repo.create(db=db, data=data)
        return appraisal_input

    



    def update_appraisal_input(
            self, db: Session, *, id: UUID4, appraisal_input_in: AppraisalInputUpdate
    ) -> AppraisalInputSchema:
        appraisal_input = self.repo.get_by_id(db=db, id=id)

        data = appraisal_input_in.dict()

        if data.get("department_ids"):
            data["department_ids"] = [str(d) if isinstance(d, UUIDType) else d for d in data["department_ids"]]
        appraisal_input = self.repo.update(db=db, db_obj=appraisal_input, data=data)

        return appraisal_input

    def get_appraisal_input(self, *, db: Session, id: UUID4) -> AppraisalInputSchema:
        appraisal_input = self.repo.get_by_id(db=db, id=id)

        appraisal_input_dict = appraisal_input.__dict__
        appraisal_input_dict.pop('_sa_instance_state', None)

        return AppraisalInputSchema(
            **appraisal_input_dict,
            departments=department_actions.get_many_by_ids(db=db, ids=appraisal_input.department_ids),
            appraisal_section=appraisal_section_actions.get_by_id(db=db, id=appraisal_input.appraisal_section_id),
            department_group=department_group_actions.get_by_id(db=db, id=appraisal_input.department_group_id),
        )
    



    def get_appraisal_input_by_section_id(self, *, db: Session, section_id: UUID4) -> AppraisalInputSchema:
        appraisal_input = self.repo.get_by_field(db=db, field='appraisal_section_id', value=section_id)

        appraisal_input_dict = appraisal_input.__dict__
        appraisal_input_dict.pop('_sa_instance_state', None)

        return AppraisalInputSchema(
            **appraisal_input_dict,
            departments=department_actions.get_many_by_ids(db=db, ids=appraisal_input.department_ids),
            appraisal_section=appraisal_section_actions.get_by_id(db=db, id=appraisal_input.appraisal_section_id),
            department_group=department_group_actions.get_by_id(db=db, id=appraisal_input.department_group_id),
        )

    def delete_appraisal_input(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_appraisal_input_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalInputSchema]:
        appraisal_inputs = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_inputs

    def search_appraisal_inputs(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalInputSchema]:
        appraisal_inputs = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_inputs


appraisal_input_service = AppraisalInputService()
