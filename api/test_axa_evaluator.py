#!/usr/bin/env python3
"""
Quick test of AXA evaluator on a few sample startups
"""

import sys
sys.path.insert(0, '/home/akyo/startup_swiper/api')

from database import SessionLocal
from models_startup import Startup
from axa_comprehensive_evaluator import StartupEvaluator, CategoryType, analyze_results, print_summary
import json

def main():
    print("\n🧪 Testing AXA Evaluator on Sample Startups\n")
    
    db = SessionLocal()
    
    # Get a few diverse startups
    test_startups = db.query(Startup).limit(5).all()
    
    print(f"Testing with {len(test_startups)} startups:")
    for s in test_startups:
        print(f"  • {s.company_name} ({s.primary_industry})")
    
    print("\n" + "="*60)
    print("Starting evaluation...")
    print("="*60 + "\n")
    
    evaluator = StartupEvaluator(use_nvidia_nim=True)
    
    results = []
    for startup in test_startups:
        try:
            evaluation = evaluator.evaluate_startup(startup)
            results.append(evaluation.__dict__)
            
            # Convert CategoryMatch objects to dicts
            results[-1]['categories_matched'] = [
                {
                    'category': cm.category,
                    'matches': cm.matches,
                    'confidence': cm.confidence,
                    'reasoning': cm.reasoning,
                    'key_indicators': cm.key_indicators,
                    'potential_use_cases': cm.potential_use_cases,
                    'risk_factors': cm.risk_factors
                }
                for cm in results[-1]['categories_matched']
            ]
            
            print(f"\n✓ Evaluated: {startup.company_name}")
            print(f"  Overall Score: {results[-1]['overall_score']:.1f}")
            print(f"  Tier: {results[-1]['priority_tier']}")
            
            matched = [c for c in results[-1]['categories_matched'] if c['matches']]
            if matched:
                print(f"  Matched Categories: {len(matched)}")
                for m in matched:
                    print(f"    - {m['category']} (confidence: {m['confidence']}%)")
            
        except Exception as e:
            print(f"\n✗ Error evaluating {startup.company_name}: {e}")
            import traceback
            traceback.print_exc()
    
    evaluator.close()
    db.close()
    
    # Save results
    with open('/home/akyo/startup_swiper/downloads/axa_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    print(f"\nResults saved to: downloads/axa_test_results.json")
    
    # Quick analysis
    if results:
        analysis = analyze_results(results)
        print_summary(analysis)

if __name__ == '__main__':
    main()
