# Morn

English | [简体中文](README_CN.md)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

#### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/morn-ai/morn.git
cd morn

# Install dependencies
uv sync

# Run the development server
uv run python app/app.py
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/morn-ai/morn.git
cd morn

# Install dependencies
pip install -e .

# Run the development server
python app/app.py
```

## Authentication

This project implements a flexible authentication system that supports two authentication modes:

1. **JWT Mode** (`jwt`): JWT (JSON Web Token) based authentication system that supports login token acquisition and API access protection
2. **No Auth Mode** (`none`): No authentication required, anyone can access APIs, suitable for development environments or internal systems

### Configuration

Set the following environment variables:

```bash
# Authentication mode (none | jwt)
# none: No authentication required, anyone can access APIs
# jwt: JWT authentication required
MORN_AUTH_MODE=jwt

# Admin credentials
MORN_ADMIN_USERNAME=admin
MORN_ADMIN_PASSWORD=your_password

# JWT configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# Brute force protection configuration
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=300
MAX_ATTEMPTS_PER_MINUTE=10
FAILED_ATTEMPT_DELAY=2
```

### API Endpoints

#### 1. User Login

**POST** `/login`

Request body:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

#### 2. Get Current User Information

**GET** `/me`

Include Bearer Token in request header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{
  "username": "admin"
}
```

#### 3. Protected APIs

All APIs that require authentication need to include a Bearer Token in the request header.

For example, the chat API:
**POST** `/api/v1/chat/completions`

Request headers:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Authentication Mode Details

#### JWT Mode (Default)
- Set `MORN_AUTH_MODE=jwt`
- All APIs require valid JWT tokens
- Users must login first to get tokens
- Suitable for production environments

#### No Auth Mode
- Set `MORN_AUTH_MODE=none`
- All APIs can be accessed directly without tokens
- Login API accepts any username and password
- Suitable for development environments or internal systems

### Usage in Code

#### Protecting Routes

Add dependency to routes that require authentication:

```python
from app.api.auth import require_auth
from app.schemas.auth import TokenData
from typing import Annotated
from fastapi import Depends

@router.post("/protected-endpoint")
async def protected_endpoint(
    current_user: Annotated[TokenData, Depends(require_auth)]
):
    # Only authenticated users can access
    return {"message": f"Hello {current_user.username}!"}
```

#### Getting Current User Information

```python
async def some_function(current_user: Annotated[TokenData, Depends(require_auth)]):
    username = current_user.username
    # Use username for business logic
```

### Security Considerations

1. **Production Environment**: Always change `JWT_SECRET_KEY` to a strong secret
2. **HTTPS**: Production environment must use HTTPS
3. **Token Expiration**: Set reasonable token expiration time
4. **Password Security**: Use strong passwords and change them regularly
5. **Brute Force Protection**: The system includes built-in protection against brute force attacks

### Brute Force Protection

The system includes comprehensive protection against brute force attacks:

- **Failed Attempt Tracking**: Tracks failed login attempts per IP address
- **Account Lockout**: Temporarily locks accounts after exceeding maximum failed attempts
- **Rate Limiting**: Limits login attempts per minute per IP address
- **Delayed Response**: Adds delay after failed attempts to increase attack cost
- **Automatic Cleanup**: Periodically cleans up old records to prevent memory leaks

#### Configuration Options

- `MAX_FAILED_ATTEMPTS`: Maximum failed attempts before lockout (default: 5)
- `LOCKOUT_DURATION`: Lockout duration in seconds (default: 300 = 5 minutes)
- `MAX_ATTEMPTS_PER_MINUTE`: Maximum attempts per minute per IP (default: 10)
- `FAILED_ATTEMPT_DELAY`: Delay in seconds after failed attempt (default: 2)

#### Security Status API

You can check the security status for your IP address:

```bash
GET /api/v1/security/status
```

Response:
```json
{
  "ip_address": "127.0.0.1",
  "is_locked": false,
  "is_rate_limited": false,
  "failed_attempts": 0,
  "remaining_attempts": 5,
  "lockout_remaining": null,
  "recent_attempts_count": 0
}
```
