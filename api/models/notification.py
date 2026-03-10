from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    id: str
    user_email: str
    title: str
    message: str
    type: str  # 'new_draw', 'payment_update', 'draw_result', 'system'
    draw_id: Optional[str] = None
    draw_title: Optional[str] = None
    amount: Optional[int] = None
    read: bool = False
    created_at: str
    expires_at: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = "View Draw"

class NotificationInDB(Notification):
    pass

class NotificationCreate(BaseModel):
    user_email: str
    title: str
    message: str
    type: str
    draw_id: Optional[str] = None
    draw_title: Optional[str] = None
    amount: Optional[int] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = "View Draw"