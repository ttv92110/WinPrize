from typing import Optional

from pydantic import BaseModel 

class LuckyDrawCreate(BaseModel):
    user_pay: int
    time_interval: str  # 1hour, 12hours, day, 10days, 15days, month, 3months, 6months, 1year
    winner_get: int
    visible: bool = True
    
class LuckyDrawResponse(BaseModel):
    id: str
    user_pay: int
    time_interval: str
    winner_get: int
    status: str
    visible: bool
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    closed_at: Optional[str] = None
    