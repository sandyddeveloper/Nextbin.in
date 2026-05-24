from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class EmailPermissionUpdate(BaseModel):
    email: Optional[Dict[str, bool]] = None
    push: Optional[Dict[str, bool]] = None

class EmailPushRequest(BaseModel):
    to: str
    subject: str
    body: str
    type: Optional[str] = None

class PushNotificationRequest(BaseModel):
    title: Optional[str] = None
    message: str
    playerIds: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None
    imageUrl: Optional[str] = None
    buttons: Optional[List[Any]] = None

class WishCreate(BaseModel):
    wish: str
    timestamp: Optional[str] = None
    name: Optional[str] = None
    recipient: Optional[str] = None
