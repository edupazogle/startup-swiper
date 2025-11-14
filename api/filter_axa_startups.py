#!/usr/bin/env python3
"""
AXA Startup Filter - Identify startups matching AXA's strategic criteria

This script filters the 4,374 SLUSH 2025 startups based on AXA's specific needs:
- Rule 1: Agentic Platform Enablers (for internal platform building)
- Rule 2: Agentic Service Providers (non-insurance enterprise solutions)
- Rule 3: Insurance-Specific Solutions (claims, underwriting, etc.)
- Rule 4: Health Innovations (insurance-applicable)
- Rule 5: Development & Legacy Modernization (code, QA, migration)

Each startup receives a priority score (0-100) and tier assignment.

Usage:
    # Filter with default threshold (score >= 40)
    python3 api/filter_axa_startups.py --output downloads/axa_startups.json
    
    # High priority only (score >= 60)
    python3 api/filter_axa_startups.py --min-score 60 --output downloads/axa_high_priority.json
    
    # By specific rule
    python3 api/filter_axa_startups.py --rule 1 --output downloads/axa_rule1_platform.json
    
    # Generate all tier files
    python3 api/filter_axa_startups.py --split-by-tier --output-dir downloads/axa_tiers/
    
    # With detailed scoring breakdown
    python3 api/filter_axa_startups.py --include-scoring --stats --output downloads/axa_scored.json
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# KEYWORD DEFINITIONS FOR EACH RULE
# ============================================================================

RULE_1_KEYWORDS = {
    'primary': [
        'observability', 'monitoring', 'tracing', 'agent orchestration',
        'llm ops', 'mlops', 'ai ops', 'agent framework', 'multi-agent',
        'vector database', 'embedding', 'rag', 'workflow automation',
        'agent builder', 'model deployment', 'ai platform', 'agent testing'
    ],
    'secondary': [
        'langchain', 'llm', 'agent', 'orchestration', 'infrastructure',
        'platform', 'framework', 'sdk', 'api management', 'agent mesh',
        'llm monitoring', 'ai infrastructure', 'model ops'
    ]
}

RULE_2_KEYWORDS = {
    'primary': [
        'marketing automation', 'sales ai', 'customer support automation',
        'recruiting ai', 'hr automation', 'finance automation',
        'contract intelligence', 'data analytics ai', 'conversational ai',
        'customer service ai', 'sales enablement', 'lead generation'
    ],
    'secondary': [
        'automation', 'ai agent', 'intelligent assistant', 'chatbot',
        'virtual assistant', 'rpa', 'process automation', 'workflow',
        'business intelligence', 'analytics', 'crm', 'erp'
    ]
}

RULE_3_KEYWORDS = {
    'primary': [
        'insurance', 'insurtech', 'claims', 'underwriting', 'policy',
        'actuarial', 'reinsurance', 'fraud detection insurance',
        'insurance platform', 'claims automation', 'underwriting automation',
        'insurance ai', 'risk assessment insurance'
    ],
    'secondary': [
        'claim', 'policyholder', 'premium', 'coverage', 'fnol',
        'loss adjusting', 'insurance distribution', 'insurance compliance',
        'insurance regulatory', 'carrier'
    ]
}

RULE_4_KEYWORDS = {
    'primary': [
        'health analytics', 'medical ai', 'telemedicine', 'digital health',
        'healthtech', 'wellness platform', 'remote monitoring',
        'healthcare data', 'preventive health', 'population health',
        'mental health platform', 'chronic disease', 'digital therapeutics'
    ],
    'secondary': [
        'health', 'healthcare', 'medical', 'wellness', 'wearable',
        'telehealth', 'patient', 'clinical', 'diagnosis', 'treatment',
        'health insurance', 'payer', 'hospital', 'care management'
    ]
}

RULE_5_KEYWORDS = {
    'primary': [
        'code generation', 'ai coding', 'test automation', 'qa automation',
        'legacy modernization', 'cobol migration', 'mainframe modernization',
        'code migration', 'legacy integration', 'devops automation',
        'ci/cd', 'code intelligence', 'automated testing'
    ],
    'secondary': [
        'developer', 'software development', 'programming', 'code',
        'testing', 'quality assurance', 'legacy', 'migration',
        'integration', 'api', 'microservices', 'cloud migration',
        'technical debt', 'refactoring', 'copilot', 'code assistant'
    ]
}

EXCLUSION_KEYWORDS = [
    'insurance carrier we are', 'insurance company we provide',
    'b2c', 'consumer app', 'gaming', 'game', 'entertainment',
    'food delivery', 'restaurant', 'e-commerce platform',
    'online marketplace', 'social network', 'dating',
    'cryptocurrency', 'nft', 'blockchain gaming'
]


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def text_search(text: str, keywords: List[str]) -> int:
    """Search for keywords in text, return count of matches"""
    if not text:
        return 0
    text_lower = text.lower()
    count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return count


def matches_rule_1(startup: Dict) -> Tuple[bool, int, List[str]]:
    """Rule 1: Agentic Platform Enablers"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []))}"
    
    primary_matches = text_search(search_text, RULE_1_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_1_KEYWORDS['secondary'])
    
    # Need at least 1 primary or 2 secondary matches
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_1_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_2(startup: Dict) -> Tuple[bool, int, List[str]]:
    """Rule 2: Agentic Service Providers (Non-Insurance)"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []))}"
    
    # Exclude if insurance-specific
    if text_search(search_text, ['insurance', 'insurtech', 'claims', 'underwriting']) > 0:
        return False, 0, []
    
    primary_matches = text_search(search_text, RULE_2_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_2_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 3
    confidence = min(100, (primary_matches * 25) + (secondary_matches * 8))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_2_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_3(startup: Dict) -> Tuple[bool, int, List[str]]:
    """Rule 3: Insurance-Specific Solutions"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []))}"
    
    primary_matches = text_search(search_text, RULE_3_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_3_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 35) + (secondary_matches * 12))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_3_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_4(startup: Dict) -> Tuple[bool, int, List[str]]:
    """Rule 4: Health Innovations (Insurance Applicable)"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []))}"
    
    primary_matches = text_search(search_text, RULE_4_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_4_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 2
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_4_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def matches_rule_5(startup: Dict) -> Tuple[bool, int, List[str]]:
    """Rule 5: Development & Legacy Modernization"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')} {' '.join(startup.get('topics', []))}"
    
    primary_matches = text_search(search_text, RULE_5_KEYWORDS['primary'])
    secondary_matches = text_search(search_text, RULE_5_KEYWORDS['secondary'])
    
    matches = primary_matches >= 1 or secondary_matches >= 3
    confidence = min(100, (primary_matches * 30) + (secondary_matches * 10))
    
    matched_keywords = []
    text_lower = search_text.lower()
    for kw in RULE_5_KEYWORDS['primary']:
        if kw in text_lower:
            matched_keywords.append(kw)
    
    return matches, confidence, matched_keywords[:5]


def should_exclude(startup: Dict) -> bool:
    """Check if startup should be excluded"""
    search_text = f"{startup.get('description', '')} {startup.get('shortDescription', '')}".lower()
    
    # Check exclusion keywords
    for keyword in EXCLUSION_KEYWORDS:
        if keyword in search_text:
            return True
    
    return False


def calculate_traction_score(startup: Dict) -> int:
    """Calculate corporate traction score (0-25 points)"""
    description = f"{startup.get('description', '')} {startup.get('shortDescription', '')}".lower()
    
    # Look for indicators of corporate customers
    enterprise_indicators = [
        'fortune 500', 'enterprise', 'global companies', 'leading companies',
        'customers include', 'trusted by', 'partners with', 'major corporations'
    ]
    
    has_indicators = sum(1 for indicator in enterprise_indicators if indicator in description)
    
    if has_indicators >= 3:
        return 25
    elif has_indicators >= 2:
        return 20
    elif has_indicators >= 1:
        return 15
    elif startup.get('employees', '').startswith(('11-50', '51-200', '201-500', '501+')):
        return 10
    else:
        return 5


def calculate_innovation_score(startup: Dict) -> int:
    """Calculate innovation score (0-15 points)"""
    description = f"{startup.get('description', '')} {startup.get('shortDescription', '')}".lower()
    
    innovation_keywords = [
        'ai', 'artificial intelligence', 'machine learning', 'deep learning',
        'automation', 'autonomous', 'agentic', 'innovative', 'breakthrough',
        'patent', 'proprietary', 'cutting-edge', 'next-generation'
    ]
    
    count = sum(1 for keyword in innovation_keywords if keyword in description)
    
    if count >= 5:
        return 15
    elif count >= 3:
        return 12
    elif count >= 2:
        return 8
    elif count >= 1:
        return 5
    else:
        return 3


def calculate_stage_score(startup: Dict) -> int:
    """Calculate company stage score (0-10 points)"""
    maturity = str(startup.get('maturity', '')).lower()
    employees = startup.get('employees', '')
    
    if 'scaleup' in maturity:
        return 10
    elif 'startup' in maturity:
        return 8
    elif 'validating' in maturity or 'deploying' in maturity:
        return 6
    elif 'emerging' in maturity:
        return 6
    elif employees and (employees.startswith('11-50') or employees.startswith('51-')):
        return 7
    else:
        return 3


def calculate_geo_score(startup: Dict) -> int:
    """Calculate geographic advantage score (0-5 points)"""
    country = str(startup.get('billingCountry', '')).upper()
    
    # European countries
    eu_countries = ['FI', 'FINLAND', 'DE', 'GERMANY', 'FR', 'FRANCE', 'GB', 'UK', 
                    'UNITED KINGDOM', 'ES', 'SPAIN', 'IT', 'ITALY', 'SE', 'SWEDEN',
                    'NL', 'NETHERLANDS', 'BE', 'BELGIUM', 'CH', 'SWITZERLAND',
                    'NO', 'NORWAY', 'DK', 'DENMARK', 'AT', 'AUSTRIA', 'IE', 'IRELAND']
    
    if country in eu_countries:
        return 5
    elif country in ['US', 'UNITED STATES', 'CA', 'CANADA']:
        return 2
    else:
        return 0


def calculate_data_quality_score(startup: Dict) -> int:
    """Calculate data quality score (0-5 points)"""
    if startup.get('is_enriched') or startup.get('enrichment'):
        return 5
    elif startup.get('website') and startup.get('description'):
        return 3
    elif startup.get('website'):
        return 1
    else:
        return 0


def calculate_axa_score(startup: Dict) -> Dict:
    """Calculate comprehensive AXA priority score"""
    
    # Check exclusions first
    if should_exclude(startup):
        return {
            'total_score': 0,
            'tier': 'Excluded',
            'matched_rules': [],
            'rule_scores': {},
            'breakdown': {'excluded': True}
        }
    
    # Check rule matches
    rule_matches = []
    rule_scores = {}
    max_rule_score = 0
    
    rules = {
        'Rule 1: Platform Enablers': (matches_rule_1, 40),
        'Rule 2: Service Providers': (matches_rule_2, 35),
        'Rule 3: Insurance Solutions': (matches_rule_3, 35),
        'Rule 4: Health Innovations': (matches_rule_4, 30),
        'Rule 5: Dev & Legacy': (matches_rule_5, 35)
    }
    
    for rule_name, (rule_func, base_score) in rules.items():
        matches, confidence, keywords = rule_func(startup)
        if matches:
            rule_matches.append(rule_name)
            # Score is base_score weighted by confidence
            score = int(base_score * (confidence / 100))
            rule_scores[rule_name] = {
                'score': score,
                'confidence': confidence,
                'keywords': keywords
            }
            max_rule_score = max(max_rule_score, score)
    
    # Multiple rule bonus
    multi_rule_bonus = 10 if len(rule_matches) > 1 else 0
    rule_total = max_rule_score + multi_rule_bonus
    
    # Other scoring factors
    traction = calculate_traction_score(startup)
    innovation = calculate_innovation_score(startup)
    stage = calculate_stage_score(startup)
    geo = calculate_geo_score(startup)
    data_quality = calculate_data_quality_score(startup)
    
    total_score = rule_total + traction + innovation + stage + geo + data_quality
    
    # Determine tier
    if total_score >= 80:
        tier = 'Tier 1: Must Meet'
    elif total_score >= 60:
        tier = 'Tier 2: High Priority'
    elif total_score >= 40:
        tier = 'Tier 3: Medium Priority'
    elif total_score >= 20:
        tier = 'Tier 4: Low Priority'
    else:
        tier = 'Excluded'
    
    return {
        'total_score': total_score,
        'tier': tier,
        'matched_rules': rule_matches,
        'rule_scores': rule_scores,
        'breakdown': {
            'rule_score': rule_total,
            'multi_rule_bonus': multi_rule_bonus,
            'traction': traction,
            'innovation': innovation,
            'stage': stage,
            'geographic': geo,
            'data_quality': data_quality
        }
    }


# ============================================================================
# MAIN FILTERING LOGIC
# ============================================================================

def filter_startups(startups: List[Dict], min_score: int = 40, 
                   specific_rule: Optional[int] = None) -> List[Dict]:
    """Filter and score startups based on AXA criteria"""
    
    filtered = []
    
    for startup in startups:
        scoring = calculate_axa_score(startup)
        
        # Apply minimum score filter
        if scoring['total_score'] < min_score:
            continue
        
        # Apply specific rule filter if requested
        if specific_rule:
            rule_name = f"Rule {specific_rule}"
            if not any(rule_name in matched for matched in scoring['matched_rules']):
                continue
        
        # Add scoring to startup data
        startup['axa_scoring'] = scoring
        filtered.append(startup)
    
    # Sort by score (highest first)
    filtered.sort(key=lambda x: x['axa_scoring']['total_score'], reverse=True)
    
    return filtered


def main():
    parser = argparse.ArgumentParser(
        description='Filter startups for AXA based on strategic criteria',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Input/Output
    parser.add_argument('--input', default='docs/architecture/ddbb/slush2_extracted.json',
                        help='Input database file')
    parser.add_argument('--output', '-o',
                        help='Output file (single file mode)')
    parser.add_argument('--output-dir',
                        help='Output directory (for split-by-tier mode)')
    
    # Filtering options
    parser.add_argument('--min-score', type=int, default=40,
                        help='Minimum score threshold (default: 40)')
    parser.add_argument('--rule', type=int, choices=[1, 2, 3, 4, 5],
                        help='Filter by specific rule only')
    parser.add_argument('--split-by-tier', action='store_true',
                        help='Split output into separate files by tier')
    
    # Output options
    parser.add_argument('--include-scoring', action='store_true',
                        help='Include detailed scoring breakdown in output')
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics')
    parser.add_argument('--csv', action='store_true',
                        help='Also export summary CSV')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.output and not args.output_dir:
        parser.error("Either --output or --output-dir must be specified")
    
    # Load startups
    base_path = Path(__file__).parent.parent
    input_file = base_path / args.input
    
    logger.info(f"Loading startups from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        startups = json.load(f)
    logger.info(f"Loaded {len(startups)} startups")
    
    # Filter startups
    logger.info(f"Filtering with min_score={args.min_score}")
    if args.rule:
        logger.info(f"Filtering for Rule {args.rule} only")
    
    filtered = filter_startups(startups, args.min_score, args.rule)
    logger.info(f"Filtered to {len(filtered)} startups ({100*len(filtered)/len(startups):.1f}%)")
    
    # Statistics
    if args.stats:
        print("\n" + "="*70)
        print("AXA STARTUP FILTERING RESULTS")
        print("="*70)
        
        # Tier breakdown
        tier_counts = {}
        for s in filtered:
            tier = s['axa_scoring']['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print(f"\n📊 TIER BREAKDOWN:")
        for tier in ['Tier 1: Must Meet', 'Tier 2: High Priority', 
                     'Tier 3: Medium Priority', 'Tier 4: Low Priority']:
            count = tier_counts.get(tier, 0)
            if count > 0:
                print(f"  {tier}: {count}")
        
        # Rule breakdown
        rule_counts = {}
        for s in filtered:
            for rule in s['axa_scoring']['matched_rules']:
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        print(f"\n📋 RULE MATCHES:")
        for rule, count in sorted(rule_counts.items()):
            print(f"  {rule}: {count}")
        
        # Top 10 by score
        print(f"\n🏆 TOP 10 STARTUPS BY SCORE:")
        for i, s in enumerate(filtered[:10], 1):
            score = s['axa_scoring']['total_score']
            tier = s['axa_scoring']['tier']
            rules = ', '.join([r.split(':')[0] for r in s['axa_scoring']['matched_rules']])
            print(f"  {i}. {s['name']} (Score: {score}, {rules})")
        
        print("="*70 + "\n")
    
    # Output
    if args.split_by_tier:
        output_dir = base_path / args.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Split by tier
        by_tier = {}
        for s in filtered:
            tier = s['axa_scoring']['tier']
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(s)
        
        # Save each tier
        for tier, startups_in_tier in by_tier.items():
            tier_num = tier.split(':')[0].replace('Tier ', '').strip()
            filename = f"axa_tier{tier_num}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(startups_in_tier, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(startups_in_tier)} startups to {filepath}")
    
    if args.output:
        output_path = base_path / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove scoring if not requested
        output_data = filtered
        if not args.include_scoring:
            output_data = []
            for s in filtered:
                s_copy = s.copy()
                s_copy.pop('axa_scoring', None)
                output_data.append(s_copy)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved {len(output_data)} startups to {args.output}")
    
    # CSV export
    if args.csv and args.output:
        import csv
        csv_path = str(args.output).replace('.json', '.csv')
        csv_full_path = base_path / csv_path
        
        with open(csv_full_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['name', 'website', 'country', 'maturity', 'score', 'tier', 'matched_rules']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for s in filtered:
                writer.writerow({
                    'name': s['name'],
                    'website': s.get('website', ''),
                    'country': s.get('billingCountry', ''),
                    'maturity': s.get('maturity', ''),
                    'score': s['axa_scoring']['total_score'],
                    'tier': s['axa_scoring']['tier'],
                    'matched_rules': '; '.join(s['axa_scoring']['matched_rules'])
                })
        
        logger.info(f"✓ Saved CSV to {csv_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
