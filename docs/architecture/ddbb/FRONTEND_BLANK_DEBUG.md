# Frontend Blank Screen - Debugging Guide

## Issue
Frontend shows blank page at http://localhost:5000

## ✅ Fixed Issues

1. **React Hooks Error**: Moved `useState` and `useEffect` hooks inside the component
2. **TypeScript Errors**: Fixed `EventCategory` type casting with `as any`

## 🔍 Verification Steps

### 1. Check Services
```bash
# API
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# Frontend
curl http://localhost:5000
# Should return HTML with <div id="root"></div>
```

### 2. Check Browser Console
1. Open http://localhost:5000
2. Press F12 to open Developer Tools
3. Click "Console" tab
4. Look for errors (red text)

### Common Errors to Check:
- ❌ `Failed to fetch` → API not running
- ❌ `Cannot read property` → Missing data
- ❌ `Unexpected token` → JSON parse error  
- ❌ `Module not found` → Import error

### 3. Check Network Tab
1. In Developer Tools, click "Network" tab
2. Refresh page (F5)
3. Check for failed requests (red status)

Should see:
- ✅ `/@vite/client` → 200 OK
- ✅ `/src/main.tsx` → 200 OK
- ✅ `/src/App.tsx` → 200 OK

### 4. Check React Rendering
In browser console, run:
```javascript
document.getElementById('root')
// Should show: <div id="root">...</div> with content
// If empty: React not rendering
```

## 🛠️ Quick Fixes

### If API Not Running
```bash
cd /home/akyo/startup_swiper
./simple_launch.sh restart
```

### If Frontend Not Loading
```bash
cd /home/akyo/startup_swiper/app/startup-swipe-schedu

# Rebuild
npm run build

# Restart dev server
pkill -f vite
npm run dev
```

### If TypeScript Errors
```bash
cd /home/akyo/startup_swiper/app/startup-swipe-schedu
npx tsc --noEmit
# Fix any errors shown
```

## 📋 Checklist

- ✅ API running on port 8000
- ✅ Frontend serving on port 5000
- ✅ HTML contains `<div id="root"></div>`
- ✅ Vite client loading
- ✅ No TypeScript errors
- ✅ No build errors
- 🔄 Check browser console for runtime errors
- 🔄 Check network tab for failed requests

## 🎯 Expected Behavior

When working correctly:
1. Open http://localhost:5000
2. See Slush 2025 UI with aurora background
3. See startup cards in swipe view
4. Navigation tabs at bottom

## 📞 Debug Commands

```bash
# Check all processes
ps aux | grep -E "uvicorn|vite" | grep -v grep

# Check logs
tail -f /home/akyo/startup_swiper/logs/api.log
tail -f /home/akyo/startup_swiper/logs/frontend.log

# Test API
curl http://localhost:8000/startups/all?limit=1

# Check frontend files
curl -s http://localhost:5000/src/App.tsx | head -20
```

## 🔧 Manual Test

Visit in browser:
1. http://localhost:8000/docs - Should show Swagger UI
2. http://localhost:5000 - Should show app

If still blank:
1. Open browser console (F12)
2. Look for error messages
3. Check Network tab for failed requests
4. Report error messages for further debugging

## ✨ Most Likely Causes

1. **JavaScript Error**: Check browser console
2. **API Not Responding**: Check if API is running
3. **CORS Issues**: Already configured, but check network tab
4. **Missing Dependencies**: Run `npm install` in frontend dir
5. **TypeScript Error**: Run `npx tsc --noEmit` to check

## 💡 Next Steps

If blank screen persists:
1. Open browser Developer Tools (F12)
2. Copy any error messages from Console tab
3. Check Network tab for red (failed) requests
4. Report specific error for targeted fix
