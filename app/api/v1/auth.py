from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.database import get_db
from app.api.deps import get_current_user, HasActivePermission, SystemPerms
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.auth import Token, UserLogin
from app.services.audit import log_audit_action

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(
    user_in: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new administrator/user account on the server.
    """
    # Check if email is already taken
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        # Log audit trail for registration attempt
        await log_audit_action(
            db,
            action="USER_REGISTER_FAILED",
            request=request,
            details={"email": user_in.email, "reason": "Email already registered"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
        
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Check if this is the first user (make them superuser)
    count_result = await db.execute(select(User))
    users_list = count_result.scalars().all()
    
    from app.models.rbac import Role
    from app.core.permission import CoreSystemRoles
    
    if len(users_list) == 0:
        new_user.is_superuser = True
        # Get SUPER_ADMIN role
        result_role = await db.execute(select(Role).where(Role.name == CoreSystemRoles.SUPER_ADMIN))
        super_admin_role = result_role.scalar_one_or_none()
        if super_admin_role:
            new_user.roles.append(super_admin_role)
    else:
        # Get USER role
        result_role = await db.execute(select(Role).where(Role.name == CoreSystemRoles.USER))
        user_role = result_role.scalar_one_or_none()
        if user_role:
            new_user.roles.append(user_role)
            
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log audit trail for successful registration
    await log_audit_action(
        db,
        action="USER_REGISTER_SUCCESS",
        request=request,
        user_id=new_user.id,
        details={"email": new_user.email, "is_superuser": new_user.is_superuser}
    )
    
    # Generate session access token
    access_token = create_access_token(new_user.id)
    active_role = CoreSystemRoles.SUPER_ADMIN if new_user.is_superuser else CoreSystemRoles.USER
    
    from app.core.response import APIResponse
    return APIResponse(
        message="Registration successful.",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_code": new_user.user_code,
            "active_role": active_role
        },
        status_code=status.HTTP_201_CREATED
    )

@router.post("/login", response_model=Token)
async def login_access_token(
    login_in: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Password login, retrieve a JWT session token.
    """
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_in.password, user.hashed_password):
        # Log failed login attempt
        await log_audit_action(
            db,
            action="USER_LOGIN_FAILED",
            request=request,
            details={"email": login_in.email, "reason": "Incorrect credentials"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        # Log failed login due to inactive account
        await log_audit_action(
            db,
            action="USER_LOGIN_FAILED",
            request=request,
            user_id=user.id,
            details={"email": login_in.email, "reason": "Inactive account"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # Log successful login
    await log_audit_action(
        db,
        action="USER_LOGIN_SUCCESS",
        request=request,
        user_id=user.id,
        details={"email": user.email}
    )
    
    # Resolve active role
    active_role = "USER"
    if user.is_superuser:
        active_role = "SUPER_ADMIN"
    elif user.role_names:
        roles = [r.upper() for r in user.role_names]
        if "SUPER_ADMIN" in roles:
            active_role = "SUPER_ADMIN"
        elif "ADMIN" in roles:
            active_role = "ADMIN"
        elif "STAFF" in roles:
            active_role = "STAFF"
        else:
            active_role = roles[0]
            
    access_token = create_access_token(user.id)
    
    from app.core.response import APIResponse
    return APIResponse(
        message="Login successful.",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_code": user.user_code,
            "active_role": active_role
        }
    )

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Get details of the currently authenticated administrator session.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the currently authenticated user's profile details.
    """
    updates = {}
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
        updates["full_name"] = user_in.full_name
        if current_user.staff_master:
            current_user.staff_master.full_name = user_in.full_name
            
    if user_in.email is not None:
        if user_in.email != current_user.email:
            result = await db.execute(select(User).where(User.email == user_in.email))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered by another user."
                )
            current_user.email = user_in.email
            updates["email"] = user_in.email
            
    if user_in.password is not None and user_in.password.strip() != "":
        current_user.hashed_password = get_password_hash(user_in.password)
        updates["password_changed"] = True
        
    if updates:
        await db.commit()
        await db.refresh(current_user)
        
        await log_audit_action(
            db,
            action="USER_PROFILE_UPDATED",
            request=request,
            user_id=current_user.id,
            details=updates
        )
        
    return current_user

from app.models.audit import AuditLog

@router.get(
    "/audit-logs",
    response_model=list[dict],
    dependencies=[Depends(HasActivePermission(SystemPerms.VIEW_AUDIT_LOGS))]
)
async def read_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve security audit logs.
    """
    result = await db.execute(
        select(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "request_id": log.request_id,
            "platform": log.platform,
            "ip_address": log.ip_address,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]
