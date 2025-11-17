# GitHub Actions Workflows

## API Health Check

This workflow monitors the health of your API and AI agents every 30 minutes.

### Setup Instructions

#### 1. Configure GitHub Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

**Required Secrets:**
- `API_BASE_URL` - Your API base URL (e.g., `https://api.yourapp.com`)
- `EMAIL_USERNAME` - Gmail address for sending alerts (e.g., `alerts@yourdomain.com`)
- `EMAIL_PASSWORD` - Gmail App Password (see below)
- `ALERT_EMAIL` - Email address to receive alerts (can be same or different)

**Optional Secrets:**
- `API_KEY` - If your API requires authentication
- `SLACK_WEBHOOK_URL` - For Slack notifications (optional)

#### 2. Set Up Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → 2-Step Verification → App passwords
4. Generate an app password for "Mail"
5. Copy the 16-character password and add it as `EMAIL_PASSWORD` secret

**Alternative Email Providers:**
- **SendGrid**: Use their SMTP (smtp.sendgrid.net:587) + API key
- **Mailgun**: Use their SMTP (smtp.mailgun.org:587) + credentials
- **AWS SES**: Use their SMTP (email-smtp.region.amazonaws.com:587) + SMTP credentials

#### 3. Customize Health Check Endpoints

Edit the workflow file to match your actual API endpoints:

```yaml
# Update these URLs in .github/workflows/api-health-check.yml
API_BASE_URL: 'https://your-actual-api.com'

# And update the endpoint paths:
/health                          # Main API health
/api/insights-agent/health      # Insights AI
/api/meeting-agent/health       # Meeting AI
/api/concierge-agent/health     # Concierge AI
```

#### 4. Adjust Schedule

Change the cron schedule if needed (currently every 30 minutes):

```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'   # Every hour
  # - cron: '0 */6 * * *' # Every 6 hours
  # - cron: '0 9,17 * * *' # 9 AM and 5 PM daily
```

#### 5. Test the Workflow

Trigger manually to test:
1. Go to **Actions** tab in your repository
2. Select "API & Agents Health Check"
3. Click "Run workflow"
4. Check the results and verify email is sent on failure

### Monitoring Options

#### Option A: GitHub Actions (Current Setup)
- ✅ Free tier: 2,000 minutes/month for private repos
- ✅ Unlimited for public repos
- ✅ Simple setup, no external dependencies
- ⚠️ Limited to GitHub's infrastructure

#### Option B: Uptime Monitoring Services
Consider these if you need more features:

1. **UptimeRobot** (Free tier: 50 monitors)
   - Simple HTTP/HTTPS monitoring
   - Email/SMS/Slack alerts
   - Status pages

2. **Better Uptime** (Free tier: 10 monitors)
   - Multi-location checks
   - Incident management
   - Status pages

3. **Pingdom** (Paid, from $10/month)
   - Enterprise-grade monitoring
   - Advanced alerting
   - Performance insights

4. **Healthchecks.io** (Free tier: 20 checks)
   - Cron job monitoring
   - Dead man's switch
   - Simple API

#### Option C: Self-Hosted Solution

Create a simple monitoring script on your server:

```bash
# /usr/local/bin/health-check.sh
#!/bin/bash
curl -f https://your-api.com/health || mail -s "API Down" alerts@yourdomain.com
```

Add to crontab:
```bash
*/30 * * * * /usr/local/bin/health-check.sh
```

### Email Alert Example

When a check fails, you'll receive an email like:

```
Subject: 🚨 API Health Check Failed - Startup Rise Platform

API Health Check Failed!

Repository: edupazogle/startup-swiper
Run: https://github.com/edupazogle/startup-swiper/actions/runs/12345
Time: 2025-11-17T10:30:00Z

Please check the workflow logs for details:
https://github.com/edupazogle/startup-swiper/actions/runs/12345

This is an automated alert from GitHub Actions.
```

### Troubleshooting

**Workflow not running?**
- Check Actions are enabled: Settings → Actions → Allow all actions
- Verify cron syntax is correct
- Check if repository is active (push a commit to trigger)

**Email not sending?**
- Verify Gmail App Password is correct (not your regular password)
- Check EMAIL_USERNAME and EMAIL_PASSWORD secrets are set
- Try manual workflow trigger to test

**False positives?**
- Increase timeout values in the workflow
- Check if API endpoints are correct
- Verify API_KEY is set correctly if required

### Best Practices

1. **Test First**: Always test manually before relying on automated checks
2. **Monitor the Monitors**: Set up alerts if the workflow itself fails
3. **Keep Secrets Secure**: Use GitHub secrets, never commit credentials
4. **Document Endpoints**: Keep this README updated with endpoint changes
5. **Review Regularly**: Check workflow history weekly for patterns

### Advanced Features to Consider

1. **Response Time Monitoring**: Add timing checks
2. **Database Health**: Check database connectivity
3. **Dependency Checks**: Monitor external services
4. **Status Page**: Create public status page using results
5. **Escalation**: Send SMS for critical failures (via Twilio)
6. **Metrics Collection**: Store check results for trend analysis
