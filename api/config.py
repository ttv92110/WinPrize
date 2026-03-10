import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Use /tmp directory on Vercel (writable), otherwise local data directory
    if os.getenv("VERCEL"):
        DATA_DIR = Path("/tmp/data")
    else:
        BASE_DIR = Path(__file__).parent.parent
        DATA_DIR = BASE_DIR / "data"
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    # File paths
    USERS_FILE = DATA_DIR / "users.json"
    LUCKY_DRAWS_FILE = DATA_DIR / "lucky_draws.json"
    USER_DRAWS_FILE = DATA_DIR / "user_draws.json"
    PAYMENTS_FILE = DATA_DIR / "payments.json"  # New payments file
    PASSWORD_RESETS_FILE = DATA_DIR / "password_resets.json"  # New file
    EMAIL_VERIFICATIONS_FILE = DATA_DIR / "email_verifications.json"  # New file
    
    # App settings
    
    # App settings
    APP_NAME = "Win Prize"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    # Email settings
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@winprize.com")
    FROM_NAME = os.getenv("FROM_NAME", "WinPrize Support")