#!/usr/bin/env python3
"""
CB Insights Bulk Organization ID Resolver

Recovers CB Insights organization IDs (orgId) for a large list of startup names.
Supports multiple resolution strategies and comprehensive error handling.

Key Features:
- Batch processing with rate limiting
- Multiple resolution methods (organization lookup, profiles, etc.)
- Progress tracking and detailed logging
- CSV output with match quality indicators
- Duplicate handling and name normalization
"""

import asyncio
import aiohttp
import json
import csv
import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/akyo/startup_swiper/logs/cbinsights_bulk_resolver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CB Insights API credentials
CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"
CB_INSIGHTS_BASE_URL = "https://api.cbinsights.com"


class CBInsightsBulkResolver:
    """Resolve multiple startup names to CB Insights organization IDs"""
    
    def __init__(self, client_id: str, client_secret: str, batch_size: int = 100):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = CB_INSIGHTS_BASE_URL
        self.bearer_token: Optional[str] = None
        self.batch_size = batch_size
        self.results: List[Dict] = []
        self.failed: List[Dict] = []
        
    async def authorize(self) -> bool:
        """Get authorization bearer token"""
        auth_url = f"{self.base_url}/v2/authorize"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.bearer_token = data.get("token")
                        logger.info(f"✅ Authorization successful")
                        return True
                    else:
                        logger.error(f"❌ Authorization failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Authorization error: {str(e)}")
            return False
    
    async def resolve_names_lookup(self, names: List[str]) -> Dict[str, List[Dict]]:
        """
        Resolve names using /v2/organizations lookup endpoint
        
        This endpoint accepts a list of names and returns organizations.
        Best for exact name matches.
        """
        if not self.bearer_token:
            logger.error("Not authorized")
            return {}
        
        lookup_url = f"{self.base_url}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        results_by_name = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "names": names,
                    "limit": 100
                }
                
                async with session.post(lookup_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        organizations = data.get("orgs", [])
                        logger.info(f"✅ Lookup found {len(organizations)} results for {len(names)} names")
                        
                        # Map results by requested name
                        for org in organizations:
                            org_name = org.get("name", "").lower()
                            for requested_name in names:
                                if requested_name.lower() == org_name:
                                    if requested_name not in results_by_name:
                                        results_by_name[requested_name] = []
                                    results_by_name[requested_name].append(org)
                        
                        return results_by_name
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Lookup failed: {response.status} - {error_text}")
                        return {}
        except Exception as e:
            logger.error(f"❌ Lookup error: {str(e)}")
            return {}
    
    async def resolve_names_profiles(self, names: List[str]) -> Dict[str, List[Dict]]:
        """
        Resolve names using /v2/organizations (profiles) endpoint with orgNames filter
        
        This is a more comprehensive endpoint that accepts orgNames array.
        Supports partial matching and advanced filtering.
        """
        if not self.bearer_token:
            logger.error("Not authorized")
            return {}
        
        profiles_url = f"{self.base_url}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        results_by_name = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Request body for profiles endpoint (firmographics)
                payload = {
                    "orgNames": names,  # Array of exact names
                    "limit": 100
                }
                
                async with session.post(profiles_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        organizations = data.get("orgs", [])
                        logger.info(f"✅ Profiles search found {len(organizations)} results")
                        
                        # Map results by name
                        for org in organizations:
                            org_name = org.get("name", "").lower()
                            for requested_name in names:
                                if requested_name.lower() == org_name:
                                    if requested_name not in results_by_name:
                                        results_by_name[requested_name] = []
                                    results_by_name[requested_name].append(org)
                        
                        return results_by_name
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Profiles search failed: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"❌ Profiles search error: {str(e)}")
            return {}
    
    async def resolve_names_keyword(self, names: List[str]) -> Dict[str, List[Dict]]:
        """
        Resolve names using keyword search on profiles endpoint
        
        Falls back to keyword matching when exact match fails.
        Useful for partial matches and variations.
        """
        if not self.bearer_token:
            logger.error("Not authorized")
            return {}
        
        profiles_url = f"{self.base_url}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        results_by_name = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for name in names:
                    payload = {
                        "keyword": name,  # Keyword search
                        "limit": 10
                    }
                    
                    async with session.post(profiles_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            organizations = data.get("orgs", [])
                            
                            if organizations:
                                results_by_name[name] = organizations
                                logger.info(f"✅ Keyword search found {len(organizations)} results for '{name}'")
                        
                        # Rate limiting - don't hammer the API
                        await asyncio.sleep(0.1)
                
                return results_by_name
        except Exception as e:
            logger.error(f"❌ Keyword search error: {str(e)}")
            return {}
    
    async def resolve_bulk(self, startup_names: List[str], use_methods: List[str] = None) -> List[Dict]:
        """
        Resolve a large list of startup names to CB Insights IDs
        
        Args:
            startup_names: List of startup company names
            use_methods: List of resolution methods to try in order
                        ['lookup', 'profiles', 'keyword']
        
        Returns:
            List of results with fields:
            - input_name: Original name provided
            - cb_insights_id: CB Insights organization ID
            - cb_insights_name: Name from CB Insights
            - description: Company description
            - confidence: Match confidence (exact/partial/keyword)
            - method: Which method found the match
            - all_results: All candidates found (for manual review)
        """
        if use_methods is None:
            use_methods = ['lookup', 'profiles', 'keyword']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 BULK ORGANIZATION ID RESOLVER")
        logger.info(f"{'='*80}")
        logger.info(f"Companies to resolve: {len(startup_names)}")
        logger.info(f"Methods: {', '.join(use_methods)}")
        
        # Normalize input
        startup_names = list(set([name.strip() for name in startup_names if name.strip()]))
        logger.info(f"After deduplication: {len(startup_names)} unique names")
        
        resolved = {}
        remaining = set(startup_names)
        
        # Try each resolution method in order
        for method in use_methods:
            if not remaining:
                break
            
            logger.info(f"\n▶️  Using {method.upper()} method ({len(remaining)} remaining)...")
            
            names_to_search = list(remaining)
            
            # Split into batches
            for i in range(0, len(names_to_search), self.batch_size):
                batch = names_to_search[i:i + self.batch_size]
                logger.info(f"   Processing batch {i//self.batch_size + 1} ({len(batch)} names)...")
                
                if method == 'lookup':
                    results = await self.resolve_names_lookup(batch)
                elif method == 'profiles':
                    results = await self.resolve_names_profiles(batch)
                elif method == 'keyword':
                    results = await self.resolve_names_keyword(batch)
                else:
                    continue
                
                # Process results
                for name, orgs in results.items():
                    if name in remaining and orgs:
                        # Take the first (best) match
                        org = orgs[0]
                        resolved[name] = {
                            'input_name': name,
                            'cb_insights_id': org.get('orgId'),
                            'cb_insights_name': org.get('name'),
                            'description': org.get('description', '')[:100],
                            'confidence': 'exact',
                            'method': method,
                            'all_results': len(orgs)
                        }
                        remaining.remove(name)
                
                # Rate limiting
                await asyncio.sleep(0.5)
        
        # Log results
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ RESOLUTION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Resolved: {len(resolved)}")
        logger.info(f"Unresolved: {len(remaining)}")
        logger.info(f"Success rate: {len(resolved)/len(startup_names)*100:.1f}%")
        
        if remaining:
            logger.info(f"\n⚠️  Unresolved names ({len(remaining)}):")
            for name in sorted(remaining):
                logger.info(f"   - {name}")
        
        return list(resolved.values())
    
    def save_results_csv(self, results: List[Dict], output_file: str) -> str:
        """Save resolution results to CSV"""
        if not results:
            logger.warning("No results to save")
            return ""
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'input_name',
                'cb_insights_id',
                'cb_insights_name',
                'description',
                'confidence',
                'method',
                'all_results'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"✅ Results saved to: {output_file}")
        return output_file
    
    def save_results_json(self, results: List[Dict], output_file: str) -> str:
        """Save resolution results to JSON"""
        if not results:
            logger.warning("No results to save")
            return ""
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_resolved': len(results),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Results saved to: {output_file}")
        return output_file


async def main():
    """Example usage"""
    
    # Example: Large list of startup names
    STARTUP_NAMES = [
        "Simplifai",
        "Stripe",
        "OpenAI",
        "Figma",
        "Notion",
        "Canva",
        "Airbnb",
        "Uber",
        "Slack",
        "Discord",
        "Retool",
        "Webflow",
        "Airtable",
        "Zapier",
        "Unknown Company That Doesn't Exist XYZ",  # Test unresolved
    ]
    
    # You can also load from CSV:
    # df = pd.read_csv('startup_list.csv')
    # STARTUP_NAMES = df['company_name'].tolist()
    
    # Initialize resolver
    resolver = CBInsightsBulkResolver(
        CBINSIGHTS_CLIENT_ID,
        CBINSIGHTS_CLIENT_SECRET,
        batch_size=50
    )
    
    # Authorize
    if not await resolver.authorize():
        logger.error("Failed to authorize")
        sys.exit(1)
    
    # Resolve all names using all methods
    results = await resolver.resolve_bulk(
        STARTUP_NAMES,
        use_methods=['lookup', 'profiles', 'keyword']
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    csv_file = f"/home/akyo/startup_swiper/downloads/cbinsights_bulk_resolution_{timestamp}.csv"
    json_file = f"/home/akyo/startup_swiper/downloads/cbinsights_bulk_resolution_{timestamp}.json"
    
    resolver.save_results_csv(results, csv_file)
    resolver.save_results_json(results, json_file)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 RESOLUTION SUMMARY")
    print("="*80)
    print(f"Total Input Names: {len(STARTUP_NAMES)}")
    print(f"Successfully Resolved: {len(results)}")
    print(f"Unresolved: {len(STARTUP_NAMES) - len(results)}")
    print(f"Success Rate: {len(results)/len(STARTUP_NAMES)*100:.1f}%")
    print(f"\nOutput Files:")
    print(f"  CSV: {csv_file}")
    print(f"  JSON: {json_file}")
    print("="*80)
    
    # Print top 10 results
    print("\n📋 Sample Results (first 10):")
    for i, result in enumerate(results[:10], 1):
        print(f"{i}. {result['input_name']:30} → ID: {result['cb_insights_id']:10} ({result['confidence']})")


if __name__ == "__main__":
    asyncio.run(main())
