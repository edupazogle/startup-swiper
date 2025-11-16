#!/usr/bin/env python3
"""
Batch script to recalculate Rise Scores for all startups using the rebalanced algorithm.
This script ONLY updates the overall_score field without re-running LLM evaluations.
Uses the same batch processing pattern as axa_enhanced_evaluator.py for consistency.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models_startup import Startup


@dataclass
class ScoreUpdate:
    """Data class for score updates"""
    startup_id: int
    startup_name: str
    old_score: float
    new_score: float
    tier: str
    confidence_avg: float
    rule_count: int
    maturity: Optional[str] = None
    country: Optional[str] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[float] = None


class RiseScoreCalculator:
    """Calculate Rise Scores using the new rebalanced algorithm"""
    
    def __init__(self):
        self.updates: List[ScoreUpdate] = []
        self.stats = {
            'total': 0,
            'updated': 0,
            'unchanged': 0,
            'errors': 0,
            'score_increases': 0,
            'score_decreases': 0,
        }
    
    def calculate_rise_score(
        self,
        startup: Startup,
        categories_matched: List[dict],
        matched_rules: List[str],
        can_use_as_provider: bool
    ) -> tuple[float, str]:
        """
        Calculate Rise Score using new rebalanced algorithm.
        
        Returns: (overall_score, priority_tier)
        """
        
        # Base score: Flat 20 points if can deliver
        base_score = 20 if matched_rules else 0
        
        # Rule match bonus (max 25 points) - PRIMARY DRIVER
        rule_match_bonus = 0
        if len(matched_rules) >= 3:
            rule_match_bonus = 25
        elif len(matched_rules) == 2:
            rule_match_bonus = 15
        elif len(matched_rules) == 1:
            rule_match_bonus = 10
        
        # Confidence boost (max 25 points) - INCREASED
        avg_confidence = 0
        if categories_matched:
            confidences = [cat.get('confidence', 0) for cat in categories_matched]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        confidence_points = (avg_confidence / 100) * 25
        
        # Maturity bonus (max 12 points) - IMPROVED GRANULARITY
        maturity_points = 0
        if startup.maturity:
            maturity_lower = startup.maturity.lower()
            if 'scaleup' in maturity_lower or 'established' in maturity_lower:
                maturity_points = 12
            elif 'scaling' in maturity_lower or 'growth' in maturity_lower:
                maturity_points = 8
            elif 'deploying' in maturity_lower or 'startup' in maturity_lower:
                maturity_points = 5
            elif 'validating' in maturity_lower:
                maturity_points = 3
            elif 'emerging' in maturity_lower:
                maturity_points = 1
        
        # Funding stage bonus (max 10 points)
        funding_points = 0
        if startup.funding_stage:
            stage_lower = startup.funding_stage.lower()
            if 'series c' in stage_lower or 'series d' in stage_lower or 'series e' in stage_lower:
                funding_points = 10
            elif 'series b' in stage_lower:
                funding_points = 8
            elif 'series a' in stage_lower:
                funding_points = 6
            elif 'seed' in stage_lower:
                funding_points = 4
        
        # Total funding boost (max 8 points) - INCREASED
        funding_amount_points = 0
        if startup.total_funding:
            if startup.total_funding >= 100_000_000:  # $100M+
                funding_amount_points = 8
            elif startup.total_funding >= 50_000_000:  # $50M+
                funding_amount_points = 6
            elif startup.total_funding >= 20_000_000:  # $20M+
                funding_amount_points = 5
            elif startup.total_funding >= 10_000_000:  # $10M+
                funding_amount_points = 3
            elif startup.total_funding >= 5_000_000:   # $5M+
                funding_amount_points = 1
        
        # Geographic bonus (max 15 points) - REDUCED FROM 20
        geo_points = 0
        country = startup.company_country or startup.billingCountry or ''
        
        if country:
            country_code = country.upper().strip()
            eu_countries = ['DE', 'FR', 'GB', 'UK', 'ES', 'IT', 'NL', 'BE', 'SE', 'FI', 'DK', 'NO', 'AT', 'CH', 'LU', 'IE', 'PL', 'CZ', 'PT', 'GR', 'HU', 'RO', 'SK', 'HR']
            
            if country_code in eu_countries:
                geo_points = 15
            elif country_code in ['US', 'CA']:
                geo_points = 8
            elif country_code in ['SG', 'JP', 'AU', 'KR', 'NZ']:
                geo_points = 5
        
        # Calculate total score
        overall_score = min(100, base_score + rule_match_bonus + confidence_points + maturity_points + funding_points + funding_amount_points + geo_points)
        
        # Adjust score if not usable as provider (REDUCED PENALTY - 40%)
        if not can_use_as_provider and overall_score > 0:
            overall_score = overall_score * 0.6
        
        # Determine tier
        if overall_score >= 80:
            tier = "Tier 1: Critical Priority"
        elif overall_score >= 60:
            tier = "Tier 2: High Priority"
        elif overall_score >= 40:
            tier = "Tier 3: Medium Priority"
        else:
            tier = "Tier 4: Low Priority"
        
        return overall_score, tier, avg_confidence
    
    def process_startup_batch(self, startups: List[Startup], evaluation_data: dict) -> List[ScoreUpdate]:
        """Process a batch of startups and calculate new scores"""
        batch_updates = []
        
        for startup in startups:
            try:
                self.stats['total'] += 1
                
                # Get evaluation data for this startup
                startup_eval = evaluation_data.get(str(startup.id))
                if not startup_eval:
                    self.stats['errors'] += 1
                    continue
                
                # Extract data from evaluation
                categories_matched = startup_eval.get('categories_matched', [])
                matched_rules = startup_eval.get('matched_rules', [])
                can_use_as_provider = startup_eval.get('can_use_as_provider', False)
                old_score = startup_eval.get('overall_score', 0)
                
                # Calculate new score
                new_score, tier, avg_confidence = self.calculate_rise_score(
                    startup,
                    categories_matched,
                    matched_rules,
                    can_use_as_provider
                )
                
                # Track changes
                if new_score != old_score:
                    self.stats['updated'] += 1
                    if new_score > old_score:
                        self.stats['score_increases'] += 1
                    else:
                        self.stats['score_decreases'] += 1
                else:
                    self.stats['unchanged'] += 1
                
                # Create update record
                update = ScoreUpdate(
                    startup_id=startup.id,
                    startup_name=startup.company_name,
                    old_score=old_score,
                    new_score=new_score,
                    tier=tier,
                    confidence_avg=avg_confidence,
                    rule_count=len(matched_rules),
                    maturity=startup.maturity,
                    country=startup.company_country,
                    funding_stage=startup.funding_stage,
                    total_funding=startup.total_funding,
                )
                batch_updates.append(update)
                self.updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing startup {startup.id} ({startup.company_name}): {e}")
                self.stats['errors'] += 1
        
        return batch_updates
    
    def update_database(self, db: Session, updates: List[ScoreUpdate]) -> int:
        """Update database with new scores"""
        count = 0
        
        try:
            for update in updates:
                startup = db.query(Startup).filter(Startup.id == update.startup_id).first()
                if startup:
                    startup.axa_overall_score = update.new_score
                    startup.axa_priority_tier = update.tier
                    count += 1
            
            db.commit()
            logger.info(f"✓ Updated {count} startups in database")
            return count
        
        except Exception as e:
            db.rollback()
            logger.error(f"Database update error: {e}")
            raise
    
    def print_batch_summary(self, batch_num: int, updates: List[ScoreUpdate]):
        """Print summary of batch processing"""
        if not updates:
            return
        
        old_scores = [u.old_score for u in updates]
        new_scores = [u.new_score for u in updates]
        
        avg_old = sum(old_scores) / len(old_scores) if old_scores else 0
        avg_new = sum(new_scores) / len(new_scores) if new_scores else 0
        
        logger.info(f"\nBatch {batch_num} Summary:")
        logger.info(f"  Startups: {len(updates)}")
        logger.info(f"  Avg old score: {avg_old:.1f}%")
        logger.info(f"  Avg new score: {avg_new:.1f}%")
        logger.info(f"  Change: {avg_new - avg_old:+.1f}%")
        
        # Show distribution
        tier1_new = len([u for u in updates if u.new_score >= 80])
        tier2_new = len([u for u in updates if 60 <= u.new_score < 80])
        tier3_new = len([u for u in updates if 40 <= u.new_score < 60])
        tier4_new = len([u for u in updates if u.new_score < 40])
        
        logger.info(f"  Tier 1 (80%+): {tier1_new}")
        logger.info(f"  Tier 2 (60-80%): {tier2_new}")
        logger.info(f"  Tier 3 (40-60%): {tier3_new}")
        logger.info(f"  Tier 4 (<40%): {tier4_new}")
    
    def print_final_summary(self):
        """Print final summary of all updates"""
        logger.info("\n" + "="*70)
        logger.info("RISE SCORE UPDATE COMPLETE")
        logger.info("="*70)
        logger.info(f"\nStatistics:")
        logger.info(f"  Total startups processed: {self.stats['total']}")
        logger.info(f"  Scores updated: {self.stats['updated']}")
        logger.info(f"  Scores unchanged: {self.stats['unchanged']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info(f"  Score increases: {self.stats['score_increases']}")
        logger.info(f"  Score decreases: {self.stats['score_decreases']}")
        
        if self.updates:
            old_scores = [u.old_score for u in self.updates]
            new_scores = [u.new_score for u in self.updates]
            
            logger.info(f"\nScore Distribution:")
            logger.info(f"  Old avg: {sum(old_scores)/len(old_scores):.1f}%")
            logger.info(f"  New avg: {sum(new_scores)/len(new_scores):.1f}%")
            logger.info(f"  Old min: {min(old_scores):.1f}%, max: {max(old_scores):.1f}%")
            logger.info(f"  New min: {min(new_scores):.1f}%, max: {max(new_scores):.1f}%")
            
            # New tier distribution
            tier1 = len([u for u in self.updates if u.new_score >= 80])
            tier2 = len([u for u in self.updates if 60 <= u.new_score < 80])
            tier3 = len([u for u in self.updates if 40 <= u.new_score < 60])
            tier4 = len([u for u in self.updates if u.new_score < 40])
            
            logger.info(f"\nNew Tier Distribution:")
            logger.info(f"  Tier 1 (80%+): {tier1} ({tier1/len(self.updates)*100:.1f}%)")
            logger.info(f"  Tier 2 (60-80%): {tier2} ({tier2/len(self.updates)*100:.1f}%)")
            logger.info(f"  Tier 3 (40-60%): {tier3} ({tier3/len(self.updates)*100:.1f}%)")
            logger.info(f"  Tier 4 (<40%): {tier4} ({tier4/len(self.updates)*100:.1f}%)")
        
        logger.info("\n✓ Rise Score update complete!")


def load_evaluation_data(json_file: str) -> dict:
    """Load evaluation data from JSON file"""
    logger.info(f"Loading evaluation data from {json_file}...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create lookup dict by startup_id
    lookup = {str(item['startup_id']): item for item in data}
    logger.info(f"✓ Loaded {len(lookup)} evaluations")
    
    return lookup


def main():
    """Main function to update Rise Scores"""
    
    # Configuration
    BATCH_SIZE = 50
    EVALUATION_FILE = '/home/akyo/startup_swiper/evaluator/downloads/axa_enhanced_results.json'
    
    logger.info("="*70)
    logger.info("RISE SCORE BATCH UPDATE - Rebalanced Algorithm")
    logger.info("="*70)
    logger.info(f"\nStarting at: {datetime.now().isoformat()}")
    logger.info(f"Batch size: {BATCH_SIZE}")
    logger.info(f"Evaluation file: {EVALUATION_FILE}")
    
    # Load evaluation data
    try:
        evaluation_data = load_evaluation_data(EVALUATION_FILE)
    except FileNotFoundError:
        logger.error(f"Evaluation file not found: {EVALUATION_FILE}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in evaluation file: {e}")
        return 1
    
    # Initialize calculator
    calculator = RiseScoreCalculator()
    db = SessionLocal()
    
    try:
        # Get total count
        total_count = db.query(Startup).count()
        logger.info(f"✓ Found {total_count} startups to process\n")
        
        # Process in batches
        batch_num = 0
        for offset in range(0, total_count, BATCH_SIZE):
            batch_num += 1
            
            # Fetch batch
            startups = db.query(Startup).offset(offset).limit(BATCH_SIZE).all()
            
            if not startups:
                break
            
            # Process batch
            updates = calculator.process_startup_batch(startups, evaluation_data)
            
            # Print batch summary
            calculator.print_batch_summary(batch_num, updates)
            
            # Update database
            calculator.update_database(db, updates)
            
            # Log progress
            processed = min(offset + BATCH_SIZE, total_count)
            logger.info(f"Progress: {processed}/{total_count} ({processed/total_count*100:.1f}%)\n")
        
        # Print final summary
        calculator.print_final_summary()
        
        logger.info(f"\nCompleted at: {datetime.now().isoformat()}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
