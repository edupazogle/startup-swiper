#!/usr/bin/env python3
"""
Bulk CB Insights ID Resolution for All Startups

This script:
1. Retrieves all startups from the database without CB Insights IDs
2. Resolves IDs using CB Insights API
3. Updates the database with resolved IDs
4. Tracks progress and saves results
"""

import asyncio
import aiohttp
import sys
import os
from datetime import datetime
from pathlib import Path
import csv

sys.path.insert(0, '/home/akyo/startup_swiper/api')
from database import engine
from sqlalchemy import text
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/akyo/startup_swiper/logs/startup_id_resolution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CB Insights API credentials
CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"
CB_INSIGHTS_BASE_URL = "https://api.cbinsights.com"


class StartupIDResolver:
    """Resolve CB Insights IDs for database startups"""
    
    def __init__(self):
        self.bearer_token = None
        self.resolved = []
        self.failed = []
        self.total = 0
        
    async def authorize(self) -> bool:
        """Get authorization bearer token"""
        auth_url = f"{CB_INSIGHTS_BASE_URL}/v2/authorize"
        payload = {
            "clientId": CBINSIGHTS_CLIENT_ID,
            "clientSecret": CBINSIGHTS_CLIENT_SECRET
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.bearer_token = data.get("token")
                        logger.info("✅ Authorization successful")
                        return True
                    else:
                        logger.error(f"❌ Authorization failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Authorization error: {str(e)}")
            return False
    
    def get_unresolved_startups(self) -> list:
        """Get all startups without CB Insights IDs"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, company_name FROM startups 
                    WHERE cb_insights_id IS NULL
                    ORDER BY company_name
                """))
                startups = result.fetchall()
                logger.info(f"Found {len(startups)} startups without CB Insights IDs")
                return startups
        except Exception as e:
            logger.error(f"Error fetching startups: {str(e)}")
            return []
    
    async def resolve_batch(self, names: list) -> dict:
        """Resolve a batch of startup names"""
        if not self.bearer_token:
            logger.error("Not authorized")
            return {}
        
        lookup_url = f"{CB_INSIGHTS_BASE_URL}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"names": names, "limit": 100}
                
                async with session.post(lookup_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        organizations = data.get("orgs", [])
                        
                        # Map results by name
                        results = {}
                        for org in organizations:
                            org_name = org.get("name", "").lower()
                            for requested_name in names:
                                if requested_name.lower() == org_name:
                                    results[requested_name] = org.get("orgId")
                        
                        return results
                    else:
                        logger.warning(f"⚠️ Batch lookup failed: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Batch lookup error: {str(e)}")
            return {}
    
    async def resolve_keyword_fallback(self, name: str) -> int:
        """Fallback keyword search for a single name"""
        if not self.bearer_token:
            return None
        
        profiles_url = f"{CB_INSIGHTS_BASE_URL}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"keyword": name, "limit": 5}
                
                async with session.post(profiles_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        organizations = data.get("orgs", [])
                        
                        # Return first result if found
                        if organizations:
                            return organizations[0].get("orgId")
                    
                    return None
        except Exception as e:
            logger.debug(f"Keyword search error for '{name}': {str(e)}")
            return None
    
    def update_database(self, startup_id: int, cb_insights_id: int):
        """Update startup with CB Insights ID"""
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE startups 
                    SET cb_insights_id = :cb_id
                    WHERE id = :startup_id
                """), {"cb_id": cb_insights_id, "startup_id": startup_id})
                conn.commit()
        except Exception as e:
            logger.error(f"Database update error for startup {startup_id}: {str(e)}")
    
    async def resolve_all(self):
        """Resolve all startups"""
        logger.info("\n" + "="*80)
        logger.info("🔍 STARTUP CB INSIGHTS ID RESOLUTION")
        logger.info("="*80)
        
        # Authorize
        if not await self.authorize():
            logger.error("Failed to authorize")
            return
        
        # Get unresolved startups
        startups = self.get_unresolved_startups()
        self.total = len(startups)
        
        logger.info(f"Total to resolve: {self.total}")
        
        # Process in batches
        batch_size = 50
        resolved_count = 0
        failed_count = 0
        
        for i in range(0, len(startups), batch_size):
            batch = startups[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(startups) + batch_size - 1) // batch_size
            
            logger.info(f"\n▶️  Batch {batch_num}/{total_batches} ({len(batch)} startups)")
            
            # Extract names
            names = [name for _, name in batch]
            ids_map = {name: sid for sid, name in batch}
            
            # Try lookup
            results = await self.resolve_batch(names)
            
            # Process results
            for name, cb_id in results.items():
                if cb_id:
                    startup_id = ids_map[name]
                    self.update_database(startup_id, cb_id)
                    self.resolved.append({
                        'startup_id': startup_id,
                        'name': name,
                        'cb_insights_id': cb_id,
                        'method': 'lookup'
                    })
                    resolved_count += 1
            
            # Fallback for unresolved
            unresolved = [name for name in names if name not in results]
            for name in unresolved:
                logger.debug(f"Trying keyword search for: {name}")
                cb_id = await self.resolve_keyword_fallback(name)
                
                if cb_id:
                    startup_id = ids_map[name]
                    self.update_database(startup_id, cb_id)
                    self.resolved.append({
                        'startup_id': startup_id,
                        'name': name,
                        'cb_insights_id': cb_id,
                        'method': 'keyword'
                    })
                    resolved_count += 1
                else:
                    self.failed.append({
                        'startup_id': ids_map[name],
                        'name': name,
                        'reason': 'No match found'
                    })
                    failed_count += 1
                
                await asyncio.sleep(0.05)  # Rate limiting
            
            # Progress update
            progress_pct = (resolved_count + failed_count) / self.total * 100
            logger.info(f"   Progress: {resolved_count + failed_count}/{self.total} ({progress_pct:.1f}%) | Resolved: {resolved_count}")
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        # Log results
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ RESOLUTION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total startups: {self.total}")
        logger.info(f"Resolved: {resolved_count} ({resolved_count/self.total*100:.1f}%)")
        logger.info(f"Failed: {failed_count} ({failed_count/self.total*100:.1f}%)")
        logger.info(f"{'='*80}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save resolution results to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save resolved
        resolved_file = f"/home/akyo/startup_swiper/downloads/startup_resolution_resolved_{timestamp}.csv"
        os.makedirs(os.path.dirname(resolved_file), exist_ok=True)
        
        with open(resolved_file, 'w', newline='', encoding='utf-8') as f:
            if self.resolved:
                writer = csv.DictWriter(f, fieldnames=['startup_id', 'name', 'cb_insights_id', 'method'])
                writer.writeheader()
                writer.writerows(self.resolved)
        
        logger.info(f"✅ Resolved results saved: {resolved_file}")
        
        # Save failed
        if self.failed:
            failed_file = f"/home/akyo/startup_swiper/downloads/startup_resolution_failed_{timestamp}.csv"
            
            with open(failed_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['startup_id', 'name', 'reason'])
                writer.writeheader()
                writer.writerows(self.failed)
            
            logger.info(f"⚠️ Failed results saved: {failed_file}")


async def main():
    resolver = StartupIDResolver()
    await resolver.resolve_all()


if __name__ == "__main__":
    asyncio.run(main())
