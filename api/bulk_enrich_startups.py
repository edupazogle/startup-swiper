#!/usr/bin/env python3
"""
Bulk Enrichment Script - Process ALL startups efficiently
Optimized for handling thousands of startups with:
- Parallel processing
- Smart rate limiting
- Progress tracking
- Resume capability
- Batch deployment
"""

import json
import time
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BulkEnricher:
    """Manages bulk enrichment of startups"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.enriched_file = self.base_path / "docs/architecture/ddbb/slush2_enriched.json"
        self.database_file = self.base_path / "docs/architecture/ddbb/slush2_extracted.json"
        self.progress_file = self.base_path / "api/.enrichment_progress.json"
        
    def load_database(self) -> List[Dict]:
        """Load startup database"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return []
    
    def load_enriched(self) -> Dict[str, Dict]:
        """Load previously enriched startups"""
        if self.enriched_file.exists():
            try:
                with open(self.enriched_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Create lookup by name
                    return {s.get('name', ''): s for s in (data if isinstance(data, list) else [data])}
            except Exception as e:
                logger.warning(f"Could not load enriched data: {e}")
        return {}
    
    def load_progress(self) -> Dict:
        """Load enrichment progress"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total": 0,
            "enriched": 0,
            "failed": 0,
            "last_index": 0,
            "started_at": None,
            "last_updated": None
        }
    
    def save_progress(self, progress: Dict):
        """Save enrichment progress"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save progress: {e}")
    
    def enrich_batch(self, startups: List[Dict], start_idx: int, batch_size: int, 
                     delay: float, max_workers: int) -> Dict:
        """
        Enrich a batch of startups in parallel
        """
        enriched_data = []
        failed = []
        
        logger.info(f"Starting enrichment of {len(startups)} startups (batch {start_idx})")
        logger.info(f"Using {max_workers} parallel workers with {delay}s delay")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for idx, startup in enumerate(startups):
                startup_idx = start_idx + idx
                
                # Submit enrichment task
                future = executor.submit(
                    self._enrich_single,
                    startup,
                    startup_idx,
                    len(startups) + start_idx
                )
                futures[future] = (startup, startup_idx)
                
                # Rate limiting: add delay between submissions
                if idx % 5 == 0 and idx > 0:
                    time.sleep(delay)
            
            # Process completed tasks
            completed = 0
            for future in as_completed(futures):
                startup, idx = futures[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result:
                        enriched_data.append(result)
                        logger.info(f"✓ [{idx+1}] {startup.get('name', 'Unknown')} - Enriched")
                    else:
                        failed.append(startup.get('name', 'Unknown'))
                        logger.warning(f"✗ [{idx+1}] {startup.get('name', 'Unknown')} - Failed")
                except Exception as e:
                    failed.append(startup.get('name', 'Unknown'))
                    logger.warning(f"✗ [{idx+1}] Error: {str(e)}")
                
                # Log progress every 10 completions
                if completed % 10 == 0:
                    logger.info(f"Progress: {completed}/{len(startups)} completed")
        
        return {
            "enriched": enriched_data,
            "failed": failed,
            "success_count": len(enriched_data),
            "failure_count": len(failed),
            "success_rate": len(enriched_data) / len(startups) if startups else 0
        }
    
    def _enrich_single(self, startup: Dict, current_idx: int, total: int) -> Optional[Dict]:
        """Enrich a single startup"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from enrich_startups import StartupEnricher
            
            enricher = StartupEnricher(timeout=10, delay=0)
            
            website = startup.get('website', '')
            if not website:
                return None
            
            enrichment = enricher.enrich_startup(startup)
            if enrichment and enrichment.get('enrichment_success'):
                return {
                    **startup,
                    "enrichment": enrichment,
                    "is_enriched": True,
                    "last_enriched_date": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.debug(f"Enrichment error for {startup.get('name', '')}: {e}")
        
        return None
    
    def deploy_all_enrichment(self, enriched_startups: List[Dict]) -> bool:
        """Deploy all enriched startups to database"""
        try:
            logger.info("Starting deployment of enriched data...")
            
            # Load current database
            database = self.load_database()
            if not database:
                logger.error("Could not load database for deployment")
                return False
            
            # Create lookup of enriched startups by name
            enriched_lookup = {s.get('name', ''): s for s in enriched_startups}
            
            # Merge enriched data into database
            updated_count = 0
            for startup in database:
                name = startup.get('name', '')
                if name in enriched_lookup:
                    startup['enrichment'] = enriched_lookup[name].get('enrichment')
                    startup['is_enriched'] = True
                    startup['last_enriched_date'] = enriched_lookup[name].get('last_enriched_date')
                    updated_count += 1
            
            # Backup original
            backup_path = self.database_file.with_suffix('.json.backup')
            if not backup_path.exists():
                logger.info(f"Creating backup: {backup_path.name}")
                with open(self.database_file, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Save updated database
            with open(self.database_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Deployment complete: {updated_count} startups updated")
            
            # Also update app copy
            app_copy = Path(__file__).parent.parent / "app/startup-swipe-schedu/startups/slush2_extracted.json"
            if app_copy.parent.exists():
                with open(app_copy, 'w', encoding='utf-8') as f:
                    json.dump(database, f, indent=2, ensure_ascii=False)
                logger.info(f"✓ App copy updated: {app_copy}")
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Bulk enrich all startups in the database'
    )
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of startups to enrich (default: all)')
    parser.add_argument('--skip', type=int, default=0,
                       help='Number of startups to skip')
    parser.add_argument('--delay', type=float, default=1,
                       help='Delay between requests in seconds')
    parser.add_argument('--workers', type=int, default=3,
                       help='Number of parallel workers')
    parser.add_argument('--deploy', action='store_true',
                       help='Deploy enriched data after enrichment')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last checkpoint')
    
    args = parser.parse_args()
    
    enricher = BulkEnricher()
    
    # Load database
    logger.info("Loading startup database...")
    database = enricher.load_database()
    if not database:
        logger.error("Failed to load database")
        sys.exit(1)
    
    logger.info(f"Database loaded: {len(database)} startups")
    
    # Load already enriched
    enriched_lookup = enricher.load_enriched()
    logger.info(f"Previously enriched: {len(enriched_lookup)} startups")
    
    # Get startups that need enrichment
    remaining = [s for s in database 
                if s.get('name', '') not in enriched_lookup and not s.get('is_enriched')]
    
    if args.resume:
        progress = enricher.load_progress()
        skip_count = progress.get('last_index', 0)
        logger.info(f"Resuming from position {skip_count}")
    else:
        skip_count = args.skip
    
    remaining = remaining[skip_count:]
    
    if args.limit:
        remaining = remaining[:args.limit]
    
    if not remaining:
        logger.info("No startups to enrich!")
        return
    
    logger.info(f"Enriching {len(remaining)} startups...")
    logger.info(f"Estimated time: ~{len(remaining) * args.delay / 60:.1f} minutes")
    
    # Process in batches
    batch_size = 100
    all_enriched = []
    
    for batch_idx in range(0, len(remaining), batch_size):
        batch = remaining[batch_idx:batch_idx + batch_size]
        current_idx = skip_count + batch_idx
        
        logger.info(f"\n=== Batch {batch_idx // batch_size + 1} ===")
        
        result = enricher.enrich_batch(
            batch,
            current_idx,
            len(remaining),
            args.delay,
            args.workers
        )
        
        all_enriched.extend(result['enriched'])
        
        # Save progress
        progress = {
            "total": len(database),
            "enriched": len(all_enriched),
            "failed": len(result['failed']),
            "last_index": current_idx + len(batch),
            "success_rate": result['success_rate'],
            "started_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        enricher.save_progress(progress)
        
        logger.info(f"Batch complete: {result['success_count']}/{len(batch)} successful")
        logger.info(f"Overall: {len(all_enriched)} enriched, success rate: {result['success_rate']*100:.1f}%")
        
        # Brief pause between batches
        if batch_idx + batch_size < len(remaining):
            time.sleep(2)
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("ENRICHMENT COMPLETE")
    logger.info("="*60)
    logger.info(f"Total enriched: {len(all_enriched)}")
    logger.info(f"Success rate: {len(all_enriched)/len(remaining)*100:.1f}%")
    
    # Deploy if requested
    if args.deploy or input("\nDeploy enriched data to database? (y/n): ").lower() == 'y':
        logger.info("Deploying enriched data...")
        if enricher.deploy_all_enrichment(all_enriched):
            logger.info("✓ Deployment successful!")
        else:
            logger.error("✗ Deployment failed!")
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
