from fastapi import APIRouter, HTTPException, Request 
from fastapi.templating import Jinja2Templates
from api.services.google_sheets_db import sheets_db_manager
from api.config import Config
from api.utils.email import EmailService
from datetime import datetime, timedelta
import uuid
import random 
from pathlib import Path

router = APIRouter(prefix="/verify")

# ========== صرف Google Sheets استعمال کریں ==========
verifications_db = sheets_db_manager.verifications_db
users_db = sheets_db_manager.users_db
# ===================================================

# Email service
email_service = EmailService()

# Templates
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

def generate_6digit_pin():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_verified(record): 
    verified_val = record.get("verified", False)
    if isinstance(verified_val, bool):
        return verified_val
    elif isinstance(verified_val, str):
        return verified_val.lower() == "true"
    return False

@router.post("/send-pin")
async def send_verification_pin(request: Request, data: dict):
    try:
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")
        user_status = data.get("user_status", "user")
        
        if not email or not name or not password:
            raise HTTPException(status_code=400, detail="Missing required fields")
         
        existing_users = users_db.find_by_field("email", email)
        if existing_users:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Delete old unverified verifications
        existing_verifications = verifications_db.find_by_field("email", email)
        for ver in existing_verifications:
            if not ver.get("verified", False):
                try:
                    expires_at = datetime.strptime(ver["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                    if datetime.now() > expires_at:
                        verifications_db.delete(ver["id"])
                except:
                    verifications_db.delete(ver["id"])
        
        pin = generate_6digit_pin() 
        pin = str(pin).zfill(6)
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=20)
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        verification = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": password,
            "pin": str(pin).zfill(6),
            "created_at": created_at.strftime(date_format),
            "expires_at": expires_at.strftime(date_format),
            "verified": False,
            "attempts": 0,
            "user_status": user_status
        }
        
        verifications_db.insert(verification)
        
        email_sent = await email_service.send_verification_pin(
            to_email=email,
            user_name=name,
            pin=pin
        )
        
        if email_sent:
            return {
                "success": True,
                "message": "Verification PIN sent to your email",
                "email": email
            }
        else:
            verifications_db.delete(verification["id"])
            raise HTTPException(status_code=500, detail="Failed to send verification email")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending PIN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
 
@router.post("/verify-pin")
async def verify_pin(data: dict):
    try:
        email = data.get("email")
        pin = data.get("pin")
        
        if not email or not pin:
            raise HTTPException(status_code=400, detail="Email and PIN are required")
        
        verifications = verifications_db.find_by_field("email", email)
        
        # صرف unverified والے filter کریں (string "FALSE" کو بھی false سمجھیں)
        unverified = []
        for v in verifications:
            verified_val = v.get("verified")
            is_verified = False
            if isinstance(verified_val, bool):
                is_verified = verified_val
            elif isinstance(verified_val, str):
                is_verified = verified_val.lower() == "true"
            
            if not is_verified:
                unverified.append(v)
        
        if not unverified:
            existing_users = users_db.find_by_field("email", email)
            if existing_users:
                raise HTTPException(status_code=400, detail="Email already verified. Please login.")
            raise HTTPException(status_code=400, detail="No pending verification found")
        
        verification = sorted(unverified, key=lambda x: x.get("created_at", ""), reverse=True)[0]
         
        try:
            expires_at = datetime.strptime(verification["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
            if datetime.now() > expires_at:
                verifications_db.delete(verification["id"])
                raise HTTPException(status_code=400, detail="PIN has expired. Please request a new one.")
        except:
            pass
        
        if verification.get("attempts", 0) >= 5:
            verifications_db.delete(verification["id"])
            raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new PIN.")
        
        # ========== اہم تبدیلی: PIN comparison ========== 
        db_pin = str(verification.get("pin", ""))
        input_pin = str(pin).zfill(6)  
        
        if len(db_pin) == 5:
            db_pin = "0" + db_pin
        elif len(db_pin) == 4:
            db_pin = "00" + db_pin
        elif len(db_pin) == 3:
            db_pin = "000" + db_pin
        elif len(db_pin) == 2:
            db_pin = "0000" + db_pin
        elif len(db_pin) == 1:
            db_pin = "00000" + db_pin
        

        if db_pin != input_pin: 
            verification["attempts"] = verification.get("attempts", 0) + 1
            verifications_db.update(verification["id"], {"attempts": verification["attempts"]})
            remaining = 5 - verification["attempts"]
            raise HTTPException(status_code=400, detail=f"Invalid PIN. {remaining} attempts remaining.")
        # =================================================
         
        user_data = {
            "id": str(uuid.uuid4()),
            "name": verification["name"],
            "email": verification["email"],
            "password": verification["password"],
            "user_status": verification.get("user_status", "user"),
            "email_verified": True,
            "verified_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        }
        
        users_db.insert(user_data) 
         
        verification["verified"] = True
        verification["verified_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        verifications_db.update(verification["id"], verification)
         
        for v in unverified:
            if v["id"] != verification["id"]:
                verifications_db.delete(v["id"])
         
        import asyncio
        asyncio.create_task(email_service.send_welcome_email(
            to_email=email,
            user_name=verification["name"]
        ))
        
        return {
            "success": True,
            "message": "Email verified successfully! Your account has been created.",
            "user": {
                "name": verification["name"],
                "email": verification["email"],
                "user_status": verification.get("user_status", "user")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resend-pin")
async def resend_pin(data: dict):
    try:
        email = data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
         
        existing_users = users_db.find_by_field("email", email)
        if existing_users: 
            raise HTTPException(status_code=400, detail="Email already verified. Please login.")
        
        verifications = verifications_db.find_by_field("email", email) 
         
        unverified = []
        for v in verifications:
            verified_val = v.get("verified") 
            is_verified = False
            if isinstance(verified_val, bool):
                is_verified = verified_val
            elif isinstance(verified_val, str):
                is_verified = verified_val.lower() == "true"
            else:
                is_verified = False
            
            if not is_verified:
                unverified.append(v)
        
        if not unverified:
            raise HTTPException(status_code=400, detail="No pending verification found. Please register again.")
         
        verification = unverified[0]
        verifications_db.delete(verification["id"]) 
         
        pin = generate_6digit_pin()
        pin = str(pin).zfill(6)
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=20)
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        new_verification = {
            "id": str(uuid.uuid4()),
            "email": verification["email"],
            "name": verification["name"],
            "password": verification["password"],
            "pin": pin,
            "created_at": created_at.strftime(date_format),
            "expires_at": expires_at.strftime(date_format),
            "verified": False,
            "attempts": 0,
            "user_status": verification.get("user_status", "user")
        }
        
        verifications_db.insert(new_verification) 
         
        email_sent = await email_service.send_verification_pin(
            to_email=email,
            user_name=verification["name"],
            pin=pin
        )
        
        if email_sent: 
            return {
                "success": True,
                "message": "New verification PIN sent to your email"
            }
        else:
            verifications_db.delete(new_verification["id"]) 
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except HTTPException:
        raise
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/check/{email}")
async def check_verification_status(email: str):
    try:
        users = users_db.find_by_field("email", email)
        if users:
            return {"verified": True, "message": "Email already verified"}
        
        verifications = verifications_db.find_by_field("email", email)
        pending = [v for v in verifications if not v.get("verified", False)]
        
        if pending:
            verification = pending[0]
            try:
                expires_at = datetime.strptime(verification["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                if datetime.now() > expires_at:
                    return {"verified": False, "expired": True, "message": "Verification expired"}
            except:
                pass
            return {
                "verified": False, 
                "pending": True,
                "expires_at": verification.get("expires_at", ""),
                "attempts": verification.get("attempts", 0)
            }
        
        return {"verified": False, "message": "No verification found"}
        
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
