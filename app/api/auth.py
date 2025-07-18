from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
import time

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config.agent_config import config
from app.schemas.auth import Token, UserLogin, TokenData
from app.api.brute_force_protection import brute_force_protection

router = APIRouter()
security = HTTPBearer(auto_error=False)  # Don't auto-raise error for missing token


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret_key, algorithm=config.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data


async def get_current_user(credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]) -> \
Optional[TokenData]:
    """Get current user - returns None if no credentials provided"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


@router.post("/api/v1/login", response_model=Token)
async def login_for_access_token(body: UserLogin, request: Request):
    """User login to get access token with brute force protection"""
    # Get client IP address
    client_ip = request.client.host if request.client else "unknown"
    if request.headers.get("x-forwarded-for"):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
    elif request.headers.get("x-real-ip"):
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            client_ip = x_real_ip

    # Check if IP is locked out
    if brute_force_protection.is_ip_locked(client_ip):
        lockout_remaining = brute_force_protection.get_lockout_remaining(client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked. Please try again in {lockout_remaining} seconds.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check rate limiting
    if brute_force_protection.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait before trying again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If auth mode is "none", allow any login attempt
    if config.morn_auth_mode == "none":
        access_token_expires = timedelta(minutes=config.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": body.username}, expires_delta=access_token_expires
        )
        brute_force_protection.record_attempt(client_ip, True)
        return Token(
            access_token=access_token,
            expires_in=config.jwt_access_token_expire_minutes * 60
        )

    # Normal JWT authentication
    if body.username == config.morn_admin_username and body.password == config.morn_admin_password:
        access_token_expires = timedelta(minutes=config.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": body.username}, expires_delta=access_token_expires
        )
        brute_force_protection.record_attempt(client_ip, True)
        return Token(
            access_token=access_token,
            expires_in=config.jwt_access_token_expire_minutes * 60
        )
    else:
        # Record failed attempt
        brute_force_protection.record_attempt(client_ip, False)

        # Add delay for failed attempts
        time.sleep(brute_force_protection.failed_attempt_delay)

        # Get remaining attempts
        remaining_attempts = brute_force_protection.get_remaining_attempts(client_ip)

        if remaining_attempts == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account locked due to too many failed attempts. Please try again later.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect username or password. {remaining_attempts} attempts remaining.",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.get("/me", response_model=TokenData)
async def read_users_me(current_user: Annotated[Optional[TokenData], Depends(get_current_user)]):
    """Get current user information"""
    if current_user is None:
        # If auth mode is "none", return a default user
        if config.morn_auth_mode == "none":
            return TokenData(username="anonymous")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return current_user


# Dependency function for protecting routes that require authentication
def require_auth(current_user: Annotated[Optional[TokenData], Depends(get_current_user)]) -> TokenData:
    """Dependency function that requires user authentication based on auth_mode"""
    if config.morn_auth_mode == "none":
        # In "none" mode, return a default user if no authentication provided
        return current_user or TokenData(username="anonymous")
    else:
        # In "jwt" mode, require proper authentication
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
