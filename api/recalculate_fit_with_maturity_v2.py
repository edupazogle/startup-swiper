#!/usr/bin/env python3
"""
Recalculate AXA Fit Score with Maturity Factors
Uses SQL query to avoid JSON parsing issues
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Maturity scoring configuration
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
    if value <= 0:
        return brackets[-1][1]
    for threshold, score in brackets:
        if value >= threshold:
            return score
    return brackets[-1][1]


def score_funding_stage(stage: Optional[str]) -> int:
    if not stage:
        return FUNDING_STAGE_SCORES['unknown']
    stage_lower = str(stage).lower().replace(' ', '_')
    for key, score in FUNDING_STAGE_SCORES.items():
        if key in stage_lower:
            return score
    return FUNDING_STAGE_SCORES['unknown']


def calculate_maturity_score(startup_data: Tuple) -> Dict[str, Any]:
    (startup_id, name, funding_stage, total_funding, employees, 
     founding_year, rev_min, rev_max) = startup_data
    
    # Parse and score components
    emp_count = parse_employee_count(employees)
    current_year = datetime.now().year
    age = current_year - founding_year if founding_year else 0
    
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
    
    return {
        'maturity_score': round(maturity_score, 2),
        'growth_stage': growth_stage,
        'components': {
            'funding_stage': {'value': funding_stage or 'unknown', 'score': funding_stage_score},
            'funding_amount': {'value': total_funding, 'score': funding_amount_score},
            'revenue': {'score': revenue_score},
            'team_size': {'value': employees, 'parsed': emp_count, 'score': team_score},
            'company_age': {'founding_year': founding_year, 'age': age, 'score': age_score},
            'growth_stage': {'stage': growth_stage, 'score': growth_score}
        }
    }


def recalculate_fit_score(original_score, maturity_score, can_use_as_provider, 
                         weight_orig=0.60, weight_mat=0.40):
    combined = original_score * weight_orig + maturity_score * weight_mat
    if not can_use_as_provider:
        combined *= 0.5
    
    if combined >= 80:
        tier = "Tier 1: Critical Priority"
    elif combined >= 65:
        tier = "Tier 2: High Priority"
    elif combined >= 45:
        tier = "Tier 3: Medium Priority"
    else:
        tier = "Tier 4: Low Priority"
    
    return {
        'original_score': round(original_score, 2),
        'maturity_score': round(maturity_score, 2),
        'combined_score': round(combined, 2),
        'new_tier': tier
    }


def main():
    print("\n" + "="*80)
    print("🔄 RECALCULATING FIT SCORES WITH MATURITY FACTORS")
    print("="*80 + "\n")
    
    # Load evaluations
    input_file = 'downloads/axa_full_3665_results.json'
    output_file = 'downloads/axa_enhanced_with_maturity.json'
    
    print(f"📂 Loading evaluations: {input_file}")
    with open(input_file, 'r') as f:
        evaluations = json.load(f)
    print(f"✓ Loaded {len(evaluations)} evaluations\n")
    
    # Connect to database
    print("🗄️  Connecting to database...")
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    
    # Process each evaluation
    enhanced_results = []
    stats = {'total': 0, 'tier_changes': 0, 'score_improvements': 0, 
             'score_decreases': 0, 'new_tiers': {}}
    
    print("⚙️  Processing with weights: Original=60%, Maturity=40%\n")
    
    for i, eval_data in enumerate(evaluations, 1):
        if i % 100 == 0:
            print(f"  Processed: {i}/{len(evaluations)}")
        
        startup_id = eval_data['startup_id']
        original_score = eval_data['overall_score']
        original_tier = eval_data['priority_tier']
        can_use = eval_data.get('can_use_as_provider', False)
        
        # Query startup data
        cursor.execute('''
            SELECT id, company_name, funding_stage, total_funding, employees,
                   founding_year, latest_revenue_min, latest_revenue_max
            FROM startups WHERE id = ?
        ''', (startup_id,))
        
        startup_data = cursor.fetchone()
        if not startup_data:
            enhanced_results.append(eval_data)
            continue
        
        # Calculate maturity
        maturity_data = calculate_maturity_score(startup_data)
        
        # Recalculate fit score
        new_score_data = recalculate_fit_score(
            original_score, maturity_data['maturity_score'], can_use
        )
        
        # Create enhanced result
        enhanced_result = {
            **eval_data,
            'maturity_analysis': maturity_data,
            'score_recalculation': new_score_data,
            'final_score': new_score_data['combined_score'],
            'final_tier': new_score_data['new_tier'],
            'original_tier': original_tier
        }
        
        enhanced_results.append(enhanced_result)
        
        # Update stats
        stats['total'] += 1
        if new_score_data['new_tier'] != original_tier:
            stats['tier_changes'] += 1
        if new_score_data['combined_score'] > original_score:
            stats['score_improvements'] += 1
        elif new_score_data['combined_score'] < original_score:
            stats['score_decreases'] += 1
        stats['new_tiers'][new_score_data['new_tier']] = stats['new_tiers'].get(new_score_data['new_tier'], 0) + 1
    
    conn.close()
    
    # Save results
    print(f"\n💾 Saving enhanced results: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(enhanced_results, f, indent=2)
    
    # Print summary
    print(f"\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80 + "\n")
    print(f"Total Processed:      {stats['total']}")
    print(f"Tier Changes:         {stats['tier_changes']} ({stats['tier_changes']*100/stats['total']:.1f}%)")
    print(f"Score Improvements:   {stats['score_improvements']} ({stats['score_improvements']*100/stats['total']:.1f}%)")
    print(f"Score Decreases:      {stats['score_decreases']} ({stats['score_decreases']*100/stats['total']:.1f}%)\n")
    print("New Tier Distribution:")
    for tier in sorted(stats['new_tiers'].keys()):
        count = stats['new_tiers'][tier]
        print(f"  {tier}: {count} ({count*100/stats['total']:.1f}%)")
    print(f"\n✅ Complete! Enhanced results: {output_file}\n")


if __name__ == '__main__':
    main()
