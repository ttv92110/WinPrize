import json
import os
from pathlib import Path

def init_data_files():
    """Initialize all JSON data files with proper structure"""
    
    # Get data directory from environment or use default
    data_dir = Path(os.getenv("DATA_DIR", "/tmp/data"))
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Initialize users.json
    users_file = data_dir / "users.json"
    if not users_file.exists() or users_file.stat().st_size == 0:
        with open(users_file, 'w') as f:
            json.dump([], f, indent=4)
        print(f"✅ Initialized {users_file}")
    
    # Initialize user_draws.json
    user_draws_file = data_dir / "user_draws.json"
    if not user_draws_file.exists() or user_draws_file.stat().st_size == 0:
        with open(user_draws_file, 'w') as f:
            json.dump([], f, indent=4)
        print(f"✅ Initialized {user_draws_file}")
    
    # Initialize lucky_draws.json with sample data if empty
    lucky_draws_file = data_dir / "lucky_draws.json"
    if not lucky_draws_file.exists() or lucky_draws_file.stat().st_size == 0:
        sample_draws = [
    {
        "id": "lucky_00001",
        "user_pay": 1,
        "time_interval": "day",
        "winner_get": 100,
        "created_at": "09/03/2026T01h:01m:00s",
        "closed_at": "10/03/2026T01h:01m:00s",
        "status": "open",
        "visible": True
    },
    {
        "id": "lucky_00002",
        "user_pay": 10,
        "time_interval": "week",
        "winner_get": 1000,
        "created_at": "09/03/2026T01h:01m:00s",
        "closed_at": "16/03/2026T01h:01m:00s",
        "status": "open",
        "visible": True
    },
    {
        "id": "lucky_00003",
        "user_pay": 100,
        "time_interval": "month",
        "winner_get": 10000,
        "created_at": "09/03/2026T01h:01m:00s",
        "closed_at": "08/04/2026T01h:01m:00s",
        "status": "open",
        "visible": True
    }
]
        with open(lucky_draws_file, 'w') as f:
            json.dump(sample_draws, f, indent=4)
        print(f"✅ Initialized {lucky_draws_file} with sample data")
    else:
        print(f"✅ {lucky_draws_file} already exists")
    
    print("\n🎉 All data files initialized successfully!")

# Run initialization when module is imported
init_data_files()
