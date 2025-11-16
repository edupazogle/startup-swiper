#!/usr/bin/env python3
"""
Monitor Tier Reports Generation Progress

Shows real-time progress of report generation with ETA
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

CHECKPOINT_FILE = Path("/tmp/tier_reports_checkpoint.json")
LOG_FILE = Path("/tmp/tier1_generation.log")

def get_checkpoint_data():
    """Get current checkpoint data"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except:
            return None
    return None

def count_log_entries(log_file):
    """Count generated entries in log"""
    try:
        with open(log_file) as f:
            lines = f.readlines()
        return sum(1 for line in lines if "✅ Generated & saved:" in line)
    except:
        return 0

def get_process_status():
    """Check if generation process is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "generate_tier_reports_optimized"],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def monitor_tier1():
    """Monitor Tier 1 generation"""
    print("=" * 80)
    print("TIER 1 REPORT GENERATION MONITOR")
    print("=" * 80)
    print(f"Started at: 2025-11-16 03:08:35")
    print(f"Tier: Tier 1 (Critical Priority) - 227 startups")
    print(f"Concurrency: 5")
    print()
    
    start_time = datetime.now()
    logged_entries = 0
    max_entries = 227
    
    while True:
        # Count completed
        completed = count_log_entries(LOG_FILE)
        elapsed = datetime.now() - start_time
        
        if completed > logged_entries:
            logged_entries = completed
            
            # Calculate progress
            progress_pct = (completed / max_entries) * 100
            
            # Calculate ETA
            if completed > 0:
                time_per_entry = elapsed.total_seconds() / completed
                remaining = max_entries - completed
                eta_seconds = time_per_entry * remaining
                eta = datetime.now() + timedelta(seconds=eta_seconds)
                
                print(f"Progress: {completed}/{max_entries} ({progress_pct:.1f}%)")
                print(f"  Elapsed: {elapsed.total_seconds():.0f}s ({elapsed.total_seconds()/60:.1f}m)")
                print(f"  ETA: {eta.strftime('%H:%M:%S')} (~{int(eta_seconds/60)}m remaining)")
                print(f"  Rate: {completed/elapsed.total_seconds():.2f} reports/second")
            print()
        
        # Check if process is still running
        if not get_process_status() and completed >= max_entries:
            print("\n✅ TIER 1 GENERATION COMPLETE!")
            break
        
        time.sleep(5)

if __name__ == "__main__":
    monitor_tier1()
