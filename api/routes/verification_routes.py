from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.services.file_db import FileDB
from api.config import Config
from api.utils.email import EmailService
from datetime import datetime, timedelta
import uuid
import random
import os
from pathlib import Path

router = APIRouter(prefix="/verify")

# Database files
verifications_db = FileDB(str(Config.EMAIL_VERIFICATIONS_FILE))
users_db = FileDB(str(Config.USERS_FILE))

# Email service
email_service = EmailService()

# Templates
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

def generate_6digit_pin():
    """Generate a random 6-digit PIN"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

@router.post("/send-pin")
async def send_verification_pin(request: Request, data: dict):
    """Send 6-digit PIN to email for verification"""
    try:
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")
        user_status = data.get("user_status", "user")
        
        if not email or not name or not password:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Check if email already exists and is verified
        existing_users = users_db.find_by_field("email", email)
        if existing_users:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check for existing unverified verifications and delete them
        existing_verifications = verifications_db.find_by_field("email", email)
        for ver in existing_verifications:
            if not ver.get("verified", False):
                # Check if expired
                expires_at = datetime.strptime(ver["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                if datetime.now() > expires_at:
                    verifications_db.delete(ver["id"])
        
        # Generate 6-digit PIN
        pin = generate_6digit_pin()
        
        # Set expiration (20 minutes from now)
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=20)
        
        # Format dates
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        # Create verification record
        verification = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": password,  # Store temporarily
            "pin": pin,
            "created_at": created_at.strftime(date_format),
            "expires_at": expires_at.strftime(date_format),
            "verified": False,
            "attempts": 0,
            "user_status": user_status
        }
        
        verifications_db.insert(verification)
        
        # Send PIN via email
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
            # Delete verification if email failed
            verifications_db.delete(verification["id"])
            raise HTTPException(status_code=500, detail="Failed to send verification email")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending PIN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-pin")
async def verify_pin(data: dict):
    """Verify the 6-digit PIN"""
    try:
        email = data.get("email")
        pin = data.get("pin")
        
        if not email or not pin:
            raise HTTPException(status_code=400, detail="Email and PIN are required")
        
        # Find verification record
        verifications = verifications_db.find_by_field("email", email)
        
        # Filter unverified ones
        unverified = [v for v in verifications if not v.get("verified", False)]
        
        if not unverified:
            raise HTTPException(status_code=400, detail="No pending verification found")
        
        # Get the most recent one
        verification = sorted(unverified, 
                            key=lambda x: x.get("created_at", ""), 
                            reverse=True)[0]
        
        # Check if expired
        expires_at = datetime.strptime(verification["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        if datetime.now() > expires_at:
            verifications_db.delete(verification["id"])
            raise HTTPException(status_code=400, detail="PIN has expired. Please request a new one.")
        
        # Check attempts (max 5 attempts)
        if verification.get("attempts", 0) >= 5:
            verifications_db.delete(verification["id"])
            raise HTTPException(status_code=400, detail="Too many failed attempts. Please request a new PIN.")
        
        # Verify PIN
        if verification["pin"] != pin:
            # Increment attempts
            verification["attempts"] = verification.get("attempts", 0) + 1
            verifications_db.update(verification["id"], {"attempts": verification["attempts"]})
            
            remaining = 5 - verification["attempts"]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid PIN. {remaining} attempts remaining."
            )
        
        # PIN is correct - create user account
        user_data = {
            "id": str(uuid.uuid4()),
            "name": verification["name"],
            "email": verification["email"],
            "password": verification["password"],  # In production, hash this
            "user_status": verification.get("user_status", "user"),
            "email_verified": True,
            "verified_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        }
        
        users_db.insert(user_data)
        
        # Mark verification as verified
        verification["verified"] = True
        verification["verified_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        verifications_db.update(verification["id"], verification)
        
        # Delete old verifications
        for v in unverified:
            if v["id"] != verification["id"]:
                verifications_db.delete(v["id"])
        
        # Send welcome email
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
        print(f"Error verifying PIN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resend-pin")
async def resend_pin(data: dict):
    """Resend verification PIN"""
    try:
        email = data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Find existing verification
        verifications = verifications_db.find_by_field("email", email)
        unverified = [v for v in verifications if not v.get("verified", False)]
        
        if not unverified:
            raise HTTPException(status_code=400, detail="No pending verification found")
        
        # Delete old verification
        verification = unverified[0]
        verifications_db.delete(verification["id"])
        
        # Generate new PIN
        pin = generate_6digit_pin()
        
        # Set new expiration (20 minutes)
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=20)
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        # Create new verification
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
        
        # Send new PIN
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
        print(f"Error resending PIN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check/{email}")
async def check_verification_status(email: str):
    """Check if email is verified"""
    try:
        # Check if user exists
        users = users_db.find_by_field("email", email)
        if users:
            return {"verified": True, "message": "Email already verified"}
        
        # Check for pending verification
        verifications = verifications_db.find_by_field("email", email)
        pending = [v for v in verifications if not v.get("verified", False)]
        
        if pending:
            # Check if expired
            verification = pending[0]
            expires_at = datetime.strptime(verification["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
            if datetime.now() > expires_at:
                return {"verified": False, "expired": True, "message": "Verification expired"}
            return {
                "verified": False, 
                "pending": True,
                "expires_at": verification["expires_at"],
                "attempts": verification.get("attempts", 0)
            }
        
        return {"verified": False, "message": "No verification found"}
        
    except Exception as e:
        print(f"Error checking verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))