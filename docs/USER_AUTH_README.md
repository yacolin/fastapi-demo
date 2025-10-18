# User Authentication Module

This module provides JWT-based user authentication for the FastAPI application, translated from the Go implementation.

## Features

- **User Registration** - Create new user accounts with password hashing
- **User Login** - Authenticate users and issue JWT tokens
- **Token Refresh** - Refresh access tokens using refresh tokens
- **Protected Routes** - Middleware for protecting endpoints with JWT authentication

## Files Created

### 1. `controllers/user.py`

Main user authentication controller with endpoints:

- `POST /api/v1/users/login` - User login
- `POST /api/v1/users/register` - User registration
- `POST /api/v1/users/refresh` - Refresh access token
- `GET /api/v1/users/me` - Get current user info (protected)

### 2. `utils/jwt_utils.py`

JWT token utilities:

- `hash_password()` - Hash passwords using bcrypt
- `check_password_hash()` - Verify password against hash
- `generate_access_token()` - Generate 15-minute access tokens
- `generate_refresh_token()` - Generate 7-day refresh tokens
- `decode_token()` - Decode and validate JWT tokens

### 3. `utils/jwt_middleware.py`

JWT authentication middleware:

- `get_current_user()` - FastAPI dependency for protected routes

### 4. `users_table.sql`

SQL schema for creating the users table

## Database Schema

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);
```

## Installation

1. Install new dependencies:

```bash
pip install -r requirements.txt
```

2. Set JWT secret in `.env` file:

```env
JWT_SECRET=your-super-secret-key-change-this-in-production
```

3. Create the users table:

```bash
mysql -u your_user -p your_database < users_table.sql
```

## API Usage

### 1. Register a New User

```bash
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "请求成功",
  "data": null,
  "timestamp": 1729260645
}
```

### 2. Login

```bash
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "timestamp": 1729260645
}
```

### 3. Refresh Access Token

```bash
POST /api/v1/users/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "timestamp": 1729260645
}
```

### 4. Get Current User Info (Protected)

```bash
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**

```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "created_at": 1729260645,
    "updated_at": 1729260645
  },
  "timestamp": 1729260645
}
```

## Using Authentication Middleware

To protect any endpoint with JWT authentication, use the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from utils.jwt_middleware import get_current_user
from controllers.user import User

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}!"}
```

## Token Configuration

- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days
- **Algorithm**: HS256
- **Secret Key**: Configured via `JWT_SECRET` environment variable

## Security Notes

1. **Change the JWT Secret**: Update `JWT_SECRET` in your `.env` file to a strong, random value
2. **HTTPS Only**: Always use HTTPS in production to prevent token interception
3. **Password Requirements**: Consider adding password strength requirements
4. **Rate Limiting**: Implement rate limiting on login/register endpoints
5. **Token Blacklist**: Consider implementing token blacklist for logout functionality

## Error Codes

The module uses standardized business error codes from `utils/biz_code.py`:

- `4100` - INVALID_PWD: Invalid password
- `4301` - ACCESS_TK_GEN: Failed to generate access token
- `4302` - REFRESH_TK_GEN: Failed to generate refresh token
- `4303` - TK_INVALID: Invalid token
- `4305` - TK_NOT_FOUND: Token not found in request
- `4306` - TK_FORMAT: Invalid token format
- `4309` - TK_USER_ID: Missing user_id in token
- `5104` - DB_CREATE: Database creation error
- `5106` - USER_NOT_FOUND: User not found

## Comparison with Go Implementation

This Python implementation mirrors the Go version with these equivalents:

| Go File        | Python File               | Purpose                    |
| -------------- | ------------------------- | -------------------------- |
| `user.go`      | `controllers/user.py`     | User endpoints             |
| `cryptoPwd.go` | `utils/jwt_utils.py`      | Password & token utilities |
| `JWTAuth.go`   | `utils/jwt_middleware.py` | JWT middleware             |

**Key differences:**

- Python uses `passlib` with bcrypt instead of Go's `bcrypt` package
- Python uses `python-jose` for JWT instead of Go's `jwt/v5`
- Async/await pattern instead of synchronous handlers
- FastAPI dependency injection instead of Gin middleware
