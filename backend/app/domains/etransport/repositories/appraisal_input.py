from datetime import datetime
from typing import Optional, Sequence, Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import log
from crud.base import CRUDBase
from domains.appraisal.models import Appraisal
from domains.appraisal.models.appraisal_input import AppraisalInput
from domains.appraisal.schemas.appraisal_input import (
    AppraisalInputCreate, AppraisalInputUpdate
)
from domains.organization.repositories.staff import staff_actions
from utils.exceptions import http_500_exc_internal_server_error


class CRUDAppraisalInput(CRUDBase[AppraisalInput, AppraisalInputCreate, AppraisalInputUpdate]):
    def list_appraisal_input_for_staff(
            self, *, db: Session,
            skip: int = 0, limit: int = 100,
            appraisal_id: Optional[UUID] = None,
            staff_id: Optional[UUID] = None,
            appraisal_year: Optional[int] = None,
            cycle: Optional[str] = None,
            department_id: Optional[UUID] = None,
            is_global: Optional[bool] = None,
            is_active: Optional[bool] = None,
            date_from: datetime = None,
            date_to: datetime = None,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[AppraisalInput]:
        """
        Fetch form inputs (appraisal_inputs) filtered by staff ID, year, cycle, department, and designation.
        Designation takes precedence over department.
        """
        # Start with the base query for form_inputs
        query = self.query.outerjoin(Appraisal)
        try:
            # Filter by appraisal year and cycle
            if appraisal_year: query = query.filter(Appraisal.year == appraisal_year)
            if cycle: query = query.filter(Appraisal.cycle == cycle)

            # Staff-specific filters
            if staff_id:
                staff = staff_actions.get_by_id(db=db, id=staff_id)

                # Create filters for both designation and department
                query = query.filter(or_(
                    AppraisalInput.department_ids.contains([staff.department_id])
                ))

            elif department_id:
                query = query.filter(AppraisalInput.department_ids.contains([department_id]))

            if is_global is not None:
                query = query.filter(AppraisalInput.is_global == is_global)
            if is_active is not None:
                query = query.filter(AppraisalInput.is_active == is_active)

            if appraisal_id:
                query = query.filter(AppraisalInput.appraisal_id == appraisal_id)

            if date_to: query = query.filter(AppraisalInput.created_date <= date_to)
            if date_from: query = query.filter(AppraisalInput.created_date >= date_from)

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
                query = query.order_by(desc(AppraisalInput.created_date)).offset(skip).limit(limit)

            result = db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise http_500_exc_internal_server_error()


appraisal_input_actions = CRUDAppraisalInput(
    AppraisalInput,
    select_related=(
        AppraisalInput.appraisal_section,
        AppraisalInput.department_group,
    )
)
