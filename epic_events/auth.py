import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from epic_events.models import User
from epic_events.config import JWT_SECRET_KEY

# Configuration
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 h
TOKEN_FILE = os.path.expanduser("~/.epic_events/token")

def create_token(user_email: str, role: str) -> str:
    data = {
        "sub": user_email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def save_token(token: str):
    """Save JWT token to file"""
    token_dir = os.path.dirname(TOKEN_FILE)
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    os.chmod(TOKEN_FILE, 0o600)  # User read/write only

def set_current_user(user: User):
    """Store current user email in environment"""
    os.environ['EPIC_EVENTS_USER'] = user.email

def get_current_user(session) -> Optional[User]:
    """Get current user from token"""
    try:
        if not os.path.exists(TOKEN_FILE):
            return None
        
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            return None
            
        return session.query(User).filter(User.email == user_email).first()
    except (JWTError, FileNotFoundError):
        return None

def clear_current_user():
    """Remove token file"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)