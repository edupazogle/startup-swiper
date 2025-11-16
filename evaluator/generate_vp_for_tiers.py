#!/usr/bin/env python3
"""
Generate value propositions for Tier 2, 3, and 4 startups
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal
from models_startup import Startup
import asyncio
from value_proposition_generator import ValuePropositionGenerator
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

async def main():
    # Load Tier 2, 3, and 4 startups
    db = SessionLocal()
    try:
        tiers = ['Tier 2: High Priority', 'Tier 3: Medium Priority', 'Tier 4: Low Priority']
        
        query = db.query(Startup).filter(
            Startup.axa_priority_tier.in_(tiers)
        ).order_by(
            # Process in priority order: Tier 2 first, then 3, then 4
            Startup.axa_priority_tier
        )
        
        startups = query.all()
        
        if not startups:
            logger.error("No Tier 2/3/4 startups found")
            return
        
        logger.info(f"📚 Loaded {len(startups)} Tier 2/3/4 startups from database")
        
        # Show breakdown
        for tier in tiers:
            count = sum(1 for s in startups if s.axa_priority_tier == tier)
            logger.info(f"   {tier}: {count} companies")
        
    finally:
        db.close()
    
    # Generate value propositions with good concurrency
    async with ValuePropositionGenerator(
        batch_size=3,
        max_workers=15
    ) as generator:
        
        results = await generator.generate_value_propositions(startups)
        
        # Save results
        output_path = Path(__file__).parent / "downloads" / "value_propositions_tier234.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        generator.save_results(output_path)
        
        # Print summary
        print("\n" + "="*80)
        print("VALUE PROPOSITION GENERATION SUMMARY - TIER 2/3/4")
        print("="*80)
        print(f"✓ Successfully processed: {len(results)}")
        print(f"✗ Errors: {len(generator.errors)}")
        print(f"📁 Output file: {output_path}")
        
        # Show sample results
        if results:
            print("\n" + "-"*80)
            print("SAMPLE VALUE PROPOSITIONS")
            print("-"*80)
            for vp in results[:5]:
                print(f"\n🏢 {vp.company_name}")
                print(f"   Value: {vp.value_proposition}")
                print(f"   Product: {vp.core_product}")
                print(f"   Customers: {vp.target_customers}")
                print(f"   Confidence: {vp.confidence}")

if __name__ == "__main__":
    asyncio.run(main())
