from datetime import datetime
from typing import List, Any, Optional, Literal

from fastapi import HTTPException, status
from pydantic import ValidationError, UUID4
from sqlalchemy.orm import Session

from config.logger import log
from domains.appraisal.repositories.appraisal_submission import (
    appraisal_submission_actions as appraisal_submission_repo
)
from domains.appraisal.schemas.appraisal_submission import (
    AppraisalSubmissionSchema, AppraisalSubmissionUpdate, AppraisalSubmissionCreate
)


class AppraisalSubmissionService:

    def __init__(self):
        self.repo = appraisal_submission_repo

    def get_filtered_submissions(
            self, *, db: Session,
            skip: int = 0, limit: int = 100,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID4] = None,
            staff_id: Optional[UUID4] = None,
            submitted: Optional[bool] = None,
            completed: Optional[bool] = None,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = self.repo.get_filtered_submissions(
            db=db, skip=skip, limit=limit,
            appraisal_year=appraisal_year,
            cycle=cycle,
            department_id=department_id,
            staff_id=staff_id,
            submitted=submitted,
            completed=completed,
            order_by=order_by,
            order_direction=order_direction,
        )
        return appraisal_submissions

    def list_appraisal_submissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            staff_id: str = None,
            date_from: datetime = None,
            date_to: datetime = None,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = self.repo.get_all(
            db=db, skip=skip, limit=limit,
            staff_id=staff_id,
            date_from=date_from, date_to=date_to,
            order_by=order_by, order_direction=order_direction
        )
        return appraisal_submissions

    def create_appraisal_submission(
            self, db: Session, *,appraisal_submission_in: AppraisalSubmissionCreate
    ) -> AppraisalSubmissionSchema:
        appraisal_submission = self.repo.create(db=db, data=appraisal_submission_in)
        return appraisal_submission

    def update_appraisal_submission(
            self, *, db: Session, id: UUID4, appraisal_submission_in: AppraisalSubmissionUpdate
    ) -> AppraisalSubmissionSchema:
        appraisal_submission = self.repo.get(db=db, id=id)
        if not appraisal_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal submission not found"
            )
        if appraisal_submission.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appraisal submission already completed"
            )
        appraisal_submission = self.repo.update(
            db=db, db_obj=appraisal_submission, data=appraisal_submission_in
        )
        return appraisal_submission

    def get_appraisal_submission(self, db: Session, *, id: UUID4) -> AppraisalSubmissionSchema:
        appraisal_submission = self.repo.get_by_id(db=db, id=id)
        return appraisal_submission

    def delete_appraisal_submission(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_appraisal_submission_by_id(self, *, id: UUID4) -> AppraisalSubmissionSchema:
        appraisal_submission = self.repo.get(id)
        if not appraisal_submission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Appraisal submission not found"
            )
        return appraisal_submission

    def get_appraisal_submission_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_submissions

    def search_appraisal_submissions(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[AppraisalSubmissionSchema]:
        appraisal_submissions = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return appraisal_submissions

    def list_appraisal_submissions_by_staff(
            self, *, db: Session, skip: int = 0, limit: int = 100, staff_id: UUID4, year: int
    ):
        return self.repo.get_all_appraisal_submissions_by_staff(
            db=db, skip=skip, limit=limit, staff_id=staff_id, year=year
        )

    def list_appraisal_submissions_by_department(
            self, *, db: Session, skip: int = 0, limit: int = 100, department_id: UUID4, year: int,
    ):
        return self.repo.get_all_appraisal_submissions_by_department(
            db=db, skip=skip, limit=limit, department_id=department_id, year=year
        )

    def update_submission_answer(
            self, *, db,
            id: UUID4,
            group_name: str,
            field_name: str,
            new_answer: str,
    ):
        return self.repo.update_answer_in_submission(
            db=db, id=id, group_name=group_name, field_name=field_name, new_answer=new_answer
        )

    def modify_or_add_answers(
            self, *, db: Session, id: UUID4, updates: dict
    ) -> AppraisalSubmissionSchema:
        try:
            return self.repo.modify_or_add_answers(
                db=db, id=id, updates=updates
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
        except AttributeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format received.'
            )
        except:
            log.exception('Failed to modify or add appraisal submission answers')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='An error occurred.'
            )

    def get_summary_results(
            self, *, db: Session,
            year: int = None,
            staff_id: UUID4 = None,
            department_group_id: UUID4 = None,
            cycle: str = None
    ) -> dict[str, Any]:
        return self.repo.get_summary_results(
            db=db, year=year, staff_id=staff_id, department_group_id=department_group_id, cycle=cycle
        )


appraisal_submission_service = AppraisalSubmissionService()
