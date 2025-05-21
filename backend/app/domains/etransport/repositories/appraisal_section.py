from typing import (
    Optional, Literal, List
)

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST

from config.logger import log
from crud.base import CRUDBase
from domains.appraisal.models import AppraisalSection
from domains.appraisal.schemas.appraisal_section import AppraisalSectionCreate, AppraisalSectionUpdate
from utils.exceptions import http_500_exc_internal_server_error


class CRUDAppraisalSection(CRUDBase[AppraisalSection, AppraisalSectionCreate, AppraisalSectionUpdate]):
    def get_all(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            cycle_id: UUID4 = None,
    ) -> List[AppraisalSection]:
        query = self.query
        try:
            if cycle_id: query = query.filter(AppraisalSection.appraisal_cycle_id == cycle_id)
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = query.order_by(desc(self.model.created_date))

            query = query.offset(skip).limit(limit)
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


appraisal_section_actions = CRUDAppraisalSection(AppraisalSection)
