from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class PermissionResponse(BaseModel):
    id: int
    name: str
    codename: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    permissions: List[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    role_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    permissions: List[str] = [] # list of codenames


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    permissions: Optional[List[str]] = None # list of codenames


class StaffCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    reporting_to_id: Optional[int] = None


class StaffAssignRole(BaseModel):
    user_code: str
    roles: List[str] # List of role names


class StaffResponse(BaseModel):
    id: int
    profile_code: str
    full_name: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    reporting_to_id: Optional[int] = None
    is_active: bool
    email: str
    user_code: str

    model_config = ConfigDict(from_attributes=True)
