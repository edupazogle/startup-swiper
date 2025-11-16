#!/usr/bin/env python3
"""
Monitor value proposition generation progress
"""
import json
import time
import sys
from pathlib import Path
from datetime import datetime

CHECKPOINT_FILE = Path(__file__).parent / "downloads" / "vp_checkpoint.json"

def format_time(seconds):
    """Format seconds into readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def main():
    print("🎯 VALUE PROPOSITION GENERATION MONITOR")
    print("=" * 80)
    
    target_total = 2665  # Tier 2, 3, 4 companies
    start_time = time.time()
    
    try:
        while True:
            if CHECKPOINT_FILE.exists():
                with open(CHECKPOINT_FILE) as f:
                    data = json.load(f)
                
                processed = len(data.get('processed_ids', []))
                remaining = target_total - processed
                progress_pct = (processed / target_total) * 100
                
                # Calculate rate and ETA
                elapsed = time.time() - start_time
                if processed > 0 and elapsed > 0:
                    rate = processed / elapsed  # companies per second
                    eta_seconds = remaining / rate if rate > 0 else 0
                else:
                    rate = 0
                    eta_seconds = 0
                
                # Progress bar
                bar_width = 50
                filled = int(bar_width * progress_pct / 100)
                bar = "█" * filled + "░" * (bar_width - filled)
                
                # Clear and redraw
                print("\033[H\033[J", end="")  # Clear screen
                print("🎯 VALUE PROPOSITION GENERATION MONITOR")
                print("=" * 80)
                print(f"\nProgress: {processed:,} / {target_total:,} companies ({progress_pct:.1f}%)")
                print(f"[{bar}]")
                print(f"\n📊 Statistics:")
                print(f"   ✓ Processed: {processed:,} companies")
                print(f"   ⏳ Remaining: {remaining:,} companies")
                print(f"   ⚡ Rate: {rate*60:.1f} companies/min")
                print(f"   ⏱️  Elapsed: {format_time(elapsed)}")
                print(f"   🎯 ETA: {format_time(eta_seconds)}")
                print(f"\n📁 Checkpoint: {CHECKPOINT_FILE}")
                print(f"   Last updated: {data.get('timestamp', 'unknown')}")
                
            else:
                print("\n⏳ Waiting for checkpoint file to be created...")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
