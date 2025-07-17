# Authentication Mode Examples

This document provides examples of how to use different authentication modes in the Morn application.

## JWT Mode (Default)

### Environment Variables
```bash
export MORN_AUTH_MODE=jwt
export MORN_ADMIN_USERNAME=admin
export MORN_ADMIN_PASSWORD=your_secure_password
export JWT_SECRET_KEY=your-secret-key-change-in-production
export JWT_ALGORITHM=HS256
export JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### Usage Examples

#### 1. Login to get access token
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_secure_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

#### 2. Access protected API with token
```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": false
  }'
```

#### 3. Get current user info
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response:
```json
{
  "username": "admin"
}
```

## No Auth Mode

### Environment Variables
```bash
export MORN_AUTH_MODE=none
# No other auth-related environment variables needed
```

### Usage Examples

#### 1. Login with any credentials (for compatibility)
```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "any_user",
    "password": "any_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

#### 2. Access API without token
```bash
curl -X POST "http://localhost:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": false
  }'
```

#### 3. Get current user info without token
```bash
curl -X GET "http://localhost:8000/me"
```

Response:
```json
{
  "username": "anonymous"
}
```

## Frontend Integration Examples

### JWT Mode

#### Login Component
```javascript
const login = async (username, password) => {
  const response = await fetch('/api/v1/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    throw new Error('Login failed');
  }
};
```

#### API Calls with Authentication
```javascript
const callApi = async (endpoint, data) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
};
```

### No Auth Mode

#### API Calls without Authentication
```javascript
const callApi = async (endpoint, data) => {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
};
```

## Testing Different Modes

### Using the Test Script
```bash
# Run the test script to verify both modes work correctly
python test_auth_modes.py
```

### Manual Testing

#### Test JWT Mode
```bash
# Set JWT mode
export MORN_AUTH_MODE=jwt
export MORN_ADMIN_USERNAME=admin
export MORN_ADMIN_PASSWORD=admin123
export JWT_SECRET_KEY=test-secret

# Start server
python app/app.py

# In another terminal, test without token (should fail)
curl http://localhost:8000/me

# Test with correct login
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Test No Auth Mode
```bash
# Set no auth mode
export MORN_AUTH_MODE=none

# Start server
python app/app.py

# In another terminal, test without token (should work)
curl http://localhost:8000/me

# Test with any login credentials
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "any", "password": "any"}'
```

## Security Considerations

### JWT Mode
- ✅ Suitable for production environments
- ✅ Provides proper user authentication
- ✅ Token expiration and refresh mechanisms
- ✅ Secure password validation

### No Auth Mode
- ⚠️ Only suitable for development or internal systems
- ⚠️ No security protection
- ⚠️ Anyone can access all APIs
- ⚠️ Should never be used in production

## Migration Guide

### From JWT to No Auth
1. Set `MORN_AUTH_MODE=none`
2. Remove authentication headers from API calls
3. Update frontend to handle anonymous users

### From No Auth to JWT
1. Set `MORN_AUTH_MODE=jwt`
2. Configure admin credentials and JWT secret
3. Add authentication headers to API calls
4. Implement login flow in frontend
5. Handle authentication errors 
