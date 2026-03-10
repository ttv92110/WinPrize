from fastapi import APIRouter, HTTPException, Request
from api.services.notification_service import notification_service
from api.services.file_db import FileDB
from api.config import Config

router = APIRouter(prefix="/notifications")
users_db = FileDB(str(Config.USERS_FILE))

def get_user_from_email(email: str):
    """Verify user exists"""
    users = users_db.find_by_field("email", email)
    return users[0] if users else None

@router.get("/{email}")
async def get_notifications(email: str, unread_only: bool = False, limit: int = 50):
    """Get notifications for a user"""
    user = get_user_from_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = notification_service.get_user_notifications(email, unread_only, limit)
    return {
        "success": True,
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n.get("read", False)])
    }

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
    
    count = notification_service.mark_all_as_read(email)
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
        
        # Soft delete by marking as read (or you can implement actual delete)
        success = notification_service.mark_as_read(notification_id, email)
        if success:
            return {"success": True, "message": "Notification deleted"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/count/{email}")
async def get_unread_count(email: str):
    """Get unread notifications count"""
    user = get_user_from_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = notification_service.get_user_notifications(email, unread_only=True)
    return {"unread_count": len(notifications)}