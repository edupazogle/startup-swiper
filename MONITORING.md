# Monitoring Setup - Startup Rise Platform

## UptimeRobot Configuration

Your platform is monitored using UptimeRobot to ensure API and AI agents are always available.

### Quick Start

#### 1. **Set Your API URL**

Edit `/home/akyo/startup_swiper/api/.env` and add:
```bash
API_BASE_URL=https://your-actual-api-url.com
```

#### 2. **Run Setup Script**

```bash
cd /home/akyo/startup_swiper/api
python setup_uptime_monitoring.py
```

This will create 4 monitors:
- ✅ API Health Check
- ✅ Insights AI Agent
- ✅ Meeting AI Agent  
- ✅ Concierge AI Agent

#### 3. **Configure Alerts**

1. Go to [UptimeRobot Settings](https://uptimerobot.com/dashboard#mySettings)
2. Click "Add Alert Contact"
3. Add your email/phone for notifications
4. Re-run the setup script to update monitors with alerts

#### 4. **Check Status Anytime**

```bash
cd /home/akyo/startup_swiper/api
python check_uptime_status.py
```

## What Gets Monitored

| Monitor | Endpoint | Check Interval | What It Checks |
|---------|----------|----------------|----------------|
| API Health | `/health` | Every 5 min | API is responding |
| Insights AI | `/api/ai-concierge/health` | Every 5 min | Insights agent working |
| Meeting AI | `/api/ai-concierge/health` | Every 5 min | Meeting agent working |
| Concierge AI | `/api/ai-concierge/health` | Every 5 min | Concierge agent working |

## Alert Notifications

When a service goes down, you'll receive:
- 📧 **Email** - Instant notification
- 📱 **SMS** - Optional (requires upgrade)
- 💬 **Slack** - Optional webhook integration
- 🔔 **Push** - Mobile app notifications
- 📊 **Status Page** - Public or private status page

### Email Alert Example

```
Subject: [Down] Startup Rise - API Health

Your monitor "Startup Rise - API Health" is DOWN!

Monitor: Startup Rise - API Health
URL: https://your-api.com/health
Status: DOWN
Reason: Connection Timeout
Time: 2025-11-17 14:30:00 UTC

View monitor: https://uptimerobot.com/dashboard
```

## API Endpoints to Update

**IMPORTANT**: Update these URLs in `setup_uptime_monitoring.py` to match your actual API:

```python
# Current (example):
API_BASE_URL = 'http://localhost:8000'

# Update to your production URL:
API_BASE_URL = 'https://api.startup-rise.com'

# Also update individual agent endpoints:
monitors = [
    {'url': f'{API_BASE_URL}/health'},  # Main API
    {'url': f'{API_BASE_URL}/api/insights-ai/health'},  # Update path
    {'url': f'{API_BASE_URL}/api/meeting-ai/health'},   # Update path
    {'url': f'{API_BASE_URL}/api/concierge-ai/health'}, # Update path
]
```

## UptimeRobot Dashboard

Access your dashboard: [https://uptimerobot.com/dashboard](https://uptimerobot.com/dashboard)

### Key Features

1. **Real-time Status** - See all monitors at a glance
2. **Uptime Percentage** - Last 24h, 7d, 30d, 90d
3. **Response Times** - Average response time graphs
4. **Incident History** - When and why services went down
5. **Alert Logs** - Who was notified and when

## Free Tier Limits

✅ **50 Monitors** - More than enough for your 4 services  
✅ **5 Minute Intervals** - Check every 5 minutes  
✅ **2 Months History** - Keep 60 days of logs  
✅ **Email & Push** - Unlimited notifications  
✅ **Public Status Pages** - 1 included  

To upgrade for SMS or faster checks: [UptimeRobot Plans](https://uptimerobot.com/pricing/)

## Creating a Public Status Page

1. Go to [Public Status Pages](https://uptimerobot.com/dashboard#publicStatusPages)
2. Click "Create Public Status Page"
3. Select your monitors
4. Customize branding (logo, colors)
5. Get shareable URL (e.g., `status.startup-rise.com`)

This gives users transparency when services are down!

## Troubleshooting

### Setup Script Fails

**Problem**: "API key invalid"  
**Solution**: Verify `UPTIME_ROBOT_API_KEY` in `.env` is correct

**Problem**: "No alert contacts found"  
**Solution**: Add contacts in dashboard first, then re-run script

**Problem**: "Connection timeout"  
**Solution**: Check if `API_BASE_URL` is accessible from internet

### Monitors Show Down But Service Works

**Problem**: False positive alerts  
**Solution**: 
1. Check if health endpoint returns "ok" in response
2. Verify endpoint is publicly accessible (not behind VPN)
3. Check response time (timeout is 30 seconds default)
4. Look at UptimeRobot logs for specific error

### Not Receiving Alerts

**Problem**: Monitors show down but no email  
**Solution**:
1. Verify alert contacts are added in dashboard
2. Check spam folder
3. Re-run setup script to link monitors to contacts
4. Test: Pause a monitor manually and check for notification

## Advanced Configuration

### Webhook Alerts (Slack/Discord/Teams)

1. Create incoming webhook in your chat app
2. Add as "Webhook" contact in UptimeRobot
3. Customize JSON payload:

```json
{
  "text": "🚨 *monitorFriendlyName* is *alertTypeFriendlyName*",
  "attachments": [{
    "color": "danger",
    "fields": [
      {"title": "URL", "value": "*monitorURL*"},
      {"title": "Time", "value": "*alertDateTime*"}
    ]
  }]
}
```

### Custom Maintenance Windows

Schedule downtime to prevent false alerts:

```python
# In UptimeRobot dashboard:
# Settings → Maintenance Windows → Add New
# Or use API:
import requests

requests.post(
    "https://api.uptimerobot.com/v2/newMWindow",
    data={
        'api_key': UPTIME_ROBOT_API_KEY,
        'type': 1,  # Once
        'friendly_name': 'Scheduled Maintenance',
        'start_time': '1234567890',  # Unix timestamp
        'duration': 60,  # Minutes
        'monitors': '123-456-789',  # Monitor IDs
    }
)
```

### API Integration

Check status programmatically:

```python
import requests
import os

response = requests.post(
    "https://api.uptimerobot.com/v2/getMonitors",
    data={
        'api_key': os.getenv('UPTIME_ROBOT_API_KEY'),
        'format': 'json',
    }
)

monitors = response.json()['monitors']
for m in monitors:
    print(f"{m['friendly_name']}: {m['status']}")  # 2 = Up, 9 = Down
```

## Comparison with Other Services

| Feature | UptimeRobot | Better Uptime | Pingdom | Healthchecks.io |
|---------|-------------|---------------|---------|-----------------|
| **Free Monitors** | 50 | 10 | 0 | 20 |
| **Check Interval** | 5 min | 3 min | - | Variable |
| **Status Page** | ✅ | ✅ | 💰 | ✅ |
| **SMS Alerts** | 💰 | 💰 | 💰 | ❌ |
| **API Access** | ✅ | ✅ | ✅ | ✅ |
| **Cron Monitoring** | ❌ | ❌ | ❌ | ✅ |

**Recommendation**: UptimeRobot is perfect for your use case!

## Maintenance Checklist

### Weekly
- [ ] Check dashboard for any incidents
- [ ] Verify all monitors are green
- [ ] Review response time trends

### Monthly  
- [ ] Review uptime percentages (should be >99.9%)
- [ ] Test alert notifications
- [ ] Update monitor URLs if API changes
- [ ] Check alert contact list is current

### Quarterly
- [ ] Review and optimize check intervals
- [ ] Consider upgrading if needs change
- [ ] Audit who receives alerts
- [ ] Update status page branding

## Support

- 📚 [UptimeRobot Docs](https://uptimerobot.com/api/)
- 💬 [Support](https://uptimerobot.com/support/)
- 🐦 [@uptimerobot](https://twitter.com/uptimerobot)

## Next Steps

1. ✅ Run `setup_uptime_monitoring.py`
2. ✅ Add alert contacts in dashboard
3. ✅ Verify all monitors are green
4. ✅ Set up status page (optional)
5. ✅ Test by pausing a monitor
6. ✅ Add to team wiki/runbook
