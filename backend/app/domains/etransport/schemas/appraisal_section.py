from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from db.schemas import BaseSchema


# AppraisalSection
class AppraisalSectionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    appraisal_cycle_id: Optional[UUID4] = None


# Properties to receive via API on creation
class AppraisalSectionCreate(AppraisalSectionBase):
    name: str
    description: Optional[str] = None
    appraisal_cycle_id: UUID4


# Properties to receive via API on update
class AppraisalSectionUpdate(AppraisalSectionBase):
    pass


class AppraisalSectionInDBBase(AppraisalSectionBase, BaseSchema):
    pass


# Additional properties to return via API
class AppraisalSectionSchema(AppraisalSectionInDBBase):
    pass
