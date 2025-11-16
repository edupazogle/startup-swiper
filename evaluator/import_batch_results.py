#!/usr/bin/env python3
"""
Import AXA Enhanced Batch Evaluation Results into Database

Reads JSONL results from batch evaluator and updates the startup database.

Usage:
    source .venv/bin/activate
    python3 evaluator/import_batch_results.py
    python3 evaluator/import_batch_results.py --results-file downloads/axa_batch_results.jsonl
    python3 evaluator/import_batch_results.py --dry-run
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal
from models_startup import Startup


def score_to_tier(score: float) -> str:
    """Convert numeric score to tier classification"""
    if score >= 75:
        return "Tier 1: Critical Priority"
    elif score >= 60:
        return "Tier 2: High Priority"
    elif score >= 45:
        return "Tier 3: Medium Priority"
    else:
        return "Tier 4: Low Priority"


def import_batch_results(
    results_file: Path,
    dry_run: bool = False
) -> Dict:
    """Import batch evaluation results into database"""
    
    db = SessionLocal()
    stats = {
        'total': 0,
        'imported': 0,
        'not_found': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    logger.info("=" * 90)
    logger.info("IMPORTING AXA BATCH EVALUATION RESULTS")
    logger.info("=" * 90)
    
    if not results_file.exists():
        logger.error(f"Results file not found: {results_file}")
        return stats
    
    logger.info(f"Reading results from: {results_file}")
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be saved\n")
    
    try:
        with open(results_file) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    result = json.loads(line.strip())
                    stats['total'] += 1
                    
                    # Extract result data
                    startup_id = result.get('startup_id')
                    score = result.get('score')
                    rule = result.get('rule')
                    confidence = result.get('confidence', 'medium')
                    scaling = result.get('scaling_potential', 'medium')
                    scaling_margin = result.get('scaling_margin', 0)
                    can_be_provider = result.get('can_be_provider', False)
                    strengths = result.get('strengths', [])
                    concerns = result.get('concerns', [])
                    reasoning = result.get('reasoning', '')
                    
                    # Find startup
                    startup = db.query(Startup).filter(Startup.id == startup_id).first()
                    
                    if not startup:
                        logger.warning(f"Line {line_num}: Startup ID {startup_id} not found")
                        stats['not_found'] += 1
                        continue
                    
                    # Calculate new tier
                    old_score = startup.axa_overall_score or 0
                    old_tier = startup.axa_priority_tier or "Tier 4: Low Priority"
                    new_tier = score_to_tier(score)
                    
                    # Update startup
                    startup.axa_overall_score = score
                    startup.axa_priority_tier = new_tier
                    startup.axa_can_use_as_provider = can_be_provider
                    
                    # Store evaluation details in fit summary
                    fit_summary = {
                        'evaluation_date': datetime.now().isoformat(),
                        'method': 'Batch LLM Evaluation (NVIDIA NIM)',
                        'model': 'qwen/qwen3-next-80b-a3b-instruct',
                        'rule': rule,
                        'confidence': confidence,
                        'scaling_potential': scaling,
                        'scaling_margin': scaling_margin,
                        'strengths': strengths,
                        'concerns': concerns,
                        'reasoning': reasoning
                    }
                    
                    startup.axa_fit_summary = json.dumps(fit_summary)
                    
                    # Log change
                    score_change = score - old_score
                    tier_changed = old_tier != new_tier
                    
                    if score_change != 0 or tier_changed:
                        stats['updated'] += 1
                        logger.info(
                            f"✓ {startup.company_name:30s} | "
                            f"Score: {old_score:6.1f} → {score:6.1f} ({score_change:+.1f}) | "
                            f"{old_tier[:8]:8s} → {new_tier[:8]:8s} | "
                            f"Confidence: {confidence:6s} | Scaling: {scaling:6s}"
                        )
                    else:
                        stats['skipped'] += 1
                    
                    stats['imported'] += 1
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Line {line_num}: Invalid JSON: {e}")
                    stats['errors'] += 1
                except Exception as e:
                    logger.error(f"Line {line_num}: Error processing result: {e}")
                    stats['errors'] += 1
        
        # Commit changes if not dry run
        if not dry_run and stats['imported'] > 0:
            db.commit()
            logger.info(f"\n✓ Database updated with {stats['imported']} startups")
        elif dry_run:
            db.rollback()
            logger.info(f"\n(DRY RUN) Would update {stats['imported']} startups")
        
    except Exception as e:
        logger.error(f"Error reading results file: {e}")
        db.rollback()
    finally:
        db.close()
    
    # Print summary
    logger.info("\n" + "=" * 90)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 90)
    logger.info(f"Total lines read: {stats['total']}")
    logger.info(f"Successfully imported: {stats['imported']}")
    logger.info(f"  - Updated scores: {stats['updated']}")
    logger.info(f"  - Skipped (no change): {stats['skipped']}")
    logger.info(f"Startup not found: {stats['not_found']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info("=" * 90 + "\n")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Import AXA batch evaluation results into database'
    )
    parser.add_argument(
        '--results-file',
        type=Path,
        default=Path('downloads/axa_batch_results.jsonl'),
        help='Path to JSONL results file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without updating database'
    )
    
    args = parser.parse_args()
    
    stats = import_batch_results(args.results_file, dry_run=args.dry_run)
    
    # Exit with error code if there were failures
    if stats['errors'] > 0 or stats['not_found'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
