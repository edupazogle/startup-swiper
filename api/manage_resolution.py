#!/usr/bin/env python3
"""
CB Insights ID Resolution Manager

Monitor and manage the bulk ID resolution process for all startups in the database.
"""

import sys
import subprocess
import time
from pathlib import Path

sys.path.insert(0, '/home/akyo/startup_swiper/api')
from database import engine
from sqlalchemy import text


def get_resolution_stats():
    """Get current resolution statistics"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM startups WHERE cb_insights_id IS NOT NULL"))
            with_id = result.fetchone()[0]
            
            result = conn.execute(text("SELECT COUNT(*) FROM startups"))
            total = result.fetchone()[0]
            
            return {
                'total': total,
                'resolved': with_id,
                'remaining': total - with_id,
                'percentage': (with_id / total * 100) if total > 0 else 0
            }
    except Exception as e:
        print(f"Error: {e}")
        return None


def start_resolution():
    """Start the background resolution process"""
    print("\n🚀 Starting CB Insights ID resolution process...")
    print("   This may take several hours for all startups.")
    print("   Process will run in background.\n")
    
    cmd = "cd /home/akyo/startup_swiper && nohup python3 api/resolve_all_startup_ids.py > /tmp/startup_resolution_bg.log 2>&1 &"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("✅ Process started")
        print("   View logs: tail -f /tmp/startup_resolution_bg.log")
        return True
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        return False


def monitor_resolution():
    """Monitor the ongoing resolution process"""
    print("\n📊 CB INSIGHTS ID RESOLUTION MONITOR")
    print("="*60)
    
    while True:
        stats = get_resolution_stats()
        
        if stats:
            print(f"\nResolved: {stats['resolved']:,} / {stats['total']:,} ({stats['percentage']:.1f}%)")
            print(f"Remaining: {stats['remaining']:,}")
            
            # Progress bar
            bar_length = 40
            filled = int(bar_length * stats['percentage'] / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"Progress: [{bar}] {stats['percentage']:.1f}%")
            
            if stats['remaining'] == 0:
                print("\n✅ RESOLUTION COMPLETE!")
                break
        
        print("\n(Refresh in 30 seconds... Press Ctrl+C to stop monitoring)")
        time.sleep(30)


def show_summary():
    """Show detailed summary"""
    stats = get_resolution_stats()
    
    if not stats:
        print("Error getting stats")
        return
    
    print("\n" + "="*60)
    print("CB INSIGHTS ID RESOLUTION SUMMARY")
    print("="*60)
    print(f"\nTotal Startups: {stats['total']:,}")
    print(f"Resolved: {stats['resolved']:,} ({stats['percentage']:.1f}%)")
    print(f"Remaining: {stats['remaining']:,} ({100-stats['percentage']:.1f}%)")
    
    # Calculate estimated time
    if stats['remaining'] > 0:
        # Assume ~3-5 seconds per startup for lookup + fallback
        est_seconds = stats['remaining'] * 4
        est_minutes = est_seconds / 60
        est_hours = est_minutes / 60
        
        print(f"\nEstimated Time Remaining:")
        if est_hours > 1:
            print(f"  ~{est_hours:.1f} hours ({est_minutes:.0f} minutes)")
        else:
            print(f"  ~{est_minutes:.0f} minutes")
    
    print("\n" + "="*60)


def show_help():
    """Show usage information"""
    print("""
CB Insights ID Resolution Manager

Usage:
  python3 manage_resolution.py [command]

Commands:
  start      - Start the background resolution process
  monitor    - Monitor the ongoing resolution process
  status     - Show current resolution statistics
  summary    - Show detailed summary
  help       - Show this help message

Examples:
  python3 manage_resolution.py status   # Check progress
  python3 manage_resolution.py start    # Start resolution
  python3 manage_resolution.py monitor  # Monitor progress

View Logs:
  tail -f /tmp/startup_resolution_bg.log

Results:
  /home/akyo/startup_swiper/downloads/startup_resolution_resolved_*.csv
  /home/akyo/startup_swiper/downloads/startup_resolution_failed_*.csv
    """)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        cmd = "status"
    else:
        cmd = sys.argv[1].lower()
    
    if cmd == "start":
        start_resolution()
    elif cmd == "monitor":
        try:
            monitor_resolution()
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    elif cmd == "status":
        show_summary()
    elif cmd == "summary":
        show_summary()
    elif cmd in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"Unknown command: {cmd}")
        show_help()
