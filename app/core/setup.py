from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.rbac import Permission, Role
from app.core.permission import CoreSystemRoles, ALL_PERMISSIONS
import logging

logger = logging.getLogger("nextbin.api.setup")

async def setup_roles_and_permissions(db: AsyncSession):
    """
    Safely syncs all constants (Roles and Permissions) into the database.
    Equivalent to Django's setup_roles command.
    """
    logger.info("Starting setup and sync for Roles and Permissions...")

    # 1. Sync Permissions
    perms_count = 0
    for codename, label in ALL_PERMISSIONS.items():
        # Check if permission already exists
        result = await db.execute(select(Permission).where(Permission.codename == codename))
        existing_perm = result.scalar_one_or_none()
        
        if not existing_perm:
            new_perm = Permission(codename=codename, name=label, description=label)
            db.add(new_perm)
            perms_count += 1
            logger.info(f"  + Added Permission: {codename}")
            
    await db.commit()

    # 2. Sync Roles
    roles_count = 0
    for role_name in CoreSystemRoles.values:
        result = await db.execute(select(Role).where(Role.name == role_name))
        existing_role = result.scalar_one_or_none()
        
        if not existing_role:
            new_role = Role(name=role_name, description=f"{role_name.title()} Role")
            db.add(new_role)
            roles_count += 1
            logger.info(f"  + Added Role: {role_name}")
            
    await db.commit()

    # 3. Assign all permissions to SUPER_ADMIN
    result_super = await db.execute(select(Role).where(Role.name == CoreSystemRoles.SUPER_ADMIN))
    super_admin_role = result_super.scalar_one_or_none()

    if super_admin_role:
        result_perms = await db.execute(select(Permission))
        all_perms = result_perms.scalars().all()
        super_admin_role.permissions = all_perms
        await db.commit()
        logger.info(f"  + Assigned all permissions to: {CoreSystemRoles.SUPER_ADMIN}")

    logger.info(f"Sync complete! Added {perms_count} permissions and {roles_count} roles.")
