#!/usr/bin/env python3
"""
Fix UptimeRobot Monitoring - Remove broken monitors and redeploy correctly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')

def delete_monitor(monitor_id):
    """Delete a monitor by ID"""
    try:
        response = requests.post(
            "https://api.uptimerobot.com/v2/deleteMonitor",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json',
                'id': monitor_id
            }
        )
        response.raise_for_status()
        result = response.json()
        return result['stat'] == 'ok'
    except Exception as e:
        print(f"❌ Error deleting monitor {monitor_id}: {e}")
        return False

def get_all_monitors():
    """Get all monitors"""
    try:
        response = requests.post(
            "https://api.uptimerobot.com/v2/getMonitors",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json'
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            return result.get('monitors', [])
        return []
    except Exception as e:
        print(f"❌ Error fetching monitors: {e}")
        return []

def main():
    print("=" * 70)
    print("🔧 FIXING UPTIMEROBOT MONITORING")
    print("=" * 70)
    print()
    
    # Get all monitors
    monitors = get_all_monitors()
    print(f"📊 Found {len(monitors)} monitors")
    print()
    
    # IDs of broken monitors to delete
    broken_monitor_names = [
        'Startup Rise - API Endpoint',  # Wrong method (POST instead of GET)
        'Startup Rise - Authentication',  # POST endpoint without auth - will always fail
        'Startup Rise - Concierge AI Agent',  # POST endpoint without auth
        'Startup Rise - Insights AI Agent',  # Wrong path
        'Startup Rise - Meeting AI Agent',  # Wrong path
        'Startup Rise - API Health',  # Old name, wrong config
    ]
    
    deleted = 0
    for monitor in monitors:
        if monitor['friendly_name'] in broken_monitor_names:
            print(f"🗑️  Deleting: {monitor['friendly_name']} (ID: {monitor['id']})")
            if delete_monitor(monitor['id']):
                print(f"   ✅ Deleted")
                deleted += 1
            else:
                print(f"   ❌ Failed")
            print()
    
    print("=" * 70)
    print(f"✅ Deleted {deleted} broken monitors")
    print("=" * 70)
    print()
    print("Next step: Run deploy_monitoring.py to create corrected monitors")
    print()

if __name__ == "__main__":
    main()
