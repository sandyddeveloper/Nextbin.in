from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import encrypt_credential
from app.api.deps import (
    get_current_user,
    HasActivePermission,
    InstagramPerms
)
from app.models.user import User
from app.modules.instagram.models import InstagramAccount, InstagramRule, InstagramChatLog
from app.schemas.instagram import (
    InstagramAccountCreate,
    InstagramAccountResponse,
    InstagramRuleCreate,
    InstagramRuleResponse,
    InstagramChatLogResponse
)
from app.modules.instagram.tasks import send_instagram_message_task
from app.services.audit import log_audit_action

router = APIRouter()

# Accounts CRUD
@router.post("/accounts", response_model=InstagramAccountResponse, dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_ACCOUNTS))])
async def link_instagram_account(
    acc_in: InstagramAccountCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Link a new Instagram account. The password is encrypted securely using AES before DB save.
    """
    # Verify username uniqueness
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.username == acc_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Instagram account already linked")

    encrypted_pw = encrypt_credential(acc_in.password)
    account = InstagramAccount(
        username=acc_in.username,
        encrypted_password=encrypted_pw,
        is_active=acc_in.is_active,
        status="DISCONNECTED"
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    # Audit log
    await log_audit_action(
        db,
        action="IG_ACCOUNT_LINKED",
        request=request,
        user_id=current_user.id,
        details={"instagram_username": account.username, "account_id": account.id}
    )
    
    return account

@router.get("/accounts", response_model=List[InstagramAccountResponse], dependencies=[Depends(HasActivePermission(InstagramPerms.VIEW_ACCOUNTS))])
async def list_instagram_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(InstagramAccount))
    return result.scalars().all()

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_ACCOUNTS))])
async def delete_instagram_account(
    account_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Instagram account not found")
        
    await db.delete(account)
    await db.commit()
    
    # Audit log
    await log_audit_action(
        db,
        action="IG_ACCOUNT_UNLINKED",
        request=request,
        user_id=current_user.id,
        details={"instagram_username": account.username, "account_id": account_id}
    )
    
    return None

# Rules CRUD
@router.post("/accounts/{account_id}/rules", response_model=InstagramRuleResponse, dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_RULES))])
async def create_auto_reply_rule(
    account_id: int,
    rule_in: InstagramRuleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Define a new auto-reply logic node triggered by incoming messages containing keyword matches.
    """
    # Verify account exists
    acc_check = await db.execute(select(InstagramAccount).where(InstagramAccount.id == account_id))
    if not acc_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Instagram account not found")

    new_rule = InstagramRule(
        account_id=account_id,
        trigger_keyword=rule_in.trigger_keyword,
        response_text=rule_in.response_text,
        is_active=rule_in.is_active
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    # Audit log
    await log_audit_action(
        db,
        action="IG_RULE_CREATED",
        request=request,
        user_id=current_user.id,
        details={"account_id": account_id, "trigger_keyword": rule_in.trigger_keyword}
    )
    
    return new_rule

@router.get("/accounts/{account_id}/rules", response_model=List[InstagramRuleResponse], dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_RULES))])
async def list_auto_reply_rules(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(InstagramRule).where(InstagramRule.account_id == account_id))
    return result.scalars().all()

# Chat Log Audit Router
@router.get("/accounts/{account_id}/logs", response_model=List[InstagramChatLogResponse], dependencies=[Depends(HasActivePermission(InstagramPerms.VIEW_CHAT_LOGS))])
async def list_instagram_chat_logs(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InstagramChatLog)
        .where(InstagramChatLog.account_id == account_id)
        .order_by(InstagramChatLog.timestamp.desc())
    )
    return result.scalars().all()

# Message Dispatcher Endpoint
@router.post("/accounts/{account_id}/send-dm", response_model=dict, dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_ACCOUNTS))])
async def dispatch_direct_message(
    account_id: int,
    thread_id: str,
    text: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dispatches an Instagram Direct Message to a background task runner.
    Ensures immediate response returning task status.
    """
    send_instagram_message_task(account_id, thread_id, text)
    
    # Audit log
    await log_audit_action(
        db,
        action="IG_DM_DISPATCHED",
        request=request,
        user_id=current_user.id,
        details={"account_id": account_id, "thread_id": thread_id}
    )
    
    return {"message": f"Direct Message task submitted to background queue for execution."}

@router.post("/accounts/{account_id}/connect", response_model=dict, dependencies=[Depends(HasActivePermission(InstagramPerms.MANAGE_ACCOUNTS))])
async def trigger_account_connection(
    account_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger NILA background worker to log in and connect to the Instagram account immediately.
    """
    result = await db.execute(select(InstagramAccount).where(InstagramAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Instagram account not found")

    from app.modules.instagram.tasks import connect_instagram_account_task
    connect_instagram_account_task(account_id)
    
    # Audit log
    await log_audit_action(
        db,
        action="IG_CONNECTION_DISPATCHED",
        request=request,
        user_id=current_user.id,
        details={"account_id": account_id, "username": account.username}
    )
    
    return {"message": f"Background connection task submitted to worker for Instagram Account ID: {account_id}."}
