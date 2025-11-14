# Startup Swiper - Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
cd /home/akyo/startup_swiper
./launch.sh
```

That's it! All services will start automatically.

## 📋 Common Commands

| Command | Description |
|---------|-------------|
| `./launch.sh` | Start all services |
| `./launch.sh stop` | Stop all services |
| `./launch.sh restart` | Restart all services |
| `./launch.sh status` | Check service status |
| `./launch.sh test` | Run health checks only |

## 🌐 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI backend |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Frontend | http://localhost:5000 | React application |

## 📁 Important Files

```
startup_swiper/
├── launch.sh              # Main launcher ⭐
├── LAUNCH_GUIDE.md        # Full documentation
├── QUICK_REFERENCE.md     # This file
├── .venv/                 # Python environment
├── api/
│   ├── requirements.txt   # Python dependencies
│   └── main.py           # API entry point
├── app/startup-swipe-schedu/
│   └── package.json      # Frontend dependencies
└── logs/                 # All service logs
    ├── api.log
    └── frontend.log
```

## 🔍 Check Logs

```bash
# API logs
tail -f logs/api.log

# Frontend logs  
tail -f logs/frontend.log

# All logs
tail -f logs/*.log
```

## 🛠️ Troubleshooting

### Port in use?
```bash
./launch.sh stop
./launch.sh start
```

### Dependencies issue?
```bash
source .venv/bin/activate
pip install -r api/requirements.txt
```

### Frontend not starting?
```bash
cd app/startup-swipe-schedu
npm install
```

## 📝 Environment Setup

Create `api/.env` file:
```env
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
DATABASE_URL=sqlite:///./startup_swiper.db
```

## 🧪 Development

### Run API Only
```bash
source .venv/bin/activate
cd api
uvicorn main:app --reload --port 8000
```

### Run Frontend Only
```bash
cd app/startup-swipe-schedu
npm run dev
```

## 📦 Dependencies Summary

### Python (API)
- FastAPI 0.109.0 - Web framework
- Uvicorn 0.27.0 - ASGI server
- SQLAlchemy 2.0.25 - ORM
- LiteLLM 1.44.28 - LLM integration
- Pydantic 2.5.3 - Data validation
- python-jose 3.3.0 - JWT auth

### JavaScript (Frontend)
- React 19.0.0 - UI framework
- Vite 6.3.5 - Build tool
- Tailwind CSS 4.1.11 - Styling
- Radix UI - Component library

## 🔐 API Authentication

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

## 🤖 LLM Integration

```bash
# Simple LLM call
curl -X POST http://localhost:8000/llm/simple \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is AI?","model":"gpt-4o"}'
```

## 📊 Health Check

```bash
# Check if services are running
./launch.sh status

# Or manually
curl http://localhost:8000/
curl http://localhost:5000/
```

## 🎯 Key Features

- ✅ Automatic port management
- ✅ Virtual environment setup
- ✅ Dependency installation
- ✅ Health checks
- ✅ Background service launching
- ✅ Comprehensive logging
- ✅ Graceful shutdown
- ✅ Hot reload (development)

## 💡 Tips

1. **First time setup**: Just run `./launch.sh` - it handles everything
2. **Development**: Leave services running, they auto-reload on changes
3. **Logs**: Always check `logs/` directory for debugging
4. **Status**: Run `./launch.sh status` anytime to see what's running
5. **Clean shutdown**: Press `Ctrl+C` or run `./launch.sh stop`

## 🆘 Need Help?

1. Check `LAUNCH_GUIDE.md` for detailed documentation
2. View logs: `tail -f logs/api.log`
3. Run tests: `./launch.sh test`
4. Check status: `./launch.sh status`

---

**Ready to go?** Just run: `./launch.sh` 🚀
