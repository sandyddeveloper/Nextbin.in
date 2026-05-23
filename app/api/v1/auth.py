from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.services.audit import log_audit_action

router = APIRouter()

@router.post("/register", response_model=UserResponse)
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
        is_active=user_in.is_active,
        is_superuser=False
    )
    
    # Check if this is the first user (make them superuser)
    count_result = await db.execute(select(User))
    if len(count_result.scalars().all()) == 0:
        new_user.is_superuser = True
        
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
    
    return new_user

@router.post("/login", response_model=Token)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, retrieve a JWT Bearer token.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        await log_audit_action(
            db,
            action="USER_LOGIN_FAILED",
            request=request,
            details={"email": form_data.username, "reason": "Incorrect credentials"}
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
            details={"email": form_data.username, "reason": "Inactive account"}
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
    
    return Token(
        access_token=create_access_token(user.id),
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Get details of the currently authenticated administrator session.
    """
    return current_user

from app.models.audit import AuditLog

@router.get("/audit-logs", response_model=list[dict])
async def read_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve security audit logs for superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access security audit logs."
        )
        
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
