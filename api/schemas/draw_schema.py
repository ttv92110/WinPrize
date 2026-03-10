from pydantic import BaseModel 

class LuckyDrawCreate(BaseModel):
    user_pay: int
    time_interval: str
    winner_get: int
    visible: bool = True
    
class LuckyDrawResponse(BaseModel):
    id: str
    user_pay: int
    time_interval: str
    winner_get: int
    status: str
    visible: bool
    