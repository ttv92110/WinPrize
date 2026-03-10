from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Payment(BaseModel):
    id: str
    user_email: str
    user_name: str
    lucky_draw_id: str
    lucky_draw_title: str
    amount: int
    holder_name: str
    account_bank_from: str  # Easypaisa/Jazzcash/Allied Bank/Meezan Bank
    account_number_from: str
    account_bank_to: str    # Easypaisa/Jazzcash/Allied Bank/Meezan Bank
    account_number_to: str
    recipient_name: str
    transaction_id: str
    status: str  # pending/paid/cancel
    created_at: str
    updated_at: Optional[str] = None
    notes: Optional[str] = None

class PaymentInDB(Payment):
    pass