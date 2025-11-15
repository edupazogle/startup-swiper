# Quick Start - Enhanced AXA Testing

## ⚡ TL;DR

✅ **Setup Complete**: Enhanced AXA provider list (125 candidates) is ready
✅ **Votes Reset**: Database cleared for fresh testing
✅ **Ready to Launch**: Start the app and test swiping

---

## 🚀 Quick Launch (3 Steps)

### Step 1: Backend
```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
python3 api/main.py
```
*Runs on http://localhost:8000*

### Step 2: Frontend
```bash
cd /home/akyo/startup_swiper/app/startup-swipe-schedu
npm run dev
```
*Usually http://localhost:5173 or 5000*

### Step 3: Test
- Open browser → app URL
- Click "Swipe" tab
- See 125 AXA candidates
- Test voting (swipe right/left)
- Check Dashboard for "Interested" list

---

## 📊 What's New

**Enhanced List**: 125 LLM-assessed candidates (was 8)
**Top Candidate**: ICEYE (80/100 score, $864M funding)
**Data Source**: `downloads/axa_enhanced_final.json`
**API Endpoint**: `GET /startups/axa/filtered`
**Votes**: Reset to 0 for clean testing

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads on localhost
- [ ] "Swipe" tab shows 125 candidates
- [ ] Top startup is ICEYE
- [ ] Swiping right creates vote
- [ ] Dashboard shows interested startups
- [ ] Votes persist on page refresh

---

## 📁 Key Files

| File | Change |
|------|--------|
| `api/main.py:627` | Updated to use `axa_enhanced_final.json` |
| `downloads/axa_enhanced_final.json` | 125 candidates ready |
| `startup_swiper.db` | Votes reset |
| `SETUP_ENHANCED_AXA_TESTING.md` | Detailed guide |

---

## 🎯 Expected Results

**In Swipe Tab:**
- ICEYE (#1, $864M)
- Matillion (#2, $307M)
- M-Files (#3, $146M)
- Yazen (#4, $29M)
- Qare (#5, $30M)
- + 120 more candidates

**In Dashboard:**
- Interested section at top
- Shows swiped-right startups
- Vote counts
- Empty at first (votes reset)

---

## ⚠️ If Something Goes Wrong

**Port 8000 in use?**
```bash
pkill -f "python3 api/main.py"
# Then retry: python3 api/main.py
```

**Module import error?**
```bash
cd /home/akyo/startup_swiper
source .venv/bin/activate
pip install -r api/requirements.txt
```

**Frontend not loading?**
```bash
cd app/startup-swipe-schedu
npm install
npm run dev
```

---

## 📞 Documentation

- **Setup Guide**: `SETUP_ENHANCED_AXA_TESTING.md`
- **Full Details**: `AXA_PROVIDER_FILTERING_FINAL_SUMMARY.md`
- **Tech Info**: `AXA_LLM_ENHANCEMENT_COMPLETE.md`

---

**Status**: ✅ Ready to Launch
**Date**: November 15, 2025
