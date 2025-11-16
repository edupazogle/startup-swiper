# Deployment Options for Startup Swiper

## Option 1: GitHub Pages Only (Static/Offline Mode) ✅ FREE

**What works:**
- ✅ Full PWA functionality
- ✅ All data stored in browser localStorage
- ✅ Swipe, vote, schedule meetings
- ✅ Add insights and ideas
- ✅ Works 100% offline
- ✅ No server costs

**What doesn't work:**
- ❌ Real-time sync across devices
- ❌ AI chat features (requires backend)
- ❌ Multi-user authentication sync

**Setup:**
1. Current workflow already deploys to: https://edupazogle.github.io/startup-swiper/
2. No backend needed - everything runs in browser
3. Free forever with GitHub Pages

**Files:**
- `.github/workflows/deploy-static.yml` (new - pure static)
- `.github/workflows/deploy.yml` (current - works but limited)

---

## Option 2: GitHub Pages + Free Backend (Render.com) ✅ FREE

**What works:**
- ✅ Everything from Option 1
- ✅ AI chat features
- ✅ Real-time sync
- ✅ Multi-user support
- ✅ Database persistence

**Limitations:**
- ⚠️ Render free tier sleeps after 15min inactivity
- ⚠️ First request takes 30-50 seconds to wake up
- ⚠️ 750 hours/month free (enough for hobby use)

**Setup:**
1. Frontend: GitHub Pages (free)
2. Backend: Render.com (free tier)

**Steps:**
```bash
# 1. Push backend to GitHub (already done)
git push origin main

# 2. Create Render service
# Go to: https://render.com
# - Click "New +" → "Web Service"
# - Connect your GitHub repo
# - Use these settings:
#   - Name: startup-swiper-api
#   - Root Directory: api
#   - Build Command: pip install -r requirements.txt
#   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
#   - Plan: Free

# 3. Update frontend to use Render URL
# In .github/workflows/deploy.yml, line 43:
#   VITE_API_URL: https://your-app.onrender.com
```

**Files needed:**
- `render.yaml` (created) - Render configuration
- `Dockerfile` (created) - Alternative to render.yaml

---

## Option 3: Self-Hosted (Your Own Server) ✅ FULL CONTROL

**What works:**
- ✅ Everything
- ✅ No sleep/wake delays
- ✅ Full control
- ✅ Can handle any load

**Requirements:**
- Server (VPS, AWS, DigitalOcean, etc.)
- Domain name (optional)

**Setup:**

### Using Docker Compose (Easiest):
```bash
# 1. Clone repo on server
git clone https://github.com/edupazogle/startup-swiper.git
cd startup-swiper

# 2. Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_key_here
EOF

# 3. Start services
docker-compose up -d

# Services will run on:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5000
```

### Using SystemD Service (Production):
```bash
# 1. Install on server
sudo cp -r . /var/www/startup-swiper
cd /var/www/startup-swiper

# 2. Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt

cd app/startup-swipe-schedu
npm install
cd ../..

# 3. Install systemd service
sudo cp startup-swiper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable startup-swiper
sudo systemctl start startup-swiper

# 4. Check status
sudo systemctl status startup-swiper
```

### Using Launch Script (Development):
```bash
# Simple resilient launcher
./launch-resilient.sh start

# Features:
# - Auto-restart on crash
# - Health monitoring
# - Log management
# - Process supervision

# Commands:
./launch-resilient.sh start    # Start all services
./launch-resilient.sh stop     # Stop all services
./launch-resilient.sh status   # Check status
./launch-resilient.sh restart  # Restart services
./launch-resilient.sh logs api # View API logs
```

---

## Recommendation

**For your use case (Slush 2025 event):**

### Best: Option 2 (GitHub Pages + Render.com Free)

**Why:**
1. ✅ **Free** - No costs
2. ✅ **All features work** - Including AI chat
3. ✅ **Easy setup** - 5 minutes on Render.com
4. ✅ **No server management** - Fully managed
5. ⚠️ **Acceptable tradeoff** - 30s first load after sleep is fine for event use

**Setup time: 5 minutes**

### Alternative: Option 1 (Pure Static)

If you're okay without AI features and just need:
- Swipe/vote on startups
- Schedule meetings
- Add insights
- Works offline

**Then Option 1 is perfect and 100% free forever!**

---

## Current Status

Your GitHub Actions is trying to connect to:
```
VITE_API_URL: https://startup-swiper-1.onrender.com
```

**This service doesn't exist yet!**

**Quick fix (2 options):**

### A) Deploy backend to Render (5 min):
1. Go to render.com
2. Sign in with GitHub
3. New Web Service → Connect repo
4. Done!

### B) Switch to static-only (1 min):
```bash
# Replace deploy.yml with deploy-static.yml
cd /home/akyo/startup_swiper
mv .github/workflows/deploy.yml .github/workflows/deploy-backend.yml.disabled
mv .github/workflows/deploy-static.yml .github/workflows/deploy.yml
git add -A
git commit -m "Switch to static-only deployment"
git push
```

Choose your path and I'll help you set it up! 🚀
