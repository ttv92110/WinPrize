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



'''
Project : WinPrize/

api/models/draw.py :   
api/models/enrollment.py :  
api/models/user.py :  
api/models/notification.py :  
api/models/password_reset.py :  
api/models/payment.py :  
api/models/veriication.py :   
api/routes/admin_routes.py :   
api/routes/auth_routes.py :   
api/routes/draw_routes.py : 
api/routes/notifications_routes.py :  
api/routes/password_routes.py :   
api/routes/verification_routes.py :    
api/schemas/draw_schemas.py : 
api/schemas/enrollment_schema.py :    
api/schemas/user_schema.py :  
api/services/draw_engine.py :  
api/services/file_db.py : 
api/services/notification_service.py :  
api/utils/email.py : 
api/main.py :   

api/config.py:   
api/init_data.py: have same code which you give
api/startup.py: have same code  which you give
 
other file are also there.
'''
