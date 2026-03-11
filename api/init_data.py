import json
import os
from pathlib import Path 
from datetime import datetime, timedelta

def init_data_files(): 
    data_dir = Path(os.getenv("DATA_DIR", "/tmp/data"))
    data_dir.mkdir(exist_ok=True, parents=True)
     
    users_file = data_dir / "users.json"
    if not users_file.exists() or users_file.stat().st_size == 0:
        sample_users = [
            {
                "name": "Admin User",
                "email": "ttv92110@gmail.com",
                "password": "admin@2020",  # In production, hash this
                "user_status": "staff",
                "id": "55f124a3-b12c-4289-90a3-8a592e411ac7",
                "email_verified": True,
                "verified_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
            }
        ]
        with open(users_file, 'w') as f:
            json.dump(sample_users, f, indent=4)
        print(f"✅ Initialized {users_file} with sample admin user")
    else:
        print(f"✅ {users_file} already exists")
     
    email_verifications_file = data_dir / "email_verifications.json"
    if not email_verifications_file.exists() or email_verifications_file.stat().st_size == 0:
        # Create timestamps
        now = datetime.now()
        expires = now + timedelta(minutes=20)
        verified_at = now + timedelta(minutes=1)
        
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        
        sample_verifications = [
            {
                "id": "77f124a3-d12c-6289-a2a3-ac7046333ce9",
                "email": "ttv92110@gmail.com",
                "name": "Admin User",
                "password": "admin@2020",
                "pin": "600026",
                "created_at": now.strftime(date_format),
                "expires_at": expires.strftime(date_format),
                "verified": True,
                "attempts": 0,
                "user_status": "staff",
                "verified_at": verified_at.strftime(date_format)
            }
        ]
        with open(email_verifications_file, 'w') as f:
            json.dump(sample_verifications, f, indent=4)
        print(f"✅ Initialized {email_verifications_file} with sample verifications")
    else:
        print(f"✅ {email_verifications_file} already exists")
    
    # Initialize user_draws.json
    user_draws_file = data_dir / "user_draws.json"
    if not user_draws_file.exists() or user_draws_file.stat().st_size == 0:
        with open(user_draws_file, 'w') as f:
            json.dump([], f, indent=4)
        print(f"✅ Initialized {user_draws_file}")
    else:
        print(f"✅ {user_draws_file} already exists")
    
    # Initialize payments.json
    payments_file = data_dir / "payments.json"
    if not payments_file.exists() or payments_file.stat().st_size == 0:
        with open(payments_file, 'w') as f:
            json.dump([], f, indent=4)
        print(f"✅ Initialized {payments_file}")
    else:
        print(f"✅ {payments_file} already exists")
    
    # Initialize password_resets.json
    password_resets_file = data_dir / "password_resets.json"
    if not password_resets_file.exists() or password_resets_file.stat().st_size == 0:
        with open(password_resets_file, 'w') as f:
            json.dump([], f, indent=4)
        print(f"✅ Initialized {password_resets_file}")
    else:
        print(f"✅ {password_resets_file} already exists")
    
    # Initialize lucky_draws.json with sample data if empty
    lucky_draws_file = data_dir / "lucky_draws.json"
    if not lucky_draws_file.exists() or lucky_draws_file.stat().st_size == 0:
        now = datetime.now() 
        expires = now + timedelta(days=1)
        date_format = "%d/%m/%YT%Hh:%Mm:%Ss"
        sample_draws = [
            # {
            #     "id": "lucky_00001",
            #     "user_pay": 1,
            #     "time_interval": "day",
            #     "winner_get": 100,
            #     "created_at": now.strftime(date_format),
            #     "closed_at": expires.strftime(date_format),
            #     "status": "open",
            #     "visible": True,
            #     "title": "Daily Draw #1",
            #     "description": "Win Rs. 100 with just Rs. 1",
            #     "auto_complete": True
            # }
        ]
        with open(lucky_draws_file, 'w') as f:
            json.dump(sample_draws, f, indent=4)
        print(f"✅ Initialized {lucky_draws_file} with sample data")
    else:
        print(f"✅ {lucky_draws_file} already exists")
    
    print("\n🎉 All data files initialized successfully!") 
# Run initialization when module is imported
if __name__ == "__main__":
    pass
    init_data_files()
else:
    pass
    # Auto-run when imported
    init_data_files()