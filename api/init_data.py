import json
import os
from pathlib import Path 
from datetime import datetime, timedelta

def init_data_files(): 
    data_dir = Path(os.getenv("DATA_DIR", "/tmp/data"))
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Note: یہ فائلیں اب صرف backup کے لیے ہیں۔ اصل ڈیٹا Google Sheets میں ہے
    users_file = data_dir / "users.json"
    if not users_file.exists() or users_file.stat().st_size == 0:
        sample_users = [
            {
                "name": "Admin User",
                "email": "",
                "password": "",
                "user_status": "staff",
                "id": "55f124a3-b12c-4289-90a3-8a592e411ac7",
                "email_verified": True,
                "verified_at": datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
            }
        ]
        with open(users_file, 'w') as f:
            json.dump(sample_users, f, indent=4)
        print(f"✅ Initialized {users_file} with sample admin user")
    
    # باقی فائلیں ویسے ہی رہیں گی...
    
    print("\n🎉 All data files initialized successfully!")


# Run initialization when module is imported
if __name__ == "__main__":
    pass
    init_data_files()
else:
    pass
    # Auto-run when imported
    init_data_files()