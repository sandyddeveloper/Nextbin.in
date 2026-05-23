from sqlalchemy import Column, String, Integer, Text, DateTime
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(Integer, nullable=True) # Can be NULL for unauthenticated login attempts
    action = Column(String, index=True, nullable=False) # e.g., "USER_LOGIN_SUCCESS", "IG_MESSAGE_SENT"
    request_id = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False) # web, ios, android, unknown
    ip_address = Column(String, nullable=False)
    details = Column(Text, nullable=True) # JSON details
