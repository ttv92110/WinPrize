from pydantic import BaseModel 
from typing import Optional

class LuckyDraw(BaseModel):
    id: str
    user_pay: int
    time_interval: str  # day, week, month
    winner_get: int
    status: str  # open, completed, finished, awaiting
    visible: bool
    created_at: Optional[str] = None
    closed_at: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None
    auto_complete: Optional[bool] = True
    
class LuckyDrawInDB(LuckyDraw):
    pass

