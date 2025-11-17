#!/usr/bin/env python3
"""
Deploy UptimeRobot Monitoring - Auto-create without prompts
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

UPTIME_ROBOT_API = "https://api.uptimerobot.com/v2/newMonitor"
UPTIME_ROBOT_GET_API = "https://api.uptimerobot.com/v2/getMonitors"

def get_alert_contacts():
    """Fetch available alert contacts from UptimeRobot"""
    try:
        response = requests.post(
            "https://api.uptimerobot.com/v2/getAlertContacts",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json'
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            contacts = result.get('alert_contacts', [])
            return [f"{contact['id']}_0_0" for contact in contacts]
        return []
    except Exception as e:
        print(f"⚠️  Could not fetch alert contacts: {e}")
        return []

def get_existing_monitors():
    """Get list of existing monitors"""
    try:
        response = requests.post(
            UPTIME_ROBOT_GET_API,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json'
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            monitors = result.get('monitors', [])
            return {monitor['friendly_name']: monitor for monitor in monitors}
        return {}
    except Exception as e:
        print(f"❌ Error fetching existing monitors: {e}")
        return {}

def create_monitor(name, url, monitor_type=1, keyword_type=None, keyword_value=None, alert_contacts=None, 
                  http_method=None, post_type=None, post_value=None, post_content_type=None):
    """Create a new UptimeRobot monitor"""
    data = {
        'api_key': UPTIME_ROBOT_API_KEY,
        'format': 'json',
        'type': monitor_type,
        'url': url,
        'friendly_name': name,
        'interval': 300,  # Check every 5 minutes
    }
    
    if keyword_type and keyword_value:
        data['keyword_type'] = keyword_type
        data['keyword_value'] = keyword_value
    
    if alert_contacts:
        data['alert_contacts'] = '-'.join(alert_contacts)
    
    # Add POST request parameters
    if http_method is not None:
        data['http_method'] = http_method
    if post_type is not None:
        data['post_type'] = post_type
    if post_value is not None:
        data['post_value'] = post_value
    if post_content_type is not None:
        data['post_content_type'] = post_content_type
    
    try:
        response = requests.post(
            UPTIME_ROBOT_API,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=data
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            print(f"✅ {name}")
            print(f"   URL: {url}")
            print(f"   ID: {result['monitor']['id']}")
            return True
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            print(f"❌ {name}: {error_msg}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def deploy():
    """Deploy all monitors automatically"""
    print("=" * 70)
    print("🚀 DEPLOYING UPTIMEROBOT MONITORING")
    print("=" * 70)
    print()
    
    if not UPTIME_ROBOT_API_KEY:
        print("❌ UPTIME_ROBOT_API_KEY not found in .env")
        return False
    
    print(f"📡 API: {API_BASE_URL}")
    print()
    
    # Get alert contacts
    alert_contacts = get_alert_contacts()
    if alert_contacts:
        print(f"✅ Alert contacts: {len(alert_contacts)} configured")
    else:
        print("⚠️  No alert contacts (add in dashboard for notifications)")
    print()
    
    # Get existing monitors
    existing = get_existing_monitors()
    print(f"📊 Existing monitors: {len(existing)}")
    print()
    
    # Define monitors
    monitors = [
        {
            'name': 'Startup Rise - Main Page',
            'url': API_BASE_URL,
            'monitor_type': 1,
            'keyword_type': 1,
            'keyword_value': 'Startup Rise',
        },
        {
            'name': 'Startup Rise - Login Form',
            'url': f'{API_BASE_URL}/',
            'monitor_type': 1,
            'keyword_type': 1,
            'keyword_value': 'password',  # Login page contains password field
        },
        {
            'name': 'Startup Rise - API Health (GET)',
            'url': f'{API_BASE_URL}/health',
            'monitor_type': 1,
            'http_method': 1,  # GET method
            'keyword_type': 2,  # Keyword exists
            'keyword_value': 'healthy',  # API returns "status": "healthy"
        },
        {
            'name': 'Startup Rise - API Docs',
            'url': f'{API_BASE_URL}/docs',
            'monitor_type': 1,
            'keyword_type': 1,
            'keyword_value': 'swagger',  # FastAPI docs page
        },
    ]
    
    print("Creating monitors...")
    print()
    
    created = 0
    skipped = 0
    
    for monitor in monitors:
        if monitor['name'] in existing:
            print(f"⏭️  {monitor['name']} (already exists)")
            skipped += 1
        else:
            if create_monitor(
                name=monitor['name'],
                url=monitor['url'],
                monitor_type=monitor['monitor_type'],
                keyword_type=monitor.get('keyword_type'),
                keyword_value=monitor.get('keyword_value'),
                alert_contacts=alert_contacts,
                http_method=monitor.get('http_method'),
                post_type=monitor.get('post_type'),
                post_value=monitor.get('post_value'),
                post_content_type=monitor.get('post_content_type'),
            ):
                created += 1
        print()
    
    print("=" * 70)
    print(f"✅ Deployed: {created} | ⏭️  Skipped: {skipped}")
    print("=" * 70)
    print()
    print("📊 Dashboard: https://uptimerobot.com/dashboard")
    print()
    
    if not alert_contacts:
        print("⚠️  NEXT STEP: Add alert contact at:")
        print("   https://uptimerobot.com/dashboard#mySettings")
        print("   Then re-run this script to update monitors")
    else:
        print("✅ Monitoring active with alerts!")
    
    return True

if __name__ == "__main__":
    deploy()
