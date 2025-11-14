# Startup Swiper - Launch Guide

## Quick Start

```bash
# Launch all services
./launch.sh

# Or explicitly start
./launch.sh start
```

## Overview

The `launch.sh` script is a comprehensive launcher that handles:
- ✅ Port clearing (8000, 5000, 3000)
- ✅ Virtual environment setup
- ✅ Dependency installation
- ✅ Basic health checks
- ✅ API service launch
- ✅ Frontend service launch
- ✅ Backend service launch
- ✅ Additional services management
- ✅ Logging and monitoring

## Requirements

### System Requirements
- Python 3.8+ (recommended: 3.12)
- Node.js 16+ and npm
- Linux/macOS (for port management commands)
- `lsof` and `fuser` utilities

### Python Dependencies
See `api/requirements.txt` for full list:
- FastAPI 0.109.0
- Uvicorn 0.27.0
- SQLAlchemy 2.0.25
- LiteLLM 1.44.28
- And many more...

## Commands

### Start Services
```bash
./launch.sh start
# or simply
./launch.sh
```
Starts all services in the background with logging.

### Stop Services
```bash
./launch.sh stop
```
Gracefully stops all running services and clears ports.

### Restart Services
```bash
./launch.sh restart
```
Stops and then starts all services.

### Check Status
```bash
./launch.sh status
```
Shows the current status of all services and ports.

### Run Tests Only
```bash
./launch.sh test
```
Runs basic health checks without starting services.

## Services

### 1. API Service (Port 8000)
- **Technology**: FastAPI + Uvicorn
- **Location**: `api/`
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Features**:
  - RESTful API endpoints
  - Authentication (JWT)
  - Database integration (SQLAlchemy)
  - LLM integration (LiteLLM)
  - Auto-generated OpenAPI docs

### 2. Frontend Service (Port 5000)
- **Technology**: React + Vite
- **Location**: `app/startup-swipe-schedu/`
- **URL**: http://localhost:5000
- **Features**:
  - Modern React UI
  - Hot module replacement
  - Tailwind CSS
  - GitHub Spark components

### 3. Backend Service (Port 3000)
- **Status**: Optional/Not implemented
- **Note**: API service acts as the primary backend

### 4. Additional Services
- **Location**: `services/`
- **Services**:
  - CB Insights integration
  - Other microservices as needed

## Logs

All logs are stored in the `logs/` directory:

```
logs/
├── api.log          # API service output
├── frontend.log     # Frontend dev server output
├── backend.log      # Backend service output
├── services.log     # Additional services output
├── api.pid          # API process ID
└── frontend.pid     # Frontend process ID
```

### View Logs
```bash
# API logs
tail -f logs/api.log

# Frontend logs
tail -f logs/frontend.log

# All logs
tail -f logs/*.log
```

## Basic Health Tests

The launch script runs the following tests before starting services:

1. ✓ Directory structure verification
2. ✓ Virtual environment check
3. ✓ Python packages verification
4. ✓ Node.js availability
5. ✓ npm availability
6. ✓ Port availability check

## Troubleshooting

### Port Already in Use
```bash
# The script automatically clears ports, but if issues persist:
./launch.sh stop
# Wait a few seconds
./launch.sh start
```

### Dependencies Not Installed
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r api/requirements.txt

# For frontend
cd app/startup-swipe-schedu
npm install
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
./launch.sh
```

### Service Won't Start
```bash
# Check logs
./launch.sh status
tail -f logs/api.log

# Check if ports are free
lsof -i :8000
lsof -i :5000
```

### Database Issues
```bash
# The script auto-creates database tables
# If you need to reset the database:
cd api
rm -f *.db  # Remove SQLite databases
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

## Environment Variables

Create a `.env` file in the `api/` directory for configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./startup_swiper.db

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Other services
CB_INSIGHTS_API_KEY=your-cb-insights-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

## Development Workflow

### Standard Development
```bash
# 1. Start all services
./launch.sh

# 2. Make changes to code (hot reload enabled)

# 3. View logs if needed
tail -f logs/api.log

# 4. Stop when done
./launch.sh stop
```

### API Only Development
```bash
source .venv/bin/activate
cd api
uvicorn main:app --reload --port 8000
```

### Frontend Only Development
```bash
cd app/startup-swipe-schedu
npm run dev
```

## Architecture

```
startup_swiper/
├── launch.sh              # Main launch script
├── LAUNCH_GUIDE.md       # This guide
├── .venv/                # Python virtual environment
├── api/                  # FastAPI backend
│   ├── main.py          # API entry point
│   ├── requirements.txt # Python dependencies
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   ├── auth.py          # Authentication
│   └── llm_config.py    # LLM integration
├── app/                  # Frontend application
│   └── startup-swipe-schedu/
│       ├── package.json
│       └── src/
├── services/             # Additional services
│   └── cbinsights/
├── logs/                 # Service logs
└── docs/                 # Documentation
```

## Production Deployment

For production, consider:

1. **Use a process manager**: systemd, supervisor, or PM2
2. **Reverse proxy**: nginx or Apache
3. **HTTPS**: Let's Encrypt certificates
4. **Environment variables**: Secure secret management
5. **Database**: PostgreSQL or MySQL instead of SQLite
6. **Logging**: Centralized logging (ELK, Grafana)
7. **Monitoring**: Health checks and alerts

### Example systemd Service
```ini
[Unit]
Description=Startup Swiper API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/startup_swiper
Environment="PATH=/path/to/startup_swiper/.venv/bin"
ExecStart=/path/to/startup_swiper/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info

### LLM Integration
- `POST /llm/simple` - Simple LLM call
- `POST /llm/chat` - Chat with message history

### Data Endpoints
- `/calendar-events/` - Calendar management
- `/linkedin-chat-messages/` - LinkedIn integration
- `/votes/` - Voting system
- `/ideas/` - Ideas management
- `/startup-ratings/` - Startup ratings
- And many more...

See http://localhost:8000/docs for complete API documentation.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run `./launch.sh status` to verify services
3. Run `./launch.sh test` to check system health
4. Review this guide for common solutions

## License

[Add your license information here]
