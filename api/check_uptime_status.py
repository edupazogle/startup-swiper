#!/usr/bin/env python3
"""
Check current status of UptimeRobot monitors
Shows real-time status and recent downtime
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')
UPTIME_ROBOT_API = "https://api.uptimerobot.com/v2/getMonitors"

STATUS_MAP = {
    0: "⏸️  Paused",
    1: "⏳ Not checked yet",
    2: "✅ Up",
    8: "⚠️  Seems down",
    9: "❌ Down"
}

def get_monitors_status():
    """Fetch and display status of all monitors"""
    if not UPTIME_ROBOT_API_KEY:
        print("❌ Error: UPTIME_ROBOT_API_KEY not found in .env file")
        return
    
    try:
        response = requests.post(
            UPTIME_ROBOT_API,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'api_key': UPTIME_ROBOT_API_KEY,
                'format': 'json',
                'logs': 1,  # Include logs
                'response_times': 1,  # Include response times
                'alert_contacts': 1,  # Include alert contacts
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if result['stat'] != 'ok':
            print(f"❌ API Error: {result.get('error', {}).get('message', 'Unknown error')}")
            return
        
        monitors = result.get('monitors', [])
        
        if not monitors:
            print("ℹ️  No monitors found. Run setup_uptime_monitoring.py first.")
            return
        
        print("=" * 80)
        print("UptimeRobot Monitor Status - Startup Rise Platform")
        print("=" * 80)
        print()
        
        all_up = True
        
        for monitor in monitors:
            status_code = monitor.get('status', 0)
            status = STATUS_MAP.get(status_code, "❓ Unknown")
            name = monitor.get('friendly_name', 'Unknown')
            url = monitor.get('url', 'N/A')
            uptime_ratio = monitor.get('custom_uptime_ratio', 'N/A')
            
            print(f"{status} {name}")
            print(f"   URL: {url}")
            print(f"   Uptime (30 days): {uptime_ratio}%")
            
            # Response time
            response_times = monitor.get('response_times', [])
            if response_times:
                avg_response = sum([rt.get('value', 0) for rt in response_times]) / len(response_times)
                print(f"   Avg Response Time: {avg_response:.0f}ms")
            
            # Recent logs (last 5 events)
            logs = monitor.get('logs', [])
            if logs:
                print(f"   Recent Events:")
                for log in logs[:3]:  # Show last 3 events
                    log_type = log.get('type')
                    log_datetime = datetime.fromtimestamp(log.get('datetime', 0))
                    
                    event_icon = "🔴" if log_type == 1 else "🟢" if log_type == 2 else "⚠️"
                    event_text = "Down" if log_type == 1 else "Up" if log_type == 2 else "Paused"
                    
                    print(f"      {event_icon} {event_text} - {log_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                    if log.get('reason'):
                        print(f"         Reason: {log['reason'].get('detail', 'N/A')}")
            
            print()
            
            if status_code not in [2]:  # Not up
                all_up = False
        
        print("=" * 80)
        if all_up:
            print("✅ All systems operational!")
        else:
            print("⚠️  Some systems are experiencing issues")
        print("=" * 80)
        print()
        print("📊 Full dashboard: https://uptimerobot.com/dashboard")
        
    except Exception as e:
        print(f"❌ Error fetching monitor status: {e}")

if __name__ == "__main__":
    get_monitors_status()
