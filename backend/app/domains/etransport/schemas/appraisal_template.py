from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from db.schemas import TimestampBase, BaseSchema


# AppraisalTemplate
class AppraisalTemplateBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    org_type: Optional[str] = None


# Properties to receive via API on creation
class AppraisalTemplateCreate(AppraisalTemplateBase):
    name: str


# Properties to receive via API on update
class AppraisalTemplateUpdate(AppraisalTemplateBase):
    pass


class AppraisalTemplateInDBBase(AppraisalTemplateBase, BaseSchema):
    pass


# Additional properties to return via API
class AppraisalTemplateSchema(AppraisalTemplateInDBBase):
    pass
