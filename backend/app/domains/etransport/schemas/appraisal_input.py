from typing import Optional, List

from pydantic import BaseModel
from pydantic import UUID4

from db.schemas import BaseSchema
from domains.appraisal.schemas.appraisal_section import AppraisalSectionSchema
from domains.appraisal.schemas.department_group import DepartmentGroupSchema
from domains.organization.schemas.department import DepartmentSchema
from utils.schemas import FormField


class AppraisalFormInputFields(BaseModel):
    group_name: str
    group_description: Optional[str] = None
    fields: Optional[List[FormField]]


# AppraisalInput
class AppraisalInputBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    appraisal_section_id: Optional[UUID4]
    department_group_id: Optional[UUID4] = None
    form_fields: List[AppraisalFormInputFields]
    department_ids: Optional[List[UUID4]] = None
    is_global: Optional[bool] = None
    is_active: Optional[bool] = None


# Properties to receive via API on creation
class AppraisalInputCreate(AppraisalInputBase):
    appraisal_section_id: UUID4


# Properties to receive via API on update
class AppraisalInputUpdate(AppraisalInputBase):
    pass


class AppraisalInputInDBBase(AppraisalInputBase, BaseSchema):
    pass


# Additional properties to return via API
class AppraisalInputSchema(AppraisalInputInDBBase):
    appraisal_section: Optional[AppraisalSectionSchema] = None
    department_group: Optional[DepartmentGroupSchema] = None
    departments: Optional[List[DepartmentSchema]] = None
