#!/usr/bin/env python3
"""
Setup UptimeRobot Monitoring for Startup Rise Platform
Monitors: API Health, Insights AI, Meeting AI, Concierge AI
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')  # Update with your actual API URL

# UptimeRobot API v2 endpoint (v3 uses same authentication)
UPTIME_ROBOT_API = "https://api.uptimerobot.com/v2/newMonitor"
UPTIME_ROBOT_GET_API = "https://api.uptimerobot.com/v2/getMonitors"

# Alert contacts - you need to get these from your UptimeRobot account
# Leave empty and the script will show you available contacts
ALERT_CONTACTS = []  # e.g., ["2428789_0_0"] - will be auto-detected

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
            print(f"✅ Found {len(contacts)} alert contact(s)")
            for contact in contacts:
                contact_id = f"{contact['id']}_0_0"  # Format: id_threshold_recurrence
                print(f"   - {contact['friendly_name']} ({contact['type_name']}): {contact_id}")
            return [f"{contact['id']}_0_0" for contact in contacts]
        else:
            print(f"⚠️  No alert contacts found. Please add one in UptimeRobot dashboard first.")
            return []
    except Exception as e:
        print(f"❌ Error fetching alert contacts: {e}")
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

def create_monitor(name, url, monitor_type=1, keyword_type=None, keyword_value=None, alert_contacts=None):
    """
    Create a new UptimeRobot monitor
    
    Args:
        name: Monitor friendly name
        url: URL to monitor
        monitor_type: 1=HTTP(s), 2=Keyword, 3=Ping, 4=Port
        keyword_type: 1=exists, 2=not exists (for keyword monitoring)
        keyword_value: Keyword to search for
        alert_contacts: List of alert contact IDs
    """
    data = {
        'api_key': UPTIME_ROBOT_API_KEY,
        'format': 'json',
        'type': monitor_type,
        'url': url,
        'friendly_name': name,
        'interval': 300,  # Check every 5 minutes
    }
    
    # Add keyword monitoring if specified
    if keyword_type and keyword_value:
        data['keyword_type'] = keyword_type
        data['keyword_value'] = keyword_value
    
    # Add alert contacts if available
    if alert_contacts:
        data['alert_contacts'] = '-'.join(alert_contacts)
    
    try:
        response = requests.post(
            UPTIME_ROBOT_API,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=data
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            print(f"✅ Created monitor: {name}")
            print(f"   URL: {url}")
            print(f"   Monitor ID: {result['monitor']['id']}")
            return True
        else:
            print(f"❌ Failed to create monitor {name}: {result.get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error creating monitor {name}: {e}")
        return False

def setup_monitors():
    """Setup all required monitors"""
    print("=" * 60)
    print("UptimeRobot Monitoring Setup - Startup Rise Platform")
    print("=" * 60)
    print()
    
    # Validate API key
    if not UPTIME_ROBOT_API_KEY:
        print("❌ Error: UPTIME_ROBOT_API_KEY not found in .env file")
        print("   Please add your API key to /home/akyo/startup_swiper/api/.env")
        return
    
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"🔑 API Key: {UPTIME_ROBOT_API_KEY[:10]}...")
    print()
    
    # Get alert contacts
    print("Fetching alert contacts...")
    alert_contacts = get_alert_contacts()
    print()
    
    if not alert_contacts:
        print("⚠️  WARNING: No alert contacts configured!")
        print("   Please add an email/SMS contact in UptimeRobot dashboard:")
        print("   https://uptimerobot.com/dashboard#mySettings")
        print()
        proceed = input("Continue without alerts? (y/N): ")
        if proceed.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Get existing monitors
    print("Checking existing monitors...")
    existing = get_existing_monitors()
    print(f"Found {len(existing)} existing monitor(s)")
    print()
    
    # Define monitors to create
    monitors = [
        {
            'name': 'Startup Rise - API Health',
            'url': f'{API_BASE_URL}/health',
            'monitor_type': 1,  # HTTP(s)
            'keyword_type': 1,  # Keyword exists
            'keyword_value': 'healthy',  # Look for "healthy" in response
        },
        {
            'name': 'Startup Rise - Concierge AI Agent',
            'url': f'{API_BASE_URL}/concierge/ask',
            'monitor_type': 1,
            'keyword_type': 1,
            'keyword_value': 'answer',  # Concierge returns JSON with "answer" field
        },
    ]
    
    print("Creating monitors...")
    print()
    
    created = 0
    skipped = 0
    
    for monitor in monitors:
        if monitor['name'] in existing:
            print(f"⏭️  Skipped (already exists): {monitor['name']}")
            skipped += 1
        else:
            if create_monitor(
                name=monitor['name'],
                url=monitor['url'],
                monitor_type=monitor['monitor_type'],
                keyword_type=monitor.get('keyword_type'),
                keyword_value=monitor.get('keyword_value'),
                alert_contacts=alert_contacts
            ):
                created += 1
        print()
    
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"✅ Created: {created} monitor(s)")
    print(f"⏭️  Skipped: {skipped} monitor(s)")
    print()
    print("📊 View your monitors:")
    print("   https://uptimerobot.com/dashboard")
    print()
    print("⚙️  Configure alerts:")
    print("   https://uptimerobot.com/dashboard#mySettings")
    print()
    print("📧 Alert contacts configured: ", "Yes" if alert_contacts else "No")
    print()
    
    if not alert_contacts:
        print("⚠️  IMPORTANT: Add alert contacts in UptimeRobot dashboard")
        print("   to receive notifications when services go down!")
    
    print()
    print("Next steps:")
    print("1. Verify monitors are running in UptimeRobot dashboard")
    print("2. Update monitor URLs in this script if needed")
    print("3. Configure notification channels (email, SMS, Slack, etc.)")
    print("4. Set up a status page (optional)")

if __name__ == "__main__":
    setup_monitors()
