from fastapi import APIRouter, HTTPException, Request
from api.services.notification_service import notification_service
from api.services.google_sheets_db import sheets_db_manager
from api.config import Config

router = APIRouter(prefix="/notifications")

# ========== صرف Google Sheets استعمال کریں ==========
users_db = sheets_db_manager.users_db
# ===================================================

def get_user_from_email(email: str):
    """Verify user exists"""
    users = users_db.find_by_field("email", email)
    return users[0] if users else None

@router.get("/{email}")
async def get_notifications(email: str, unread_only: bool = False, limit: int = 1000):
    """Get notifications for a user"""
    user = get_user_from_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = notification_service.get_user_notifications(email, unread_only, limit)
    
    # Convert string "False" to boolean False for each notification
    for n in notifications:
        if isinstance(n.get("read"), str):
            n["read"] = n["read"].lower() == "true"
    
    return {
        "success": True,
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n.get("read", False)])
    }

@router.get("/count/{email}")
async def get_unread_count(email: str):
    """Get unread notifications count"""
    user = get_user_from_email(email)
    if not user:
        return {"unread_count": 0}
    
    # Get all notifications (not just unread)
    all_notifications = notification_service.get_user_notifications(email, unread_only=False, limit=1000)
    
    # Count unread notifications
    unread_count = 0
    for n in all_notifications:
        read_val = n.get("read", False)
        
        # Handle both string and boolean
        if isinstance(read_val, str):
            if read_val.lower() == "false":
                unread_count += 1
        elif read_val is False:
            unread_count += 1
    
    print(f"📊 Unread count for {email}: {unread_count} (total notifications: {len(all_notifications)})")
    
    return {"unread_count": unread_count}

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str, request: Request):
    """Mark a notification as read"""
    try:
        data = await request.json()
        email = data.get("email")
        
        user = get_user_from_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = notification_service.mark_as_read(notification_id, email)
        if success:
            return {"success": True, "message": "Notification marked as read"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-all-read/{email}")
async def mark_all_read(email: str):
    """Mark all notifications as read for a user"""
    user = get_user_from_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
     
    all_notifications = notification_service.get_user_notifications(email, unread_only=False, limit=1000)
    
    count = 0
    for n in all_notifications: 
        read_val = n.get("read", False)
        is_read = False
        
        if isinstance(read_val, str):
            is_read = read_val.lower() == "true"
        else:
            is_read = read_val
         
        if not is_read:
            success = notification_service.mark_as_read(n["id"], email)
            if success:
                count += 1
    
    return {"success": True, "message": f"{count} notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, request: Request):
    """Delete a notification"""
    try:
        data = await request.json()
        email = data.get("email")
        
        user = get_user_from_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
         
        success = notification_service.mark_as_read(notification_id, email)
        if success:
            return {"success": True, "message": "Notification deleted"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 