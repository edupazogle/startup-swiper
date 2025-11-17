# JWT Authentication Implementation Summary

## Overview
Successfully implemented JWT authentication with refresh tokens and 7-day session expiration for the Startup Swiper application.

## Backend Changes

### 1. Database Schema (`api/models.py`)
Added new `RefreshToken` table:
```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
```

### 2. Authentication Service (`api/auth.py`)
Updated token configuration:
- **Access Token**: 30 minutes (short-lived for security)
- **Refresh Token**: 7 days (stored in database)

New functions added:
- `create_refresh_token()` - Creates and stores refresh token in DB
- `verify_refresh_token()` - Validates refresh token and returns user
- `revoke_refresh_token()` - Revokes a single refresh token
- `revoke_all_user_tokens()` - Revokes all tokens for a user (logout from all devices)

### 3. API Schemas (`api/schemas.py`)
Updated Token schema:
```python
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # seconds until access token expires
```

### 4. API Endpoints (`api/main.py`)
Updated and new endpoints:

**POST /auth/login**
- Returns both access_token and refresh_token
- Access token expires in 30 minutes
- Refresh token expires in 7 days

**POST /auth/refresh** (NEW)
- Accepts refresh_token
- Returns new access_token and refresh_token
- Revokes old refresh token (one-time use)

**POST /auth/logout** (NEW)
- Revokes the provided refresh token
- Clears client-side tokens

**POST /auth/logout-all** (NEW)
- Revokes all refresh tokens for the user
- Logs out from all devices

## Frontend Changes

### 1. Auth Service (`src/lib/authService.ts`)
New centralized authentication service with:

**Token Management:**
- Stores access_token, refresh_token, and expiry in localStorage
- Automatic token refresh when within 5 minutes of expiry
- Prevents multiple simultaneous refresh requests

**Methods:**
- `login(email, password)` - Authenticate and store tokens
- `logout()` - Revoke tokens and clear storage
- `isAuthenticated()` - Check if user has valid tokens
- `refreshAccessToken()` - Refresh expired access token
- `authenticatedFetch()` - Make authenticated API calls with auto-retry on 401

### 2. API Client (`src/lib/api.ts`)
Updated to use `authService` for authenticated requests:
- Public endpoints (health, login, register) - no auth required
- All other endpoints - automatic JWT authentication
- Automatic redirect to login on authentication failure

### 3. Login Component (`src/components/LoginView.tsx`)
Simplified to use `authService`:
```typescript
const user = await authService.login(email, password)
```

### 4. App Component (`src/App.tsx`)
Updated authentication flow:
1. Check JWT authentication on app load
2. Fallback to legacy localStorage session
3. Updated logout to use `authService.logout()`

## Security Features

1. **Short-lived Access Tokens**: 30 minutes reduces exposure if stolen
2. **Refresh Token Rotation**: Each refresh generates a new token and revokes the old one
3. **Database Token Storage**: Refresh tokens stored securely in database
4. **Token Revocation**: Ability to invalidate tokens immediately
5. **Automatic Refresh**: Frontend automatically refreshes tokens before expiry
6. **One-time Use**: Refresh tokens are revoked after use

## Session Duration

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days
- **Total Session**: Up to 7 days with automatic refresh
- **After 7 days**: User must log in again

## Testing

Tested endpoints:
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eduardo.paz@axa.com","password":"123"}'

# Refresh
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"..."}'

# Get current user (with JWT)
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## User Experience

1. **Login**: User enters credentials, receives tokens, stays logged in
2. **Active Use**: Access token refreshes automatically every 30 minutes
3. **Return Visit**: If within 7 days, user stays logged in
4. **After 7 Days**: User must log in again
5. **Logout**: All tokens revoked, requires new login

## Database Migration

The `refresh_tokens` table is automatically created when the backend starts. No manual migration needed.

## Environment Variables

Required in `.env`:
```
SECRET_KEY=your-secret-key-change-this-in-production
```

## Implementation Complete ✅

All components are working:
- Backend JWT generation and validation
- Database token storage and rotation
- Frontend auth service with automatic refresh
- Secure token storage in localStorage
- 7-day session expiration
- Logout functionality
