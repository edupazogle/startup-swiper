# 🚀 QUICK DEPLOY TO PRODUCTION

## Current Status: ✅ PRODUCTION READY

All tests passed. System verified and ready for deployment.

## Deploy in 3 Steps

### Step 1: Push to GitHub (2 minutes)
```bash
cd /home/akyo/startup_swiper

# If not initialized
git init
git add .
git commit -m "Production deployment - NVIDIA NIM + New Calendar"

# Add your repository
git remote add origin https://github.com/YOUR_USERNAME/startup-swiper.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render.com (5 minutes)

1. Go to https://render.com/dashboard
2. Click **"New"** → **"Blueprint"**
3. **Connect** your GitHub repository
4. Click **"Apply"** (uses render.yaml automatically)

### Step 3: Set Environment Variables (2 minutes)

**Backend Service:**
```
NVIDIA_API_KEY=nvapi-<your-key>
DATABASE_URL=sqlite:///./startup_swiper.db
SECRET_KEY=<run: openssl rand -hex 32>
```

**Frontend Service:**
```
VITE_API_URL=https://YOUR-API-NAME.onrender.com
```

## That's It! 🎉

Wait 5-10 minutes for deployment, then test:
- Visit your frontend URL
- Login: nicolas.desaintromain@axa.com / 123
- Try AI Concierge: "Find AI startups"

## What You're Deploying

✅ **Complete Platform:**
- 52 calendar events
- 3,487 startups
- AI Concierge with NVIDIA NIM (DeepSeek-R1)
- New calendar view (list-based, no overlaps)
- Enhanced chat UX
- AXA startup filtering
- Mobile responsive

✅ **Tested Features:**
- Calendar view (redesigned)
- AI Concierge (NVIDIA NIM working)
- Startup search (MCP database integration)
- Chat interface (scrollable, proper colors)
- Authentication
- Filtering

## Need Help?

See **PRODUCTION_DEPLOYMENT.md** for detailed instructions.

---

**Pro Tip:** The first deployment takes ~10 minutes. Subsequent deployments are ~3 minutes.
