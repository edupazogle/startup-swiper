# Production Deployment - Complete Implementation

This directory contains everything needed for a fully production-ready deployment of the Startup Swiper application on Digital Ocean.

## 🎯 What's Included

### Configuration Files

1. **`nginx-production.conf`** - Complete NGINX configuration
   - HTTPS/SSL termination
   - API reverse proxy (all endpoints)
   - Static file serving
   - CORS headers
   - Compression
   - Security headers
   - WebSocket support

2. **`startup-swiper.service`** - Systemd service definition
   - Auto-start on boot
   - Auto-restart on failure
   - Proper logging
   - Resource limits
   - Security hardening

3. **`.github/workflows/deploy-production.yml`** - CI/CD Pipeline
   - Automated deployment on push
   - Frontend build & deploy
   - API code & dependencies update
   - NGINX configuration deployment
   - Health checks & verification

### Deployment Scripts

1. **`deploy-nginx.sh`** - NGINX configuration deployment
   - Backs up existing config
   - Tests new configuration
   - Rolls back on error
   - Reloads NGINX safely

2. **`verify_production.sh`** - Comprehensive production verification
   - 15 automated tests
   - Frontend accessibility
   - API health
   - User authentication flow
   - SSL certificate
   - Performance checks
   - Security headers

3. **`test_what_works.sh`** - Quick status check
4. **`test_production.sh`** - Full API test suite
5. **`test_production_comprehensive.sh`** - Detailed endpoint tests

### Documentation

1. **`DEPLOYMENT_GUIDE.md`** - Step-by-step deployment instructions
2. **`PRODUCTION_DEPLOYMENT_STATUS.md`** - Current deployment status
3. **This README** - Overview and quick reference

---

## 🚀 Quick Start

### Prerequisites

Ensure these GitHub Secrets are configured:
- `DO_SSH_PRIVATE_KEY` - SSH private key for server access
- `DO_HOST` - Server IP address or hostname
- `DO_USER` - SSH username (typically `appuser`)

### Deploy to Production

```bash
# Commit and push changes
git add -A
git commit -m "Deploy to production"
git push origin main

# Or trigger manually
gh workflow run deploy-production.yml

# Monitor deployment
gh run watch
```

### First-Time Server Setup

On the Digital Ocean server, run these commands:

```bash
# 1. Install NGINX configuration
cd /home/appuser/startup-swiper
sudo bash deploy-nginx.sh

# 2. Install systemd service
sudo cp startup-swiper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable startup-swiper
sudo systemctl start startup-swiper

# 3. Verify everything works
./verify_production.sh
```

---

## ✅ Verification

### Automated Testing

```bash
# Run comprehensive verification (recommended)
./verify_production.sh

# Expected output: All 15 tests passing
# ✓ PRODUCTION READY - All tests passed!
```

### Manual Verification

```bash
# 1. Check frontend
curl -I https://tilyn.ai/
# Should return: HTTP/2 200

# 2. Check API health
curl https://tilyn.ai/api/health
# Should return: {"status":"healthy", ...}

# 3. Test user registration
curl -X POST https://tilyn.ai/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@test.com","password":"Test123!","username":"testuser"}'
# Should return: User object with ID

# 4. Test authentication
curl -X POST https://tilyn.ai/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@test.com","password":"Test123!"}'
# Should return: JWT access token
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Digital Ocean Server                     │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ NGINX (Port 80/443)                                     │ │
│  │  - SSL Termination                                      │ │
│  │  - Static file serving (/frontend)                      │ │
│  │  - Reverse proxy (/api, /auth, /concierge, etc)        │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│                 ▼                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FastAPI (Port 8000 - localhost only)                   │ │
│  │  - 91 API endpoints                                     │ │
│  │  - AI Concierge (Qwen agents)                          │ │
│  │  - User authentication (JWT)                           │ │
│  │  - Startup data & insights                             │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│                 ▼                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ SQLite Database                                         │ │
│  │  - 3,665+ startups                                      │ │
│  │  - User accounts                                        │ │
│  │  - Events, meetings, insights                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Production Features

### Frontend (React + Vite)
- ✅ Built and optimized bundle
- ✅ PWA support (15MB cache)
- ✅ Responsive design
- ✅ Auroral theme system
- ✅ Service worker for offline support
- ✅ Performance optimizations

### Backend (FastAPI + Python)
- ✅ 91 API endpoints
- ✅ JWT authentication
- ✅ AI-powered concierge
- ✅ Event search & management
- ✅ Startup insights generation
- ✅ WhitePaper analysis
- ✅ Real-time features

### Infrastructure
- ✅ HTTPS/SSL enabled
- ✅ Auto-deployment via GitHub Actions
- ✅ Systemd service management
- ✅ Automated health checks
- ✅ Log rotation configured
- ✅ Security headers
- ✅ CORS properly configured
- ✅ Compression enabled

---

## 🔧 Maintenance

### View Logs

```bash
# API logs
sudo journalctl -u startup-swiper -f

# Or direct log files
tail -f /home/appuser/startup-swiper/logs/api.log

# NGINX logs
sudo tail -f /var/log/nginx/tilyn.ai-access.log
sudo tail -f /var/log/nginx/tilyn.ai-error.log
```

### Restart Services

```bash
# Restart API
sudo systemctl restart startup-swiper

# Reload NGINX (without downtime)
sudo systemctl reload nginx

# Check status
sudo systemctl status startup-swiper
sudo systemctl status nginx
```

### Database Backup

```bash
# Create backup
cp /home/appuser/startup-swiper/startup_swiper.db \
   /home/appuser/backups/startup_swiper_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 /home/appuser/startup-swiper/startup_swiper.db \
  ".backup '/home/appuser/backups/startup_swiper_$(date +%Y%m%d).db'"
```

### Update Application

```bash
# Automatic (recommended)
git push origin main

# Manual
ssh appuser@<server-ip>
cd /home/appuser/startup-swiper
git pull
sudo systemctl restart startup-swiper
```

---

## 🔐 Security

### Implemented Security Features

- ✅ HTTPS/TLS 1.2+ only
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ JWT authentication
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS properly configured
- ✅ Firewall configured (UFW)
- ✅ Systemd security hardening
- ✅ No exposed credentials

### Security Checklist

```bash
# Check SSL certificate
sudo certbot certificates

# Check firewall status
sudo ufw status

# Check for security updates
sudo apt list --upgradable

# Review API logs for suspicious activity
sudo journalctl -u startup-swiper | grep -i error
```

---

## 📈 Monitoring

### Health Check Endpoints

- **API**: https://tilyn.ai/api/health
- **Frontend**: https://tilyn.ai/
- **Docs**: https://tilyn.ai/api/docs

### Setup Automated Monitoring

Add to crontab:
```bash
crontab -e

# Add:
*/5 * * * * /home/appuser/startup-swiper/verify_production.sh > /dev/null || echo "Production check failed" | mail -s "Alert" admin@example.com
```

---

## 🐛 Troubleshooting

### Common Issues

1. **API Not Starting**
   ```bash
   # Check logs
   sudo journalctl -u startup-swiper -n 50
   
   # Check process
   ps aux | grep uvicorn
   
   # Restart
   sudo systemctl restart startup-swiper
   ```

2. **NGINX 502 Bad Gateway**
   ```bash
   # Check if API is running
   curl http://localhost:8000/health
   
   # Check NGINX error log
   sudo tail -f /var/log/nginx/tilyn.ai-error.log
   ```

3. **Database Locked**
   ```bash
   # Check for stale connections
   lsof | grep startup_swiper.db
   
   # Restart API
   sudo systemctl restart startup-swiper
   ```

4. **SSL Certificate Expired**
   ```bash
   # Renew certificate
   sudo certbot renew
   
   # Reload NGINX
   sudo systemctl reload nginx
   ```

---

## 📞 Support

- **Documentation**: See `DEPLOYMENT_GUIDE.md`
- **API Docs**: https://tilyn.ai/api/docs
- **Status**: Run `./verify_production.sh`
- **Issues**: Check GitHub Issues

---

## 🎉 Success Criteria

Your production deployment is complete when:

- [ ] `./verify_production.sh` shows all tests passing
- [ ] Frontend loads at https://tilyn.ai
- [ ] API health check returns 200 OK
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] Authenticated endpoints work
- [ ] SSL certificate is valid
- [ ] Systemd service is running
- [ ] Logs are being written
- [ ] Performance is acceptable (<2s response time)

---

**Last Updated**: November 17, 2025  
**Version**: 2.0.0 - Complete Production Implementation
