# Production Deployment Guide

## Complete Production Setup - tilyn.ai

This guide covers the full production deployment process for the Startup Swiper application.

---

## 🚀 Quick Deployment

### Automatic Deployment (Recommended)

The application automatically deploys when you push to the `main` branch:

```bash
git push origin main
```

Or trigger manually:

```bash
gh workflow run deploy-production.yml
```

### Monitor Deployment

```bash
gh run watch
```

---

## 📋 Prerequisites

### On Digital Ocean Server

1. **Server Access**
   ```bash
   ssh appuser@<server-ip>
   ```

2. **Required Software**
   - Python 3.11+
   - Node.js 18+
   - NGINX
   - Git
   - Certbot (for SSL)

3. **Directory Structure**
   ```
   /home/appuser/startup-swiper/
   ├── api/                  # FastAPI backend
   ├── frontend/             # React frontend (built)
   ├── .venv/               # Python virtual environment
   ├── startup_swiper.db    # SQLite database
   ├── logs/                # Application logs
   ├── nginx-production.conf
   └── deploy-nginx.sh
   ```

4. **Environment Variables**
   
   Create `/home/appuser/startup-swiper/api/.env`:
   ```bash
   # API Keys
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   
   # Database
   DATABASE_URL=sqlite:///./startup_swiper.db
   
   # JWT Secret (generate with: openssl rand -hex 32)
   JWT_SECRET_KEY=your_secret_key_here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Optional: LangSmith
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=startup-swiper-prod
   ```

---

## 🔧 Manual Setup Steps

### Step 1: Clone Repository

```bash
ssh appuser@<server-ip>
cd /home/appuser
git clone https://github.com/edupazogle/startup-swiper.git
cd startup-swiper
```

### Step 2: Setup Python Backend

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
cd api
pip install -r requirements.txt

# Initialize database (if needed)
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### Step 3: Build Frontend

```bash
cd /home/appuser/startup-swiper/app/startup-swipe-schedu

# Install dependencies
npm install

# Build for production
npm run build

# Copy to frontend directory
mkdir -p /home/appuser/startup-swiper/frontend
cp -r dist/* /home/appuser/startup-swiper/frontend/
```

### Step 4: Configure NGINX

```bash
# Deploy NGINX configuration
cd /home/appuser/startup-swiper
sudo bash deploy-nginx.sh
```

Or manually:

```bash
# Copy configuration
sudo cp nginx-production.conf /etc/nginx/sites-available/tilyn.ai

# Enable site
sudo ln -s /etc/nginx/sites-available/tilyn.ai /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

### Step 5: Setup SSL Certificate

```bash
# Install Certbot (if not already installed)
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d tilyn.ai -d www.tilyn.ai

# Auto-renewal is handled by certbot's systemd timer
sudo systemctl status certbot.timer
```

### Step 6: Start API Service

**Option A: Systemd Service (Recommended)**

Create `/etc/systemd/system/startup-swiper.service`:

```ini
[Unit]
Description=Startup Swiper FastAPI Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/home/appuser/startup-swiper/api
Environment="PATH=/home/appuser/startup-swiper/.venv/bin"
ExecStart=/home/appuser/startup-swiper/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable startup-swiper
sudo systemctl start startup-swiper
sudo systemctl status startup-swiper
```

**Option B: Manual Start**

```bash
cd /home/appuser/startup-swiper/api
nohup /home/appuser/startup-swiper/.venv/bin/uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  > /home/appuser/startup-swiper/logs/api.log 2>&1 &
```

---

## ✅ Verification

### Run Automated Tests

```bash
# Quick check
./test_what_works.sh

# Comprehensive verification
./verify_production.sh
```

### Manual Verification

```bash
# Test API health
curl https://tilyn.ai/api/health

# Test frontend
curl -I https://tilyn.ai/

# Test registration
curl -X POST https://tilyn.ai/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123!","username":"testuser"}'

# Test login
curl -X POST https://tilyn.ai/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

---

## 🔍 Troubleshooting

### API Not Starting

```bash
# Check logs
tail -f /home/appuser/startup-swiper/logs/api.log

# Check process
ps aux | grep uvicorn

# Check port
sudo lsof -i :8000

# Restart manually
cd /home/appuser/startup-swiper/api
pkill -f uvicorn
nohup /home/appuser/startup-swiper/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/api.log 2>&1 &
```

### NGINX Issues

```bash
# Check NGINX status
sudo systemctl status nginx

# Check NGINX logs
sudo tail -f /var/log/nginx/tilyn.ai-error.log
sudo tail -f /var/log/nginx/tilyn.ai-access.log

# Test configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

### Database Issues

```bash
# Check database file
ls -lh /home/appuser/startup-swiper/startup_swiper.db

# Backup database
cp startup_swiper.db startup_swiper.db.backup.$(date +%Y%m%d)

# Check database integrity
sqlite3 startup_swiper.db "PRAGMA integrity_check;"
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R appuser:appuser /home/appuser/startup-swiper

# Fix permissions
chmod -R 755 /home/appuser/startup-swiper
chmod 644 /home/appuser/startup-swiper/startup_swiper.db
```

---

## 🔄 Updates and Maintenance

### Deploy Updates

Automatic (recommended):
```bash
git push origin main
```

Manual:
```bash
ssh appuser@<server-ip>
cd /home/appuser/startup-swiper
git pull origin main
cd app/startup-swipe-schedu
npm install
npm run build
cp -r dist/* ../../frontend/
sudo systemctl restart startup-swiper
```

### Database Backup

```bash
# Create backup
sqlite3 /home/appuser/startup-swiper/startup_swiper.db ".backup '/home/appuser/backups/startup_swiper_$(date +%Y%m%d).db'"

# Or using cp
cp /home/appuser/startup-swiper/startup_swiper.db /home/appuser/backups/startup_swiper_$(date +%Y%m%d).db
```

### Log Rotation

Create `/etc/logrotate.d/startup-swiper`:

```
/home/appuser/startup-swiper/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 appuser appuser
    sharedscripts
    postrotate
        systemctl reload startup-swiper >/dev/null 2>&1 || true
    endscript
}
```

---

## 📊 Monitoring

### Health Checks

Set up automated health checks:

```bash
# Add to crontab
crontab -e

# Add line:
*/5 * * * * curl -sf https://tilyn.ai/api/health > /dev/null || echo "API down!" | mail -s "API Alert" admin@example.com
```

### Performance Monitoring

```bash
# Check API response time
time curl -s https://tilyn.ai/api/health

# Check database size
du -h /home/appuser/startup-swiper/startup_swiper.db

# Check disk space
df -h

# Check memory
free -h
```

---

## 🔐 Security

### Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Keep System Updated

```bash
sudo apt update
sudo apt upgrade
sudo reboot  # if kernel updated
```

### Regular Security Audits

```bash
# Check for security updates
sudo apt list --upgradable

# Check SSL certificate expiry
sudo certbot certificates
```

---

## 📞 Support

- **Documentation**: See `PRODUCTION_DEPLOYMENT_STATUS.md`
- **API Docs**: https://tilyn.ai/api/docs
- **GitHub**: https://github.com/edupazogle/startup-swiper
- **Testing Scripts**: `./verify_production.sh`

---

## ✅ Checklist

- [ ] Server provisioned on Digital Ocean
- [ ] DNS configured (tilyn.ai → server IP)
- [ ] SSL certificate installed
- [ ] NGINX configured and running
- [ ] Python backend running
- [ ] Frontend built and deployed
- [ ] Database initialized
- [ ] Environment variables set
- [ ] Verification tests passing
- [ ] Monitoring configured
- [ ] Backups configured
- [ ] Firewall configured
- [ ] Log rotation configured

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0
