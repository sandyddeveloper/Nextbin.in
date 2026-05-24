import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core.response import APIResponse
from app.schemas.nilagravity import (
    EmailPermissionUpdate,
    EmailPushRequest,
    PushNotificationRequest,
    WishCreate
)
from app.services.nilagravity import (
    get_kv_val,
    set_kv_val,
    lpush_kv_val
)
from app.api.deps import (
    get_current_user,
    HasActivePermission,
    NilagravityPerms,
    get_user_permissions
)
from app.models.user import User
from fastapi.concurrency import run_in_threadpool
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx
import re

router = APIRouter()
logger = logging.getLogger("nextbin.api.nilagravity")

APP_CONFIG = {
    "version": "1.0.2",
    "buildNumber": 102,
    "releaseNotes": "Minor bug fixes and performance improvements.",
    "updateUrl": "https://play.google.com/store/apps/details?id=com.nila.dashboard",
    "criticalUpdate": False,
}

INITIAL_PERMISSIONS = {
    "email": {
        "marketing": True,
        "security": True,
        "updates": True,
    },
    "push": {
        "notifications": True,
        "reminders": True,
    },
}

def send_nila_email(to_email: str, subject: str, html_content: str, text_content: str = ""):
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        logger.warning("Gmail SMTP credentials missing. Simulating email sending.")
        return True, "Simulated successfully"
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Nila Admin <{settings.EMAIL_USER}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=5.0) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            server.sendmail(settings.EMAIL_USER, to_email, msg.as_string())
        return True, "Sent successfully"
    except Exception as e:
        logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
        return False, str(e)

async def trigger_onesignal_push(message: str, title: str = None, player_ids: list = None, data: dict = None, image_url: str = None, buttons: list = None):
    if not settings.ONESIGNAL_APP_ID or not settings.ONESIGNAL_API_KEY:
        logger.warning("OneSignal credentials not configured. Simulating push.")
        return True, {
            "simulated": True,
            "message": "Push notification simulated successfully (credentials missing).",
            "data": {
                "title": title or "Nila Dashboard",
                "message": message,
                "targetCount": len(player_ids) if player_ids else "All Subscribed Users",
                "payload": data
            }
        }
    try:
        push_payload = {
            "app_id": settings.ONESIGNAL_APP_ID,
            "contents": {"en": message}
        }
        if title:
            push_payload["headings"] = {"en": title}
        if data:
            push_payload["data"] = data
        if image_url:
            push_payload["big_picture"] = image_url
        if buttons:
            push_payload["buttons"] = buttons

        if player_ids and len(player_ids) > 0:
            is_uuid = bool(re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", player_ids[0], re.IGNORECASE))
            if is_uuid:
                push_payload["include_subscription_ids"] = player_ids
            else:
                push_payload["include_aliases"] = {"external_id": player_ids}
        else:
            push_payload["included_segments"] = ["Subscribed Users"]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://onesignal.com/api/v1/notifications",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
                },
                json=push_payload,
                timeout=10.0
            )
        
        if response.status_code >= 400:
            logger.error(f"OneSignal error response: {response.text}")
            return False, {"error": "OneSignal API rejected request", "detail": response.json()}
        
        return True, response.json()
    except Exception as e:
        logger.error(f"OneSignal HTTP error: {str(e)}")
        return False, {"error": str(e)}


@router.get("/app/update")
async def get_app_update():
    return APIResponse(data=APP_CONFIG)


@router.post("/auth/logout")
async def logout_user():
    response = APIResponse(
        message="Successfully logged out. Client-side session tokens should now be cleared.",
        data=None
    )
    response.delete_cookie("token", path="/")
    return response


@router.get("/email/permission")
async def get_email_permission(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    perms = await get_kv_val(db, "email_permissions", default=INITIAL_PERMISSIONS)
    return APIResponse(data=perms)


@router.post("/email/permission")
async def update_email_permission(
    body: EmailPermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current = await get_kv_val(db, "email_permissions", default=INITIAL_PERMISSIONS)
    updated = dict(current)
    if body.email is not None:
        updated["email"] = {**updated.get("email", {}), **body.email}
    if body.push is not None:
        updated["push"] = {**updated.get("push", {}), **body.push}
        
    await set_kv_val(db, "email_permissions", updated)
    return APIResponse(
        message="Permissions updated successfully",
        data=updated
    )


@router.post("/email/push", dependencies=[Depends(HasActivePermission(NilagravityPerms.SEND_NOTIFICATIONS))])
async def trigger_email_push(body: EmailPushRequest):
    button_html = ""
    if body.type == "approval":
        button_html = """
        <div style="margin-top: 30px; text-align: center;">
          <a href="#" style="background-color: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">Approve Action</a>
        </div>
        """
    
    html_template = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #05070a; color: #f8fafc; padding: 40px; border-radius: 20px; max-width: 600px; margin: auto; border: 1px solid #1e293b;">
      <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #6366f1; margin: 0; font-size: 28px;">Nila Dashboard</h1>
        <p style="color: #94a3b8; margin-top: 5px;">Secure Notification Service</p>
      </div>
      
      <div style="background: rgba(255, 255, 255, 0.03); padding: 30px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1);">
        <h2 style="margin-top: 0; color: #fff;">{body.subject}</h2>
        <p style="line-height: 1.6; color: #cbd5e1;">{body.body}</p>
        {button_html}
      </div>
      
      <div style="text-align: center; margin-top: 30px; font-size: 12px; color: #64748b;">
        <p>This is an automated notification from Nila Admin System.</p>
        <p>&copy; 2026 Nila Dashboard. All rights reserved.</p>
      </div>
    </div>
    """
    success, message_detail = await run_in_threadpool(
        send_nila_email,
        to_email=body.to,
        subject=body.subject,
        html_content=html_template,
        text_content=body.body
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {message_detail}"
        )
    return APIResponse(
        message=f"Email successfully sent to {body.to}"
    )


@router.post("/notifications/push", dependencies=[Depends(HasActivePermission(NilagravityPerms.SEND_NOTIFICATIONS))])
async def trigger_notifications_push(body: PushNotificationRequest):
    success, result = await trigger_onesignal_push(
        message=body.message,
        title=body.title,
        player_ids=body.playerIds,
        data=body.data,
        image_url=body.imageUrl,
        buttons=body.buttons
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to trigger push notification")
        )
    
    msg = "Push notification triggered successfully via OneSignal API."
    if result.get("simulated"):
        msg = result.get("message")
        
    return APIResponse(
        message=msg,
        data=result.get("data", result)
    )


@router.get("/vault/request", dependencies=[Depends(HasActivePermission(NilagravityPerms.MANAGE_VAULT))])
async def get_vault_request():
    return APIResponse(data={"status": "ready"})


@router.post("/vault/request", dependencies=[Depends(HasActivePermission(NilagravityPerms.MANAGE_VAULT))])
async def trigger_vault_request(request: Request, db: AsyncSession = Depends(get_db)):
    base_url = str(request.base_url).rstrip('/')
    approval_url = f"{base_url}{settings.API_V1_STR}/nilagravity/vault/approve?token=nila-eternal-2026"
    
    html_template = f"""
    <div style="font-family: serif; padding: 40px; background: #050000; color: #fff; border: 2px solid #7f1d1d; border-radius: 12px; max-width: 500px; margin: auto;">
      <h1 style="color: #ef4444; text-align: center; font-size: 24px; text-transform: uppercase; letter-spacing: 3px;">Sanctuary Access Request</h1>
      <p style="text-align: center; font-style: italic; color: #94a3b8; margin-bottom: 30px;">"Someone is knocking at the door of the Eternal Heart."</p>
      
      <div style="margin: 40px 0; text-align: center;">
        <a href="{approval_url}" style="background: #ef4444; color: #fff; padding: 18px 40px; text-decoration: none; border-radius: 4px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; border: 1px solid #ff0000; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);">
          Approve Access
        </a>
      </div>
      
      <p style="font-size: 11px; color: #444; text-align: center; margin-top: 40px;">If this wasn't you, ignore this message. The vault remains sealed.</p>
    </div>
    """
    
    target_email = settings.EMAIL_USER
    success, message_detail = await run_in_threadpool(
        send_nila_email,
        to_email=target_email,
        subject="🚨 [IvaruNila] Sanctuary Vault Access Requested",
        html_content=html_template,
        text_content=f"Vault access request. Approve at: {approval_url}"
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send request: {message_detail}"
        )
    return APIResponse(
        message="Request sent"
    )


@router.get("/vault/approve")
async def approve_vault_via_get(
    token: str = None, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if token == "nila-eternal-2026":
        await set_kv_val(db, "vault_unlocked", True)
        
        await trigger_onesignal_push(
            message="The cosmic alignment is complete. Tap to enter the sacred sanctuary.",
            title="Sanctuary Vault Unlocked! 🌌",
            data={
                "action": "unlock_vault",
                "screen": "SanctuaryActivity"
            }
        )
        return RedirectResponse(url=f"{settings.NEXT_PUBLIC_API_URL}/?vault=unlocked")
        
    # If not a link-based request, require NilagravityPerms.MANAGE_VAULT
    user_perms = await get_user_permissions(db, current_user)
    if NilagravityPerms.MANAGE_VAULT not in user_perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to perform this action. Required: '{NilagravityPerms.MANAGE_VAULT}'"
        )
        
    unlocked = await get_kv_val(db, "vault_unlocked", default=False)
    is_debug = settings.DEBUG
    return APIResponse(
        data={"unlocked": is_debug or unlocked}
    )


@router.post("/vault/approve")
async def approve_vault_via_post(token: str = None, db: AsyncSession = Depends(get_db)):
    if token == "nila-eternal-2026":
        await set_kv_val(db, "vault_unlocked", True)
        
        await trigger_onesignal_push(
            message="The cosmic alignment is complete. Tap to enter the sacred sanctuary.",
            title="Sanctuary Vault Unlocked! 🌌",
            data={
                "action": "unlock_vault",
                "screen": "SanctuaryActivity"
            }
        )
        return APIResponse(
            message="Vault Unlocked"
        )
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Token"
    )


@router.post("/wish")
async def register_wish(body: WishCreate, db: AsyncSession = Depends(get_db)):
    timestamp_str = body.timestamp or "just now"
    name_str = body.name or "A Soul"
    
    html_template = f"""
    <div style="font-family: serif; padding: 40px; background: #030000; color: #fff; border: 1px solid #164e63; text-align: center; border-radius: 20px;">
      <div style="margin-bottom: 30px;">
        <span style="font-size: 40px;">✨</span>
      </div>
      <h1 style="color: #22d3ee; font-style: italic; font-weight: 300;">A Wish from the Ether</h1>
      <div style="margin: 40px 0; padding: 30px; background: rgba(34, 211, 238, 0.05); border-radius: 20px; border: 1px dashed rgba(34, 211, 238, 0.2);">
        <p style="font-size: 24px; line-height: 1.6; font-style: italic; color: #fff;">
          "{body.wish}"
        </p>
      </div>
      <p style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 2px;">
        Transmitted at {timestamp_str}
      </p>
    </div>
    """
    
    target_email = body.recipient or settings.EMAIL_USER
    success, message_detail = await run_in_threadpool(
        send_nila_email,
        to_email=target_email,
        subject=f"✨ [IvaruNila] New Wish Transmitted: {name_str}",
        html_content=html_template,
        text_content=f"Wish from {name_str}: {body.wish} (at {timestamp_str})"
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transmission Failed: {message_detail}"
        )
        
    await lpush_kv_val(
        db,
        "wishes",
        {
            "wish": body.wish,
            "name": name_str,
            "timestamp": timestamp_str
        }
    )
    
    return APIResponse(
        message="Wish transmitted and stored in KV"
    )
