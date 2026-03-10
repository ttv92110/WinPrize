from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.services.file_db import FileDB
from api.config import Config
from datetime import datetime, timedelta
import uuid
import secrets
import os
from pathlib import Path
from api.utils.email import EmailService

router = APIRouter(prefix="/password")  # This sets the prefix

# Database files
users_db = FileDB(str(Config.USERS_FILE))
password_resets_db = FileDB(str(Config.PASSWORD_RESETS_FILE))

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
        # For Vercel production
        return f"https://{request.url.hostname}"
    else:
        # For local development
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
            # Don't reveal if user exists or not for security
            return {"success": True, "message": "If your email exists, you will receive reset instructions"}
        
        user = users[0]
        
        # Check for existing unused reset tokens and mark them as used
        existing_resets = password_resets_db.find_by_field("user_email", email)
        for reset in existing_resets:
            if not reset.get("used", False):
                password_resets_db.update(reset["id"], {"used": True})
        
        # Generate unique token (one-time use)
        token = secrets.token_urlsafe(32)
        
        # Set expiration (1 hour from now)
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=1)
        
        # Format dates
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
            return {
                "success": True, 
                "message": "Password reset instructions have been sent to your email"
            }
        else:
            # Log the error but don't reveal to user
            print(f"Failed to send email to {user['email']}")
            return {
                "success": True, 
                "message": "If your email exists, you will receive reset instructions"
            }
            
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# THIS IS THE CRITICAL ROUTE - Make sure it's defined correctly
@router.get("/reset/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    """Show password reset page"""
    try:
        print(f"Accessing reset page with token: {token}")  # Debug log
        
        # Find valid reset record
        resets = password_resets_db.find_by_field("token", token)
        
        if not resets:
            print(f"No reset record found for token: {token}")
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {
                    "request": request, 
                    "error": "Invalid or expired reset link"
                }
            )
        
        reset = resets[0]
        print(f"Found reset record for user: {reset['user_email']}")
        
        # Check if already used
        if reset.get("used", False):
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {
                    "request": request, 
                    "error": "This reset link has already been used"
                }
            )
        
        # Check if expired
        current_time = datetime.now()
        expires_at = datetime.strptime(reset["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        
        if current_time > expires_at:
            return templates.TemplateResponse(
                "reset_password_error.html", 
                {
                    "request": request, 
                    "error": "This reset link has expired"
                }
            )
        
        # Show reset password form
        return templates.TemplateResponse(
            "reset_password.html", 
            {
                "request": request, 
                "token": token,
                "email": reset["user_email"]
            }
        )
    except Exception as e:
        print(f"Error in reset_password_page: {str(e)}")
        return templates.TemplateResponse(
            "reset_password_error.html", 
            {
                "request": request, 
                "error": "An error occurred. Please try again."
            }
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
        
        # Find valid reset record
        resets = password_resets_db.find_by_field("token", token)
        
        if not resets:
            raise HTTPException(status_code=400, detail="Invalid reset link")
        
        reset = resets[0]
        
        # Check if already used
        if reset.get("used", False):
            raise HTTPException(status_code=400, detail="Reset link has already been used")
        
        # Check if expired
        current_time = datetime.now()
        expires_at = datetime.strptime(reset["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        
        if current_time > expires_at:
            raise HTTPException(status_code=400, detail="Reset link has expired")
        
        # Update user password
        user = users_db.find_by_id(reset["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update password (in production, hash it)
        users_db.update(user["id"], {"password": new_password})
        
        # Mark reset as used
        reset["used"] = True
        reset["used_at"] = current_time.strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        password_resets_db.update(reset["id"], reset)
        
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
    """Check if token is valid (for AJAX calls)"""
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
    