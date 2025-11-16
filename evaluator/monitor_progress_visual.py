#!/usr/bin/env python3
"""
Visual Progress Monitor for AXA Evaluation
Shows real-time progress with charts and statistics
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def format_time(seconds):
    """Format seconds to readable time"""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

def progress_bar(current, total, width=50):
    """Create a text progress bar"""
    if total == 0:
        return "[" + "=" * width + "]"
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percentage = (current / total) * 100
    return f"[{bar}] {percentage:5.1f}% ({current}/{total})"

def create_distribution_chart(data, width=40):
    """Create horizontal bar chart"""
    if not data:
        return ""
    
    max_val = max(data.values()) if data.values() else 1
    chart = ""
    for label, value in sorted(data.items()):
        bar_width = int((value / max_val) * width) if max_val > 0 else 0
        bar = "▓" * bar_width + "░" * (width - bar_width)
        chart += f"  {label:20s} [{bar}] {value:4d}\n"
    return chart

def tail_log(file_path, n=10):
    """Get last n lines from log file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            return lines[-n:] if len(lines) > n else lines
    except:
        return []

def parse_log_stats(log_file):
    """Parse log file for statistics"""
    stats = {
        'total_batches': 0,
        'completed': 0,
        'errors': 0,
        'checkpoints': 0,
        'last_update': None
    }
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if 'Batch complete' in line or 'Checkpoint saved' in line:
                    # Extract number from "... (N total)"
                    if '(' in line and 'total)' in line:
                        num_str = line.split('(')[1].split(' total')[0]
                        try:
                            stats['completed'] = int(num_str)
                        except:
                            pass
                
                if 'ERROR' in line:
                    stats['errors'] += 1
                
                if 'Checkpoint saved' in line:
                    stats['checkpoints'] += 1
                
                if 'Starting:' in line and 'batches' in line:
                    try:
                        parts = line.split('Starting:')[1].split('batches')[0].strip()
                        stats['total_batches'] = int(parts)
                    except:
                        pass
        
        if os.path.exists(log_file):
            stats['last_update'] = datetime.fromtimestamp(
                os.path.getmtime(log_file)
            ).strftime('%H:%M:%S')
    except Exception as e:
        pass
    
    return stats

def main():
    log_file = Path("logs/api.log")
    checkpoint_file = Path("downloads/axa_enhanced_checkpoint.json")
    
    start_time = time.time()
    last_count = 0
    
    while True:
        clear_screen()
        
        # Header
        print("=" * 80)
        print("🔍 AXA EVALUATION - LIVE PROGRESS MONITOR")
        print("=" * 80)
        print(f"⏰ Monitor Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  Elapsed: {format_time(time.time() - start_time)}")
        print()
        
        # Parse log statistics
        log_stats = parse_log_stats(log_file)
        
        # Load checkpoint data
        checkpoint_data = None
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
            except Exception as e:
                print(f"⚠️  Error reading checkpoint: {e}")
                pass
        
        # Progress Section
        print("📊 OVERALL PROGRESS")
        print("-" * 80)
        
        if checkpoint_data:
            total_evaluated = checkpoint_data.get('total_evaluated', 0)
            target = 2665  # Expected after filtering
            
            # Track rate
            if total_evaluated > last_count:
                last_count = total_evaluated
            
            print(progress_bar(total_evaluated, target, 60))
            print()
            
            # Estimated completion
            if total_evaluated > 0:
                elapsed = time.time() - start_time
                rate = (total_evaluated / elapsed) * 60 if elapsed > 0 else 0
                remaining = target - total_evaluated
                est_seconds = remaining / (rate / 60) if rate > 0 else 0
                
                print(f"  Rate: {rate:.1f} startups/minute")
                print(f"  ETA: {format_time(est_seconds)}")
                print()
        else:
            print("  ⏳ Waiting for first checkpoint...")
            print()
        
        # Statistics Section
        print("📈 STATISTICS")
        print("-" * 80)
        
        if checkpoint_data:
            stats = checkpoint_data.get('stats', {})
            config = checkpoint_data.get('config', {})
            
            print(f"  Evaluated:        {checkpoint_data.get('total_evaluated', 0):,}")
            print(f"  Providers:        {stats.get('provider_count', 0):,} ({stats.get('provider_count', 0) * 100 / max(checkpoint_data.get('total_evaluated', 1), 1):.1f}%)")
            print(f"  Non-Providers:    {stats.get('non_provider_count', 0):,} ({stats.get('non_provider_count', 0) * 100 / max(checkpoint_data.get('total_evaluated', 1), 1):.1f}%)")
            print(f"  Errors:           {stats.get('errors', 0)}")
            print(f"  Checkpoints Saved: {log_stats['checkpoints']}")
            print()
            
            last_update = checkpoint_data.get('last_updated', 'N/A')
            if 'T' in last_update:
                last_update = last_update.split('T')[1][:8]
            print(f"  Last Update:      {last_update}")
            print(f"  Workers:          {config.get('workers', 'N/A')}")
            print(f"  Batch Size:       {config.get('batch_size', 'N/A')}")
            print()
        else:
            print("  ⏳ Waiting for data...")
            print()
        
        # Tier Distribution
        if checkpoint_data and checkpoint_data.get('stats'):
            print("🎯 TIER DISTRIBUTION")
            print("-" * 80)
            
            tier_data = {
                'Tier 1 (Critical)': stats.get('tier_1', 0),
                'Tier 2 (High)': stats.get('tier_2', 0),
                'Tier 3 (Medium)': stats.get('tier_3', 0),
                'Tier 4 (Low)': stats.get('tier_4', 0)
            }
            
            print(create_distribution_chart(tier_data, 50))
        
        # Recent Activity
        print("📝 RECENT ACTIVITY")
        print("-" * 80)
        
        if checkpoint_data and 'results' in checkpoint_data:
            # Show last 5 evaluated startups
            results = checkpoint_data['results']
            
            # Handle both dict and list formats
            if isinstance(results, dict):
                recent = list(results.items())[-5:]
            elif isinstance(results, list):
                recent = [(i, r) for i, r in enumerate(results[-5:])]
            else:
                recent = []
            
            if recent:
                for startup_id, result in recent:
                    name = result.get('name', f'ID {startup_id}')[:40]
                    is_provider = result.get('venture_clienting_analysis', {}).get('can_axa_use_as_provider', False)
                    tier = result.get('tier', 'N/A')
                    score = result.get('score', 0)
                    
                    provider_icon = "✅" if is_provider else "❌"
                    print(f"  {provider_icon} {name:40s} | Tier {tier} | Score: {score:3.0f}")
            else:
                print("  ⏳ Waiting for results...")
        else:
            print("  ⏳ Waiting for evaluation data...")
        
        print()
        print("=" * 80)
        print("Press Ctrl+C to exit (evaluation continues in background)")
        print("=" * 80)
        
        # Update every 3 seconds
        try:
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped. Evaluation continues in background.")
            print(f"   Checkpoint: downloads/axa_enhanced_checkpoint.json")
            print(f"   Results will be in: downloads/axa_full_3665_results.json")
            break

if __name__ == '__main__':
    main()
