#!/usr/bin/env python3
"""
Ultra-Fast Parallel Enrichment System
Optimized for maximum speed with:
- Async/await for I/O bound operations
- Multiple parallel workers (10-50)
- Smart rate limiting with burst capacity
- Batch processing with checkpoints
- GPU-ready for AI enrichment
- Progress tracking with ETA
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass
from collections import deque
import sys

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class EnrichmentStats:
    """Track enrichment statistics"""
    total: int = 0
    enriched: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: float = 0
    last_checkpoint: int = 0
    
    @property
    def success_rate(self) -> float:
        attempted = self.enriched + self.failed
        return (self.enriched / attempted * 100) if attempted > 0 else 0
    
    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time
    
    @property
    def rate_per_second(self) -> float:
        return self.enriched / self.elapsed_seconds if self.elapsed_seconds > 0 else 0
    
    @property
    def eta_seconds(self) -> float:
        remaining = self.total - (self.enriched + self.failed + self.skipped)
        return remaining / self.rate_per_second if self.rate_per_second > 0 else 0

class RateLimiter:
    """Token bucket rate limiter with burst capacity"""
    
    def __init__(self, rate: int = 10, burst: int = 20):
        self.rate = rate  # requests per second
        self.burst = burst  # burst capacity
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until a token is available"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # If no tokens available, wait
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

class UltraFastEnricher:
    """Ultra-fast async enrichment system"""
    
    def __init__(self, workers: int = 20, rate_limit: int = 10):
        self.base_path = Path(__file__).parent.parent
        self.database_file = self.base_path / "docs/architecture/ddbb/slush_full_list.json"
        self.output_file = self.base_path / "docs/architecture/ddbb/slush_full_list_enriched.json"
        self.checkpoint_file = self.base_path / "api/.ultra_enrichment_checkpoint.json"
        
        self.workers = workers
        self.rate_limiter = RateLimiter(rate=rate_limit, burst=rate_limit * 2)
        self.stats = EnrichmentStats()
        
        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(workers)
        
    def load_database(self) -> List[Dict]:
        """Load startup database"""
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return []
    
    def load_checkpoint(self) -> Dict:
        """Load progress checkpoint"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"enriched_names": [], "last_index": 0}
    
    def save_checkpoint(self, enriched_names: List[str], last_index: int):
        """Save progress checkpoint"""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    "enriched_names": enriched_names,
                    "last_index": last_index,
                    "timestamp": datetime.utcnow().isoformat()
                }, f)
        except Exception as e:
            logger.warning(f"Could not save checkpoint: {e}")
    
    async def enrich_startup_async(self, startup: Dict, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Enrich a single startup using async HTTP"""
        async with self.semaphore:
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                website = startup.get('website', '')
                if not website:
                    return None
                
                # Normalize URL
                if not website.startswith('http'):
                    website = f"https://{website}"
                
                # Fetch website with timeout
                async with session.get(
                    website,
                    timeout=aiohttp.ClientTimeout(total=10),
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    
                    # Quick extraction (lightweight)
                    enrichment_data = self._extract_data(html, website)
                    
                    if enrichment_data:
                        return {
                            **startup,
                            "enrichment": enrichment_data,
                            "is_enriched": True,
                            "last_enriched_date": datetime.utcnow().isoformat()
                        }
                        
            except asyncio.TimeoutError:
                logger.debug(f"Timeout: {startup.get('company_name', '')}")
            except Exception as e:
                logger.debug(f"Error enriching {startup.get('company_name', '')}: {str(e)[:50]}")
            
            return None
    
    def _extract_data(self, html: str, url: str) -> Dict:
        """Quick data extraction from HTML"""
        import re
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = list(set(re.findall(email_pattern, html)))[:5]
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        phones = list(set(re.findall(phone_pattern, html)))[:5]
        
        # Extract social media
        social = {}
        social_patterns = {
            'linkedin': r'linkedin\.com/company/([^/"\s]+)',
            'twitter': r'twitter\.com/([^/"\s]+)',
            'facebook': r'facebook\.com/([^/"\s]+)',
            'instagram': r'instagram\.com/([^/"\s]+)'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, html.lower())
            if matches:
                social[platform] = f"https://{platform}.com/{matches[0]}"
        
        # Extract tech stack (basic detection)
        tech_stack = []
        tech_indicators = {
            'React': ['react', '_next'],
            'Vue.js': ['vue.js', '__vue__'],
            'Angular': ['ng-', 'angular'],
            'WordPress': ['wp-content', 'wordpress'],
            'Shopify': ['shopify', 'cdn.shopify'],
            'Wix': ['wix.com', 'static.wixstatic'],
            'Node.js': ['node.js'],
            'Django': ['django'],
            'Rails': ['rails']
        }
        
        html_lower = html.lower()
        for tech, indicators in tech_indicators.items():
            if any(ind in html_lower for ind in indicators):
                tech_stack.append(tech)
        
        # Extract page title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        page_title = title_match.group(1) if title_match else ""
        
        return {
            "enrichment_date": datetime.utcnow().isoformat(),
            "enrichment_success": True,
            "sources_checked": ["company_website"],
            "website_url": url,
            "page_title": page_title[:200],
            "emails": emails,
            "phone_numbers": phones,
            "social_media": social,
            "tech_stack": tech_stack,
            "enrichment_method": "ultra_fast_async"
        }
    
    async def process_batch(self, startups: List[Dict], session: aiohttp.ClientSession) -> List[Dict]:
        """Process a batch of startups concurrently"""
        tasks = [self.enrich_startup_async(startup, session) for startup in startups]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        enriched = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                enriched.append(result)
                self.stats.enriched += 1
            elif isinstance(result, Exception):
                self.stats.failed += 1
            else:
                self.stats.skipped += 1
        
        return enriched
    
    def print_progress(self):
        """Print enrichment progress"""
        completed = self.stats.enriched + self.stats.failed + self.stats.skipped
        progress_pct = (completed / self.stats.total * 100) if self.stats.total > 0 else 0
        
        eta_min = self.stats.eta_seconds / 60
        
        logger.info(
            f"Progress: {completed}/{self.stats.total} ({progress_pct:.1f}%) | "
            f"Enriched: {self.stats.enriched} | Failed: {self.stats.failed} | "
            f"Rate: {self.stats.rate_per_second:.1f}/s | "
            f"ETA: {eta_min:.1f}m"
        )
    
    async def enrich_all(self, start_from: int = 0, limit: Optional[int] = None) -> List[Dict]:
        """Enrich all startups with async processing"""
        logger.info("Loading database...")
        database = self.load_database()
        
        if not database:
            logger.error("No database loaded")
            return []
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        enriched_names = set(checkpoint.get('enriched_names', []))
        
        # Filter startups that need enrichment
        to_enrich = [
            s for s in database 
            if s.get('company_name') not in enriched_names 
            and s.get('website')
            and not s.get('is_enriched')
        ]
        
        # Apply start and limit
        to_enrich = to_enrich[start_from:]
        if limit:
            to_enrich = to_enrich[:limit]
        
        self.stats.total = len(to_enrich)
        self.stats.start_time = time.time()
        
        logger.info(f"Starting ultra-fast enrichment...")
        logger.info(f"Total: {self.stats.total} startups")
        logger.info(f"Workers: {self.workers}")
        logger.info(f"Rate limit: {self.rate_limiter.rate}/s")
        logger.info("")
        
        all_enriched = []
        batch_size = 50  # Process in batches for memory efficiency
        
        # Create persistent session
        connector = aiohttp.TCPConnector(limit=self.workers, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=300)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(0, len(to_enrich), batch_size):
                batch = to_enrich[i:i + batch_size]
                
                # Process batch
                enriched_batch = await self.process_batch(batch, session)
                all_enriched.extend(enriched_batch)
                
                # Update checkpoint
                enriched_names.update(s.get('company_name', '') for s in enriched_batch)
                self.save_checkpoint(list(enriched_names), start_from + i + batch_size)
                
                # Print progress every batch
                if (i // batch_size) % 5 == 0:
                    self.print_progress()
        
        # Final progress
        self.print_progress()
        
        return all_enriched
    
    def merge_and_save(self, enriched_startups: List[Dict]):
        """Merge enriched data back into database"""
        logger.info("\nMerging enriched data...")
        
        database = self.load_database()
        enriched_lookup = {s.get('company_name', ''): s for s in enriched_startups}
        
        updated_count = 0
        for startup in database:
            name = startup.get('company_name', '')
            if name in enriched_lookup:
                startup.update(enriched_lookup[name])
                updated_count += 1
        
        # Save updated database
        logger.info(f"Saving {updated_count} updates...")
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved to {self.database_file.name}")
        
        # Also save to slush2_extracted
        extracted_file = self.base_path / "docs/architecture/ddbb/slush2_extracted.json"
        if extracted_file.exists():
            with open(extracted_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved to {extracted_file.name}")
        
        # Update app copy
        app_copy = self.base_path / "app/startup-swipe-schedu/startups/slush2_extracted.json"
        if app_copy.parent.exists():
            with open(app_copy, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved to app copy")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ultra-fast parallel startup enrichment'
    )
    parser.add_argument('--workers', type=int, default=20,
                       help='Number of parallel workers (default: 20)')
    parser.add_argument('--rate', type=int, default=10,
                       help='Rate limit (requests/second, default: 10)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of startups to enrich')
    parser.add_argument('--start', type=int, default=0,
                       help='Start from index')
    parser.add_argument('--save', action='store_true',
                       help='Save results to database')
    
    args = parser.parse_args()
    
    enricher = UltraFastEnricher(workers=args.workers, rate_limit=args.rate)
    
    # Run enrichment
    enriched = await enricher.enrich_all(start_from=args.start, limit=args.limit)
    
    # Print final stats
    logger.info("\n" + "="*70)
    logger.info("ENRICHMENT COMPLETE")
    logger.info("="*70)
    logger.info(f"Total enriched:  {enricher.stats.enriched}")
    logger.info(f"Failed:          {enricher.stats.failed}")
    logger.info(f"Skipped:         {enricher.stats.skipped}")
    logger.info(f"Success rate:    {enricher.stats.success_rate:.1f}%")
    logger.info(f"Total time:      {enricher.stats.elapsed_seconds:.1f}s")
    logger.info(f"Rate:            {enricher.stats.rate_per_second:.2f} startups/second")
    logger.info("="*70)
    
    # Save if requested
    if args.save or (enriched and input("\nSave to database? (y/n): ").lower() == 'y'):
        enricher.merge_and_save(enriched)
        logger.info("✓ Complete!")
    else:
        logger.info("Results not saved (use --save to auto-save)")

if __name__ == "__main__":
    asyncio.run(main())
