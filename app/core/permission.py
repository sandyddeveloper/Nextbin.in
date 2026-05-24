import sys
import inspect
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, get_user_permissions
from app.models.user import User

class CoreSystemRoles:
    SUPER_ADMIN = 'SUPER_ADMIN'
    ADMIN = 'ADMIN'
    STAFF = 'STAFF'
    USER = 'USER'

    values = ['SUPER_ADMIN', 'ADMIN', 'STAFF', 'USER']

class SystemPerms:
    MANAGE_USERS = "manage_users"
    MANAGE_STAFF = "manage_staff"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"

class InstagramPerms:
    MANAGE_ACCOUNTS = "manage_instagram_accounts"
    VIEW_ACCOUNTS = "view_instagram_accounts"
    VIEW_CHAT_LOGS = "view_instagram_chat_logs"
    MANAGE_RULES = "manage_instagram_rules"

class ProjectPerms:
    MANAGE_PROJECTS = "manage_projects"
    VIEW_PROJECTS = "view_projects"

class MonitoringPerms:
    VIEW_METRICS = "view_performance_metrics"

class NilagravityPerms:
    MANAGE_VAULT = "manage_vault"
    VIEW_WISHES = "view_wishes"
    SEND_NOTIFICATIONS = "send_notifications"

# Map permission values to user-friendly descriptive labels
PERMISSION_DESCRIPTIONS = {
    SystemPerms.MANAGE_USERS: "Can create and manage general user accounts",
    SystemPerms.MANAGE_STAFF: "Can register and configure staff roles",
    SystemPerms.MANAGE_ROLES: "Can create and edit permission matrices for roles",
    SystemPerms.VIEW_AUDIT_LOGS: "Can view security audit logs",
    InstagramPerms.MANAGE_ACCOUNTS: "Can link and connect Instagram credentials",
    InstagramPerms.VIEW_ACCOUNTS: "Can view connected Instagram profiles",
    InstagramPerms.VIEW_CHAT_LOGS: "Can inspect automated response logs",
    InstagramPerms.MANAGE_RULES: "Can define keyword auto-replies for chats",
    ProjectPerms.MANAGE_PROJECTS: "Can create, modify, and delete monitored projects",
    ProjectPerms.VIEW_PROJECTS: "Can view details of monitored projects",
    MonitoringPerms.VIEW_METRICS: "Can access resource metrics and performance data",
    NilagravityPerms.MANAGE_VAULT: "Can lock, unlock, and manage access requests for the Sanctuary Vault",
    NilagravityPerms.VIEW_WISHES: "Can view dynamic wishes list from clients",
    NilagravityPerms.SEND_NOTIFICATIONS: "Can push push-notifications and emails"
}

# Collect all permission codes and descriptions dynamically
ALL_PERMISSIONS = {}

def _collect_permissions():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and name.endswith('Perms'):
            for key, val in obj.__dict__.items():
                if not key.startswith('_') and isinstance(val, str):
                    ALL_PERMISSIONS[val] = PERMISSION_DESCRIPTIONS.get(val, val.replace('_', ' ').title())

_collect_permissions()


class HasActivePermission:
    """
    FastAPI dependency check to enforce role-based access control.
    """
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    async def __call__(
        self,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        user_perms = await get_user_permissions(db, user)
        if self.permission_name not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform this action. Required: '{self.permission_name}'"
            )
        return user
