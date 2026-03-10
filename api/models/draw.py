from pydantic import BaseModel
from datetime import datetime
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

api/routes/admin_routes.py : 
api/routes/auth_routes.py :  
api/routes/draw_routes.py :
  
api/schemas/draw_schemas.py : 
api/schemas/enrollment_schemas.py :  
api/schemas/user_schemas.py : 

api/services/draw_engine.py :  
api/services/file_db.py : 

api/utils/auth.py :   

api/main.py :
         

api/config.py:   
api/init_data.py: have same code which you give
api/startup.py: have same code  which you give


data/lucky_draws.json :  
data/user_draws.json : empty no json data, data are rquired here at will fill
data/users.json : empty no json data, data are rquired here at will fill
 

templates/admin.html :  
templates/index.html :  
templates/winner.html :  

static/images/confrats.png :
static/images/favicon_icon.png :


static/js/admin_draw.js : 
static/js/admin.js : 
static/js/app.js :  
static/js/auth.js : 
static/js/draws.js : 
static/js/enroll.js :  
static/js/login.js :
static/js/register.js : 
static/js/main.js : 

static/css/style.css : style still remain same, which you give this oustanding.
 
.env file : , style still remain same, which you give this oustanding.

requirement.txt :  style still remain same, which you give this oustanding.

vercel.json :  style still remain same, which you give this oustanding.


'''
