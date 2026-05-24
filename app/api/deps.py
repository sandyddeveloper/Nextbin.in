from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.database import get_db
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    """
    Dependency  validate JWT authorization and retrieve the authenticated User context.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token payload
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
        
    # Fetch user from SQLite
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


from app.models.rbac import Permission, Role

async def get_user_permissions(db: AsyncSession, user: User) -> set[str]:
    """
    Resolves the set of permission codenames assigned to the user,
    handling the hierarchical role structure recursively.
    """
    if user.is_superuser:
        # Superuser has all permissions implicitly
        result = await db.execute(select(Permission.codename))
        return set(result.scalars().all())

    user_role_names = user.role_names
    if not user_role_names:
        return set()

    # Load all roles with their permissions to resolve hierarchy in memory
    result = await db.execute(select(Role))
    all_roles = result.scalars().all()

    # Create mapping: role_name -> role object
    role_map = {role.name.upper(): role for role in all_roles}

    # Build parent -> children map
    children_map = {}
    for role in all_roles:
        if role.parent_id:
            parent_role = next((r for r in all_roles if r.id == role.parent_id), None)
            if parent_role:
                children_map.setdefault(parent_role.name.upper(), []).append(role.name.upper())

    # Resolve all roles the user possesses including descendants (inherited roles)
    assigned_roles = [r.upper() for r in user_role_names]
    visited_roles = set()
    queue = list(assigned_roles)

    while queue:
        role_name = queue.pop(0)
        if role_name not in visited_roles:
            visited_roles.add(role_name)
            # Add child roles to queue (since parent inherits permissions of children)
            if role_name in children_map:
                queue.extend(children_map[role_name])

    # Collect all permission codenames from visited roles
    permissions = set()
    for role_name in visited_roles:
        role_obj = role_map.get(role_name)
        if role_obj:
            for perm in role_obj.permissions:
                permissions.add(perm.codename)

    return permissions


def require_permission(permission_name: str):
    """
    FastAPI dependency to enforce that the logged-in user has a specific permission.
    """
    async def dependency(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        user_perms = await get_user_permissions(db, user)
        if permission_name not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform this action. Required: '{permission_name}'"
            )
        return user
    return dependency


# Re-export new permissions module elements
from app.core.permission import (
    HasActivePermission,
    SystemPerms,
    InstagramPerms,
    ProjectPerms,
    MonitoringPerms,
    NilagravityPerms
)
