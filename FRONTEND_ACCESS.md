# Frontend Access Guide

## ✅ Frontend Status: RUNNING

The frontend is confirmed running and responding on port 5000.

## 🌐 Access URLs

Try these URLs in order:

### Local Machine
```
http://localhost:5000
http://127.0.0.1:5000
```

### Network Access (from other machines)
```
http://172.29.0.109:5000
http://10.255.255.254:5000
```

## 🔧 If "This site can't be reached"

### 1. Clear Browser Cache
```
Press: Ctrl + Shift + Delete
Select: Cached images and files
Clear data
```

Or hard refresh:
```
Press: Ctrl + Shift + R (Windows/Linux)
Press: Cmd + Shift + R (Mac)
```

### 2. Try Different Browser
- Chrome
- Firefox
- Edge
- Safari

### 3. Check Service Worker
1. Press **F12**
2. Go to **Application** tab
3. Click **Service Workers**
4. Click **Unregister** for localhost:5000
5. Refresh page

### 4. Disable Browser Extensions
- Try in Incognito/Private mode
- Disable ad blockers
- Disable VPN

### 5. Check Firewall
```bash
# Allow port 5000
sudo ufw allow 5000
```

### 6. Verify Services
```bash
# Check if running
lsof -i :5000

# Should show:
# node ... *:5000 (LISTEN)
```

## 🧪 Test Connection

### From Terminal
```bash
# Should return HTML
curl http://localhost:5000

# Should return: <title>Startup Rise 🚀 @Slush2025</title>
curl -s http://localhost:5000 | grep title
```

### From Browser Console (F12)
```javascript
// Test fetch
fetch('http://localhost:5000')
  .then(r => r.text())
  .then(t => console.log(t.substring(0, 100)))
```

## 📊 Current Status

```
✓ Port 5000: LISTENING
✓ Vite Process: RUNNING
✓ HTTP Response: 200 OK
✓ HTML Served: Yes
✓ Title: "Startup Rise 🚀 @Slush2025"
```

## 🔍 Diagnostic Commands

```bash
# Check if frontend is responding
curl -I http://localhost:5000
# Should return: HTTP/1.1 200 OK

# Check logs
tail -f logs/frontend.log

# Restart if needed
pkill -f vite
cd app/startup-swipe-schedu
npm run dev
```

## 💡 Common Issues

### Issue: "ERR_CONNECTION_REFUSED"
**Cause**: Service not running  
**Fix**: `./simple_launch.sh restart`

### Issue: "ERR_CONNECTION_RESET"
**Cause**: Firewall blocking  
**Fix**: Allow port 5000 in firewall

### Issue: Blank page
**Cause**: Service worker caching  
**Fix**: Clear service worker (see step 3 above)

### Issue: "This site can't be reached" but curl works
**Cause**: Browser cache or proxy  
**Fix**: 
1. Clear browser cache
2. Try incognito mode
3. Try different browser

## ✨ Verification

If working correctly, you should see:
- Aurora background animation
- "Startup Rise" logo
- Navigation tabs at bottom
- Startup cards in swipe view

## 📞 Network Info

```
Server listening on:
  • Local:   http://localhost:5000/
  • Network: http://10.255.255.254:5000/
  • Network: http://172.29.0.109:5000/
```

## 🎯 Quick Fix Checklist

- [ ] Hard refresh (Ctrl+Shift+R)
- [ ] Clear browser cache
- [ ] Try incognito mode
- [ ] Unregister service worker
- [ ] Try different browser
- [ ] Try 127.0.0.1:5000 instead of localhost
- [ ] Check firewall settings
- [ ] Verify service is running: `lsof -i :5000`

---

**Frontend is confirmed RUNNING and RESPONDING.**

If you still see "This site can't be reached", the issue is with:
- Browser cache/cookies
- Service worker
- Network/firewall
- Browser extensions

Try the steps above in order. 99% of issues are resolved by clearing cache and service worker.
