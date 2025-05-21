from typing import List, Optional, Literal

from sqlalchemy.orm import Session

from pydantic import UUID4
from domains.appraisal.repositories.appraisal import appraisal_actions as appraisal_repo
from domains.appraisal.schemas.appraisal import AppraisalSchema, AppraisalUpdate, AppraisalCreate


class AppraisalService:

    def __init__(self):
        self.repo = appraisal_repo

    def list_appraisals(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalSchema]:
        appraisals = self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return appraisals

    def create_appraisal(self, db: Session, *, appraisal_in: AppraisalCreate) -> AppraisalSchema:
        appraisal = self.repo.create(db=db, data=appraisal_in)
        return appraisal

    def update_appraisal(self, db: Session, *, id: UUID4, appraisal_in: AppraisalUpdate) -> AppraisalSchema:
        appraisal = self.repo.get_by_id(db=db, id=id)
        appraisal = self.repo.update(db=db, db_obj=appraisal, data=appraisal_in)
        return appraisal

    def get_appraisal(self, db: Session, *, id: UUID4) -> AppraisalSchema:
        appraisal = self.repo.get_by_id(db=db, id=id)
        return appraisal

    def delete_appraisal(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_appraisal_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSchema]:
        appraisals = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisals

    def search_appraisals(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSchema]:
        appraisals = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisals


appraisal_service = AppraisalService()
