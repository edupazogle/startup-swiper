#!/usr/bin/env python3
"""
Test the enhanced AXA provider filtering with NVIDIA NIM

This script tests edge cases and validates that unsuitable providers are properly filtered.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from filter_axa_startups_enhanced import can_be_axa_provider, should_exclude

# Test cases - startups that SHOULD be excluded (NOT viable providers for AXA)
SHOULD_EXCLUDE_CASES = [
    {
        'company_name': 'DatingApp Inc',
        'company_description': 'A mobile dating app connecting singles based on AI matchmaking algorithms. B2C social platform.',
        'primary_industry': 'Social Media',
        'topics': ['dating', 'social', 'mobile app', 'matchmaking']
    },
    {
        'company_name': 'FoodDelivery Pro',
        'company_description': 'Food delivery marketplace connecting restaurants with hungry consumers. Mobile-first consumer app.',
        'primary_industry': 'Food & Beverage',
        'topics': ['food delivery', 'marketplace', 'mobile', 'restaurants']
    },
    {
        'company_name': 'GameStudio XYZ',
        'company_description': 'Mobile gaming studio creating casual games for entertainment. Focus on consumer engagement.',
        'primary_industry': 'Gaming',
        'topics': ['mobile games', 'entertainment', 'casual gaming']
    },
    {
        'company_name': 'FashionMarket',
        'company_description': 'Online marketplace for fashion and beauty products. Direct-to-consumer e-commerce platform.',
        'primary_industry': 'E-commerce',
        'topics': ['fashion', 'e-commerce', 'consumer', 'marketplace', 'retail']
    },
    {
        'company_name': 'SocialConnect',
        'company_description': 'Social networking platform for community building and content creators. Consumer social app.',
        'primary_industry': 'Social Media',
        'topics': ['social network', 'community', 'creators', 'consumer']
    }
]

# Test cases - startups that SHOULD be included (viable providers for AXA)
SHOULD_INCLUDE_CASES = [
    {
        'company_name': 'InsureTech AI',
        'company_description': 'Enterprise AI platform for insurance claims automation and fraud detection. B2B SaaS serving insurance carriers.',
        'primary_industry': 'InsurTech',
        'topics': ['insurance', 'AI', 'claims automation', 'B2B', 'enterprise']
    },
    {
        'company_name': 'DevOps Platform',
        'company_description': 'Developer tools and CI/CD platform for enterprise software teams. Used by Fortune 500 companies.',
        'primary_industry': 'Developer Tools',
        'topics': ['devops', 'ci/cd', 'enterprise', 'automation', 'B2B']
    },
    {
        'company_name': 'DataAnalytics Pro',
        'company_description': 'Business intelligence and data analytics platform for financial services and insurance companies.',
        'primary_industry': 'Analytics',
        'topics': ['analytics', 'business intelligence', 'financial services', 'enterprise']
    },
    {
        'company_name': 'SecurityGuard',
        'company_description': 'Cybersecurity platform for enterprise threat detection and compliance management.',
        'primary_industry': 'Cybersecurity',
        'topics': ['security', 'compliance', 'enterprise', 'threat detection']
    },
    {
        'company_name': 'HealthData Corp',
        'company_description': 'Healthcare data analytics for payers and employers. Population health management platform.',
        'primary_industry': 'HealthTech',
        'topics': ['healthcare', 'payer solutions', 'analytics', 'B2B', 'employers']
    }
]


def test_filtering(use_llm=True):
    """Test the filtering logic"""
    
    print("="*80)
    print("TESTING AXA PROVIDER FILTERING - NVIDIA NIM ENHANCED")
    print("="*80)
    print()
    
    if use_llm:
        print("✓ Testing with NVIDIA NIM LLM analysis enabled")
    else:
        print("⚠ Testing WITHOUT LLM (keyword-based only)")
    
    print()
    
    # Test exclusions
    print("📛 TESTING CASES THAT SHOULD BE EXCLUDED (Not viable providers)")
    print("-" * 80)
    
    exclude_correct = 0
    exclude_total = len(SHOULD_EXCLUDE_CASES)
    
    for i, startup in enumerate(SHOULD_EXCLUDE_CASES, 1):
        company_name = startup['company_name']
        
        # Test both functions
        can_provide, reason = can_be_axa_provider(startup, use_llm=use_llm)
        should_excl = should_exclude(startup, use_llm=use_llm)
        
        is_excluded = (not can_provide) or should_excl
        
        if is_excluded:
            status = "✅ CORRECT"
            exclude_correct += 1
        else:
            status = "❌ WRONG - Should be excluded!"
        
        print(f"\n{i}. {company_name}")
        print(f"   Industry: {startup['primary_industry']}")
        print(f"   Decision: {'EXCLUDED' if is_excluded else 'INCLUDED'} {status}")
        if reason:
            print(f"   Reason: {reason[:100]}")
    
    exclude_accuracy = 100 * exclude_correct / exclude_total if exclude_total > 0 else 0
    print(f"\n📊 Exclusion Accuracy: {exclude_correct}/{exclude_total} ({exclude_accuracy:.0f}%)")
    
    # Test inclusions
    print("\n" + "="*80)
    print("✅ TESTING CASES THAT SHOULD BE INCLUDED (Viable providers)")
    print("-" * 80)
    
    include_correct = 0
    include_total = len(SHOULD_INCLUDE_CASES)
    
    for i, startup in enumerate(SHOULD_INCLUDE_CASES, 1):
        company_name = startup['company_name']
        
        can_provide, reason = can_be_axa_provider(startup, use_llm=use_llm)
        should_excl = should_exclude(startup, use_llm=use_llm)
        
        is_included = can_provide and not should_excl
        
        if is_included:
            status = "✅ CORRECT"
            include_correct += 1
        else:
            status = "❌ WRONG - Should be included!"
        
        print(f"\n{i}. {company_name}")
        print(f"   Industry: {startup['primary_industry']}")
        print(f"   Decision: {'INCLUDED' if is_included else 'EXCLUDED'} {status}")
        if reason:
            print(f"   Reason: {reason[:100]}")
    
    include_accuracy = 100 * include_correct / include_total if include_total > 0 else 0
    print(f"\n📊 Inclusion Accuracy: {include_correct}/{include_total} ({include_accuracy:.0f}%)")
    
    # Overall summary
    print("\n" + "="*80)
    print("📈 OVERALL RESULTS")
    print("="*80)
    
    total_correct = exclude_correct + include_correct
    total_cases = exclude_total + include_total
    overall_accuracy = 100 * total_correct / total_cases if total_cases > 0 else 0
    
    print(f"Total Correct: {total_correct}/{total_cases} ({overall_accuracy:.0f}%)")
    print(f"  - Exclusions: {exclude_correct}/{exclude_total} ({exclude_accuracy:.0f}%)")
    print(f"  - Inclusions: {include_correct}/{include_total} ({include_accuracy:.0f}%)")
    
    if overall_accuracy >= 90:
        print("\n✅ EXCELLENT - Filtering is highly accurate!")
    elif overall_accuracy >= 75:
        print("\n✓ GOOD - Filtering is working well with some edge cases")
    elif overall_accuracy >= 60:
        print("\n⚠ FAIR - Filtering needs improvement")
    else:
        print("\n❌ POOR - Filtering needs significant enhancement")
    
    print()
    
    return overall_accuracy >= 80


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test AXA provider filtering')
    parser.add_argument('--no-llm', action='store_true',
                       help='Test without LLM (keyword-based only)')
    
    args = parser.parse_args()
    
    success = test_filtering(use_llm=not args.no_llm)
    
    sys.exit(0 if success else 1)
