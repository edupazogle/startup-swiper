"""
Bulk Enrichment Script - CB Insights API Strategy 2 (Recommended)
Efficiently enriches startup database using batched API calls
"""

import os
import csv
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try multiple .env locations
    env_paths = [
        Path(__file__).parent.parent / '.env',  # Root .env
        Path(__file__).parent.parent / 'app' / 'startup-swipe-schedu' / '.env',  # App .env
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("⚠️  python-dotenv not installed. Using environment variables only.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BulkEnricher:
    """Bulk enrichment of startups using CB Insights API"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize enricher with API credentials"""
        # Try to import here to avoid hard dependency
        try:
            from cb_insights_enricher import CBInsightsEnricher
            self.enricher = CBInsightsEnricher(client_id, client_secret)
        except ImportError:
            logger.error("❌ CBInsightsEnricher module not found")
            raise
    
    def authorize(self) -> bool:
        """Authorize with CB Insights API"""
        return self.enricher.authorize()
    
    def load_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Load startup data from CSV"""
        startups = []
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    startups.append({
                        'startup_id': row.get('startup_id'),
                        'name': row.get('name'),
                        'cb_insights_id': int(row.get('cb_insights_id', 0)) if row.get('cb_insights_id') else None,
                    })
            
            logger.info(f"✅ Loaded {len(startups)} startups from {csv_path}")
            return startups
            
        except Exception as e:
            logger.error(f"❌ Failed to load CSV: {e}")
            return []
    
    def enrich_batch_firmographics(
        self,
        org_ids: List[int],
        db_connection: Optional[Any] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Fetch firmographics for a batch of org IDs
        
        Args:
            org_ids: List of CB Insights org IDs
            db_connection: Optional database connection for direct save
            
        Returns:
            Dictionary mapping org_id to funding data
        """
        results = {}
        
        try:
            # Fetch firmographics
            response = self.enricher.get_firmographics_by_org_ids(org_ids)
            
            if not response or not response.get('orgs'):
                logger.warning(f"⚠️  No data returned for batch of {len(org_ids)} orgs")
                return results
            
            # Extract data for each org
            for org in response['orgs']:
                try:
                    org_id = org.get('orgId')
                    
                    # Extract funding data
                    funding_data = self.enricher.extract_funding_data(org)
                    company_data = self.enricher.extract_company_data(org)
                    
                    # Combine all extracted data
                    combined_data = {
                        **company_data,
                        **funding_data,
                        'org_id': org_id,
                        'enriched_at': datetime.now().isoformat(),
                    }
                    
                    results[org_id] = combined_data
                except Exception as org_error:
                    logger.error(f"❌ Failed to extract data for org {org_id}: {org_error}", exc_info=True)
            
            logger.info(f"✅ Extracted data for {len(results)}/{len(org_ids)} orgs in batch")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to enrich batch: {e}", exc_info=True)
            return results
    
    def enrich_batch_fundings(
        self,
        org_ids: List[int]
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Fetch funding rounds for a batch of org IDs
        
        Args:
            org_ids: List of CB Insights org IDs
            
        Returns:
            Dictionary mapping org_id to list of funding rounds
        """
        results = {}
        
        try:
            # Fetch funding rounds
            response = self.enricher.get_funding_rounds(org_ids)
            
            if not response or not response.get('orgs'):
                logger.warning(f"⚠️  No funding data returned for batch of {len(org_ids)} orgs")
                return results
            
            # Extract funding rounds for each org
            for org_fundings in response['orgs']:
                org_id = org_fundings.get('orgId')
                
                # Extract funding rounds
                rounds = self.enricher.extract_funding_rounds(org_fundings)
                results[org_id] = rounds
            
            total_rounds = sum(len(rounds) for rounds in results.values())
            logger.info(f"✅ Extracted {total_rounds} funding rounds for {len(results)}/{len(org_ids)} orgs")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to enrich fundings: {e}")
            return results
    
    def bulk_enrich(
        self,
        csv_path: str,
        batch_size: int = 15,
        strategy: str = "firmographics",
        skip_count: int = 0,
        max_batches: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Bulk enrich startups from CSV
        
        Args:
            csv_path: Path to CSV file
            batch_size: Number of orgs per API call
            strategy: "firmographics" (default) or "dual" (firmographics + fundings)
            skip_count: Number of startups to skip (for resuming)
            max_batches: Maximum number of batches to process
            
        Returns:
            Summary statistics
        """
        logger.info("="*70)
        logger.info("BULK ENRICHMENT - CB Insights API v2")
        logger.info("="*70)
        logger.info(f"Strategy: {strategy}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Skip count: {skip_count}")
        if max_batches:
            logger.info(f"Max batches: {max_batches}")
        
        # Load CSV
        startups = self.load_csv(csv_path)
        if not startups:
            return {"status": "failed", "error": "Could not load CSV"}
        
        # Extract org IDs
        org_ids = [s['cb_insights_id'] for s in startups if s['cb_insights_id']]
        org_ids = org_ids[skip_count:]  # Skip if resuming
        
        logger.info(f"Total orgs to enrich: {len(org_ids)}")
        
        # Create batches
        batches = [org_ids[i:i + batch_size] for i in range(0, len(org_ids), batch_size)]
        logger.info(f"Split into {len(batches)} batches of ~{batch_size} orgs")
        
        # Track results
        all_firmographics = {}
        all_fundings = {}
        start_time = time.time()
        failed_batches = []
        
        # Process batches
        for batch_num, batch in enumerate(batches, 1):
            if max_batches and batch_num > max_batches:
                logger.info(f"⛔ Reached max batch limit ({max_batches})")
                break
            
            logger.info(f"\n[Batch {batch_num}/{len(batches)}] Processing {len(batch)} orgs...")
            
            try:
                # Phase 1: Firmographics
                logger.info(f"  Phase 1: Fetching firmographics...")
                firm_results = self.enrich_batch_firmographics(batch)
                all_firmographics.update(firm_results)
                
                # Phase 2: Funding rounds (if dual strategy)
                if strategy == "dual":
                    logger.info(f"  Phase 2: Fetching funding rounds...")
                    time.sleep(0.05)  # Brief pause between endpoints
                    funding_results = self.enrich_batch_fundings(batch)
                    all_fundings.update(funding_results)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"  ❌ Batch {batch_num} failed: {e}")
                failed_batches.append(batch_num)
                continue
        
        elapsed = time.time() - start_time
        
        # Summary
        summary = {
            "status": "completed",
            "strategy": strategy,
            "total_orgs": len(org_ids),
            "batch_size": batch_size,
            "total_batches": len(batches),
            "batches_processed": batch_num,
            "failed_batches": failed_batches,
            "firmographics_count": len(all_firmographics),
            "funding_rounds_count": sum(len(rounds) for rounds in all_fundings.values()),
            "elapsed_seconds": elapsed,
            "orgs_per_second": len(org_ids) / elapsed if elapsed > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("ENRICHMENT SUMMARY")
        logger.info("="*70)
        for key, value in summary.items():
            if key not in ['status']:
                logger.info(f"{key}: {value}")
        
        # Save results
        return {
            **summary,
            "firmographics": all_firmographics,
            "fundings": all_fundings,
        }
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save enrichment results to JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"✅ Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Bulk enrich startups using CB Insights API v2"
    )
    
    parser.add_argument(
        '--csv',
        required=True,
        help='Path to CSV file with startup data'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=15,
        help='Number of orgs per API call (default: 15)'
    )
    
    parser.add_argument(
        '--strategy',
        choices=['firmographics', 'dual'],
        default='firmographics',
        help='Enrichment strategy (default: firmographics)'
    )
    
    parser.add_argument(
        '--skip',
        type=int,
        default=0,
        help='Number of startups to skip (for resuming)'
    )
    
    parser.add_argument(
        '--max-batches',
        type=int,
        help='Maximum number of batches to process (for testing)'
    )
    
    parser.add_argument(
        '--output',
        default='api/cb_insights_enrichment_results.json',
        help='Output file for results'
    )
    
    args = parser.parse_args()
    
    # Check credentials from environment or .env file (check both naming conventions)
    client_id = os.getenv('CBI_CLIENT_ID') or os.getenv('CBINSIGHTS_CLIENT_ID')
    client_secret = os.getenv('CBI_CLIENT_SECRET') or os.getenv('CBINSIGHTS_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        logger.error("❌ CB Insights credentials not found")
        logger.error("\nTo set credentials, either:")
        logger.error("\n1. Use the app .env file:")
        logger.error("   app/startup-swipe-schedu/.env (CBINSIGHTS_CLIENT_ID/SECRET)")
        logger.error("\n2. Create a root .env file:")
        logger.error("   cp .env.example .env")
        logger.error("   # Edit .env with your credentials (CBI_CLIENT_ID/SECRET)")
        logger.error("\n3. Or set environment variables:")
        logger.error("   export CBI_CLIENT_ID='your_client_id'")
        logger.error("   export CBI_CLIENT_SECRET='your_client_secret'")
        logger.error("\n4. Or pass as arguments:")
        logger.error("   python bulk_enrich_from_csv.py --client-id ... --client-secret ...")
        sys.exit(1)
    
    env_source = "app/.env" if os.getenv('CBINSIGHTS_CLIENT_ID') else ".env or environment"
    logger.info(f"✅ Using credentials from: {env_source}")
    
    try:
        # Initialize enricher
        enricher = BulkEnricher(client_id, client_secret)
        
        # Authorize
        if not enricher.authorize():
            logger.error("❌ Failed to authorize with CB Insights API")
            sys.exit(1)
        
        # Run enrichment
        results = enricher.bulk_enrich(
            csv_path=args.csv,
            batch_size=args.batch_size,
            strategy=args.strategy,
            skip_count=args.skip,
            max_batches=args.max_batches
        )
        
        # Save results
        enricher.save_results(results, args.output)
        
        # Exit status
        if results['status'] == 'completed':
            logger.info("\n✅ Enrichment completed successfully")
            sys.exit(0)
        else:
            logger.error("\n❌ Enrichment failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
