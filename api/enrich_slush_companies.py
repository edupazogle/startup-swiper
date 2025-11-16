"""
Enrich Slush companies using CB Insights API
Uses CB Insights IDs that are already in the database
"""

import os
import sqlite3
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
env_paths = [
    Path(__file__).parent.parent / '.env',
    Path(__file__).parent.parent / 'app' / 'startup-swipe-schedu' / '.env',
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlushEnricher:
    """Enrich Slush companies from CB Insights API"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize enricher"""
        self.client_id = client_id or os.getenv('CBI_CLIENT_ID') or os.getenv('CBINSIGHTS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CBI_CLIENT_SECRET') or os.getenv('CBINSIGHTS_CLIENT_SECRET')
        self.base_url = "https://api.cbinsights.com"
        self.token = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("CB Insights credentials not found")
    
    def authorize(self) -> bool:
        """Authorize with CB Insights API"""
        try:
            url = f"{self.base_url}/v2/authorize"
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            
            if self.token:
                logger.info("✅ Successfully authorized with CB Insights API")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        if not self.token:
            raise ValueError("Not authorized")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_firmographics_by_org_ids(self, org_ids: List[int]) -> Optional[Dict[str, Any]]:
        """Get firmographics for org IDs"""
        try:
            url = f"{self.base_url}/v2/firmographics"
            payload = {"orgIds": org_ids}
            headers = self._get_headers()
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('orgs'):
                logger.info(f"✅ Retrieved firmographics for {len(data['orgs'])} organizations")
                return data
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get firmographics: {e}")
            return None
    
    def extract_funding_data(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """Extract funding data from org"""
        financials = org.get('financials', {})
        
        return {
            'cb_insights_id': org.get('orgId'),
            'company_name': org.get('summary', {}).get('name'),
            'total_funding': financials.get('totalFunding'),
            'total_equity_funding': financials.get('totalEquityFunding'),
            'last_funding_date': financials.get('lastFundingDate'),
            'valuation': financials.get('valuation'),
            'latest_revenue_min': financials.get('revenueMin'),
            'latest_revenue_max': financials.get('revenueMax'),
            'revenue_date': financials.get('revenueDate'),
            'funding_source': 'CB Insights API v2',
            'enriched_at': datetime.now().isoformat(),
        }


def enrich_slush_companies(batch_size: int = 20, max_batches: Optional[int] = None) -> Dict[str, Any]:
    """
    Enrich Slush companies from database using CB Insights IDs
    
    Args:
        batch_size: Number of orgs per batch
        max_batches: Maximum number of batches to process
        
    Returns:
        Summary dictionary
    """
    enricher = SlushEnricher()
    
    if not enricher.authorize():
        logger.error("❌ Failed to authorize with CB Insights")
        return {}
    
    # Load org IDs from database
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, company_name, cb_insights_id 
        FROM startups 
        WHERE cb_insights_id IS NOT NULL AND company_name IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    
    logger.info(f"✅ Loaded {len(rows)} companies with CB Insights IDs")
    
    # Split into batches
    batches = []
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        batches.append(batch)
    
    logger.info(f"Split into {len(batches)} batches of {batch_size}")
    
    # Process batches
    enriched_count = 0
    failed_orgs = []
    results = {
        'total_companies': len(rows),
        'enriched': 0,
        'failed': 0,
        'data': {}
    }
    
    for batch_num, batch in enumerate(batches, 1):
        if max_batches and batch_num > max_batches:
            logger.info(f"⛔ Reached max batch limit ({max_batches})")
            break
        
        logger.info(f"\n[Batch {batch_num}/{len(batches)}] Processing {len(batch)} companies...")
        
        org_ids = [row[2] for row in batch]  # Extract CB Insights IDs
        
        try:
            response = enricher.get_firmographics_by_org_ids(org_ids)
            
            if response and response.get('orgs'):
                for org in response['orgs']:
                    try:
                        funding_data = enricher.extract_funding_data(org)
                        
                        # Find matching row
                        cb_id = org.get('orgId')
                        matching_rows = [r for r in batch if r[2] == cb_id]
                        
                        if matching_rows:
                            db_id = matching_rows[0][0]
                            results['data'][db_id] = funding_data
                            enriched_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to extract data for org {org.get('orgId')}: {e}")
                        failed_orgs.append(org.get('orgId'))
            
            logger.info(f"✅ Processed {len(batch)} companies (enriched: {enriched_count})")
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"❌ Batch {batch_num} failed: {e}")
    
    results['enriched'] = enriched_count
    results['failed'] = len(failed_orgs)
    results['timestamp'] = datetime.now().isoformat()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"ENRICHMENT SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Total companies with CB Insights IDs: {len(rows)}")
    logger.info(f"Successfully enriched: {enriched_count}")
    logger.info(f"Failed: {len(failed_orgs)}")
    logger.info(f"Coverage: {100*enriched_count/len(rows):.1f}%")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich Slush companies with CB Insights data')
    parser.add_argument('--batch-size', type=int, default=20, help='Batch size')
    parser.add_argument('--max-batches', type=int, help='Maximum batches to process')
    
    args = parser.parse_args()
    
    results = enrich_slush_companies(args.batch_size, args.max_batches)
    
    # Save results
    output_file = 'api/slush_enrichment_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✅ Results saved to {output_file}")
    print(json.dumps({
        'total_companies': results['total_companies'],
        'enriched': results['enriched'],
        'failed': results['failed'],
        'coverage_percent': 100 * results['enriched'] / results['total_companies']
    }, indent=2))
