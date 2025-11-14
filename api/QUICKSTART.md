# Quick Start Guide - Startup Swiper API with Authentication

## Start the Server

```bash
cd /home/akyo/startup_swiper/api

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## Test Authentication Flow

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@startup.com",
    "password": "MySecurePass123!",
    "full_name": "Alice Johnson"
  }'
```

### 2. Login to Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@startup.com",
    "password": "MySecurePass123!"
  }'
```

Save the `access_token` from the response!

### 3. Access Protected Route
```bash
# Replace <YOUR_TOKEN> with the actual token from step 2
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## Interactive API Documentation

Visit these URLs in your browser after starting the server:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing interface
  - Try out all endpoints
  - Built-in authentication support

- **ReDoc**: http://localhost:8000/redoc
  - Beautiful API documentation
  - Easy to read and navigate

## Database Schema

The system automatically creates these tables:
- `users` - User authentication (NEW!)
- `calendar_events` - Event scheduling
- `votes` - Startup voting
- `startup_ratings` - Startup ratings
- `ideas` - User ideas
- And 8 more existing tables...

Database file: `startup_swiper.db` (SQLite)

## Configuration

Create a `.env` file in `/api/` directory:

```bash
# Secret key for JWT (REQUIRED - change this!)
SECRET_KEY=your-very-secret-key-here-change-in-production

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./startup_swiper.db

# Or use PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/startup_swiper
```

## Next Steps

1. Start the server (see above)
2. Visit http://localhost:8000/docs to explore all endpoints
3. Register a user and test authentication
4. Integrate with your frontend application
5. See `AUTH_IMPLEMENTATION.md` for detailed documentation
