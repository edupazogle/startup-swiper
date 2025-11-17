#!/usr/bin/env python3
"""
Delete old/broken monitors from UptimeRobot
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')
DELETE_API = "https://api.uptimerobot.com/v2/deleteMonitor"
GET_API = "https://api.uptimerobot.com/v2/getMonitors"

def get_all_monitors():
    """Get all monitors"""
    try:
        response = requests.post(
            GET_API,
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

def delete_monitor(monitor_id, monitor_name):
    """Delete a monitor by ID"""
    try:
        response = requests.post(
            DELETE_API,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json',
                'id': monitor_id
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] == 'ok':
            print(f"✅ Deleted: {monitor_name} (ID: {monitor_id})")
            return True
        else:
            print(f"❌ Failed to delete {monitor_name}: {result.get('error', {}).get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {monitor_name}: {e}")
        return False

def cleanup():
    """Remove old broken monitors"""
    print("=" * 70)
    print("🧹 CLEANING UP OLD MONITORS")
    print("=" * 70)
    print()
    
    monitors = get_all_monitors()
    print(f"Found {len(monitors)} total monitor(s)")
    print()
    
    # Monitors to delete (broken ones)
    to_delete = [
        'Startup Rise - API Health',
        'Startup Rise - Concierge AI',
        'tilyn.ai',
    ]
    
    deleted = 0
    
    for monitor in monitors:
        name = monitor.get('friendly_name', '')
        monitor_id = monitor.get('id')
        status = monitor.get('status')
        
        # Show status
        status_emoji = "✅" if status == 2 else "❌" if status == 9 else "⏸️"
        print(f"{status_emoji} {name} (ID: {monitor_id})")
        
        if name in to_delete:
            print(f"   ⚠️  Marked for deletion (broken/outdated)")
            if delete_monitor(monitor_id, name):
                deleted += 1
        print()
    
    print("=" * 70)
    print(f"✅ Deleted: {deleted} monitor(s)")
    print("=" * 70)
    print()
    print("Next: Run deploy_monitoring.py to create proper monitors")

if __name__ == "__main__":
    cleanup()
