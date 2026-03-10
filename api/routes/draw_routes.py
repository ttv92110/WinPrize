from fastapi import APIRouter, HTTPException
from api.schemas.draw_schema import LuckyDrawResponse
from api.schemas.enrollment_schema import UserDrawCreate, UserDrawResponse
from api.services.file_db import FileDB
from api.config import Config
from typing import List
from datetime import datetime

router = APIRouter(prefix="/draws")
lucky_db = FileDB(str(Config.LUCKY_DRAWS_FILE))
users_db = FileDB(str(Config.USERS_FILE))
user_draws_db = FileDB(str(Config.USER_DRAWS_FILE))

@router.get("/", response_model=List[LuckyDrawResponse])
async def get_draws():
    draws = lucky_db.read_all()
    current_time = datetime.now()
    
    # Check and update draw status based on closed_at
    for draw in draws:
        if draw.get("status") == "open" and draw.get("closed_at"):
            try:
                closed_time = datetime.strptime(draw["closed_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
                if current_time > closed_time:
                    # Set to awaiting instead of completed
                    draw["status"] = "awaiting"
                    lucky_db.update(draw["id"], {"status": "awaiting"})
            except:
                pass
    
    # Only return visible draws
    return [d for d in draws if d.get("visible", False)]

@router.get("/{draw_id}")
async def get_draw(draw_id: str):
    draw = lucky_db.find_by_id(draw_id)
    if not draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    return draw

@router.get("/participants/count/{draw_id}")
async def get_participants_count(draw_id: str):
    """Get number of participants in a draw"""
    all_entries = user_draws_db.read_all()
    count = len([e for e in all_entries if e.get("lucky_draw_id") == draw_id])
    return {"draw_id": draw_id, "participants": count}

@router.get("/winners/list")
async def get_winners_list():
    """Get all winners with draw details"""
    all_draws = user_draws_db.read_all()
    winners = [d for d in all_draws if d.get("status") == "win"]
    
    # Enhance with draw information and user names
    result = []
    for winner in winners:
        draw = lucky_db.find_by_id(winner["lucky_draw_id"])
        if draw:
            # Make sure winner has name field
            winner_name = winner.get("user_name") or winner.get("winner_name")
            
            # If still no name, try to get from users DB
            if not winner_name or winner_name == "Anonymous User":
                user_info = users_db.find_by_field("email", winner["user_email"])
                if user_info and len(user_info) > 0:
                    winner_name = user_info[0].get("name", "Anonymous User")
                else:
                    winner_name = "Anonymous User"
            
            # Ensure winner object has name
            winner["user_name"] = winner_name
            winner["winner_name"] = winner_name
            
            result.append({
                "winner": winner,
                "draw": draw
            })
    return result

@router.get("/user/{email}")
async def get_user_draws(email: str):
    """Get all draws a user has participated in with their status"""
    all_entries = user_draws_db.read_all()
    user_entries = [e for e in all_entries if e.get("user_email") == email]
    
    # Enhance with draw details
    result = []
    for entry in user_entries:
        draw = lucky_db.find_by_id(entry["lucky_draw_id"])
        if draw:
            # Make sure winner name is included if this entry is a winner
            if entry.get("status") == "win":
                # Get winner name from entry or fetch from users DB
                winner_name = entry.get("user_name") or entry.get("winner_name")
                if not winner_name or winner_name == "Anonymous User":
                    user_info = users_db.find_by_field("email", entry["user_email"])
                    if user_info and len(user_info) > 0:
                        winner_name = user_info[0].get("name", "Anonymous User")
                        entry["user_name"] = winner_name
                        entry["winner_name"] = winner_name
            
            result.append({
                "draw": draw,
                "participation": entry
            })
    return result

@router.post("/join")
async def join_draw(entry: UserDrawCreate):
    # Check if draw exists and is open
    draw = lucky_db.find_by_id(entry.lucky_draw_id)
    if not draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    
    if draw["status"] != "open":
        raise HTTPException(status_code=400, detail="Draw is not open")
    
    # Check if user already joined this draw
    all_entries = user_draws_db.read_all()
    existing = [e for e in all_entries 
                if e.get("user_email") == entry.user_email 
                and e.get("lucky_draw_id") == entry.lucky_draw_id]
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already joined this draw")
    
    # Check max participants if set
    if draw.get("max_participants"):
        current_count = len([e for e in all_entries if e.get("lucky_draw_id") == entry.lucky_draw_id])
        if current_count >= draw["max_participants"]:
            raise HTTPException(status_code=400, detail="Draw is full")
    
    # Create enrollment
    enrollment = entry.dict()
    enrollment["status"] = "open"
    enrollment["joined_at"] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
    user_draws_db.insert(enrollment)
    
    return {"message": "Successfully enrolled in draw", "success": True}

@router.get("/time-left/{draw_id}")
async def get_time_left(draw_id: str):
    """Get time left for a draw"""
    draw = lucky_db.find_by_id(draw_id)
    if not draw or not draw.get("closed_at"):
        return {"time_left": "Unknown"}
    
    try:
        closed_time = datetime.strptime(draw["closed_at"], "%d/%m/%YT%Hh:%Mm:%Ss")
        current_time = datetime.now()
        
        if current_time > closed_time:
            return {"time_left": "Ended", "status": draw.get("status", "ended")}
        
        diff = closed_time - current_time
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        # ========== نیا اپڈیٹڈ کوڈ ==========
        # Get time interval for better display
        time_interval = draw.get("time_interval", "")
        
        # Check if we're in the result window
        result_window = False
        result_message = ""
        
        if time_interval == "1hour" and minutes <= 10:
            result_window = True
            result_message = "Result in next 10 minutes!"
        elif time_interval == "12hours" and hours <= 1:
            result_window = True
            result_message = "Result in next hour!"
        elif time_interval == "day" and hours <= 1:
            result_window = True
            result_message = "Result in next hour!"
        elif time_interval in ["10days", "15days", "month"] and days <= 1:
            result_window = True
            result_message = "Result tomorrow!"
        elif time_interval in ["3months", "6months"] and days <= 1:
            result_window = True
            result_message = "Result tomorrow!"
        elif time_interval == "1year" and days <= 30:
            result_window = True
            result_message = "Result next month!"
        # ====================================
        
        if days > 0:
            return {
                "time_left": f"{days}d {hours}h", 
                "detailed": f"{days} days, {hours} hours",
                "result_window": result_window,
                "result_message": result_message
            }
        elif hours > 0:
            return {
                "time_left": f"{hours}h {minutes}m", 
                "detailed": f"{hours} hours, {minutes} minutes",
                "result_window": result_window,
                "result_message": result_message
            }
        else:
            return {
                "time_left": f"{minutes}m", 
                "detailed": f"{minutes} minutes",
                "result_window": result_window,
                "result_message": result_message
            }
    except:
        return {"time_left": "Invalid date"}

@router.get("/check/joined/{email}/{draw_id}")
async def check_user_joined(email: str, draw_id: str):
    """Check if user has already joined a specific draw"""
    all_entries = user_draws_db.read_all()
    joined = any(e for e in all_entries 
                if e.get("user_email") == email 
                and e.get("lucky_draw_id") == draw_id)
    return {"joined": joined}
 