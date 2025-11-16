# SSL Setup for tilyn.ai

## ✅ DNS Configuration Verified

Your domain `tilyn.ai` is correctly pointing to: **209.38.38.11**

---

## 🔒 Quick SSL Setup (5 minutes)

### Option 1: One-Command Setup

SSH into your droplet and run this single command:

```bash
ssh root@209.38.38.11

# Then run this:
sudo bash -c 'cat > /etc/nginx/sites-available/startup-swiper << "NGINXEOF"
server {
    listen 80;
    listen [::]:80;
    server_name tilyn.ai www.tilyn.ai;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api {
        rewrite ^/api/(.*) /\$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
NGINXEOF
nginx -t && systemctl reload nginx && certbot --nginx -d tilyn.ai -d www.tilyn.ai --non-interactive --agree-tos --email eduardo.paz@axa.com --redirect'
```

---

### Option 2: Step-by-Step

1. **SSH into droplet:**
   ```bash
   ssh root@209.38.38.11
   ```

2. **Update Nginx config:**
   ```bash
   nano /etc/nginx/sites-available/startup-swiper
   ```
   
   Replace with:
   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name tilyn.ai www.tilyn.ai;

       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /api {
           rewrite ^/api/(.*) /$1 break;
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /health {
           proxy_pass http://localhost:8000/health;
           access_log off;
       }
   }
   ```
   
   Save: `Ctrl+O`, `Enter`, `Ctrl+X`

3. **Test and reload Nginx:**
   ```bash
   nginx -t
   systemctl reload nginx
   ```

4. **Get SSL certificate:**
   ```bash
   certbot --nginx -d tilyn.ai -d www.tilyn.ai \
       --non-interactive \
       --agree-tos \
       --email eduardo.paz@axa.com \
       --redirect
   ```

5. **Verify:**
   ```bash
   curl -I https://tilyn.ai
   ```

---

## 🎉 After Setup

Your app will be live at:

- **🌍 Main Site:** https://tilyn.ai
- **🌍 WWW:** https://www.tilyn.ai (redirects to main)
- **📚 API Docs:** https://tilyn.ai/api/docs
- **❤️ Health Check:** https://tilyn.ai/health

---

## 🔄 Auto-Renewal

SSL certificates from Let's Encrypt are valid for 90 days.

**Certbot automatically sets up renewal!**

Check renewal status:
```bash
certbot renew --dry-run
```

View cron job:
```bash
systemctl status certbot.timer
```

---

## 🔍 Troubleshooting

### Certificate failed?

**Most common issue:** Services not ready yet

```bash
# Check if backend is running
docker-compose ps

# Check logs
docker-compose logs

# If services aren't ready, wait 5 minutes and try again
certbot --nginx -d tilyn.ai -d www.tilyn.ai \
    --non-interactive \
    --agree-tos \
    --email eduardo.paz@axa.com \
    --redirect
```

### Can't reach site?

```bash
# Check Nginx
systemctl status nginx

# Check firewall
ufw status

# Check if port 80 and 443 are open
netstat -tulpn | grep -E ':80|:443'
```

### Need to restart services?

```bash
cd /home/appuser/startup-swiper
docker-compose restart
systemctl restart nginx
```

---

## 📊 SSL Rating

After setup, test your SSL at:
https://www.ssllabs.com/ssltest/analyze.html?d=tilyn.ai

You should get an **A or A+** rating! 🏆

---

## 💡 Quick Reference

```bash
# View certificate info
certbot certificates

# Force renewal
certbot renew --force-renewal

# Test renewal
certbot renew --dry-run

# Restart Nginx
systemctl restart nginx

# Check Nginx config
nginx -t
```

---

**Need help?** Run these commands and share the output:

```bash
systemctl status nginx
docker-compose ps
certbot certificates
curl -I http://tilyn.ai
```
