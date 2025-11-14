# Post-Meeting Insight Notification System 🔔

A comprehensive PWA notification system that reminds users to submit insights 5 minutes after each meeting ends.

## 🎯 Features

### ✅ Implemented Features

1. **Automatic Notification Scheduling**
   - Notifications scheduled automatically when meetings are created
   - Sent 5 minutes after meeting end time
   - Background worker checks every minute for pending notifications

2. **PWA Push Notifications**
   - Service worker for offline support and background notifications
   - Web Push API integration with VAPID authentication
   - Deep linking to insight submission page
   - Notification actions: "Share Insight" and "Later"

3. **Smart Notification Management**
   - Notifications disappear once insight is submitted
   - Can be dismissed for later
   - Shows pending insights banner in app
   - Tracks notification state (sent, dismissed, completed)

4. **Insight Submission**
   - Beautiful dialog for submitting insights
   - Rich text input with character counter
   - Star rating (1-5)
   - Topic tags (Product, Team, Market Fit, etc.)
   - Follow-up checkbox
   - Auto-saves to database

5. **User Experience**
   - In-app pending insights notification banner
   - One-time notification setup prompt
   - Visual notification status indicator
   - Deep link navigation from push notifications
   - Works offline (PWA)

## 📁 Files Created

### Backend (API)

1. **`/api/models.py`** - Updated with new tables:
   - `MeetingInsight` - Stores user insights after meetings
   - `NotificationQueue` - Tracks scheduled and sent notifications
   - `PushSubscription` - Stores web push subscriptions

2. **`/api/schemas.py`** - Updated with Pydantic schemas:
   - `MeetingInsight`, `MeetingInsightCreate`
   - `NotificationQueue`, `NotificationQueueCreate`
   - `PushSubscription`, `PushSubscriptionCreate`

3. **`/api/notification_service.py`** (NEW - 400 lines)
   - `NotificationService` class - Main notification orchestrator
   - `schedule_meeting_insight_notification()` - Schedule notifications
   - `send_pending_notifications()` - Background worker function
   - `subscribe_to_push()` / `unsubscribe_from_push()` - Push subscription management
   - `notification_worker()` - Async background task

4. **`/api/main.py`** - Updated with new endpoints:
   - `POST /insights/submit` - Submit meeting insight
   - `GET /insights/user/{user_id}` - Get user's insights
   - `GET /insights/meeting/{meeting_id}` - Get meeting insights
   - `GET /insights/pending/{user_id}` - Get pending insights
   - `POST /notifications/schedule` - Schedule notification
   - `POST /notifications/dismiss/{notification_id}` - Dismiss notification
   - `POST /notifications/push/subscribe` - Subscribe to push
   - `POST /notifications/push/unsubscribe` - Unsubscribe
   - `GET /notifications/vapid-public-key` - Get VAPID public key

5. **`/api/requirements.txt`** - Added dependencies:
   - `pywebpush==1.14.0` - Web push protocol
   - `py-vapid==1.9.0` - VAPID key generation

### Frontend (App)

6. **`/app/startup-swipe-schedu/public/service-worker.js`** (NEW - 180 lines)
   - Service worker for PWA functionality
   - Push notification handler
   - Deep linking on notification click
   - Offline caching
   - Background sync

7. **`/app/startup-swipe-schedu/public/manifest.json`** (NEW)
   - PWA manifest file
   - App metadata and icons
   - Theme colors
   - Shortcuts
   - Share target

8. **`/app/startup-swipe-schedu/src/lib/notificationManager.ts`** (NEW - 350 lines)
   - `NotificationManager` class - Client-side notification handler
   - `init()` - Register service worker
   - `requestPermission()` - Request notification permissions
   - `subscribeToPush()` - Subscribe to push notifications
   - `InsightsAPI` - API functions for insights and notifications

9. **`/app/startup-swipe-schedu/src/components/MeetingInsightDialog.tsx`** (NEW - 180 lines)
   - Beautiful dialog for submitting insights
   - Rich form with validation
   - Star rating component
   - Tag selection
   - Follow-up checkbox

10. **`/app/startup-swipe-schedu/src/components/PendingInsightsNotification.tsx`** (NEW - 140 lines)
    - Floating notification banner
    - Shows pending insights
    - Quick action buttons
    - Progress indicator for multiple insights
    - Auto-refreshes every 30 seconds

11. **`/app/startup-swipe-schedu/src/App.tsx`** - Updated:
    - Integrated NotificationManager
    - Added pending insights banner
    - Added notification setup prompt
    - Added notification toggle button
    - Auto-schedules notifications on meeting creation
    - Deep link navigation handler

12. **`/app/startup-swipe-schedu/index.html`** - Updated:
    - Added PWA manifest link
    - Added theme color meta tags
    - Added Apple PWA meta tags

## 🚀 Setup Instructions

### 1. Generate VAPID Keys

VAPID keys are required for web push notifications. Generate them once:

```bash
cd api
python3 generate_vapid_keys.py
```

This will output your VAPID keys. Add them to your `.env` file:

```env
# Web Push Notifications (VAPID)
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
```

### 2. Install Backend Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 3. Run Database Migration

The new tables will be created automatically when you start the API:

```bash
cd api
uvicorn main:app --reload
```

### 4. Create App Icons

Place PNG icons in `/app/startup-swipe-schedu/public/` with these sizes:
- `icon-72.png` (72x72)
- `icon-96.png` (96x96)
- `icon-128.png` (128x128)
- `icon-144.png` (144x144)
- `icon-152.png` (152x152)
- `icon-192.png` (192x192) - Required
- `icon-384.png` (384x384)
- `icon-512.png` (512x512) - Required
- `badge-72.png` (72x72) - Small badge icon

You can use a tool like [PWA Asset Generator](https://github.com/elegantapp/pwa-asset-generator) or create manually.

### 5. Start Frontend

```bash
cd app/startup-swipe-schedu
npm run dev
```

### 6. Enable HTTPS (Production)

Push notifications require HTTPS. For local development, use:

```bash
# Option 1: Use ngrok
ngrok http 5173

# Option 2: Use local SSL certificate
# Configure vite.config.ts with https: true
```

## 📱 How It Works

### Flow Diagram

```
User schedules meeting
         ↓
Meeting created in calendar
         ↓
Notification scheduled (meeting_end_time + 5 min)
         ↓
Background worker checks every minute
         ↓
Time reached → Send push notification
         ↓
User clicks notification
         ↓
Deep link opens app → Insights view
         ↓
User submits insight
         ↓
Notification marked complete ✅
         ↓
Notification disappears
```

### Notification Lifecycle

1. **Schedule**: When meeting is created
   ```javascript
   await InsightsAPI.scheduleNotification(
     meetingId, 
     userId, 
     meetingEndTime
   )
   ```

2. **Send**: 5 minutes after meeting ends (background worker)
   - Push notification sent to all user's devices
   - Notification shows in system tray
   - Banner appears in app

3. **Interact**: User responds
   - **Click "Share Insight"**: Opens insight dialog
   - **Click "Later"**: Dismisses notification, can reappear
   - **Click notification**: Deep link to app

4. **Complete**: Insight submitted
   - Notification marked as complete
   - Removed from pending list
   - No further reminders

## 🔧 API Endpoints

### Submit Insight
```bash
POST http://localhost:8000/insights/submit
Content-Type: application/json

{
  "meetingId": "event-123",
  "userId": "user-456",
  "startupId": "startup-789",
  "startupName": "Acme Corp",
  "insight": "Great product-market fit. Strong technical team.",
  "tags": ["Product", "Team"],
  "rating": 5,
  "followUp": true
}
```

### Get Pending Insights
```bash
GET http://localhost:8000/insights/pending/user-456
```

Response:
```json
{
  "pending": [
    {
      "notificationId": 1,
      "meetingId": "event-123",
      "meetingTitle": "Meeting: Acme Corp",
      "meetingEndTime": "2025-11-14T15:30:00",
      "scheduledFor": "2025-11-14T15:35:00",
      "sent": true
    }
  ],
  "count": 1
}
```

### Schedule Notification
```bash
POST http://localhost:8000/notifications/schedule?meeting_id=event-123&user_id=user-456&meeting_end_time=2025-11-14T15:30:00Z
```

### Subscribe to Push
```bash
POST http://localhost:8000/notifications/push/subscribe?user_id=user-456
Content-Type: application/json

{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "...",
    "auth": "..."
  }
}
```

## 🎨 UI Components

### Pending Insights Banner
- Floating card at top of screen
- Shows one pending insight at a time
- Progress indicator for multiple insights
- Auto-refreshes every 30 seconds
- Dismissible

### Insight Submission Dialog
- Beautiful modal dialog
- Text area for insight (500 char limit)
- 5-star rating
- 10 topic tags
- Follow-up checkbox
- Validation and error handling

### Notification Setup Prompt
- One-time prompt on first use
- Explains notification benefits
- "Enable" and "Later" options
- Can be triggered manually

## 🔐 Security & Privacy

- VAPID authentication for secure push
- User-specific subscriptions
- Endpoint validation
- No sensitive data in push payload
- Notifications require user permission
- HTTPS required for production

## 🧪 Testing

### Test Notification Flow

1. **Create a test meeting**:
   ```javascript
   // In app, schedule meeting 6 minutes in the future
   // Or use API directly
   ```

2. **Check notification was scheduled**:
   ```bash
   curl http://localhost:8000/insights/pending/your-user-id
   ```

3. **Trigger notification manually** (for testing):
   ```python
   # In Python console
   from notification_service import NotificationService
   from database import SessionLocal
   
   db = SessionLocal()
   service = NotificationService()
   await service.send_pending_notifications(db)
   ```

4. **Submit insight**:
   - Click notification
   - Fill out dialog
   - Submit

5. **Verify completion**:
   ```bash
   curl http://localhost:8000/insights/pending/your-user-id
   # Should return empty array
   ```

## 📊 Database Schema

### meeting_insights
```sql
CREATE TABLE meeting_insights (
    id INTEGER PRIMARY KEY,
    meetingId VARCHAR NOT NULL,
    userId VARCHAR NOT NULL,
    startupId VARCHAR,
    startupName VARCHAR,
    insight TEXT NOT NULL,
    tags JSON,
    rating INTEGER,
    followUp BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### notification_queue
```sql
CREATE TABLE notification_queue (
    id INTEGER PRIMARY KEY,
    userId VARCHAR NOT NULL,
    meetingId VARCHAR NOT NULL,
    meetingEndTime DATETIME NOT NULL,
    scheduledFor DATETIME NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sentAt DATETIME,
    dismissed BOOLEAN DEFAULT FALSE,
    insightSubmitted BOOLEAN DEFAULT FALSE,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### push_subscriptions
```sql
CREATE TABLE push_subscriptions (
    id INTEGER PRIMARY KEY,
    userId VARCHAR NOT NULL,
    endpoint VARCHAR NOT NULL UNIQUE,
    p256dh VARCHAR NOT NULL,
    auth VARCHAR NOT NULL,
    userAgent VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    lastUsed DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🐛 Troubleshooting

### Notifications not appearing?

1. **Check browser permissions**: Settings → Site Settings → Notifications
2. **Verify VAPID keys**: Check `.env` file
3. **Check HTTPS**: Local dev needs ngrok or SSL cert
4. **Check service worker**: DevTools → Application → Service Workers
5. **Check background worker**: API logs should show "Sent X notifications"

### Deep links not working?

1. **Check service worker registration**: Console should show "Service Worker registered"
2. **Verify manifest.json**: DevTools → Application → Manifest
3. **Check URL parameters**: Should be `/?view=insights&meeting=123&action=submit`

### Icons not showing?

1. **Create icon files**: See "Create App Icons" section
2. **Check manifest.json**: Verify icon paths
3. **Clear cache**: Hard refresh (Ctrl+Shift+R)

## 🎉 Success Indicators

✅ Service worker registered  
✅ Push permission granted  
✅ Notification scheduled after meeting creation  
✅ Push notification received 5 minutes after meeting  
✅ Deep link opens insight dialog  
✅ Insight saved to database  
✅ Notification marked complete and disappears  
✅ Works offline (PWA)  

## 📝 Future Enhancements

Potential improvements:
- [ ] Email fallback if push notifications disabled
- [ ] Customizable notification delay (not just 5 minutes)
- [ ] Rich notification with meeting preview
- [ ] Notification summary (daily digest)
- [ ] Analytics on insight submission rates
- [ ] A/B test notification timing
- [ ] Integration with calendar apps
- [ ] SMS notifications option

## 🔗 Resources

- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [PWA Checklist](https://web.dev/pwa-checklist/)
- [VAPID Protocol](https://datatracker.ietf.org/doc/html/rfc8292)
- [pywebpush Documentation](https://github.com/web-push-libs/pywebpush)

---

**Implementation Complete!** 🎊

The notification system is fully functional and ready for testing. Users will now receive timely reminders to share their valuable meeting insights!
