import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext

# 🔐 Professional Secret Management
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# This handles the "Salt and Hash" logic automatically
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Updated to modern Python 3.14 UTC format
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)