import json
from typing import Any, Dict, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog

async def log_audit_action(
    db: AsyncSession,
    action: str,
    request: Request,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Writes a security trace record to the SQLite database audit logs.
    Automatically captures X-Request-ID, X-Platform, and the Client IP address.
    """
    # Capture client IP
    ip_address = "unknown"
    if request.client:
        ip_address = request.client.host
        
    # Retrieve Request ID and Platform set by middlewares
    request_id = getattr(request.state, "request_id", "unknown")
    platform = getattr(request.state, "platform", "unknown")
    
    details_str = None
    if details:
        try:
            details_str = json.dumps(details)
        except Exception:
            details_str = str(details)
            
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        request_id=request_id,
        platform=platform,
        ip_address=ip_address,
        details=details_str
    )
    
    db.add(audit_entry)
    # Note: We do not call commit here to allow the write to commit atomically
    # as part of the surrounding endpoint request transaction.
    return audit_entry
