import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import bcrypt  # 🌟 Direct native compilation bypassing passlib bugs entirely
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Production Cryptographic Secrets configuration
SECRET_KEY = "HEALTH_TECH_SUPER_SECURE_SECRET_KEY_FOR_LOCAL_DEVELOPMENT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Points FastAPI to the login route to parse bearer tokens automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_password(password: str) -> str:
    """Hashes a raw password string safely using direct native Bcrypt compilation."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password string against its secure database record."""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a securely signed JWT Access Token for the device/user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_authenticated_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Reusable FastAPI dependency that intercepts inbound requests, decodes the JWT,
    and blocks unauthorized traffic automatically with a 401 status.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate security credentials or token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except Exception:
        raise credentials_exception
