# Authentication System Implementation

## Overview
This document describes the complete implementation of the email/password authentication system with JWT tokens for the Startup Swiper API.

## Implementation Summary

### 1. Database Schema Enhancement

**New User Table** (`users`)
- `id`: Integer, Primary Key
- `email`: String, Unique, Indexed
- `hashed_password`: String (bcrypt hashed)
- `full_name`: String (optional)
- `is_active`: Boolean (default: True)
- `is_superuser`: Boolean (default: False)
- `created_at`: DateTime
- `updated_at`: DateTime

**Location**: `/api/models.py` (lines 7-17)

### 2. Security Components

**Password Hashing**
- Library: `bcrypt` (v4.0.1) via `passlib` (v1.7.4)
- Algorithm: bcrypt with automatic salt generation
- Functions:
  - `get_password_hash(password)`: Hash a plain password
  - `verify_password(plain, hashed)`: Verify password against hash

**JWT Token Generation**
- Library: `python-jose[cryptography]` (v3.3.0)
- Algorithm: HS256
- Token Expiration: 7 days (configurable)
- Functions:
  - `create_access_token(data, expires_delta)`: Generate JWT token
  - `decode_access_token(token)`: Decode and validate token

**Location**: `/api/auth.py`

### 3. Authentication Endpoints

#### POST `/auth/register`
Register a new user with email and password.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe" // optional
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-14T10:30:00"
}
```

**Error Codes**:
- `400`: Email already registered

---

#### POST `/auth/login`
Login with email and password to receive JWT access token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Codes**:
- `401`: Incorrect email or password
- `400`: Inactive user

---

#### GET `/auth/me`
Get current authenticated user information.

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-14T10:30:00"
}
```

**Error Codes**:
- `401`: Invalid or expired token
- `400`: Inactive user

---

#### GET `/auth/users`
Get list of all users (requires authentication).

**Headers**:
```
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)

**Response**:
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-11-14T10:30:00"
  }
]
```

---

#### PUT `/auth/users/{user_id}`
Update user information (users can only update themselves unless superuser).

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "email": "newemail@example.com",  // optional
  "full_name": "Jane Doe",           // optional
  "password": "NewPassword123!"      // optional
}
```

**Response**:
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2025-11-14T10:30:00"
}
```

**Error Codes**:
- `403`: Not authorized to update this user
- `404`: User not found

---

### 4. Authentication Middleware

**Dependency Functions**:
- `get_current_user`: Extract and validate JWT token, return User object
- `get_current_active_user`: Ensure user is active
- `get_current_superuser`: Ensure user has superuser privileges

**Usage in Endpoints**:
```python
@app.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.email}"}
```

**Location**: `/api/auth.py` (lines 54-88)

### 5. CRUD Operations

**User CRUD Functions** (in `/api/crud.py`):
- `get_user(db, user_id)`: Get user by ID
- `get_user_by_email(db, email)`: Get user by email
- `get_users(db, skip, limit)`: Get all users with pagination
- `create_user(db, user)`: Create new user with hashed password
- `update_user(db, user_id, user_update)`: Update user information
- `delete_user(db, user_id)`: Delete user

### 6. Pydantic Schemas

**User Schemas** (in `/api/schemas.py`):
- `UserBase`: Base user fields (email, full_name)
- `UserCreate`: For registration (adds password)
- `UserUpdate`: For updates (all fields optional)
- `User`: Public user response (excludes password)
- `UserInDB`: Complete user with all fields
- `Token`: JWT token response
- `TokenData`: Token payload data
- `UserLogin`: Login request

### 7. Configuration

**Environment Variables** (configure in `.env`):
```bash
# Secret key for JWT token signing (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this-in-production

# Database URL (default: SQLite)
DATABASE_URL=sqlite:///./startup_swiper.db

# Or use PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Token Settings**:
- Algorithm: HS256
- Expiration: 7 days (10080 minutes)
- Configurable in `/api/auth.py` line 19

### 8. Dependencies

**New Python Packages**:
```
bcrypt==4.0.1                      # Password hashing
passlib==1.7.4                     # Password hashing utilities
python-jose[cryptography]==3.3.0   # JWT token handling
pydantic[email]==2.5.3             # Email validation
```

**Installation**:
```bash
cd /home/akyo/startup_swiper/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing

**Test Script**: `/api/test_auth.py`

Run tests:
```bash
source venv/bin/activate
python test_auth.py
```

**Test Coverage**:
- ✓ User registration
- ✓ Password hashing
- ✓ User authentication
- ✓ Wrong password rejection
- ✓ JWT token generation
- ✓ Password verification
- ✓ Database integration

## Usage Examples

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Access Protected Route
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Update User Profile
```bash
curl -X PUT http://localhost:8000/auth/users/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith"
  }'
```

## Security Best Practices

### Implemented
- ✓ Passwords hashed with bcrypt (never stored in plain text)
- ✓ JWT tokens with expiration
- ✓ Email validation using Pydantic
- ✓ User active status checking
- ✓ Authorization checks for user updates
- ✓ Unique email constraint in database

### Recommended for Production
1. **Change SECRET_KEY**: Use a strong, random secret key
   ```bash
   # Generate secure key
   openssl rand -hex 32
   ```

2. **Use HTTPS**: Always use SSL/TLS in production

3. **Database**: Switch to PostgreSQL for production
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/startup_swiper
   ```

4. **Rate Limiting**: Add rate limiting to prevent brute force attacks

5. **Password Requirements**: Enforce strong password policies
   - Minimum length: 8 characters
   - Require uppercase, lowercase, numbers, special characters

6. **Email Verification**: Add email verification flow

7. **Refresh Tokens**: Implement refresh token mechanism

8. **CORS**: Restrict CORS origins in production
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

## File Structure

```
/api/
├── auth.py                    # Authentication utilities
├── crud.py                    # CRUD operations (including users)
├── models.py                  # SQLAlchemy models (including User)
├── schemas.py                 # Pydantic schemas (including auth schemas)
├── main.py                    # FastAPI app with auth endpoints
├── database.py                # Database connection
├── requirements.txt           # Python dependencies
├── test_auth.py              # Authentication tests
└── AUTH_IMPLEMENTATION.md     # This file
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **bcrypt compatibility error**
   - Solution: Ensure bcrypt==4.0.1 and passlib==1.7.4 are installed

2. **Token expired**
   - Tokens expire after 7 days by default
   - Login again to get a new token

3. **401 Unauthorized**
   - Check that Authorization header is set correctly
   - Format: `Authorization: Bearer <token>`

4. **Email already registered**
   - Each email can only be registered once
   - Use a different email or login with existing account

## Next Steps

### Recommended Enhancements
1. Add email verification workflow
2. Implement password reset functionality
3. Add OAuth2 social login (Google, GitHub, etc.)
4. Implement refresh token mechanism
5. Add user roles and permissions system
6. Create admin dashboard for user management
7. Add logging for security events
8. Implement 2FA (Two-Factor Authentication)

---

**Implementation Date**: November 14, 2025
**Status**: ✓ Complete and Tested
