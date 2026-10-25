import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Any
from app.config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def _create_token(subject: Any, expires_delta: timedelta, token_type: str) -> str:
    to_encode = {
        "sub": str(subject),
        "exp": datetime.utcnow() + expires_delta,
        "type": token_type,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def access_token_ttl() -> timedelta:
    return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """Short-lived access token (default 15 minutes)."""
    return _create_token(subject, expires_delta or access_token_ttl(), "access")


def create_refresh_token(subject: Any) -> str:
    """Long-lived refresh token, accepted only by POST /api/auth/refresh."""
    return _create_token(subject, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
