from fastapi import APIRouter, HTTPException, Request
from api.schemas.user_schema import UserCreate, UserLogin
from api.services.google_sheets_db import sheets_db_manager
from api.utils.email import EmailService
from api.config import Config
import uuid

router = APIRouter(prefix="/auth")

# ========== صرف Google Sheets استعمال کریں ==========
users_db = sheets_db_manager.users_db
# ===================================================

email_service = EmailService()

@router.post("/signup")
async def signup(user: UserCreate):
    try:
        # Check if user exists
        existing = users_db.find_by_field("email", user.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user_dict = user.dict()
        user_dict["id"] = str(uuid.uuid4())
        if "user_status" not in user_dict:
            user_dict["user_status"] = "user"
        
        # صرف Google Sheets میں save ہوگا
        users_db.insert(user_dict)
        
        # Send welcome email
        import asyncio
        asyncio.create_task(email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.name
        ))
        
        return {"message": "User created successfully", "success": True}
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    try:
        users = users_db.find_by_field("email", user.email)
        
        if not users:
            return {"success": False, "message": "Invalid email or password"}
        
        stored_user = users[0]
        if stored_user["password"] == user.password:
            return {
                "success": True, 
                "user": {
                    "name": stored_user["name"],
                    "email": stored_user["email"],
                    "user_status": stored_user.get("user_status", "user")
                }
            }
        
        return {"success": False, "message": "Invalid email or password"}
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return {"success": False, "message": "An error occurred during login"}

@router.get("/check-admin/{email}")
async def check_admin_status(email: str):
    """Check if a user is admin (staff)"""
    try:
        users = users_db.find_by_field("email", email)
        if not users:
            return {"isAdmin": False, "reason": "User not found"}
        
        is_admin = users[0].get("user_status") == "staff"
        return {
            "isAdmin": is_admin,
            "user": {
                "email": users[0]["email"],
                "name": users[0]["name"],
                "user_status": users[0].get("user_status", "user")
            }
        }
    except Exception as e:
        print(f"Error checking admin status: {str(e)}")
        return {"isAdmin": False, "reason": str(e)}

@router.get("/profile/{email}")
async def get_user_profile(email: str):
    """Get user profile by email"""
    try:
        users = users_db.find_by_field("email", email)
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        return {
            "name": user["name"],
            "email": user["email"],
            "user_status": user.get("user_status", "user"),
            "id": user["id"]
        }
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile/{email}")
async def update_user_profile(email: str, user_data: dict):
    """Update user profile"""
    try:
        users = users_db.find_by_field("email", email)
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        if "name" in user_data:
            user["name"] = user_data["name"]
        if "password" in user_data and user_data["password"]:
            user["password"] = user_data["password"]
        
        users_db.update(user["id"], user)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "name": user["name"],
                "email": user["email"],
                "user_status": user.get("user_status", "user")
            }
        }
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users(request: Request):
    """Get all users - admin only"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        admins = users_db.find_by_field("email", admin_email)
        if not admins or admins[0].get("user_status") != "staff":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        all_users = users_db.read_all()
        for user in all_users:
            if "password" in user:
                del user["password"]
        
        return all_users
    except Exception as e:
        print(f"Error getting all users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user-status/{email}")
async def update_user_status(email: str, request: Request):
    """Update user status - admin only"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        new_status = body.get("user_status")
        
        if not admin_email or not new_status:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        admins = users_db.find_by_field("email", admin_email)
        if not admins or admins[0].get("user_status") != "staff":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        users = users_db.find_by_field("email", email)
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        user["user_status"] = new_status
        users_db.update(user["id"], user)
        
        return {
            "success": True,
            "message": f"User status updated to {new_status}",
            "user": {
                "email": user["email"],
                "name": user["name"],
                "user_status": user["user_status"]
            }
        }
    except Exception as e:
        print(f"Error updating user status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    