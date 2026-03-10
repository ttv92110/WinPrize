from fastapi import APIRouter, HTTPException
from api.schemas.enrollment_schema import PaymentCreate, PaymentUpdate
from api.services.file_db import FileDB
from api.config import Config
from datetime import datetime
import uuid

router = APIRouter(prefix="/payments")

# Database files
payments_db = FileDB(str(Config.PAYMENTS_FILE))
lucky_db = FileDB(str(Config.LUCKY_DRAWS_FILE))
users_db = FileDB(str(Config.USERS_FILE))

# Bank account details
BANK_ACCOUNTS = {
    "Easypaisa": {
        "account_number": "+923401710232",
        "holder_name": "Arshad Ali",
        "instructions": "Send money to this Easypaisa number"
    },
    "Jazzcash": {
        "account_number": "+923401710232",
        "holder_name": "Arshad Ali",
        "instructions": "Send money to this Jazzcash number"
    },
    "Allied Bank": {
        "account_number": "PK32ABPA0010075819600019",
        "holder_name": "Arshad Ali",
        "instructions": "Use Allied Bank IBAN for transfer"
    },
    "Meezan Bank": {
        "account_number": "PK16MEZN0000300112289349",
        "holder_name": "Arshad Ali",
        "instructions": "Use Meezan Bank IBAN for transfer"
    }
}

@router.get("/bank-accounts")
async def get_bank_accounts():
    """Get list of bank accounts for receiving payments"""
    return BANK_ACCOUNTS

@router.get("/bank-account/{bank_name}")
async def get_bank_account(bank_name: str):
    """Get specific bank account details"""
    if bank_name not in BANK_ACCOUNTS:
        raise HTTPException(status_code=404, detail="Bank not found")
    return BANK_ACCOUNTS[bank_name]

@router.post("/create")
async def create_payment(payment: PaymentCreate):
    """Create a new payment record"""
    try:
        # Check if draw exists and is open
        draw = lucky_db.find_by_id(payment.lucky_draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        if draw["status"] != "open":
            raise HTTPException(status_code=400, detail="Draw is not open")
        
        # Check if user already has pending payment for this draw
        existing_payments = payments_db.find_by_field("user_email", payment.user_email)
        pending = [p for p in existing_payments 
                  if p.get("lucky_draw_id") == payment.lucky_draw_id 
                  and p.get("status") == "pending"]
        
        if pending:
            raise HTTPException(status_code=400, detail="You already have a pending payment for this draw")
        
        # Get bank account details for recipient
        bank_to = BANK_ACCOUNTS.get(payment.account_bank_to)
        if not bank_to:
            raise HTTPException(status_code=400, detail="Invalid recipient bank")
        
        # Create payment record
        payment_dict = payment.dict()
        payment_dict["id"] = str(uuid.uuid4())
        payment_dict["status"] = "pending"
        payment_dict["created_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        payment_dict["account_number_to"] = bank_to["account_number"]
        payment_dict["recipient_name"] = bank_to["holder_name"]
        
        payments_db.insert(payment_dict)
        
        # Create enrollment record - Fix: Don't import from draw_routes, use local reference
        from api.services.file_db import FileDB
        user_draws_db = FileDB(str(Config.USER_DRAWS_FILE))
        
        enrollment = {
            "id": str(uuid.uuid4()),
            "user_email": payment.user_email,
            "user_pay": payment.amount,
            "lucky_draw_id": payment.lucky_draw_id,
            "status": "pending",
            "joined_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        }
        user_draws_db.insert(enrollment)
        
        return {
            "success": True,
            "message": "Payment record created successfully",
            "payment_id": payment_dict["id"],
            "bank_details": {
                "bank_name": payment.account_bank_to,
                "account_number": bank_to["account_number"],
                "holder_name": bank_to["holder_name"],
                "instructions": bank_to["instructions"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{email}")
async def get_user_payments(email: str):
    """Get all payments for a user"""
    try:
        payments = payments_db.find_by_field("user_email", email)
        # Sort by date descending
        payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return payments
    except Exception as e:
        print(f"Error getting user payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/draw/{draw_id}")
async def get_draw_payments(draw_id: str):
    """Get all payments for a draw"""
    try:
        payments = payments_db.find_by_field("lucky_draw_id", draw_id)
        return payments
    except Exception as e:
        print(f"Error getting draw payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def get_pending_payments():
    """Get all pending payments (for admin)"""
    try:
        all_payments = payments_db.read_all()
        pending = [p for p in all_payments if p.get("status") == "pending"]
        return pending
    except Exception as e:
        print(f"Error getting pending payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{payment_id}")
async def update_payment_status(payment_id: str, update: PaymentUpdate):
    """Update payment status (admin only)"""
    try:
        payment = payments_db.find_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Update payment
        payment["status"] = update.status
        payment["updated_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        if update.notes:
            payment["notes"] = update.notes
        
        payments_db.update(payment_id, payment)
        
        # If payment is paid, update enrollment status
        if update.status == "paid":
            from api.services.file_db import FileDB
            user_draws_db = FileDB(str(Config.USER_DRAWS_FILE))
            enrollments = user_draws_db.find_by_field("user_email", payment["user_email"])
            for enrollment in enrollments:
                if enrollment.get("lucky_draw_id") == payment["lucky_draw_id"]:
                    user_draws_db.update(enrollment["id"], {"status": "open"})
                    break
        
        return {"success": True, "message": f"Payment status updated to {update.status}"}
    except Exception as e:
        print(f"Error updating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check/{email}/{draw_id}")
async def check_payment_status(email: str, draw_id: str):
    """Check if user has paid for a draw"""
    try:
        payments = payments_db.find_by_field("user_email", email)
        for payment in payments:
            if payment.get("lucky_draw_id") == draw_id:
                return {
                    "has_payment": True,
                    "status": payment.get("status"),
                    "payment_id": payment.get("id")
                }
        return {"has_payment": False}
    except Exception as e:
        print(f"Error checking payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    