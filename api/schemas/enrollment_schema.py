from pydantic import BaseModel, EmailStr
from typing import Optional

class UserDrawCreate(BaseModel):
    user_email: str
    user_pay: int
    lucky_draw_id: str
    
class UserDrawResponse(BaseModel):
    user_email: str
    user_pay: int
    lucky_draw_id: str
    status: str

class PaymentCreate(BaseModel):
    user_email: EmailStr
    user_name: str
    lucky_draw_id: str
    lucky_draw_title: str
    amount: int
    holder_name: str
    account_bank_from: str
    account_number_from: str
    account_bank_to: str
    transaction_id: str
    
class PaymentResponse(BaseModel):
    id: str
    user_email: str
    user_name: str
    lucky_draw_id: str
    lucky_draw_title: str
    amount: int
    holder_name: str
    account_bank_from: str
    account_number_from: str
    account_bank_to: str
    account_number_to: str
    recipient_name: str
    transaction_id: str
    status: str
    created_at: str
    updated_at: Optional[str] = None
    
class PaymentUpdate(BaseModel):
    status: str  # pending/paid/cancel
    notes: Optional[str] = None
    