# GitHub Actions Deployment Setup

## Required GitHub Secrets

To enable automatic deployment, you need to configure the following secrets in your GitHub repository:

### How to Add Secrets:
1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

### Required Secrets:

#### `DO_SSH_PRIVATE_KEY`
Your SSH private key for accessing the DigitalOcean server.

**To get your key:**
```bash
cat ~/.ssh/id_rsa
```

Copy the **entire content** including:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

#### `DO_HOST`
The hostname or IP address of your DigitalOcean server.

**Value:**
```
tilyn.ai
```

#### `DO_USER`
The SSH user for connecting to the server.

**Value:**
```
root
```

---

## Deployment Workflow

### Automatic Deployment
The workflow triggers automatically on:
- ✅ Push to `main` branch
- ✅ Changes to code files (not docs/README)

### Manual Deployment
You can also trigger deployment manually:
1. Go to **Actions** tab
2. Select **Deploy to Production (DigitalOcean)**
3. Click **Run workflow**
4. Select branch and click **Run workflow**

---

## What Gets Deployed

### ✅ Deployed:
- Frontend (React app from `app/startup-swipe-schedu/dist/`)
- API code (Python files from `api/`)
- API dependencies (from `requirements.txt`)

### 🛡️ Protected (NOT deployed):
- **Production database** (`startup_swiper.db`)
- **Environment variables** (`.env` files)
- **Virtual environments** (`venv`, `.venv`)
- **Log files** (`logs/`)
- **Python cache** (`__pycache__`, `*.pyc`)

---

## Safety Features

1. **Database Protection**: The workflow explicitly excludes `*.db` files to prevent overwriting production data

2. **Hostname Detection**: Frontend uses runtime hostname detection for API URL:
   - Production (`tilyn.ai`): `https://tilyn.ai/api`
   - Local dev: `http://localhost:8000`
   - No hardcoded URLs in build!

3. **Health Checks**: Deployment verifies:
   - API responds to health check
   - Frontend returns 200 status
   - Fails deployment if checks fail

4. **Rollback Safety**: Existing files are preserved until new ones are successfully copied

---

## Monitoring Deployment

### View Workflow Status:
1. Go to **Actions** tab
2. Click on the latest workflow run
3. See real-time logs for each step

### Check Deployment Summary:
Each deployment creates a summary showing:
- Commit SHA and branch
- Deployed components
- Protected components
- Direct link to the app

---

## Troubleshooting

### Deployment Failed?

**Check the logs:**
1. Go to Actions tab
2. Click the failed workflow
3. Review the failed step

**Common issues:**

1. **SSH Connection Failed**
   - Verify `DO_SSH_PRIVATE_KEY` is correct
   - Check `DO_HOST` is reachable
   - Ensure SSH key is added to server

2. **API Won't Start**
   - Check API logs: `/home/appuser/startup-swiper/logs/api.log`
   - Verify dependencies installed correctly
   - Check for Python errors

3. **Frontend Not Loading**
   - Verify nginx is running
   - Check nginx config: `/etc/nginx/sites-enabled/startup-swiper`
   - Look for build errors in workflow logs

### Manual Rollback:

If deployment breaks production:

```bash
# SSH to server
ssh root@tilyn.ai

# Check API logs
tail -100 /home/appuser/startup-swiper/logs/api.log

# Restart API manually
pkill -f 'uvicorn.*8000'
cd /home/appuser/startup-swiper/api
/home/appuser/startup-swiper/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &

# Check frontend
curl localhost:5000
```

---

## Local Development

The workflow is configured to **NOT** affect local development:

- Local `.env` uses `localhost:8000`
- Production uses runtime hostname detection
- Database changes only happen locally
- You can test deployment in a branch before merging to `main`

---

## Security Notes

⚠️ **Never commit:**
- SSH private keys
- `.env` files with secrets
- Database files
- API keys or tokens

✅ **Always use:**
- GitHub Secrets for sensitive data
- Environment variables for configuration
- `.gitignore` to exclude sensitive files

---

## Testing Deployment

Before merging to `main`, you can:

1. **Test build locally:**
   ```bash
   cd app/startup-swipe-schedu
   npm run build
   ```

2. **Test API locally:**
   ```bash
   cd api
   python3 -m pytest  # if you have tests
   ```

3. **Deploy to staging first** (if you have a staging server)

4. **Use workflow_dispatch** to manually deploy from a feature branch

---

## Questions?

- Check workflow logs in Actions tab
- Review this README
- Check deployment summary after each run
- SSH to server to inspect issues directly

