#!/usr/bin/env python3
"""
Recalculate AXA Fit Score with Maturity Factors
Incorporates: funding stage, funding amount, employee count, founding year, revenue
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add API directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models_startup import Startup

# Maturity scoring weights
MATURITY_WEIGHTS = {
    'funding_stage': 0.25,      # 25%
    'funding_amount': 0.20,     # 20%
    'revenue': 0.20,            # 20%
    'team_size': 0.15,          # 15%
    'company_age': 0.10,        # 10%
    'growth_stage': 0.10        # 10%
}

# Funding stage scoring (0-100)
FUNDING_STAGE_SCORES = {
    'series_d': 100,
    'series_c': 95,
    'series_b': 85,
    'series_a': 70,
    'seed': 50,
    'pre_seed': 30,
    'angel': 25,
    'grant': 20,
    'bootstrapped': 40,  # Self-funded can be mature
    'unknown': 35
}

# Employee count scoring brackets
EMPLOYEE_BRACKETS = [
    (1000, 100),    # 1000+ employees = 100 points
    (500, 95),      # 500-999
    (250, 90),      # 250-499
    (100, 85),      # 100-249
    (50, 75),       # 50-99
    (25, 65),       # 25-49
    (10, 50),       # 10-24
    (5, 35),        # 5-9
    (1, 20)         # 1-4
]

# Funding amount scoring (in millions USD)
FUNDING_BRACKETS = [
    (100, 100),     # $100M+ = 100 points
    (50, 95),       # $50-100M
    (25, 90),       # $25-50M
    (10, 85),       # $10-25M
    (5, 75),        # $5-10M
    (2, 65),        # $2-5M
    (1, 50),        # $1-2M
    (0.5, 40),      # $500K-1M
    (0.1, 25),      # $100K-500K
    (0, 10)         # <$100K or unknown
]

# Company age scoring (years since founding)
AGE_BRACKETS = [
    (15, 100),      # 15+ years = very mature
    (10, 95),       # 10-15 years
    (7, 85),        # 7-10 years
    (5, 75),        # 5-7 years = sweet spot
    (3, 65),        # 3-5 years
    (2, 50),        # 2-3 years
    (1, 35),        # 1-2 years
    (0, 20)         # <1 year or unknown
]

# Growth stage classification
GROWTH_STAGES = {
    'hypergrowth': 100,      # Scaling rapidly
    'growth': 85,            # Growing steadily
    'established': 70,       # Stable, mature
    'emerging': 50,          # Early stage
    'startup': 35,           # Very early
    'unknown': 40
}


def parse_employee_count(emp_str: Optional[str]) -> int:
    """Parse employee count from string like '10-50' or '100+'"""
    if not emp_str:
        return 0
    
    emp_str = emp_str.strip().lower()
    
    # Handle ranges like "10-50"
    if '-' in emp_str:
        parts = emp_str.split('-')
        try:
            return int(parts[1])  # Use upper bound
        except:
            pass
    
    # Handle "100+" format
    if '+' in emp_str:
        try:
            return int(emp_str.replace('+', ''))
        except:
            pass
    
    # Try direct conversion
    try:
        return int(emp_str)
    except:
        return 0


def score_funding_stage(stage: Optional[str]) -> int:
    """Score funding stage (0-100)"""
    if not stage:
        return FUNDING_STAGE_SCORES['unknown']
    
    stage_lower = stage.lower().replace(' ', '_')
    
    # Match funding stage
    for key, score in FUNDING_STAGE_SCORES.items():
        if key in stage_lower:
            return score
    
    return FUNDING_STAGE_SCORES['unknown']


def score_funding_amount(amount: Optional[float]) -> int:
    """Score funding amount (0-100)"""
    if not amount or amount <= 0:
        return 10
    
    for threshold, score in FUNDING_BRACKETS:
        if amount >= threshold:
            return score
    
    return 10


def score_employee_count(count: int) -> int:
    """Score employee count (0-100)"""
    if count <= 0:
        return 20
    
    for threshold, score in EMPLOYEE_BRACKETS:
        if count >= threshold:
            return score
    
    return 20


def score_company_age(founding_year: Optional[int]) -> int:
    """Score company age (0-100)"""
    if not founding_year:
        return 20
    
    current_year = datetime.now().year
    age = current_year - founding_year
    
    if age < 0:  # Future year, data error
        return 20
    
    for threshold, score in AGE_BRACKETS:
        if age >= threshold:
            return score
    
    return 20


def score_revenue(rev_min: Optional[float], rev_max: Optional[float]) -> int:
    """Score revenue (0-100)"""
    if not rev_min and not rev_max:
        return 40  # Unknown, neutral score
    
    # Use average of min/max or whichever is available
    if rev_min and rev_max:
        revenue = (rev_min + rev_max) / 2
    else:
        revenue = rev_min or rev_max
    
    # Convert to millions if needed
    if revenue > 1_000_000:
        revenue_millions = revenue / 1_000_000
    else:
        revenue_millions = revenue
    
    # Revenue scoring
    if revenue_millions >= 100:
        return 100
    elif revenue_millions >= 50:
        return 95
    elif revenue_millions >= 25:
        return 90
    elif revenue_millions >= 10:
        return 85
    elif revenue_millions >= 5:
        return 75
    elif revenue_millions >= 1:
        return 60
    elif revenue_millions >= 0.5:
        return 45
    else:
        return 30


def determine_growth_stage(
    funding_stage: Optional[str],
    total_funding: Optional[float],
    employees: int,
    age: int
) -> str:
    """Determine growth stage based on multiple factors"""
    
    # Hypergrowth indicators
    if total_funding and total_funding >= 50:
        return 'hypergrowth'
    if employees >= 250:
        return 'hypergrowth'
    if funding_stage and 'series' in funding_stage.lower():
        series_letter = funding_stage.lower().split('series')[-1].strip()[0]
        if series_letter in ['c', 'd', 'e', 'f']:
            return 'hypergrowth'
    
    # Growth stage
    if total_funding and total_funding >= 10:
        return 'growth'
    if employees >= 50:
        return 'growth'
    if funding_stage and 'series' in funding_stage.lower():
        series_letter = funding_stage.lower().split('series')[-1].strip()[0]
        if series_letter in ['a', 'b']:
            return 'growth'
    
    # Established
    if age >= 10:
        return 'established'
    if employees >= 100:
        return 'established'
    
    # Emerging
    if funding_stage and 'seed' in funding_stage.lower():
        return 'emerging'
    if age >= 2 and age < 5:
        return 'emerging'
    
    # Startup
    if age < 2:
        return 'startup'
    
    return 'unknown'


def calculate_maturity_score(startup: Startup) -> Dict[str, Any]:
    """Calculate comprehensive maturity score"""
    
    # Parse employee count
    emp_count = parse_employee_count(startup.employees)
    
    # Calculate age
    current_year = datetime.now().year
    age = current_year - startup.founding_year if startup.founding_year else 0
    
    # Determine growth stage
    growth_stage = determine_growth_stage(
        startup.funding_stage,
        startup.total_funding,
        emp_count,
        age
    )
    
    # Calculate individual scores
    funding_stage_score = score_funding_stage(startup.funding_stage)
    funding_amount_score = score_funding_amount(startup.total_funding)
    revenue_score = score_revenue(startup.latest_revenue_min, startup.latest_revenue_max)
    team_score = score_employee_count(emp_count)
    age_score = score_company_age(startup.founding_year)
    growth_score = GROWTH_STAGES.get(growth_stage, 40)
    
    # Weighted overall maturity score
    maturity_score = (
        funding_stage_score * MATURITY_WEIGHTS['funding_stage'] +
        funding_amount_score * MATURITY_WEIGHTS['funding_amount'] +
        revenue_score * MATURITY_WEIGHTS['revenue'] +
        team_score * MATURITY_WEIGHTS['team_size'] +
        age_score * MATURITY_WEIGHTS['company_age'] +
        growth_score * MATURITY_WEIGHTS['growth_stage']
    )
    
    return {
        'maturity_score': round(maturity_score, 2),
        'growth_stage': growth_stage,
        'components': {
            'funding_stage': {
                'value': startup.funding_stage or 'unknown',
                'score': funding_stage_score
            },
            'funding_amount': {
                'value': startup.total_funding,
                'score': funding_amount_score
            },
            'revenue': {
                'min': startup.latest_revenue_min,
                'max': startup.latest_revenue_max,
                'score': revenue_score
            },
            'team_size': {
                'value': startup.employees,
                'parsed': emp_count,
                'score': team_score
            },
            'company_age': {
                'founding_year': startup.founding_year,
                'age': age,
                'score': age_score
            },
            'growth_stage': {
                'stage': growth_stage,
                'score': growth_score
            }
        }
    }


def recalculate_fit_score(
    original_score: float,
    maturity_score: float,
    can_use_as_provider: bool,
    weight_original: float = 0.60,
    weight_maturity: float = 0.40
) -> Dict[str, Any]:
    """
    Recalculate fit score combining original evaluation with maturity
    
    Args:
        original_score: Original AXA fit score (0-100)
        maturity_score: Maturity score (0-100)
        can_use_as_provider: Whether usable as B2B provider
        weight_original: Weight for original score (default 60%)
        weight_maturity: Weight for maturity score (default 40%)
    
    Returns:
        Dict with new score and tier
    """
    
    # Calculate combined score
    combined_score = (
        original_score * weight_original +
        maturity_score * weight_maturity
    )
    
    # Apply provider penalty if needed
    if not can_use_as_provider:
        combined_score = combined_score * 0.5
    
    # Determine new tier
    if combined_score >= 80:
        tier = "Tier 1: Critical Priority"
    elif combined_score >= 65:
        tier = "Tier 2: High Priority"
    elif combined_score >= 45:
        tier = "Tier 3: Medium Priority"
    else:
        tier = "Tier 4: Low Priority"
    
    return {
        'original_score': round(original_score, 2),
        'maturity_score': round(maturity_score, 2),
        'combined_score': round(combined_score, 2),
        'new_tier': tier,
        'score_breakdown': {
            'original_contribution': round(original_score * weight_original, 2),
            'maturity_contribution': round(maturity_score * weight_maturity, 2)
        }
    }


def process_evaluations(
    input_file: str,
    output_file: str,
    weight_original: float = 0.60,
    weight_maturity: float = 0.40
):
    """Process all evaluations and recalculate scores"""
    
    print(f"\n{'='*80}")
    print(f"🔄 RECALCULATING FIT SCORES WITH MATURITY FACTORS")
    print(f"{'='*80}\n")
    
    # Load evaluations
    print(f"📂 Loading evaluations from: {input_file}")
    with open(input_file, 'r') as f:
        evaluations = json.load(f)
    print(f"✓ Loaded {len(evaluations)} evaluations\n")
    
    # Connect to database
    print("🗄️  Connecting to database...")
    db = SessionLocal()
    
    # Process each evaluation
    enhanced_results = []
    stats = {
        'total': 0,
        'tier_changes': 0,
        'score_improvements': 0,
        'score_decreases': 0,
        'new_tiers': {}
    }
    
    print(f"⚙️  Processing with weights: Original={weight_original*100}%, Maturity={weight_maturity*100}%\n")
    
    for i, eval_data in enumerate(evaluations, 1):
        if i % 100 == 0:
            print(f"  Processed: {i}/{len(evaluations)}")
        
        startup_id = eval_data['startup_id']
        startup_name = eval_data['startup_name']
        original_score = eval_data['overall_score']
        original_tier = eval_data['priority_tier']
        can_use = eval_data.get('can_use_as_provider', False)
        
        # Get startup from database
        startup = db.query(Startup).filter(Startup.id == startup_id).first()
        
        if not startup:
            print(f"⚠️  Warning: Startup ID {startup_id} not found in database")
            enhanced_results.append(eval_data)
            continue
        
        # Calculate maturity score
        maturity_data = calculate_maturity_score(startup)
        
        # Recalculate fit score
        new_score_data = recalculate_fit_score(
            original_score,
            maturity_data['maturity_score'],
            can_use,
            weight_original,
            weight_maturity
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
        
        # Update statistics
        stats['total'] += 1
        if new_score_data['new_tier'] != original_tier:
            stats['tier_changes'] += 1
        if new_score_data['combined_score'] > original_score:
            stats['score_improvements'] += 1
        elif new_score_data['combined_score'] < original_score:
            stats['score_decreases'] += 1
        
        new_tier = new_score_data['new_tier']
        stats['new_tiers'][new_tier] = stats['new_tiers'].get(new_tier, 0) + 1
    
    db.close()
    
    # Save results
    print(f"\n💾 Saving enhanced results to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(enhanced_results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"Total Processed:      {stats['total']}")
    print(f"Tier Changes:         {stats['tier_changes']} ({stats['tier_changes']*100/stats['total']:.1f}%)")
    print(f"Score Improvements:   {stats['score_improvements']} ({stats['score_improvements']*100/stats['total']:.1f}%)")
    print(f"Score Decreases:      {stats['score_decreases']} ({stats['score_decreases']*100/stats['total']:.1f}%)\n")
    
    print("New Tier Distribution:")
    for tier in sorted(stats['new_tiers'].keys()):
        count = stats['new_tiers'][tier]
        pct = count * 100 / stats['total']
        print(f"  {tier}: {count} ({pct:.1f}%)")
    
    print(f"\n✅ Complete! Enhanced results saved to: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Recalculate AXA fit scores with maturity factors'
    )
    parser.add_argument(
        '--input',
        default='downloads/axa_full_3665_results.json',
        help='Input evaluation results JSON file'
    )
    parser.add_argument(
        '--output',
        default='downloads/axa_enhanced_with_maturity.json',
        help='Output file for enhanced results'
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
    
    args = parser.parse_args()
    
    # Validate weights
    if abs(args.weight_original + args.weight_maturity - 1.0) > 0.01:
        print("❌ Error: Weights must sum to 1.0")
        sys.exit(1)
    
    process_evaluations(
        args.input,
        args.output,
        args.weight_original,
        args.weight_maturity
    )


if __name__ == '__main__':
    main()
