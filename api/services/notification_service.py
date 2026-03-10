from api.services.file_db import FileDB
from api.config import Config
from datetime import datetime, timedelta
import uuid
from typing import List, Optional

class NotificationService:
    def __init__(self):
        self.notifications_db = FileDB(str(Config.NOTIFICATIONS_FILE))
        self.users_db = FileDB(str(Config.USERS_FILE))
    
    def create_notification(self, user_email: str, title: str, message: str, 
                           notification_type: str, draw_id: Optional[str] = None,
                           draw_title: Optional[str] = None, amount: Optional[int] = None,
                           action_url: Optional[str] = None, action_text: str = "View Draw",
                           expires_in_days: int = 7):
        """Create a new notification for a user"""
        try:
            # Check if user exists
            users = self.users_db.find_by_field("email", user_email)
            if not users:
                print(f"User {user_email} not found, cannot send notification")
                return None
            
            # Create notification
            notification = {
                "id": str(uuid.uuid4()),
                "user_email": user_email,
                "title": title,
                "message": message,
                "type": notification_type,
                "draw_id": draw_id,
                "draw_title": draw_title,
                "amount": amount,
                "read": False,
                "created_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss"),
                "expires_at": (datetime.now() + timedelta(days=expires_in_days)).strftime("%d/%m/%YT%Hh:%Mm:%Ss"),
                "action_url": action_url or (f"/confirm?draw={draw_id}" if draw_id else None),
                "action_text": action_text
            }
            
            self.notifications_db.insert(notification)
            print(f"Notification created for {user_email}: {title}")
            return notification
        except Exception as e:
            print(f"Error creating notification: {str(e)}")
            return None
    
    def broadcast_to_all_users(self, title: str, message: str, notification_type: str,
                               draw_id: Optional[str] = None, draw_title: Optional[str] = None,
                               amount: Optional[int] = None, action_url: Optional[str] = None,
                               action_text: str = "View Draw", exclude_admins: bool = False):
        """Send notification to all users"""
        try:
            all_users = self.users_db.read_all()
            notifications_sent = 0
            
            for user in all_users:
                # Skip admins if exclude_admins is True
                if exclude_admins and user.get("user_status") == "staff":
                    continue
                
                self.create_notification(
                    user_email=user["email"],
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    draw_id=draw_id,
                    draw_title=draw_title,
                    amount=amount,
                    action_url=action_url,
                    action_text=action_text
                )
                notifications_sent += 1
            
            print(f"Broadcast notification sent to {notifications_sent} users")
            return notifications_sent
        except Exception as e:
            print(f"Error broadcasting notification: {str(e)}")
            return 0
    
    def get_user_notifications(self, user_email: str, unread_only: bool = False, limit: int = 50):
        """Get notifications for a specific user"""
        try:
            all_notifications = self.notifications_db.read_all()
            user_notifications = [n for n in all_notifications if n.get("user_email") == user_email]
            
            # Filter out expired notifications
            current_time = datetime.now()
            active_notifications = []
            for n in user_notifications:
                try:
                    expires_at = datetime.strptime(n["expires_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                    if current_time <= expires_at:
                        active_notifications.append(n)
                except:
                    # If expiry date is invalid, keep the notification
                    active_notifications.append(n)
            
            # Sort by date (newest first)
            active_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Filter unread if requested
            if unread_only:
                active_notifications = [n for n in active_notifications if not n.get("read", False)]
            
            # Apply limit
            return active_notifications[:limit]
        except Exception as e:
            print(f"Error getting user notifications: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: str, user_email: str) -> bool:
        """Mark a notification as read"""
        try:
            notification = self.notifications_db.find_by_id(notification_id)
            if not notification or notification.get("user_email") != user_email:
                return False
            
            self.notifications_db.update(notification_id, {"read": True})
            return True
        except Exception as e:
            print(f"Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_email: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            notifications = self.get_user_notifications(user_email, unread_only=True)
            count = 0
            for n in notifications:
                if self.mark_as_read(n["id"], user_email):
                    count += 1
            return count
        except Exception as e:
            print(f"Error marking all as read: {str(e)}")
            return 0
    
    def delete_old_notifications(self, days: int = 30):
        """Delete notifications older than specified days"""
        try:
            all_notifications = self.notifications_db.read_all()
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=days)
            
            to_keep = []
            deleted = 0
            
            for n in all_notifications:
                try:
                    created_at = datetime.strptime(n["created_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                    if created_at > cutoff_time:
                        to_keep.append(n)
                    else:
                        deleted += 1
                except:
                    # If date is invalid, keep it
                    to_keep.append(n)
            
            self.notifications_db.write_all(to_keep)
            print(f"Deleted {deleted} old notifications")
            return deleted
        except Exception as e:
            print(f"Error deleting old notifications: {str(e)}")
            return 0

# Create global instance
notification_service = NotificationService()