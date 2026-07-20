"""JWT authentication and role-based access dependency."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """Dependency: returns current user dict or raises 401."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return decode_token(token)


async def get_analyst(user: dict = Depends(get_current_user)) -> dict:
    """Dependency: analyst or admin role required."""
    if user.get("role") not in ("analyst", "admin"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user


async def get_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency: admin role required."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# Optional auth - returns None if no token provided
async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    if not token:
        return None
    try:
        return decode_token(token)
    except HTTPException:
        return None
