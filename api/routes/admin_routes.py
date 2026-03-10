from fastapi import APIRouter, HTTPException, Request
from api.services.draw_engine import run_draw
from api.services.file_db import FileDB
from api.config import Config
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/admin")
lucky_db = FileDB(str(Config.LUCKY_DRAWS_FILE))
users_db = FileDB(str(Config.USERS_FILE))
user_draws_db = FileDB(str(Config.USER_DRAWS_FILE))

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
                        # Auto-mark as awaiting for admin attention
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
        
        # ========== نیا اپڈیٹڈ کوڈ ==========
        # Calculate closed_at based on interval with appropriate result time
        if time_interval == "1hour":
            closed_at = created_at + timedelta(hours=1)
            # Last 10 minutes will be result time (automatically handled)
        elif time_interval == "12hours":
            closed_at = created_at + timedelta(hours=12)
            # Last 1 hour will be result time
        elif time_interval == "day":
            closed_at = created_at + timedelta(days=1)
            # Last hour will be result time
        elif time_interval == "10days":
            closed_at = created_at + timedelta(days=10)
            # Last day will be result day
        elif time_interval == "15days":
            closed_at = created_at + timedelta(days=15)
            # Last day will be result day
        elif time_interval == "month":
            closed_at = created_at + timedelta(days=30)
            # Last day will be result day
        elif time_interval == "3months":
            closed_at = created_at + timedelta(days=90)
            # Last day will be result day
        elif time_interval == "6months":
            closed_at = created_at + timedelta(days=180)
            # Last day will be result day
        elif time_interval == "1year":
            closed_at = created_at + timedelta(days=365)
            # Last month will be result month
        else:
            # Default to 1 day if unknown
            closed_at = created_at + timedelta(days=1)
        # ====================================
        
        # Format dates
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
            # Format title based on interval
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
        
        # Update all entries for this draw
        all_entries = user_draws_db.read_all()
        updated = False
        for i, entry in enumerate(all_entries):
            if entry.get("lucky_draw_id") == draw_id:
                if entry.get("user_email") == winner_email:
                    all_entries[i]["status"] = "win"
                    all_entries[i]["user_name"] = winner_name  # Store name
                    all_entries[i]["winner_name"] = winner_name  # Store as winner_name
                    updated = True
                else:
                    all_entries[i]["status"] = "loss"
        
        if updated:
            user_draws_db.write_all(all_entries)
            lucky_db.update(draw_id, {"status": "completed"})
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
        
        winner = run_draw(draw_id)
        
        if winner:
            lucky_db.update(draw_id, {"status": "completed"})
            # Make sure winner name is included
            return {
                "winner": {
                    "user_email": winner["user_email"],
                    "user_name": winner.get("user_name", winner.get("winner_name", "Anonymous User")),
                    "lucky_draw_id": winner["lucky_draw_id"]
                }, 
                "success": True
            }
        
        # No participants - set to awaiting
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
        
        # Check if user already has an enrollment for this draw
        enrollments = user_draws_db.find_by_field("user_email", payment["user_email"])
        existing_enrollment = None
        for enrollment in enrollments:
            if enrollment.get("lucky_draw_id") == payment["lucky_draw_id"]:
                existing_enrollment = enrollment
                break
        
        if existing_enrollment:
            # Update existing enrollment to open
            user_draws_db.update(existing_enrollment["id"], {"status": "open"})
        else:
            # Create new enrollment
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
        
        # IMPORTANT: Delete user from draw completely (remove enrollment)
        enrollments = user_draws_db.read_all()
        updated_enrollments = []
        deleted = False
        
        for enrollment in enrollments:
            # Keep all enrollments except the one for this rejected payment
            if not (enrollment.get("user_email") == payment["user_email"] 
                    and enrollment.get("lucky_draw_id") == payment["lucky_draw_id"]):
                updated_enrollments.append(enrollment)
            else:
                deleted = True
                print(f"Deleted enrollment for user {payment['user_email']} from draw {payment['lucky_draw_id']}")
        
        if deleted:
            # Write back the filtered list (without the rejected user)
            user_draws_db.write_all(updated_enrollments)
        
        return {
            "success": True, 
            "message": "Payment rejected. User has been removed from the draw.",
            "user_removed": deleted
        }
    except Exception as e:
        print(f"Error rejecting payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))