#!/usr/bin/env python3
"""
List all monitors with details
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

UPTIME_ROBOT_API_KEY = os.getenv('UPTIME_ROBOT_API_KEY')
GET_API = "https://api.uptimerobot.com/v2/getMonitors"

def list_all():
    """List all monitors"""
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
        
        if result['stat'] != 'ok':
            print(f"❌ API Error: {result.get('error', {}).get('message', 'Unknown')}")
            return
        
        monitors = result.get('monitors', [])
        
        print("=" * 80)
        print(f"ALL UPTIMEROBOT MONITORS ({len(monitors)} total)")
        print("=" * 80)
        print()
        
        for i, m in enumerate(monitors, 1):
            name = m.get('friendly_name', 'Unknown')
            url = m.get('url', 'N/A')
            monitor_id = m.get('id', 'N/A')
            status = m.get('status', 0)
            interval = m.get('interval', 0)
            
            status_text = {
                0: "⏸️  Paused",
                1: "⏳ Not checked yet", 
                2: "✅ Up",
                8: "⚠️  Seems down",
                9: "❌ Down"
            }.get(status, "❓ Unknown")
            
            print(f"{i}. {name}")
            print(f"   ID: {monitor_id}")
            print(f"   URL: {url}")
            print(f"   Status: {status_text}")
            print(f"   Check interval: {interval} seconds ({interval//60} min)")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_all()
