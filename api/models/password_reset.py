from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PasswordReset(BaseModel):
    id: str
    user_id: str
    user_email: str
    token: str
    created_at: str
    expires_at: str
    used: bool = False
    used_at: Optional[str] = None

class PasswordResetInDB(PasswordReset):
    pass

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str