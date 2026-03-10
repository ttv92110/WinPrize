import random
from api.services.file_db import FileDB
from api.config import Config

user_draws_db = FileDB(str(Config.USER_DRAWS_FILE))
lucky_db = FileDB(str(Config.LUCKY_DRAWS_FILE))
users_db = FileDB(str(Config.USERS_FILE))

def run_draw(draw_id: str):
    # Get all entries for this draw
    all_entries = user_draws_db.read_all()
    draw_entries = [e for e in all_entries 
                    if e.get("lucky_draw_id") == draw_id 
                    and e.get("status") == "open"]
    
    if not draw_entries:
        return None
    
    # Select winner
    winner = random.choice(draw_entries)
    
    # Get winner's name from users database
    user_info = users_db.find_by_field("email", winner["user_email"])
    if user_info and len(user_info) > 0:
        winner_name = user_info[0].get("name", "Anonymous User")
    else:
        winner_name = "Anonymous User"
    
    # Update all entries
    for i, entry in enumerate(all_entries):
        if entry.get("lucky_draw_id") == draw_id:
            if entry.get("user_email") == winner["user_email"]:
                all_entries[i]["status"] = "win"
                all_entries[i]["user_name"] = winner_name  # Store name in the entry
                all_entries[i]["winner_name"] = winner_name  # Also store as winner_name for clarity
            else:
                all_entries[i]["status"] = "loss"
    
    # Save updates
    user_draws_db.write_all(all_entries)
    
    # Add name to winner object before returning
    winner["user_name"] = winner_name
    winner["winner_name"] = winner_name
    
    return winner
