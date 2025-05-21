from typing import Optional, Any, Dict

from pydantic import BaseModel
from pydantic import UUID4

from db.schemas import BaseSchema
from domains.appraisal.schemas.appraisal import AppraisalSchema
from domains.appraisal.schemas.appraisal_input import AppraisalInputSchema
from domains.organization.schemas.staff import StaffSchema


# AppraisalSubmission
class AppraisalSubmissionBase(BaseModel):
    appraisal_input_id: Optional[UUID4] = None
    appraisal_id: Optional[UUID4] = None
    staff_id: Optional[UUID4] = None
    data: Dict[str, Any]
    submitted: Optional[bool] = False
    completed: Optional[bool] = False


# Properties to receive via API on creation
class AppraisalSubmissionCreate(AppraisalSubmissionBase):
    appraisal_input_id: UUID4
    appraisal_id: UUID4
    staff_id: UUID4


# Properties to receive via API on update
class AppraisalSubmissionUpdate(AppraisalSubmissionBase):
    pass


class AppraisalSubmissionInDBBase(AppraisalSubmissionBase, BaseSchema):
    pass


# Additional properties to return via API
class AppraisalSubmissionSchema(AppraisalSubmissionInDBBase):
    appraisal_input: Optional[AppraisalInputSchema] = None
    appraisal: Optional[AppraisalSchema] = None
    staff: Optional[StaffSchema] = None
