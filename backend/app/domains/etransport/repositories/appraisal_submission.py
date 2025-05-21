from datetime import datetime
from typing import Any, Optional, Sequence, Literal

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from crud.base import CRUDBase
from domains.appraisal.models import Appraisal, DepartmentGroup, AppraisalInput
from domains.appraisal.models.appraisal_submission import AppraisalSubmission
from domains.appraisal.schemas.appraisal_submission import (
    AppraisalSubmissionCreate, AppraisalSubmissionUpdate
)
from domains.organization.models import Staff, Department


class CRUDAppraisalSubmission(CRUDBase[AppraisalSubmission, AppraisalSubmissionCreate, AppraisalSubmissionUpdate]):
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
    ) -> Sequence[AppraisalSubmission]:
        """
        Fetch submissions filtered by various parameters.
        """
        query = (
            self.query
            .join(AppraisalInput)
            .join(Appraisal)
            .join(Staff)
            .join(DepartmentGroup)
            .join(Department)
        )

        # Apply dynamic filters
        if appraisal_year: query = query.filter(Appraisal.year == appraisal_year)
        if cycle: query = query.filter(Appraisal.cycle == cycle)
        if department_id: query = query.filter(Department.id == department_id)
        if staff_id: query = query.filter(AppraisalSubmission.staff_id == staff_id)
        if submitted is not None: query = query.filter(AppraisalSubmission.submitted == submitted)
        if completed is not None: query = query.filter(AppraisalSubmission.completed == completed)
        if order_by:
            try:
                order_column = getattr(self.model, order_by)
            except AttributeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Invalid key given to order_by: {order_by}'
                )
            query = self.query.order_by(
                order_column.desc() if order_direction == 'desc' else order_column.asc()
            )
        else:
            query = self.query.order_by(desc(self.model.created_date))

        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()


    def get_all(
            self, db: Session, *, skip: int = 0, limit: int = 100,
            staff_id: str = None,
            date_from: datetime = None,
            date_to: datetime = None,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[AppraisalSubmission]:
        query = self.query

        if staff_id is not None: query = query.filter(self.model.staff_id == staff_id)
        if date_to: query = query.filter(self.model.started_at <= date_to)
        if date_from: query = query.filter(self.model.started_at >= date_from)

        if order_by:
            try:
                order_column = getattr(self.model, order_by)
            except AttributeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Invalid key given to order_by: {order_by}'
                )
            query = self.query.order_by(
                order_column.desc() if order_direction == 'desc' else order_column.asc()
            )
        else:
            query = self.query.order_by(desc(self.model.created_date))

        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def get_all_appraisal_submissions_by_staff(
            self, *, db: Session, skip: int = 0, limit: int = 100, staff_id: UUID4, year: int
    ) -> Optional[Sequence[AppraisalSubmission]]:
        submissions = (
            self.query
            .join(AppraisalInput)
            .join(Appraisal)
            .filter(self.model.staff_id == staff_id, Appraisal.year == year)
            .offset(skip).limit(limit)
        )
        query = submissions.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def get_all_appraisal_submissions_by_department(
            self, *, db: Session, skip: int = 0, limit: int = 100, department_id: UUID4, year: int,
    ) -> Optional[Sequence[AppraisalSubmission]]:
        submissions = (
            self.query
            .join(AppraisalSubmission.appraisal_input)
            .join(AppraisalInput.department_group)
            .join(DepartmentGroup.department)
            .join(AppraisalInput.appraisal)
            .filter(Department.id == department_id)
            .filter(Appraisal.year == year)
            .offset(skip).limit(limit)
        )

        query = submissions.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def update_answer_in_submission(
            self, *, db: Session, id: UUID4, group_name: str, field_name: str, new_answer: str
    ) -> AppraisalSubmission:
        """
        Update a specific question's answer in a submission.
        """
        submission = self.get_by_id(db=db, id=id)

        if submission.completed:
            raise ValueError(f"Submission is marked as complete and cannot be updated.")

        # Check if the group exists in the JSON data
        if group_name not in submission.data:
            raise ValueError(f"Group '{group_name}' not found in the submission data.")

        # Check if the question exists in the group
        if field_name not in submission.data[group_name]:
            raise ValueError(f"Question '{field_name}' not found in the group '{group_name}'.")

        # Update the specific question's answer
        submission.data[group_name][field_name] = new_answer

        flag_modified(submission, "data")
        db.commit()
        db.refresh(submission)
        return submission

    def modify_or_add_answers(
            self, *, db: Session, id: UUID4, updates: dict
    ) -> AppraisalSubmission:
        """
        Modify existing answers and add new ones in the submission data field.

        Args:
            db: Database session.
            id: ID of the submission to update.
            updates: A dictionary where keys are group names, and values are dictionaries of
                     question IDs and their new answers.

        Returns:
            Submission: The updated submission.
        """
        submission = self.get_by_id(db=db, id=id)

        if submission.completed:
            raise ValueError(f"Submission is marked as complete and cannot be updated.")

        # Update or add answers
        for group_name, questions in updates.items():
            if group_name not in submission.data:
                # Add new group if it doesn't exist
                submission.data[group_name] = {}

            for field_name, new_answer in questions.items():
                # Update existing question or add new one
                submission.data[group_name][field_name] = new_answer

        flag_modified(submission, "data")
        db.commit()
        db.refresh(submission)
        return submission

    def get_summary_results(
            self, *, db: Session,
            year: int = None,
            staff_id: UUID4 = None,
            department_group_id: UUID4 = None,
            cycle: str = None
    ) -> dict[str, Any]:
        """
        Fetch summary results grouped by group_name, filtered by year, staff_id, and department_group_id
        """
        query = (
            self.query
            .join(Appraisal, AppraisalSubmission.appraisal_id == Appraisal.id)
            .join(Staff, AppraisalSubmission.staff_id == Staff.id)
            .join(AppraisalInput, AppraisalSubmission.appraisal_input_id == AppraisalInput.id)
            .join(DepartmentGroup, AppraisalInput.department_group_id == DepartmentGroup.id)
            .options(
                selectinload(AppraisalSubmission.staff_id),
                selectinload(AppraisalSubmission.appraisal_input_id),
                selectinload(AppraisalInput.department_group_id),
            )
        )

        # Apply filters dynamically
        if year:
            query = query.filter(Appraisal.year == year)
        if staff_id:
            query = query.filter(AppraisalSubmission.staff_id == staff_id)
        if department_group_id:
            query = query.filter(AppraisalInput.department_group_id == department_group_id)
        if cycle:
            query = query.filter(Appraisal.cycle == cycle)

        result = db.execute(query)
        submissions = result.scalars().all()

        # Results organized by staff
        summary_results = {}

        for submission in submissions:
            appraisal = submission.appraisal
            appraisal_id = str(appraisal.id)
            staff_id = str(submission.staff_id)
            form_template = submission.appraisal_input.form_fields

            if staff_id not in summary_results:
                summary_results[staff_id] = {
                    "appraisal_id": appraisal_id,
                    "staff_id": staff_id,
                    "groups": {}
                }

            for group in form_template:
                group_name = group["group_name"]

                if group_name not in summary_results[staff_id]["groups"]:
                    summary_results[staff_id]["groups"][group_name] = []

                for field in group["fields"]:
                    field_name = field["field_name"]
                    field_text = field["field_text"]
                    answer = submission.data.get(group_name, {}).get(field_name, None)

                    summary_results[staff_id]["groups"][group_name].append({
                        "field_name": field_name,
                        "field_text": field_text,
                        "answer": answer
                    })
        return summary_results


appraisal_submission_actions = CRUDAppraisalSubmission(
    AppraisalSubmission,
    select_related=(
        AppraisalSubmission.staff,
        AppraisalSubmission.appraisal,
        AppraisalSubmission.appraisal_input,
    )
)
