import random
from api.services.google_sheets_db import sheets_db_manager
from api.config import Config
from datetime import datetime

def run_draw(draw_id: str):
    # Get all entries for this draw
    all_entries = sheets_db_manager.user_draws_db.read_all()
    draw_entries = [e for e in all_entries 
                    if e.get("lucky_draw_id") == draw_id 
                    and e.get("status") == "open"]
    
    if not draw_entries:
        return None
    
    # Get draw details
    draw = sheets_db_manager.draws_db.find_by_id(draw_id)
    draw_title = draw.get("title", "Lucky Draw") if draw else "Lucky Draw"
    
    # Select winner
    winner = random.choice(draw_entries)
    
    # Get winner's name from users database
    user_info = sheets_db_manager.users_db.find_by_field("email", winner["user_email"])
    if user_info and len(user_info) > 0:
        winner_name = user_info[0].get("name", "Anonymous User")
    else:
        winner_name = "Anonymous User"
    
    # Update all entries
    for i, entry in enumerate(all_entries):
        if entry.get("lucky_draw_id") == draw_id:
            if entry.get("user_email") == winner["user_email"]:
                all_entries[i]["status"] = "win"
                all_entries[i]["user_name"] = winner_name
                all_entries[i]["winner_name"] = winner_name
            else:
                all_entries[i]["status"] = "loss"
    
    # Save updates to Google Sheets
    sheets_db_manager.user_draws_db.write_all(all_entries)
    
    # ========== تمام شرکاء کو نتیجہ کا نوٹیفکیشن ==========
    from api.services.notification_service import notification_service
    
    # Winner ko notification
    notification_service.create_notification(
        user_email=winner["user_email"],
        title="🏆 Congratulations! You Won!",
        message=f"You won Rs. {draw['winner_get']} in {draw_title}!",
        notification_type="draw_result",
        draw_id=draw_id,
        draw_title=draw_title,
        amount=draw['winner_get'],
        action_url="/winner",
        action_text="View Results"
    )
    
    # Losers ko notification
    for entry in draw_entries:
        if entry["user_email"] != winner["user_email"]:
            notification_service.create_notification(
                user_email=entry["user_email"],
                title="😢 Draw Result",
                message=f"The winner for {draw_title} has been announced. Better luck next time!",
                notification_type="draw_result",
                draw_id=draw_id,
                draw_title=draw_title,
                action_url="/winner",
                action_text="View Results"
            )
    
    # Add name to winner object before returning
    winner["user_name"] = winner_name
    winner["winner_name"] = winner_name
        
    # ========== Email بھیجیں تمام شرکاء کو ==========
    from api.utils.email import EmailService
    email_service = EmailService()
    
    # Winner کو email
    import asyncio
    asyncio.create_task(email_service.send_draw_result_notification(
        to_email=winner["user_email"],
        user_name=winner_name,
        draw_title=draw_title,
        is_winner=True,
        prize_amount=draw['winner_get']
    ))
    
    # Losers کو email
    for entry in draw_entries:
        if entry["user_email"] != winner["user_email"]:
            user_info = sheets_db_manager.users_db.find_by_field("email", entry["user_email"])
            user_name = user_info[0].get("name", "User") if user_info else "User"
            asyncio.create_task(email_service.send_draw_result_notification(
                to_email=entry["user_email"],
                user_name=user_name,
                draw_title=draw_title,
                is_winner=False
            ))
    
    return winner