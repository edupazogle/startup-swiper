# 🚀 Simple Deployment Guide

## Option 1: Render.com (Recommended - Free & Easiest)

### Prerequisites
- GitHub account
- Render.com account (free)

### Steps (5 minutes):

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin https://github.com/YOUR_USERNAME/startup-swiper.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repo with `render.yaml`
   - Click "Apply"

3. **Set Environment Variables**
   
   In Render Dashboard, for the **API service**, add:
   ```
   DATABASE_URL=sqlite:///./startup_swiper.db
   VAPID_PUBLIC_KEY=<run python3 api/generate_vapid_keys.py>
   VAPID_PRIVATE_KEY=<from same script>
   OPENAI_API_KEY=<your key if using AI features>
   ```

4. **Update Frontend API URL**
   
   In Render Dashboard, for the **Frontend service**, set:
   ```
   VITE_API_URL=https://YOUR-API-NAME.onrender.com
   ```

5. **Share URL** 🎉
   ```
   Frontend: https://YOUR-APP-NAME.onrender.com
   API: https://YOUR-API-NAME.onrender.com
   ```

### ✅ That's it! Your app is live.

**Note:** Free tier sleeps after 15min inactivity (cold start ~30s on first visit).

---

## Option 2: Vercel (Frontend) + Render (Backend)

### Frontend on Vercel:
1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repo
3. Set root directory: `app/startup-swipe-schedu`
4. Deploy!

### Backend on Render:
Same as Option 1, but only deploy the API service.

---

## Option 3: Railway.app (Alternative to Render)

1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Add services manually:
   - **API**: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Frontend**: `cd app/startup-swipe-schedu && npm run build && npm run preview -- --host 0.0.0.0 --port $PORT`

---

## Option 4: Docker + Any Platform (More Setup)

```bash
# Build
docker build -t startup-swiper .

# Run locally
docker run -p 3000:3000 -p 8000:8000 startup-swiper
```

Deploy to: Fly.io, DigitalOcean, AWS, etc.

---

## Quick Comparison

| Platform | Setup Time | Free Tier | Best For |
|----------|-----------|-----------|----------|
| **Render** | 5 min | ✅ Yes | Simplest full-stack |
| **Vercel + Render** | 8 min | ✅ Yes | Best performance |
| **Railway** | 7 min | ✅ Limited | Good alternative |
| **Docker** | 30+ min | Varies | Full control |

---

## Pre-Deployment Checklist

- [ ] Generate VAPID keys: `python3 api/generate_vapid_keys.py`
- [ ] Set environment variables in platform
- [ ] Update frontend API URL to production endpoint
- [ ] Test locally first: `./launch.sh`
- [ ] Push to GitHub
- [ ] Deploy!

---

## Testing Your Deployment

1. Visit your frontend URL
2. Create an account
3. Browse startups
4. Schedule a meeting
5. Check notifications work
6. Share URL with testers!

---

## Environment Variables Needed

### Backend (.env):
```env
DATABASE_URL=sqlite:///./startup_swiper.db
VAPID_PUBLIC_KEY=BG7x...
VAPID_PRIVATE_KEY=Kxp9...
OPENAI_API_KEY=sk-...
LITELLM_LOG_LEVEL=INFO
```

### Frontend:
```env
VITE_API_URL=https://your-api.onrender.com
```

---

## Common Issues

**Issue**: Frontend can't reach backend
- **Fix**: Check VITE_API_URL points to deployed API (not localhost)
- **Fix**: Enable CORS in backend for your frontend domain

**Issue**: Cold starts slow
- **Fix**: Render free tier sleeps. Upgrade to keep alive, or accept 30s first load

**Issue**: Database resets
- **Fix**: Use PostgreSQL instead of SQLite for production
- **Fix**: On Render, add PostgreSQL database (free tier available)

---

## Need Help?

Check:
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- Your `QUICK_START.md` for local setup

🎉 **Happy Testing!**
