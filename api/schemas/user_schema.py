from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_status: Optional[str] = "user"  # Default to user, can be "staff" for admin
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    name: str
    email: EmailStr
    user_status: str = "user"
    