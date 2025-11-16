"""
Resolve CB Insights Org IDs for Slush companies
Uses company name and website to find matching organizations in CB Insights
"""

import os
import csv
import json
import time
import logging
from typing import List, Dict, Optional, Any
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


class OrgIDResolver:
    """Resolves CB Insights org IDs for companies"""
    
    def __init__(self):
        self.client_id = os.getenv('CBI_CLIENT_ID') or os.getenv('CBINSIGHTS_CLIENT_ID')
        self.client_secret = os.getenv('CBI_CLIENT_SECRET') or os.getenv('CBINSIGHTS_CLIENT_SECRET')
        self.base_url = "https://api.cbinsights.com"
        self.token = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("CB Insights credentials not found")
    
    def authorize(self) -> bool:
        """Get authorization token"""
        try:
            url = f"{self.base_url}/v2/authorize"
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }
            response = requests.post(url, json=payload)
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
    
    def search_by_name(self, company_name: str, website: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for company by name and optionally website
        
        Args:
            company_name: Company name to search
            website: Optional website URL
            
        Returns:
            Organization data or None
        """
        try:
            url = f"{self.base_url}/v2/firmographics"
            payload = {
                "namePartial": [company_name],
                "limit": 10
            }
            
            # Add website filter if provided
            if website:
                # Extract domain from website
                domain = website.replace('https://', '').replace('http://', '').split('/')[0]
                payload["domain"] = [domain]
            
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('orgs') and len(data['orgs']) > 0:
                return data['orgs'][0]  # Return best match
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to search for '{company_name}': {e}")
            return None


def resolve_org_ids(input_csv: str, output_csv: str, max_searches: Optional[int] = None) -> Dict[str, Any]:
    """
    Resolve org IDs for companies in CSV
    
    Args:
        input_csv: Path to input CSV
        output_csv: Path to output CSV with org IDs
        max_searches: Maximum number of searches (for testing)
        
    Returns:
        Summary dictionary
    """
    resolver = OrgIDResolver()
    
    if not resolver.authorize():
        logger.error("❌ Failed to authorize")
        return {}
    
    # Load input CSV
    companies = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)
    
    logger.info(f"✅ Loaded {len(companies)} companies from {input_csv}")
    
    # Resolve org IDs
    resolved = 0
    not_found = 0
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(companies[0].keys()) + ['cb_insights_id', 'cb_insights_name', 'resolved_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, company in enumerate(companies):
            if max_searches and i >= max_searches:
                logger.info(f"⛔ Reached max search limit ({max_searches})")
                break
            
            company_name = company.get('company_name', '').strip()
            website = company.get('website', '').strip()
            
            if not company_name:
                logger.warning(f"Skipping row {i+2}: Missing company name")
                writer.writerow({**company, 'cb_insights_id': None, 'resolved_at': None})
                continue
            
            # Search for org
            org = resolver.search_by_name(company_name, website)
            
            if org:
                org_id = org.get('orgId')
                org_name = org.get('summary', {}).get('name')
                writer.writerow({
                    **company,
                    'cb_insights_id': org_id,
                    'cb_insights_name': org_name,
                    'resolved_at': datetime.now().isoformat()
                })
                resolved += 1
                logger.info(f"✅ [{i+1}/{len(companies)}] {company_name} → {org_name} (ID: {org_id})")
            else:
                writer.writerow({
                    **company,
                    'cb_insights_id': None,
                    'resolved_at': datetime.now().isoformat()
                })
                not_found += 1
                logger.info(f"❌ [{i+1}/{len(companies)}] {company_name} → NOT FOUND")
            
            # Rate limiting
            time.sleep(0.1)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Resolution Summary")
    logger.info(f"{'='*70}")
    logger.info(f"Total companies: {len(companies)}")
    logger.info(f"Resolved: {resolved}")
    logger.info(f"Not found: {not_found}")
    logger.info(f"Resolution rate: {100*resolved/len(companies):.1f}%")
    logger.info(f"Output saved to: {output_csv}")
    
    return {
        'total_companies': len(companies),
        'resolved': resolved,
        'not_found': not_found,
        'resolution_rate': 100 * resolved / len(companies),
        'output_file': output_csv
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Resolve CB Insights org IDs for Slush companies')
    parser.add_argument('--input', default='docs/slush_complete.csv', help='Input CSV file')
    parser.add_argument('--output', default='downloads/slush_resolved.csv', help='Output CSV file')
    parser.add_argument('--max-searches', type=int, help='Maximum searches (for testing)')
    
    args = parser.parse_args()
    
    summary = resolve_org_ids(args.input, args.output, args.max_searches)
    print(json.dumps(summary, indent=2))
