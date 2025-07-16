from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config.agent_config import AgentConfig
from app.schemas.auth import Token, UserLogin, TokenData

router = APIRouter()
config = AgentConfig()
security = HTTPBearer()


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


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> TokenData:
    """Get current user"""
    return verify_token(credentials.credentials)


@router.post("/login", response_model=Token)
async def login_for_access_token(body: UserLogin):
    """User login to get access token"""
    if body.username == config.morn_admin_username and body.password == config.morn_admin_password:
        access_token_expires = timedelta(minutes=config.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": body.username}, expires_delta=access_token_expires
        )
        return Token(
            access_token=access_token,
            expires_in=config.jwt_access_token_expire_minutes * 60
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=TokenData)
async def read_users_me(current_user: Annotated[TokenData, Depends(get_current_user)]):
    """Get current user information"""
    return current_user


# Dependency function for protecting routes that require authentication
def require_auth(current_user: Annotated[TokenData, Depends(get_current_user)]) -> TokenData:
    """Dependency function that requires user authentication"""
    return current_user
