from collections import deque
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.api.deps import (
    get_current_user,
    HasActivePermission,
    SystemPerms,
    InstagramPerms,
    ProjectPerms,
    MonitoringPerms,
    NilagravityPerms
)
from app.models.user import User
from app.models.rbac import Permission, Role, user_roles
from app.models.staff import StaffMaster
from app.core.permission import CoreSystemRoles, ALL_PERMISSIONS
from app.schemas.rbac import (
    PermissionResponse,
    RoleResponse,
    RoleCreate,
    RoleUpdate,
    StaffCreate,
    StaffAssignRole,
    StaffResponse
)
from app.core.response import APIResponse
from app.core.security import get_password_hash

router = APIRouter()

LOG_DIR = Path(__file__).resolve().parents[3] / "logs"

def tail_log_file(file_path: Path, lines: int = 200) -> list[str]:
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file not found: {file_path.name}"
        )

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        return [line.rstrip("\n") for line in deque(f, maxlen=lines)]

@router.get(
    "/permissions",
    response_model=List[PermissionResponse],
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_ROLES))]
)
async def list_permissions(db: AsyncSession = Depends(get_db)):
    """
    List all valid system permissions.
    """
    valid_codenames = list(ALL_PERMISSIONS.keys())
    result = await db.execute(select(Permission).where(Permission.codename.in_(valid_codenames)))
    permissions = result.scalars().all()
    return APIResponse(
        message="Permissions fetched successfully",
        data=[PermissionResponse.model_validate(p).model_dump() for p in permissions]
    )


@router.get(
    "/roles",
    response_model=List[RoleResponse],
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_ROLES))]
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    """
    List all registered user roles.
    """
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return APIResponse(
        message="Roles fetched successfully",
        data=[RoleResponse.model_validate(r).model_dump() for r in roles]
    )


@router.post(
    "/roles/create",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_ROLES))]
)
async def create_role(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new role and assign permissions to it.
    """
    # Check if role name already exists
    result_existing = await db.execute(select(Role).where(Role.name == role_in.role_name.upper()))
    if result_existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.role_name}' already exists."
        )

    # Get parent role if provided
    parent_id = role_in.parent_id
    if parent_id:
        result_parent = await db.execute(select(Role).where(Role.id == parent_id))
        if not result_parent.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent role ID {parent_id} does not exist."
            )

    # Fetch permissions
    permissions = []
    if role_in.permissions:
        result_perms = await db.execute(select(Permission).where(Permission.codename.in_(role_in.permissions)))
        permissions = result_perms.scalars().all()

    new_role = Role(
        name=role_in.role_name.upper(),
        description=role_in.description,
        parent_id=parent_id,
        permissions=permissions
    )
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)

    return APIResponse(
        message=f"Role '{new_role.name}' created successfully.",
        data=RoleResponse.model_validate(new_role).model_dump(),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_ROLES))]
)
async def update_role(role_id: int, role_in: RoleUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a role's name, description, parent, and replace its permissions.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    # Core system roles cannot be modified in critical ways (like renaming)
    if role.name in CoreSystemRoles.values and role_in.role_name and role_in.role_name.upper() != role.name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Core system roles cannot be renamed."
        )

    if role_in.role_name:
        role.name = role_in.role_name.upper()

    if role_in.description is not None:
        role.description = role_in.description

    if role_in.parent_id is not None:
        if role_in.parent_id == role.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A role cannot report to itself."
            )
        # Check if parent exists
        result_parent = await db.execute(select(Role).where(Role.id == role_in.parent_id))
        if not result_parent.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent role ID {role_in.parent_id} does not exist."
            )
        role.parent_id = role_in.parent_id

    if role_in.permissions is not None:
        result_perms = await db.execute(select(Permission).where(Permission.codename.in_(role_in.permissions)))
        role.permissions = result_perms.scalars().all()

    await db.commit()
    await db.refresh(role)

    return APIResponse(
        message=f"Role '{role.name}' updated successfully.",
        data=RoleResponse.model_validate(role).model_dump()
    )


@router.delete(
    "/roles/{role_id}",
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_ROLES))]
)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    """
    Permanently deletes a role. Core system roles cannot be deleted.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")

    if role.name in CoreSystemRoles.values:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete core system roles."
        )

    # Check if any user is currently assigned to this role
    # Query association table user_roles to check assignment
    # Check if there are entries in the user_roles table for this role_id
    result_assignment = await db.execute(
        select(user_roles).where(user_roles.c.role_id == role_id)
    )
    if result_assignment.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete this role because it is currently assigned to one or more active staff members."
        )

    await db.delete(role)
    await db.commit()

    return APIResponse(message="Role deleted successfully.", data={})


@router.get(
    "/logs/api",
    dependencies=[Depends(HasActivePermission(SystemPerms.VIEW_API_LOGS))]
)
async def read_api_log(lines: int = 200):
    """
    Retrieve the latest API log entries.
    """
    api_log = LOG_DIR / "api.log"
    return APIResponse(
        message="API log entries fetched successfully.",
        data={
            "file": api_log.name,
            "lines": tail_log_file(api_log, lines)
        }
    )


@router.get(
    "/logs/error",
    dependencies=[Depends(HasActivePermission(SystemPerms.VIEW_ERROR_LOGS))]
)
async def read_error_log(lines: int = 200):
    """
    Retrieve the latest error entries from the API log.
    """
    api_log = LOG_DIR / "api.log"
    error_lines = [
        line for line in tail_log_file(api_log, max(lines * 5, 500))
        if "ERROR" in line or "Error" in line or "error" in line
    ]
    return APIResponse(
        message="Error log entries fetched successfully.",
        data={
            "file": api_log.name,
            "lines": error_lines[-lines:]
        }
    )


@router.get(
    "/logs/all",
    dependencies=[Depends(HasActivePermission(SystemPerms.VIEW_ALL_LOGS))]
)
async def read_all_logs(lines: int = 200):
    """
    Retrieve the latest entries from all configured log files.
    """
    if not LOG_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logs directory not found."
        )

    files = sorted(LOG_DIR.glob("*.log"))
    data = {}
    for file_path in files:
        data[file_path.name] = tail_log_file(file_path, lines)

    return APIResponse(
        message="All log files fetched successfully.",
        data={
            "files": [file.name for file in files],
            "logs": data
        }
    )


@router.post(
    "/users/create",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_USERS))]
)
async def create_staff(staff_in: StaffCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new base staff user. Created in an inactive state initially.
    """
    # Check if user already exists
    result_existing = await db.execute(select(User).where(User.email == staff_in.email))
    if result_existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    hashed_password = get_password_hash(staff_in.password)
    new_user = User(
        email=staff_in.email,
        hashed_password=hashed_password,
        full_name=staff_in.full_name,
        is_active=False,  # Inactive until role is assigned
        is_superuser=False
    )
    db.add(new_user)
    await db.flush()

    # Create StaffMaster profile
    new_staff = StaffMaster(
        user_id=new_user.id,
        full_name=staff_in.full_name or staff_in.username,
        designation=staff_in.designation,
        department=staff_in.department,
        reporting_to_id=staff_in.reporting_to_id,
        is_active=False
    )
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)

    return APIResponse(
        message="Staff user created successfully in inactive state.",
        data={
            "id": new_staff.id,
            "profile_code": new_staff.profile_code,
            "full_name": new_staff.full_name,
            "designation": new_staff.designation,
            "department": new_staff.department,
            "reporting_to_id": new_staff.reporting_to_id,
            "is_active": new_staff.is_active,
            "email": new_user.email,
            "user_code": new_user.user_code
        },
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/users/assign-role",
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_USERS))]
)
async def assign_staff_role(role_in: StaffAssignRole, db: AsyncSession = Depends(get_db)):
    """
    Overwrites the staff roles for a user. Automatically activates the user/staff master if roles are assigned.
    """
    try:
        user_id = int(role_in.user_code.split("-")[1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_code format.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Get roles from database
    result_roles = await db.execute(select(Role).where(Role.name.in_(role_in.roles)))
    roles_list = result_roles.scalars().all()

    # Assign roles
    user.roles = roles_list

    display_name = user.full_name or user.email

    if role_in.roles:
        user.is_active = True
        
        # Activate StaffMaster
        if user.staff_master:
            user.staff_master.is_active = True
            
            # Determine designation
            designation = None
            if "SUPER_ADMIN" in role_in.roles:
                designation = "SUPER_ADMIN"
            elif "ADMIN" in role_in.roles:
                designation = "ADMIN"
            else:
                designation = sorted(role_in.roles)[0]
            user.staff_master.designation = designation
        else:
            # Create StaffMaster if missing
            new_staff = StaffMaster(
                user_id=user.id,
                full_name=display_name,
                is_active=True,
                designation=sorted(role_in.roles)[0]
            )
            db.add(new_staff)
    else:
        # If all roles removed, deactivate StaffMaster
        if user.staff_master:
            user.staff_master.is_active = False

    await db.commit()

    return APIResponse(
        message=f"Staff roles successfully updated for {display_name}.",
        data={
            "user_code": user.user_code,
            "current_staff_roles": role_in.roles,
            "is_active": user.is_active
        }
    )


@router.get(
    "/staff/list",
    response_model=List[StaffResponse],
    dependencies=[Depends(HasActivePermission(SystemPerms.MANAGE_USERS))]
)
async def list_staff(db: AsyncSession = Depends(get_db)):
    """
    List all active staff profiles.
    """
    result = await db.execute(
        select(StaffMaster).where(StaffMaster.is_deleted == False)
    )
    staff_members = result.scalars().all()
    
    response_data = []
    for s in staff_members:
        response_data.append({
            "id": s.id,
            "profile_code": s.profile_code,
            "full_name": s.full_name,
            "designation": s.designation,
            "department": s.department,
            "reporting_to_id": s.reporting_to_id,
            "is_active": s.is_active,
            "email": s.user.email if s.user else "",
            "user_code": s.user.user_code if s.user else ""
        })

    return APIResponse(
        message="Staff list fetched successfully",
        data=response_data
    )
