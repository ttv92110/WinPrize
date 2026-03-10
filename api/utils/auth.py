import hashlib
import secrets 

def hash_password(password: str) -> str:
    """Hash a password for storing"""
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    salt, hash_value = hashed.split(':')
    return hash_value == hashlib.sha256((salt + password).encode()).hexdigest()

def generate_draw_id() -> str:
    """Generate a unique draw ID"""
    import uuid
    return f"lucky_{str(uuid.uuid4())[:8]}"
