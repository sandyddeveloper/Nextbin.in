from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class InstagramAccount(BaseModel):
    __tablename__ = "instagram_accounts"

    username = Column(String, unique=True, index=True, nullable=False)
    encrypted_password = Column(String, nullable=False)
    
    # JSON-serialized session settings/cookies to preserve login state and bypass login verification limits
    session_settings = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String, default="DISCONNECTED", nullable=False)  # CONNECTED, DISCONNECTED, ERROR, 2FA_REQUIRED
    last_synced_at = Column(DateTime, nullable=True)

    chat_logs = relationship("InstagramChatLog", back_populates="account", cascade="all, delete-orphan")
    rules = relationship("InstagramRule", back_populates="account", cascade="all, delete-orphan")

class InstagramChatLog(BaseModel):
    __tablename__ = "instagram_chat_logs"

    account_id = Column(Integer, ForeignKey("instagram_accounts.id", ondelete="CASCADE"), nullable=False)
    thread_id = Column(String, index=True, nullable=False)
    message_id = Column(String, unique=True, index=True, nullable=False)
    sender_username = Column(String, nullable=False)
    text = Column(Text, nullable=True)
    direction = Column(String, nullable=False)  # INCOMING, OUTGOING
    timestamp = Column(DateTime, nullable=False)

    account = relationship("InstagramAccount", back_populates="chat_logs")

class InstagramRule(BaseModel):
    __tablename__ = "instagram_rules"

    account_id = Column(Integer, ForeignKey("instagram_accounts.id", ondelete="CASCADE"), nullable=False)
    trigger_keyword = Column(String, index=True, nullable=False)  # e.g., "price", "link", "info"
    response_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    account = relationship("InstagramAccount", back_populates="rules")
