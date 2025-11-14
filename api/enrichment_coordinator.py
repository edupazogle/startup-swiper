#!/usr/bin/env python3
"""
Enrichment Coordinator - Manage and track full enrichment process
- Resume from checkpoints
- Track progress
- Manage batch operations
- Deploy in stages
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EnrichmentCoordinator:
    """Coordinates the full enrichment process"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.database_file = self.base_path / "docs/architecture/ddbb/slush2_extracted.json"
        self.progress_file = self.base_path / "api/.enrichment_progress.json"
        self.checkpoint_dir = self.base_path / "api/.enrichment_checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def get_status(self) -> Dict:
        """Get current enrichment status"""
        try:
            with open(self.database_file, 'r') as f:
                database = json.load(f)
            
            enriched = [s for s in database if s.get('is_enriched')]
            total = len(database)
            
            status = {
                "total_startups": total,
                "enriched": len(enriched),
                "remaining": total - len(enriched),
                "percentage": (len(enriched) / total * 100) if total > 0 else 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Load progress if exists
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    status.update(progress)
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {}
    
    def print_status(self):
        """Print enrichment status"""
        status = self.get_status()
        
        logger.info("\n" + "="*60)
        logger.info("ENRICHMENT STATUS")
        logger.info("="*60)
        logger.info(f"Total Startups:    {status.get('total_startups', 0)}")
        logger.info(f"Enriched:          {status.get('enriched', 0)}")
        logger.info(f"Remaining:         {status.get('remaining', 0)}")
        logger.info(f"Completion:        {status.get('percentage', 0):.1f}%")
        
        if status.get('success_rate'):
            logger.info(f"Success Rate:      {status.get('success_rate')*100:.1f}%")
        
        if status.get('last_updated'):
            logger.info(f"Last Updated:      {status.get('last_updated')}")
        logger.info("="*60 + "\n")
    
    def run_enrichment_batch(self, batch_size: int = 100, delay: float = 1, 
                            workers: int = 3, resume: bool = True) -> bool:
        """
        Run enrichment in batches
        """
        logger.info("Starting batch enrichment...")
        
        # Check if resume possible
        skip_count = 0
        if resume and self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    skip_count = progress.get('last_index', 0)
                    logger.info(f"Resuming from position {skip_count}")
            except:
                pass
        
        # Run bulk enrichment
        cmd = [
            "python3",
            "api/bulk_enrich_startups.py",
            f"--limit={batch_size}",
            f"--skip={skip_count}",
            f"--delay={delay}",
            f"--workers={workers}",
            "--deploy"
        ]
        
        if resume:
            cmd.append("--resume")
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to run enrichment: {e}")
            return False
    
    def run_full_enrichment(self, delay: float = 1, workers: int = 3) -> bool:
        """
        Run complete enrichment of ALL startups
        Processes in stages to avoid timeouts
        """
        logger.info("Starting FULL enrichment of all startups...")
        
        status = self.get_status()
        remaining = status.get('remaining', 0)
        
        if remaining == 0:
            logger.info("✓ All startups already enriched!")
            return True
        
        logger.info(f"Need to enrich {remaining} startups")
        logger.info(f"Estimated time: ~{remaining * delay / 60:.1f} minutes")
        
        # Run enrichment without limit (all remaining)
        cmd = [
            "python3",
            "api/bulk_enrich_startups.py",
            f"--delay={delay}",
            f"--workers={workers}",
            "--deploy",
            "--resume"
        ]
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to run enrichment: {e}")
            return False
    
    def deploy_enriched_data(self) -> bool:
        """Deploy all enriched data to database"""
        logger.info("Running deployment...")
        
        cmd = ["python3", "api/deploy_enriched_data.py"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def verify_enrichment(self) -> Dict:
        """Verify enrichment quality"""
        try:
            with open(self.database_file, 'r') as f:
                database = json.load(f)
            
            enriched_startups = [s for s in database if s.get('is_enriched')]
            
            # Check quality
            quality_report = {
                "total": len(database),
                "enriched": len(enriched_startups),
                "with_emails": 0,
                "with_social": 0,
                "with_tech_stack": 0,
                "with_team": 0,
                "average_fields": 0
            }
            
            total_fields = 0
            for startup in enriched_startups:
                enrichment = startup.get('enrichment', {})
                
                if enrichment.get('emails'):
                    quality_report['with_emails'] += 1
                if enrichment.get('social_media'):
                    quality_report['with_social'] += 1
                if enrichment.get('tech_stack'):
                    quality_report['with_tech_stack'] += 1
                if enrichment.get('team_members'):
                    quality_report['with_team'] += 1
                
                # Count populated fields
                fields = sum(1 for v in enrichment.values() if v)
                total_fields += fields
            
            if enriched_startups:
                quality_report['average_fields'] = total_fields / len(enriched_startups)
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {}
    
    def print_verification(self):
        """Print verification results"""
        report = self.verify_enrichment()
        
        logger.info("\n" + "="*60)
        logger.info("ENRICHMENT QUALITY REPORT")
        logger.info("="*60)
        logger.info(f"Total Startups:      {report.get('total', 0)}")
        logger.info(f"Enriched:            {report.get('enriched', 0)}")
        logger.info(f"With Emails:         {report.get('with_emails', 0)}")
        logger.info(f"With Social Media:   {report.get('with_social', 0)}")
        logger.info(f"With Tech Stack:     {report.get('with_tech_stack', 0)}")
        logger.info(f"With Team Info:      {report.get('with_team', 0)}")
        logger.info(f"Avg Fields/Startup:  {report.get('average_fields', 0):.1f}")
        logger.info("="*60 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Manage full enrichment process'
    )
    parser.add_argument('--status', action='store_true',
                       help='Show current enrichment status')
    parser.add_argument('--batch', type=int, default=100,
                       help='Batch size for enrichment')
    parser.add_argument('--delay', type=float, default=1,
                       help='Delay between requests')
    parser.add_argument('--workers', type=int, default=3,
                       help='Number of parallel workers')
    parser.add_argument('--enrich', action='store_true',
                       help='Run enrichment process')
    parser.add_argument('--enrich-all', action='store_true',
                       help='Run complete enrichment of all startups')
    parser.add_argument('--deploy', action='store_true',
                       help='Deploy enriched data')
    parser.add_argument('--verify', action='store_true',
                       help='Verify enrichment quality')
    
    args = parser.parse_args()
    
    coordinator = EnrichmentCoordinator()
    
    # Default: show status
    if not any([args.status, args.enrich, args.enrich_all, args.deploy, args.verify]):
        args.status = True
    
    if args.status:
        coordinator.print_status()
    
    if args.enrich:
        logger.info(f"Running enrichment batch (size: {args.batch})...")
        success = coordinator.run_enrichment_batch(
            batch_size=args.batch,
            delay=args.delay,
            workers=args.workers
        )
        if success:
            coordinator.print_status()
    
    if args.enrich_all:
        logger.info("Running COMPLETE enrichment...")
        success = coordinator.run_full_enrichment(
            delay=args.delay,
            workers=args.workers
        )
        if success:
            coordinator.print_status()
            coordinator.print_verification()
    
    if args.deploy:
        success = coordinator.deploy_enriched_data()
        if success:
            coordinator.print_status()
    
    if args.verify:
        coordinator.print_verification()

if __name__ == "__main__":
    main()
