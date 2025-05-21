from datetime import datetime
from typing import Any, List, Optional, Literal

from sqlalchemy.orm import Session

from db.session import get_db
from domains.driver.schemas import appraisal_submission as schemas
from domains.driver.services.appraisal_submission import appraisal_submission_service as actions
from domains.auth.models.users import User
from fastapi import APIRouter, Depends, Query, status, Header
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import get_current_user
from utils.schemas import HTTPError

appraisal_submission_router = APIRouter(prefix='/submissions')



@appraisal_submission_router.get(
    "",
    response_model=List[schemas.AppraisalSubmissionSchema],
)
def list_appraisal_submissions(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        staff_id: UUID4 = None,
        skip: int = 0,
        limit: int = 100,
        date_from: datetime = None,
        date_to: datetime = None,
        order_by: str = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        
) -> Any:
    appraisal_submissions = actions.list_appraisal_submissions(
        db=db, skip=skip, limit=limit,
        staff_id=staff_id,
        date_from=date_from, date_to=date_to,
        order_by=order_by, order_direction=order_direction
    )
    return appraisal_submissions


@appraisal_submission_router.post(
    "",
    response_model=schemas.AppraisalSubmissionSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        appraisal_submission_in: schemas.AppraisalSubmissionCreate,
        
) -> Any:
    appraisal_submission = actions.create_appraisal_submission(db=db, appraisal_submission_in=appraisal_submission_in)
    return appraisal_submission



@appraisal_submission_router.put(
    "/{id}",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        appraisal_submission_in: schemas.AppraisalSubmissionUpdate,
        
) -> Any:
    appraisal_submission = actions.update_appraisal_submission(db=db, id=id, appraisal_submission_in=appraisal_submission_in)
    return appraisal_submission


@appraisal_submission_router.put(
    "/{id}/update-answers/",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}}
)
def modify_or_add_answers(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        updates: dict,
        
) -> Any:
    try:
        return actions.modify_or_add_answers(db=db, id=id, updates=updates)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@appraisal_submission_router.put(
    "/{id}/update-answer/",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},

)
def update_submission_answer(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        group_name: str,
        field_name: str,
        new_answer: str,
        
):
    """
    Update a specific question's answer in a submission.
    """
    try:
        return actions.update_submission_answer(
            db=db,
            id=id,
            group_name=group_name,
            field_name=field_name,
            new_answer=new_answer
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@appraisal_submission_router.get(
    "/{id}",
    response_model=schemas.AppraisalSubmissionSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> Any:
    appraisal_submission = actions.get_appraisal_submission(db=db, id=id)
    return appraisal_submission


@appraisal_submission_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_appraisal_submission(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> None:
    actions.delete_appraisal_submission(db=db, id=id)



# Summaries ########################################################################################
appraisal_summary_router = APIRouter(prefix='/summaries')


@appraisal_summary_router.get(
    "/summary_results",
    response_model=dict[str, Any],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_summary_results_endpoint(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        year: Optional[int] = Query(None, description="Filter by appraisal year"),
        staff_id: Optional[UUID4] = Query(None, description="Filter by staff ID"),
        department_group_id: Optional[UUID4] = Query(None, description="Filter by department group ID"),
        cycle: Optional[str] = Query(None, description="Filter by appraisal cycle (e.g., H1, H2)"),
        
) -> Any:
    """
    Fetch summary results grouped by group_name, filtered by year, staff_id and department_group_id.
    """
    return actions.get_summary_results(
        db=db,
        year=year,
        staff_id=staff_id,
        department_group_id=department_group_id,
        cycle=cycle
    )


@appraisal_summary_router.get(
    "/reports",
    response_model=List[schemas.AppraisalSubmissionSchema],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_filtered_submissions_report(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        skip: int = 0, limit: int = 100,
        appraisal_year: Optional[UUID4] = Query(None, description="Filter by appraisal year"),
        cycle: Optional[str] = Query(None, description="Filter by appraisal cycle (e.g., H1, H2)"),
        department_id: Optional[UUID4] = Query(None, description="Filter by department ID"),
        staff_id: Optional[UUID4] = Query(None, description="Filter by staff ID"),
        submitted: Optional[bool] = Query(None, description="Filter by submission status"),
        completed: Optional[bool] = Query(None, description="Filter by completion status"),
        order_by: Optional[str] = None,
        order_direction: Literal['asc', 'desc'] = 'asc',
        
) -> Any:
    """
    Get filtered submission reports.
    """
    return actions.get_filtered_submissions(
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
