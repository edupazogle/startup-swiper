#!/usr/bin/env python3
"""
Update Database with Maturity-Enhanced AXA Scores
Calculates maturity scores and updates axa_overall_score and axa_priority_tier in database
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Maturity scoring configuration (same as recalculation script)
FUNDING_STAGE_SCORES = {
    'series_d': 100, 'series_c': 95, 'series_b': 85, 'series_a': 70,
    'seed': 50, 'pre_seed': 30, 'angel': 25, 'grant': 20,
    'bootstrapped': 40, 'unknown': 35
}

EMPLOYEE_BRACKETS = [
    (1000, 100), (500, 95), (250, 90), (100, 85), (50, 75),
    (25, 65), (10, 50), (5, 35), (1, 20)
]

FUNDING_BRACKETS = [
    (100, 100), (50, 95), (25, 90), (10, 85), (5, 75),
    (2, 65), (1, 50), (0.5, 40), (0.1, 25), (0, 10)
]

AGE_BRACKETS = [
    (15, 100), (10, 95), (7, 85), (5, 75), (3, 65),
    (2, 50), (1, 35), (0, 20)
]

GROWTH_STAGES = {
    'hypergrowth': 100, 'growth': 85, 'established': 70,
    'emerging': 50, 'startup': 35, 'unknown': 40
}


def parse_employee_count(emp_str: Optional[str]) -> int:
    """Parse employee count from various formats"""
    if not emp_str:
        return 0
    emp_str = str(emp_str).strip().lower()
    if '-' in emp_str:
        try:
            return int(emp_str.split('-')[1])
        except:
            pass
    if '+' in emp_str:
        try:
            return int(emp_str.replace('+', ''))
        except:
            pass
    try:
        return int(emp_str)
    except:
        return 0


def score_bracket(value: float, brackets: list) -> int:
    """Score value against bracket thresholds"""
    if value <= 0:
        return brackets[-1][1]
    for threshold, score in brackets:
        if value >= threshold:
            return score
    return brackets[-1][1]


def score_funding_stage(stage: Optional[str]) -> int:
    """Score funding stage"""
    if not stage:
        return FUNDING_STAGE_SCORES['unknown']
    stage_lower = str(stage).lower().replace(' ', '_')
    for key, score in FUNDING_STAGE_SCORES.items():
        if key in stage_lower:
            return score
    return FUNDING_STAGE_SCORES['unknown']


def calculate_maturity_score(startup_data: Tuple) -> float:
    """Calculate maturity score from startup data"""
    (funding_stage, total_funding, employees, founding_year, rev_min, rev_max) = startup_data
    
    # Parse components
    emp_count = parse_employee_count(employees)
    current_year = datetime.now().year
    age = current_year - founding_year if founding_year else 0
    
    # Score individual components
    funding_stage_score = score_funding_stage(funding_stage)
    funding_amount_score = score_bracket(total_funding or 0, FUNDING_BRACKETS)
    team_score = score_bracket(emp_count, EMPLOYEE_BRACKETS)
    age_score = score_bracket(age, AGE_BRACKETS)
    
    # Revenue scoring
    if rev_min or rev_max:
        revenue = ((rev_min or 0) + (rev_max or 0)) / 2 if (rev_min and rev_max) else (rev_min or rev_max or 0)
        rev_millions = revenue / 1_000_000 if revenue > 1_000_000 else revenue
        if rev_millions >= 100:
            revenue_score = 100
        elif rev_millions >= 50:
            revenue_score = 95
        elif rev_millions >= 25:
            revenue_score = 90
        elif rev_millions >= 10:
            revenue_score = 85
        elif rev_millions >= 5:
            revenue_score = 75
        elif rev_millions >= 1:
            revenue_score = 60
        else:
            revenue_score = 45
    else:
        revenue_score = 40
    
    # Determine growth stage
    if (total_funding and total_funding >= 50) or emp_count >= 250:
        growth_stage = 'hypergrowth'
    elif (total_funding and total_funding >= 10) or emp_count >= 50:
        growth_stage = 'growth'
    elif age >= 10 or emp_count >= 100:
        growth_stage = 'established'
    elif age >= 2 and age < 5:
        growth_stage = 'emerging'
    elif age < 2:
        growth_stage = 'startup'
    else:
        growth_stage = 'unknown'
    
    growth_score = GROWTH_STAGES[growth_stage]
    
    # Weighted maturity score
    maturity_score = (
        funding_stage_score * 0.25 +
        funding_amount_score * 0.20 +
        revenue_score * 0.20 +
        team_score * 0.15 +
        age_score * 0.10 +
        growth_score * 0.10
    )
    
    return maturity_score


def calculate_final_score(
    original_score: Optional[float],
    maturity_score: float,
    can_use_as_provider: bool,
    weight_original: float = 0.60,
    weight_maturity: float = 0.40
) -> Tuple[float, str]:
    """
    Calculate final score and tier
    Returns: (final_score, tier)
    """
    # If no original score, use maturity only
    if original_score is None or original_score == 0:
        combined_score = maturity_score
    else:
        combined_score = original_score * weight_original + maturity_score * weight_maturity
    
    # Apply provider penalty if needed
    if not can_use_as_provider:
        combined_score = combined_score * 0.5
    
    # Determine tier
    if combined_score >= 80:
        tier = "Tier 1: Critical Priority"
    elif combined_score >= 65:
        tier = "Tier 2: High Priority"
    elif combined_score >= 45:
        tier = "Tier 3: Medium Priority"
    else:
        tier = "Tier 4: Low Priority"
    
    return round(combined_score, 2), tier


def update_database(
    db_path: str = "startup_swiper.db",
    weight_original: float = 0.60,
    weight_maturity: float = 0.40,
    dry_run: bool = False
):
    """Update database with maturity-enhanced scores"""
    
    print("\n" + "="*80)
    print("🔄 UPDATING DATABASE WITH MATURITY-ENHANCED SCORES")
    print("="*80 + "\n")
    
    print(f"Database: {db_path}")
    print(f"Weights: Original={weight_original*100}%, Maturity={weight_maturity*100}%")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE UPDATE'}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all startups with AXA evaluations
    cursor.execute('''
        SELECT 
            id,
            company_name,
            axa_overall_score,
            axa_priority_tier,
            axa_can_use_as_provider,
            funding_stage,
            total_funding,
            employees,
            founding_year,
            latest_revenue_min,
            latest_revenue_max
        FROM startups
        WHERE axa_overall_score IS NOT NULL
    ''')
    
    startups = cursor.fetchall()
    print(f"📊 Found {len(startups)} startups with AXA evaluations\n")
    
    if len(startups) == 0:
        print("⚠️  No startups with AXA evaluations found!")
        print("   Run the evaluator first: python3 api/axa_enhanced_evaluator.py")
        conn.close()
        return
    
    # Process each startup
    updates = []
    stats = {
        'total': 0,
        'updated': 0,
        'tier_changes': 0,
        'score_improvements': 0,
        'score_decreases': 0,
        'new_tiers': {}
    }
    
    print("⚙️  Calculating maturity scores...")
    
    for row in startups:
        (startup_id, name, original_score, original_tier, can_use,
         funding_stage, total_funding, employees, founding_year, rev_min, rev_max) = row
        
        stats['total'] += 1
        
        # Calculate maturity score
        maturity_data = (funding_stage, total_funding, employees, founding_year, rev_min, rev_max)
        maturity_score = calculate_maturity_score(maturity_data)
        
        # Calculate final score and tier
        final_score, new_tier = calculate_final_score(
            original_score,
            maturity_score,
            bool(can_use),
            weight_original,
            weight_maturity
        )
        
        # Track changes
        if new_tier != original_tier:
            stats['tier_changes'] += 1
        if final_score > (original_score or 0):
            stats['score_improvements'] += 1
        elif final_score < (original_score or 0):
            stats['score_decreases'] += 1
        
        stats['new_tiers'][new_tier] = stats['new_tiers'].get(new_tier, 0) + 1
        
        # Store update
        updates.append({
            'id': startup_id,
            'name': name,
            'original_score': original_score,
            'maturity_score': maturity_score,
            'final_score': final_score,
            'original_tier': original_tier,
            'new_tier': new_tier
        })
        
        if stats['total'] % 100 == 0:
            print(f"  Processed: {stats['total']}/{len(startups)}")
    
    print(f"  Processed: {stats['total']}/{len(startups)}\n")
    
    # Show sample changes
    print("📋 Sample Score Changes (First 5):")
    print("-" * 80)
    for update in updates[:5]:
        print(f"  {update['name']}")
        print(f"    Score: {update['original_score']:.1f} → {update['final_score']:.1f} (Maturity: {update['maturity_score']:.1f})")
        print(f"    Tier:  {update['original_tier']} → {update['new_tier']}")
        print()
    
    # Apply updates to database
    if not dry_run:
        print("💾 Updating database...")
        
        for i, update in enumerate(updates, 1):
            cursor.execute('''
                UPDATE startups
                SET axa_overall_score = ?,
                    axa_priority_tier = ?,
                    axa_evaluation_date = ?
                WHERE id = ?
            ''', (
                update['final_score'],
                update['new_tier'],
                datetime.utcnow(),
                update['id']
            ))
            
            if i % 100 == 0:
                print(f"  Updated: {i}/{len(updates)}")
        
        conn.commit()
        print(f"  Updated: {len(updates)}/{len(updates)}")
        print("\n✅ Database updated successfully!")
    else:
        print("🔍 DRY RUN - No changes made to database")
    
    conn.close()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80 + "\n")
    
    print(f"Total Processed:      {stats['total']}")
    print(f"Tier Changes:         {stats['tier_changes']} ({stats['tier_changes']*100/stats['total']:.1f}%)")
    print(f"Score Improvements:   {stats['score_improvements']} ({stats['score_improvements']*100/stats['total']:.1f}%)")
    print(f"Score Decreases:      {stats['score_decreases']} ({stats['score_decreases']*100/stats['total']:.1f}%)\n")
    
    print("New Tier Distribution:")
    for tier in sorted(stats['new_tiers'].keys()):
        count = stats['new_tiers'][tier]
        pct = count * 100 / stats['total']
        print(f"  {tier}: {count} ({pct:.1f}%)")
    
    if not dry_run:
        print("\n✅ Database update complete!")
        print(f"   All {stats['total']} startup scores have been recalculated")
        print(f"   Query example: SELECT company_name, axa_overall_score, axa_priority_tier")
        print(f"                  FROM startups WHERE axa_priority_tier = 'Tier 2: High Priority'")
    else:
        print("\n🔍 This was a dry run. To apply changes, run without --dry-run flag")
    
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update database with maturity-enhanced AXA scores'
    )
    parser.add_argument(
        '--db',
        default='startup_swiper.db',
        help='Database path (default: startup_swiper.db)'
    )
    parser.add_argument(
        '--weight-original',
        type=float,
        default=0.60,
        help='Weight for original score (0-1, default 0.60)'
    )
    parser.add_argument(
        '--weight-maturity',
        type=float,
        default=0.40,
        help='Weight for maturity score (0-1, default 0.40)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without updating database'
    )
    
    args = parser.parse_args()
    
    # Validate weights
    if abs(args.weight_original + args.weight_maturity - 1.0) > 0.01:
        print("❌ Error: Weights must sum to 1.0")
        return 1
    
    update_database(
        args.db,
        args.weight_original,
        args.weight_maturity,
        args.dry_run
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
