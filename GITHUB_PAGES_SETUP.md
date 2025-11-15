# GitHub Pages Deployment Instructions

## Step 1: Enable GitHub Pages

1. Go to your repository: https://github.com/edupazogle/startup-swiper
2. Click **Settings** (top right)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
5. Save

## Step 2: Verify Deployment

The workflow will automatically trigger. Check progress:
1. Click **Actions** tab in your repo
2. Look for "Deploy Frontend to GitHub Pages" workflow
3. Wait for it to complete (green checkmark)

## Step 3: Access Your App

Once deployed (2-5 minutes), visit:

**Frontend**: https://edupazogle.github.io/startup-swiper/
**Backend API**: https://startup-swiper-1.onrender.com
**API Health**: https://startup-swiper-1.onrender.com/health

## Test the Application

### Login Credentials:
- **Email**: nicolas.desaintromain@axa.com
- **Password**: 123

### Test Features:
- ✅ Login and see dashboard
- ✅ Swipe through startups
- ✅ Heart button to add/remove favorites
- ✅ View calendar events
- ✅ Chat with AI Concierge
- ✅ Filter startups by industry

## Future Deployments

The workflow will automatically redeploy whenever you:
1. Push changes to the `main` branch
2. Modify files in `app/startup-swipe-schedu/`
3. Update `.github/workflows/deploy.yml`

You can manually trigger it by going to:
- **Actions** tab → **Deploy Frontend to GitHub Pages** → **Run workflow** → **Main branch**

## Environment Variables

The deployment automatically sets:
- `VITE_API_URL`: Points to your Render backend
- `VITE_BASE_PATH`: `/startup-swiper/` for GitHub Pages subpath

These are configured in `.github/workflows/deploy.yml`
