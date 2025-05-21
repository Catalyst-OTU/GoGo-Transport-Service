from typing import Optional, List

from pydantic import BaseModel, UUID4

from db.schemas import BaseSchema
from domains.appraisal.schemas.appraisal_input import AppraisalInputInDBBase, AppraisalInputCreate, AppraisalInputUpdate
from utils.enum import BaseEnum


class NameChoices(BaseEnum):
    ANNUAL_APPRAISAL = "ANNUAL_APPRAISAL"
    FACULTY_QUARTER_APPRAISAL = "FACULTY_QUARTER_APPRAISAL"
    DIRECTORS_APPRAISAL = "DIRECTORS_APPRAISAL"


# AppraisalCycle
class AppraisalCycleBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    year: Optional[str] = None


# Properties to receive via API on creation
class AppraisalCycleCreate(AppraisalCycleBase):
    name: str
    description: Optional[str] = None
    # year: Optional[str] = None


# Properties to receive via API on update
class RelatedSectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    inputs: Optional[List[AppraisalInputUpdate]] = None


class RelatedSectionSchema(BaseModel):
    id: Optional[UUID4] = None
    name: Optional[str] = None
    description: Optional[str] = None
    inputs: Optional[List[AppraisalInputInDBBase]] = None


class AppraisalCycleUpdate(AppraisalCycleBase):
    name: Optional[str] = None
    appraisal_sections: Optional[List[RelatedSectionUpdate]] = None


class AppraisalCycleInDBBase(AppraisalCycleBase, BaseSchema):
    pass


# Additional properties to return via API
class AppraisalCycleSchema(AppraisalCycleInDBBase):
    pass


# Additional properties to return via API
class AppraisalCycleWithSections(AppraisalCycleInDBBase):
    appraisal_sections: Optional[List[RelatedSectionSchema]] = None
