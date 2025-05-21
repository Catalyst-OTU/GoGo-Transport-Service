from typing import Optional

from pydantic import BaseModel
from pydantic import UUID4

from db.schemas import BaseSchema


# DepartmentGroup
class DepartmentGroupBase(BaseModel):
    department_id: Optional[UUID4] = None
    name: Optional[str] = None


# Properties to receive via API on creation
class DepartmentGroupCreate(DepartmentGroupBase):
    name: str


# Properties to receive via API on update
class DepartmentGroupUpdate(DepartmentGroupBase):
    pass


class DepartmentGroupInDBBase(DepartmentGroupBase, BaseSchema):
    pass


# Additional properties to return via API
class DepartmentGroupSchema(DepartmentGroupInDBBase):
    pass
