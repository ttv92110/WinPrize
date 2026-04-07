from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.services.google_sheets_db import sheets_db_manager
from api.config import Config
from datetime import datetime, timedelta
import uuid
import secrets
import os
from pathlib import Path
from api.utils.email import EmailService

router = APIRouter(prefix="/password")

# ========== صرف Google Sheets استعمال کریں ==========
users_db = sheets_db_manager.users_db
password_resets_db = sheets_db_manager.password_resets_db
# ===================================================

# Email service
email_service = EmailService()

# Templates
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Get base URL from environment
def get_base_url(request: Request):
    """Get base URL from request"""
    if os.getenv("VERCEL"):
        return f"https://{request.url.hostname}"
    else:
        return f"{request.url.scheme}://{request.url.hostname}:{request.url.port}"

@router.post("/forgot")
async def forgot_password(request: Request, data: dict):
    """Handle forgot password request"""
    try:
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Find user by email
        users = users_db.find_by_field("email", email)
        if not users:
            return {"success": True, "message": "If your email exists, you will receive reset instructions"}
        
        user = users[0]
        
        # Mark existing unused tokens as used
        existing_resets = password_resets_db.find_by_field("user_email", email)
        for reset in existing_resets:
            if not reset.get("used", False):
                password_resets_db.update(reset["id"], {"used": True})
        
        # Generate unique token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (1 hour from now)
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=1)
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        # Create reset record
        reset_record = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "user_email": user["email"],
            "token": token,
            "created_at": created_at.strftime(date_format),
            "expires_at": expires_at.strftime(date_format),
            "used": False
        }
        
        password_resets_db.insert(reset_record)
        
        # Generate reset link
        base_url = get_base_url(request)
        reset_link = f"{base_url}/password/reset/{token}"
        
        # Send email
        email_sent = await email_service.send_password_reset_email(
            to_email=user["email"],
            reset_link=reset_link,
            user_name=user["name"]
        )
        
        if email_sent:
            return {"success": True, "message": "Password reset instructions have been sent to your email"}
        else:
            print(f"Failed to send email to {user['email']}")
            return {"success": True, "message": "If your email exists, you will receive reset instructions"}
            
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reset/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    try:
        print(f"🔍 Looking for token: {token}")
        
        resets = password_resets_db.find_by_field("token", token)
        
        if not resets:
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {"request": request, "error": "Invalid or expired reset link"}
            )
        
        reset = resets[0]
        
        # ========== اہم تبدیلی ==========
        # Google Sheets سے `used` کی value string میں آ سکتی ہے
        used_value = reset.get("used")
        print(f"🔍 used field value: '{used_value}' (type: {type(used_value)})")
        
        # مختلف possibilities کے لیے check
        is_used = False
        if used_value is True:
            is_used = True
        elif used_value == "True" or used_value == "TRUE":
            is_used = True
        elif used_value == "true":
            is_used = True
        elif used_value == 1 or used_value == "1":
            is_used = True
        elif used_value == "False":  # string "False" -> False
            is_used = False
        elif used_value == False:
            is_used = False
        else:
            # default: agar kuch bhi nahi hai to False maano
            is_used = False
        
        print(f"🔍 is_used: {is_used}")
        
        if is_used:
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {"request": request, "error": "This reset link has already been used"}
            )
        # =================================
        
        # Check if expired
        expires_at = datetime.strptime(reset["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        if datetime.now() > expires_at:
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {"request": request, "error": "This reset link has expired"}
            )
        
        return templates.TemplateResponse(
            "reset_password.html", 
            {"request": request, "token": token, "email": reset["user_email"]}
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return templates.TemplateResponse(
            "reset_password_error.html", 
            {"request": request, "error": "An error occurred"}
        )


@router.post("/reset/{token}")
async def reset_password(token: str, data: dict):
    """Handle password reset submission"""
    try:
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        
        if not new_password or not confirm_password:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        resets = password_resets_db.find_by_field("token", token)
        if not resets:
            raise HTTPException(status_code=400, detail="Invalid reset link")
        
        reset = resets[0]
        
        # ========== used check بھی اسی طرح کریں ==========
        used_value = reset.get("used")
        is_used = False
        if used_value is True or used_value == "True" or used_value == "TRUE" or used_value == "true":
            is_used = True
        elif used_value == 1 or used_value == "1":
            is_used = True
        
        if is_used:
            raise HTTPException(status_code=400, detail="Reset link has already been used")
        # ===================================================
        
        # Check if expired
        current_time = datetime.now()
        expires_at = datetime.strptime(reset["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        
        if current_time > expires_at:
            raise HTTPException(status_code=400, detail="Reset link has expired")
        
        # Update user password
        user = users_db.find_by_id(reset["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        users_db.update(user["id"], {"password": new_password})
        
        # Mark reset as used - TRUE ڈالیں
        password_resets_db.update(reset["id"], {"used": "True"})
        
        return {
            "success": True,
            "message": "Password reset successfully. You can now login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check/{token}")
async def check_token_valid(token: str):
    """Check if token is valid"""
    try:
        resets = password_resets_db.find_by_field("token", token)
        
        if not resets:
            return {"valid": False, "reason": "Invalid token"}
        
        reset = resets[0]
        
        if reset.get("used", False):
            return {"valid": False, "reason": "Token already used"}
        
        current_time = datetime.now()
        expires_at = datetime.strptime(reset["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        
        if current_time > expires_at:
            return {"valid": False, "reason": "Token expired"}
        
        return {"valid": True, "email": reset["user_email"]}
        
    except Exception as e:
        print(f"Error checking token: {str(e)}")
        return {"valid": False, "reason": "Error checking token"}