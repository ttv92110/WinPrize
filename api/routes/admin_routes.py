from fastapi import APIRouter, HTTPException, Request
from api.utils.email import EmailService
from api.services.notification_service import notification_service
from api.services.draw_engine import run_draw
from api.services.google_sheets_db import sheets_db_manager
from api.config import Config
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/admin")

# ========== صرف Google Sheets استعمال کریں ==========
lucky_db = sheets_db_manager.draws_db
users_db = sheets_db_manager.users_db
user_draws_db = sheets_db_manager.user_draws_db
# ====================================================

def is_admin(email: str) -> bool: 
    if not email:
        return False
    users = users_db.find_by_field("email", email)
    return users and len(users) > 0 and users[0].get("user_status") == "staff"

@router.get("/draws")
async def get_all_draws_admin(request: Request): 
    try:
        user_email = request.query_params.get("email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draws = lucky_db.read_all()
        
        # Check for draws that need attention (awaiting status)
        current_time = datetime.now()
        for draw in draws:
            if draw.get("status") == "open" and draw.get("closed_at"):
                try:
                    closed_time = datetime.strptime(draw["closed_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                    if current_time > closed_time:
                        if draw.get("auto_complete", True):
                            draw["status"] = "awaiting"
                            lucky_db.update(draw["id"], {"status": "awaiting"})
                except:
                    pass
        
        return draws
    except Exception as e:
        print(f"Error in get_all_draws_admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/verify-admin")
async def verify_admin(request: Request):
    """Verify if a user is admin"""
    try:
        user_email = request.query_params.get("email")
        
        if not user_email:
            return {"isAdmin": False, "reason": "No email provided"}
        
        users = users_db.find_by_field("email", user_email)
        is_admin = users and len(users) > 0 and users[0].get("user_status") == "staff"
        
        return {"isAdmin": is_admin}
    except Exception as e:
        print(f"Error in verify_admin: {str(e)}")
        return {"isAdmin": False, "reason": str(e)}
    
@router.post("/create-draw")
async def create_draw(request: Request):
    """Create a new lucky draw"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        draw_data = {k: v for k, v in body.items() if k != "user_email"}
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Generate dates
        created_at = datetime.now()
        time_interval = draw_data.get("time_interval", "day")
        
        # Calculate closed_at based on interval
        interval_map = {
            "1hour": timedelta(hours=1),
            "12hours": timedelta(hours=12),
            "day": timedelta(days=1),
            "10days": timedelta(days=10),
            "15days": timedelta(days=15),
            "month": timedelta(days=30),
            "3months": timedelta(days=90),
            "6months": timedelta(days=180),
            "1year": timedelta(days=365)
        }
        closed_at = created_at + interval_map.get(time_interval, timedelta(days=1))
        
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        # Get all draws to determine next ID
        all_draws = lucky_db.read_all()
        next_id = len(all_draws) + 1
        
        draw_data["id"] = f"lucky_{next_id:05d}"
        draw_data["status"] = "open"
        draw_data["created_at"] = created_at.strftime(date_format)
        draw_data["closed_at"] = closed_at.strftime(date_format)
        draw_data["visible"] = draw_data.get("visible", True)
        draw_data["auto_complete"] = draw_data.get("auto_complete", True)
        
        # Add optional fields with defaults
        if "title" not in draw_data:
            interval_display = {
                "1hour": "1 Hour",
                "12hours": "12 Hours",
                "day": "Daily",
                "10days": "10 Days",
                "15days": "15 Days",
                "month": "Monthly",
                "3months": "3 Months",
                "6months": "6 Months",
                "1year": "1 Year"
            }.get(time_interval, time_interval.capitalize())
            
            draw_data["title"] = f"{interval_display} Draw #{next_id}"
        
        if "description" not in draw_data:
            draw_data["description"] = f"Win Rs. {draw_data['winner_get']} with just Rs. {draw_data['user_pay']}"
        
        lucky_db.insert(draw_data)
        
        # Send notifications to all users 
        
        interval_display = {
            "1hour": "1 Hour",
            "12hours": "12 Hours", 
            "day": "Daily",
            "10days": "10 Days",
            "15days": "15 Days",
            "month": "Monthly",
            "3months": "3 Months",
            "6months": "6 Months",
            "1year": "1 Year"
        }.get(time_interval, time_interval)
        
        notification_service.broadcast_to_all_users(
            title="🎉 New Lucky Draw Added!",
            message=f"New {interval_display} Draw: Win Rs. {draw_data['winner_get']} with just Rs. {draw_data['user_pay']}!",
            notification_type="new_draw",
            draw_id=draw_data["id"],
            draw_title=draw_data["title"],
            amount=draw_data["winner_get"],
            action_url=f"/confirm?draw={draw_data['id']}",
            action_text="Join Now",
            exclude_admins=True
        )
        
    # ========== Email بھیجیں تمام صارفین کو ========== 
        email_service = EmailService()
        
        all_users = users_db.read_all()
        for user in all_users:
            if user.get("user_status") != "staff":  # Admin کو نہ بھیجیں
                import asyncio
                asyncio.create_task(email_service.send_new_draw_notification(
                    to_email=user["email"],
                    user_name=user["name"],
                    draw_title=draw_data["title"],
                    draw_prize=draw_data["winner_get"],
                    draw_fee=draw_data["user_pay"]
                ))
        
        return {"message": "Draw created successfully", "success": True, "draw": draw_data}
    except Exception as e:
        print(f"Error in create_draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-draw/{draw_id}")
async def update_draw(draw_id: str, request: Request):
    """Update an existing lucky draw"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        update_data = {k: v for k, v in body.items() if k not in ["user_email", "id"]}
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draw = lucky_db.find_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        # Update the draw
        updated_draw = lucky_db.update(draw_id, update_data)
        
        return {"success": True, "message": "Draw updated successfully", "draw": updated_draw}
    except Exception as e:
        print(f"Error in update_draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reopen-draw/{draw_id}")
async def reopen_draw(draw_id: str, request: Request):
    """Reopen a completed or awaiting draw"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draw = lucky_db.find_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        # Reopen the draw
        lucky_db.update(draw_id, {"status": "open"})
        
        return {"success": True, "message": "Draw reopened successfully"}
    except Exception as e:
        print(f"Error in reopen_draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-result/{draw_id}")
async def update_draw_result(draw_id: str, request: Request):
    """Admin manually updates draw result"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        winner_email = body.get("winner_email")
        notes = body.get("notes", "")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draw = lucky_db.find_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        # Get winner's name from users database
        user_info = users_db.find_by_field("email", winner_email)
        winner_name = "Anonymous User"
        if user_info and len(user_info) > 0:
            winner_name = user_info[0].get("name", "Anonymous User")
        
        # Get draw title
        draw_title = draw.get("title", "Lucky Draw")
        draw_prize = draw.get("winner_get", 0)
        
        # Update all entries for this draw
        all_entries = user_draws_db.read_all()
        updated = False
        participants_emails = []  # Store all participant emails for email sending
        
        for i, entry in enumerate(all_entries):
            if entry.get("lucky_draw_id") == draw_id:
                participants_emails.append(entry.get("user_email"))
                if entry.get("user_email") == winner_email:
                    all_entries[i]["status"] = "win"
                    all_entries[i]["user_name"] = winner_name
                    all_entries[i]["winner_name"] = winner_name
                    updated = True
                else:
                    all_entries[i]["status"] = "loss"
        
        if updated:
            user_draws_db.write_all(all_entries)
            lucky_db.update(draw_id, {"status": "completed"})
            
            # ========== Send emails to all participants ==========
            from api.utils.email import EmailService
            import asyncio
            
            email_service = EmailService()
            
            # Helper function to send emails
            def send_emails_sync():
                # Create new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Send email to winner
                    loop.run_until_complete(
                        email_service.send_draw_result_notification(
                            to_email=winner_email,
                            user_name=winner_name,
                            draw_title=draw_title,
                            is_winner=True,
                            prize_amount=draw_prize
                        )
                    )
                    print(f"✅ Winner email sent to {winner_email}")
                    
                    # Send emails to losers
                    for entry in all_entries:
                        if entry.get("lucky_draw_id") == draw_id:
                            if entry.get("user_email") != winner_email:
                                loser_email = entry.get("user_email")
                                loser_info = users_db.find_by_field("email", loser_email)
                                loser_name = loser_info[0].get("name", "User") if loser_info else "User"
                                
                                loop.run_until_complete(
                                    email_service.send_draw_result_notification(
                                        to_email=loser_email,
                                        user_name=loser_name,
                                        draw_title=draw_title,
                                        is_winner=False,
                                        prize_amount=0
                                    )
                                )
                                print(f"✅ Loser email sent to {loser_email}")
                finally:
                    loop.close()
            
            # Run email sending in background thread
            import threading
            email_thread = threading.Thread(target=send_emails_sync)
            email_thread.start()
            # ====================================================
            
            return {
                "success": True, 
                "message": "Draw result updated", 
                "winner": {
                    "email": winner_email, 
                    "name": winner_name,
                    "user_name": winner_name
                }
            }
        else:
            return {"success": False, "message": "Winner email not found in participants"}
    except Exception as e:
        print(f"Error in update_draw_result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-draw/{draw_id}")
async def run_draw_endpoint(draw_id: str, request: Request):
    """Run the draw to select a winner"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draw = lucky_db.find_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        if draw["status"] not in ["open", "awaiting"]:
            raise HTTPException(status_code=400, detail="Draw cannot be run")
        
        # This function already sends emails
        winner = run_draw(draw_id)
        
        if winner:
            lucky_db.update(draw_id, {"status": "completed"})
            return {
                "winner": {
                    "user_email": winner["user_email"],
                    "user_name": winner.get("user_name", winner.get("winner_name", "Anonymous User")),
                    "lucky_draw_id": winner["lucky_draw_id"]
                }, 
                "success": True
            }
        
        lucky_db.update(draw_id, {"status": "awaiting"})
        return {"message": "No participants for this draw", "success": False, "status": "awaiting"}
    except Exception as e:
        print(f"Error in run_draw_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
     
@router.delete("/delete-draw/{draw_id}")
async def delete_draw(draw_id: str, request: Request):
    """Delete a draw (soft delete by setting visible=False)"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        draw = lucky_db.find_by_id(draw_id)
        if not draw:
            raise HTTPException(status_code=404, detail="Draw not found")
        
        # Soft delete by setting visible to false
        lucky_db.update(draw_id, {"visible": False})
        
        return {"success": True, "message": "Draw deleted successfully"}
    except Exception as e:
        print(f"Error in delete_draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-payments")
async def get_pending_payments(request: Request):
    """Get all pending payments for admin"""
    try:
        user_email = request.query_params.get("email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Import here to avoid circular imports
        from api.routes.payment_routes import payments_db
        
        all_payments = payments_db.read_all()
        pending_payments = [p for p in all_payments if p.get("status") == "pending"]
        
        # Sort by date (newest first)
        pending_payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return pending_payments
    except Exception as e:
        print(f"Error getting pending payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
  
@router.post("/approve-payment/{payment_id}")
async def approve_payment(payment_id: str, request: Request):
    """Approve a payment and enroll user"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        from api.routes.draw_routes import user_draws_db
        
        # Get payment
        payment = payments_db.find_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Update payment status
        payment["status"] = "paid"
        payment["updated_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        payment["approved_by"] = user_email
        payments_db.update(payment_id, payment)
        
        # ========== SEND APPROVAL EMAIL (using asyncio.create_task) ==========
        from api.utils.email import EmailService
        import asyncio
        
        email_service = EmailService()
        
        # Get user name
        user_info = users_db.find_by_field("email", payment["user_email"])
        user_name = user_info[0].get("name", "User") if user_info else "User"
        
        print(f"📧 Sending approval email to: {payment['user_email']}")
        
        # Use asyncio.create_task instead of new event loop
        asyncio.create_task(
            email_service.send_payment_approval_email(
                to_email=payment["user_email"],
                user_name=user_name,
                draw_title=payment["lucky_draw_title"],
                amount=payment["amount"]
            )
        )
        print(f"✅ Approval email task created for {payment['user_email']}")
        # ======================================
        
        # Check if user already has an enrollment for this draw
        enrollments = user_draws_db.find_by_field("user_email", payment["user_email"])
        existing_enrollment = None
        for enrollment in enrollments:
            if enrollment.get("lucky_draw_id") == payment["lucky_draw_id"]:
                existing_enrollment = enrollment
                break
        
        if existing_enrollment:
            user_draws_db.update(existing_enrollment["id"], {"status": "open"})
        else:
            enrollment = {
                "id": str(uuid.uuid4()),
                "user_email": payment["user_email"],
                "user_pay": payment["amount"],
                "lucky_draw_id": payment["lucky_draw_id"],
                "status": "open",
                "joined_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
            }
            user_draws_db.insert(enrollment)
        
        return {"success": True, "message": "Payment approved successfully. User enrolled in draw."}
    except Exception as e:
        print(f"Error approving payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/reject-payment/{payment_id}")
async def reject_payment(payment_id: str, request: Request):
    """Reject a payment and remove user from draw completely"""
    try:
        body = await request.json()
        user_email = body.get("user_email")
        reason = body.get("reason", "Payment rejected by admin - Fake/Invalid transaction")
        
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        from api.routes.draw_routes import user_draws_db
        
        # Get payment
        payment = payments_db.find_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Update payment status
        payment["status"] = "cancel"
        payment["updated_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        payment["rejected_by"] = user_email
        payment["rejection_reason"] = reason
        payments_db.update(payment_id, payment)
        
        # ========== SEND REJECTION EMAIL ==========
        from api.utils.email import EmailService
        email_service = EmailService()
        
        # Get user name
        user_info = users_db.find_by_field("email", payment["user_email"])
        user_name = user_info[0].get("name", "User") if user_info else "User"
        
        print(f"📧 Sending rejection email to: {payment['user_email']}, Reason: {reason}")
        
        # Send email synchronously
        email_service.send_payment_rejection_email_sync(
            to_email=payment["user_email"],
            user_name=user_name,
            draw_title=payment["lucky_draw_title"],
            amount=payment["amount"],
            reason=reason
        )
        # ========================================
        
        # IMPORTANT: Delete user from draw completely (remove enrollment)
        enrollments = user_draws_db.read_all()
        updated_enrollments = []
        deleted = False
        
        for enrollment in enrollments:
            if not (enrollment.get("user_email") == payment["user_email"] 
                    and enrollment.get("lucky_draw_id") == payment["lucky_draw_id"]):
                updated_enrollments.append(enrollment)
            else:
                deleted = True
                print(f"Deleted enrollment for user {payment['user_email']} from draw {payment['lucky_draw_id']}")
        
        if deleted:
            user_draws_db.write_all(updated_enrollments)
        
        return {
            "success": True, 
            "message": "Payment rejected. User has been removed from the draw.",
            "user_removed": deleted
        }
    except Exception as e:
        print(f"Error rejecting payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ========== Admin: User Management ==========
@router.get("/users")
async def get_all_users_admin(request: Request):
    """Get all users (admin only)"""
    try:
        user_email = request.query_params.get("email")
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        all_users = users_db.read_all()
        # Remove passwords
        for user in all_users:
            if "password" in user:
                del user["password"]
        return all_users
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verifications")
async def get_all_verifications_admin(request: Request):
    """Get all email verifications (admin only)"""
    try:
        user_email = request.query_params.get("email")
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        verifications = sheets_db_manager.verifications_db.read_all()
        return verifications
    except Exception as e:
        print(f"Error getting verifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-draws")
async def get_all_user_draws_admin(request: Request):
    """Get all user enrollments (admin only)"""
    try:
        user_email = request.query_params.get("email")
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        user_draws = user_draws_db.read_all()
        return user_draws
    except Exception as e:
        print(f"Error getting user draws: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-stats")
async def get_payment_stats(request: Request):
    """Get payment statistics (admin only)"""
    try:
        user_email = request.query_params.get("email")
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        all_payments = payments_db.read_all()
        
        total_paid = 0
        total_pending = 0
        total_cancelled = 0
        total_amount = 0
        
        for p in all_payments:
            status = p.get("status")
            amount = p.get("amount", 0)
            if status == "paid":
                total_paid += 1
                total_amount += amount
            elif status == "pending":
                total_pending += 1
            elif status == "cancel":
                total_cancelled += 1
        
        return {
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_cancelled": total_cancelled,
            "total_amount": total_amount
        }
    except Exception as e:
        print(f"Error getting payment stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user/{user_id}")
async def update_user_by_admin(user_id: str, request: Request):
    """Update user details (status, name) - admin only"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        user = users_db.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        if "name" in body:
            user["name"] = body["name"]
        if "user_status" in body:
            user["user_status"] = body["user_status"]
        
        users_db.update(user_id, user)
        # Remove password from response
        if "password" in user:
            del user["password"]
        return {"success": True, "user": user}
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user/{user_id}")
async def delete_user_by_admin(user_id: str, request: Request):
    """Delete a user and associated data (admin only)"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        user = users_db.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        email = user["email"]
        
        # Delete user
        users_db.delete(user_id)
        
        # Delete related verifications
        verifications = sheets_db_manager.verifications_db.find_by_field("email", email)
        for v in verifications:
            sheets_db_manager.verifications_db.delete(v["id"])
        
        # Delete user draws
        user_draws = user_draws_db.find_by_field("user_email", email)
        for ud in user_draws:
            user_draws_db.delete(ud["id"])
        
        # Optionally delete payments (or just mark as orphaned)
        from api.routes.payment_routes import payments_db
        payments = payments_db.find_by_field("user_email", email)
        for p in payments:
            payments_db.delete(p["id"])
        
        return {"success": True, "message": "User and associated data deleted"}
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== Admin: Verification Management ==========
@router.put("/verification/{verification_id}")
async def update_verification(verification_id: str, request: Request):
    """Update verification (PIN, verified status) - admin only"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        verification = sheets_db_manager.verifications_db.find_by_id(verification_id)
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Update allowed fields
        if "pin" in body:
            verification["pin"] = str(body["pin"]).zfill(6)
        if "verified" in body:
            verification["verified"] = body["verified"] in [True, "true", "True", 1]
        
        sheets_db_manager.verifications_db.update(verification_id, verification)
        return {"success": True, "verification": verification}
    except Exception as e:
        print(f"Error updating verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/verification/{verification_id}")
async def delete_verification(verification_id: str, request: Request):
    """Delete a verification record - admin only"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        verification = sheets_db_manager.verifications_db.find_by_id(verification_id)
        if not verification:
            # Already deleted, treat as success
            return {"success": True, "message": "Verification already deleted"}
        
        sheets_db_manager.verifications_db.delete(verification_id)
        return {"success": True, "message": "Verification deleted"}
    except Exception as e:
        print(f"Error deleting verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ========== Admin: User Draw Management ==========
@router.get("/draws-list")
async def get_all_draws_list(request: Request):
    """Get list of all draw IDs and titles (for dropdown) - admin only"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        all_draws = lucky_db.read_all()
        draw_list = [{"id": d["id"], "title": d.get("title", d["id"])} for d in all_draws]
        return draw_list
    except Exception as e:
        print(f"Error getting draws list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user-draw/{draw_id}")
async def update_user_draw(draw_id: str, request: Request):
    """Update user draw (status, lucky_draw_id) - admin only"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        enrollment = user_draws_db.find_by_id(draw_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        # Update allowed fields
        if "status" in body:
            enrollment["status"] = body["status"]
        if "lucky_draw_id" in body:
            # Validate that the target draw exists
            target_draw = lucky_db.find_by_id(body["lucky_draw_id"])
            if not target_draw:
                raise HTTPException(status_code=400, detail="Target draw not found")
            enrollment["lucky_draw_id"] = body["lucky_draw_id"]
        
        user_draws_db.update(draw_id, enrollment)
        return {"success": True, "enrollment": enrollment}
    except Exception as e:
        print(f"Error updating user draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user-draw/{draw_id}")
async def delete_user_draw(draw_id: str, request: Request):
    """Delete a user draw enrollment - admin only"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        enrollment = user_draws_db.find_by_id(draw_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        user_draws_db.delete(draw_id)
        return {"success": True, "message": "Enrollment deleted"}
    except Exception as e:
        print(f"Error deleting user draw: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/user-verification/{email}")
async def update_user_verification(email: str, request: Request):
    """Update user's email verification status (admin only)"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        verified = body.get("verified")
        if verified is None:
            raise HTTPException(status_code=400, detail="Verified status required")
        
        # Find verification record for this email
        verifications = sheets_db_manager.verifications_db.find_by_field("email", email)
        if not verifications:
            raise HTTPException(status_code=404, detail="No verification record found for this user")
        
        # Update the most recent verification record
        verification = sorted(verifications, key=lambda x: x.get("created_at", ""), reverse=True)[0]
        verification["verified"] = verified
        sheets_db_manager.verifications_db.update(verification["id"], verification)
        
        return {"success": True, "message": f"Verification status updated to {verified}"}
    except Exception as e:
        print(f"Error updating user verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== Admin: Payment Management ==========
@router.get("/all-payments")
async def get_all_payments_admin(request: Request):
    """Get all payments (admin only)"""
    try:
        user_email = request.query_params.get("email")
        if not user_email or not is_admin(user_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        all_payments = payments_db.read_all()
        # Sort by date descending
        all_payments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_payments
    except Exception as e:
        print(f"Error getting all payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/payment/{payment_id}")
async def update_payment_by_admin(payment_id: str, request: Request):
    """Update payment status or notes (admin only)"""
    try:
        body = await request.json()
        admin_email = body.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        payment = payments_db.find_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Update allowed fields
        if "status" in body:
            payment["status"] = body["status"]
        if "notes" in body:
            payment["notes"] = body["notes"]
        payment["updated_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
        
        payments_db.update(payment_id, payment)
        return {"success": True, "payment": payment}
    except Exception as e:
        print(f"Error updating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/payment/{payment_id}")
async def delete_payment_by_admin(payment_id: str, request: Request):
    """Delete a payment record (admin only)"""
    try:
        admin_email = request.query_params.get("admin_email")
        if not admin_email or not is_admin(admin_email):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from api.routes.payment_routes import payments_db
        payment = payments_db.find_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payments_db.delete(payment_id)
        return {"success": True, "message": "Payment deleted"}
    except Exception as e:
        print(f"Error deleting payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    