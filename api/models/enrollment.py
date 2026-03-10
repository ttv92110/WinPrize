from pydantic import BaseModel
from typing import Optional

class UserDraw(BaseModel):
    user_email: str
    user_pay: int
    lucky_draw_id: str
    status: str  # open, loss, win
    
class UserDrawInDB(UserDraw):
    id: Optional[str] = None
    