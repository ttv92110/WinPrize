from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmailVerification(BaseModel):
    id: str
    email: str
    name: str
    password: str  # Temporarily stored until verified
    pin: str  # 6-digit PIN
    created_at: str
    expires_at: str
    verified: bool = False
    attempts: int = 0
    user_status: str = "user"  # Default user status

class EmailVerificationInDB(EmailVerification):
    pass

class VerifyPinRequest(BaseModel):
    email: str
    pin: str

class ResendPinRequest(BaseModel):
    email: str