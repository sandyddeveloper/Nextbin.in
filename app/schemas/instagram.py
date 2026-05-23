from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Account Schemas
class InstagramAccountBase(BaseModel):
    username: str
    is_active: Optional[bool] = True

class InstagramAccountCreate(InstagramAccountBase):
    password: str

class InstagramAccountResponse(InstagramAccountBase):
    id: int
    status: str
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Rule Schemas
class InstagramRuleBase(BaseModel):
    trigger_keyword: str
    response_text: str
    is_active: Optional[bool] = True

class InstagramRuleCreate(InstagramRuleBase):
    pass

class InstagramRuleResponse(InstagramRuleBase):
    id: int
    account_id: int

    model_config = ConfigDict(from_attributes=True)

# Chat Log Schemas
class InstagramChatLogResponse(BaseModel):
    id: int
    account_id: int
    thread_id: str
    message_id: str
    sender_username: str
    text: Optional[str] = None
    direction: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
