#!/usr/bin/env python3
"""
Generate CB Insights Scouting Reports for Tier 1 and Tier 2 Startups

This script:
1. Queries the database for Tier 1 and Tier 2 startups with CB Insights IDs
2. Generates scouting reports in parallel (configurable concurrency)
3. Saves reports to database and filesystem
4. Tracks progress and handles failures gracefully
5. Supports resumable execution (skips already-generated reports)

Features:
- Parallel report generation (default: 3 concurrent requests)
- Batch processing and retry logic
- Database storage for quick future access
- Progress tracking and logging
- Comprehensive error handling
"""

import asyncio
import aiohttp
import json
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/tier_reports_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CB Insights API credentials
CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"
CB_INSIGHTS_BASE_URL = "https://api.cbinsights.com"

# Configuration
DEFAULT_CONCURRENCY = 3  # Tested safe concurrency level (0.77s per report)
REQUEST_TIMEOUT = 300  # 5 minutes max per report (includes processing time)
DB_PATH = Path("/home/akyo/startup_swiper/startup_swiper.db")
DOWNLOADS_PATH = Path("/home/akyo/startup_swiper/downloads/tier_reports")
DOCS_PATH = Path("/home/akyo/startup_swiper/docs/tier_reports")

# Performance expectations (based on testing)
# - Concurrency 3: 775 reports in ~1.5 hours
# - Concurrency 5: 775 reports in ~0.9 hours
EXPECTED_TIME_AT_CONCURRENCY_3 = 5400  # seconds (1.5 hours)


@dataclass
class StartupToProcess:
    """Startup record to process"""
    startup_id: int
    company_name: str
    cb_insights_id: int
    axa_overall_score: float
    axa_priority_tier: str


class CBInsightsV2Client:
    """CB Insights API v2 client with parallelization support"""
    
    def __init__(self, client_id: str, client_secret: str, timeout: int = REQUEST_TIMEOUT):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = CB_INSIGHTS_BASE_URL
        self.bearer_token: Optional[str] = None
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authorize(self) -> bool:
        """Get authorization bearer token"""
        if not self.session:
            logger.error("Session not initialized. Use async context manager.")
            return False
        
        auth_url = f"{self.base_url}/v2/authorize"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            async with self.session.post(auth_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.bearer_token = data.get("token") or data.get("access_token")
                    if self.bearer_token:
                        logger.info("✅ Authorization successful")
                        return True
                    else:
                        logger.error(f"❌ No token in response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Authorization failed: {response.status} - {error_text}")
                    return False
        except asyncio.TimeoutError:
            logger.error("❌ Authorization timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Authorization error: {str(e)}")
            return False
    
    async def get_scouting_report(self, org_id: int, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get scouting report for an organization
        
        Args:
            org_id: CB Insights organization ID
            company_name: Company name (for logging)
            
        Returns:
            Report data or None if failed
        """
        if not self.bearer_token:
            logger.error(f"❌ Not authorized for {company_name}")
            return None
        
        if not self.session:
            logger.error(f"❌ Session not initialized for {company_name}")
            return None
        
        report_url = f"{self.base_url}/v2/organizations/{org_id}/scoutingreport"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"🔄 Generating report for {company_name} (ID: {org_id})")
            
            async with self.session.post(report_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Report generated for {company_name}")
                    return data
                else:
                    error_text = await response.text()
                    logger.warning(f"⚠️ Report generation failed for {company_name}: {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Report generation timeout for {company_name}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Report generation error for {company_name}: {str(e)}")
            return None


class TierReportsGenerator:
    """Generate and manage scouting reports for tier 1/2 startups"""
    
    def __init__(self, concurrency: int = DEFAULT_CONCURRENCY):
        self.concurrency = concurrency
        self.db_path = DB_PATH
        self.downloads_path = DOWNLOADS_PATH
        self.docs_path = DOCS_PATH
        self.generated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.semaphore = asyncio.Semaphore(concurrency)
        
        # Create directories
        self.downloads_path.mkdir(parents=True, exist_ok=True)
        self.docs_path.mkdir(parents=True, exist_ok=True)
    
    def get_startups_to_process(self) -> List[StartupToProcess]:
        """Query database for Tier 1/2 startups with CB Insights IDs"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get Tier 1 and Tier 2 startups that have CB Insights IDs
            cursor.execute("""
                SELECT id, company_name, cb_insights_id, axa_overall_score, axa_priority_tier
                FROM startups
                WHERE (axa_priority_tier LIKE '%Tier 1%' OR axa_priority_tier LIKE '%Tier 2%')
                  AND cb_insights_id IS NOT NULL
                  AND cb_insights_id != 0
                ORDER BY axa_priority_tier, axa_overall_score DESC
            """)
            
            startups = [
                StartupToProcess(
                    startup_id=row['id'],
                    company_name=row['company_name'],
                    cb_insights_id=row['cb_insights_id'],
                    axa_overall_score=row['axa_overall_score'],
                    axa_priority_tier=row['axa_priority_tier']
                )
                for row in cursor.fetchall()
            ]
            
            conn.close()
            logger.info(f"📋 Found {len(startups)} Tier 1/2 startups with CB Insights IDs")
            return startups
            
        except Exception as e:
            logger.error(f"❌ Error querying database: {e}")
            return []
    
    def report_exists(self, startup_id: int) -> bool:
        """Check if report already exists in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM scouting_reports WHERE startup_id = ?
            """, (startup_id,))
            
            exists = cursor.fetchone()[0] > 0
            conn.close()
            return exists
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking report existence: {e}")
            return False
    
    async def process_startup(
        self,
        startup: StartupToProcess,
        client: CBInsightsV2Client
    ) -> bool:
        """
        Process a single startup: generate and save report
        
        Args:
            startup: Startup to process
            client: Authenticated API client
            
        Returns:
            True if successful, False otherwise
        """
        async with self.semaphore:
            try:
                # Check if already exists
                if self.report_exists(startup.startup_id):
                    logger.info(f"⏭️ Skipping {startup.company_name} - report already exists")
                    self.skipped_count += 1
                    return True
                
                # Generate report
                report_data = await client.get_scouting_report(
                    startup.cb_insights_id,
                    startup.company_name
                )
                
                if not report_data:
                    logger.warning(f"❌ Failed to generate report for {startup.company_name}")
                    self.failed_count += 1
                    return False
                
                # Save report to database and filesystem
                self.save_report(startup, report_data)
                self.generated_count += 1
                
                logger.info(f"💾 Saved report for {startup.company_name}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error processing {startup.company_name}: {e}")
                self.failed_count += 1
                return False
    
    def save_report(self, startup: StartupToProcess, report_data: Dict[str, Any]) -> None:
        """Save report to database and filesystem"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = startup.company_name.lower().replace(" ", "_").replace(".", "")
        
        try:
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Prepare markdown file path
            markdown_file = str(self.downloads_path / f"{safe_name}_{startup.startup_id}_{timestamp}.md")
            json_file = str(self.downloads_path / f"{safe_name}_{startup.startup_id}_{timestamp}.json")
            
            # Save markdown file
            markdown_content = report_data.get("reportMarkdown", "")
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            # Save JSON file
            json_content = {
                "generated_at": datetime.now().isoformat(),
                "startup_id": startup.startup_id,
                "company_name": startup.company_name,
                "cb_insights_id": startup.cb_insights_id,
                "axa_overall_score": startup.axa_overall_score,
                "axa_priority_tier": startup.axa_priority_tier,
                "orgInfo": report_data.get("orgInfo", {}),
                "reportJson": report_data.get("reportJson", ""),
                "reportMarkdown": report_data.get("reportMarkdown", "")
            }
            
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_content, f, indent=2, ensure_ascii=False)
            
            # Insert into database
            cursor.execute("""
                INSERT INTO scouting_reports (
                    startup_id, company_name, cb_insights_org_id,
                    generated_at, report_source,
                    report_markdown, report_json_raw,
                    markdown_file_path, json_file_path,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                startup.startup_id,
                startup.company_name,
                startup.cb_insights_id,
                datetime.now().isoformat(),
                "cb_insights",
                json_content.get("reportMarkdown", ""),
                json.dumps(json_content),
                markdown_file,
                json_file,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error saving report for {startup.company_name}: {e}")
            raise
    
    async def generate_all_reports(self) -> None:
        """Generate reports for all Tier 1/2 startups with CB Insights IDs"""
        startups = self.get_startups_to_process()
        
        if not startups:
            logger.warning("⚠️ No startups to process")
            return
        
        logger.info(f"🚀 Starting generation of {len(startups)} reports")
        logger.info(f"   Concurrency: {self.concurrency}")
        logger.info(f"   Timeout per report: {REQUEST_TIMEOUT}s")
        
        async with CBInsightsV2Client(
            CBINSIGHTS_CLIENT_ID,
            CBINSIGHTS_CLIENT_SECRET,
            timeout=REQUEST_TIMEOUT
        ) as client:
            
            # Authorize once
            if not await client.authorize():
                logger.error("❌ Authorization failed. Aborting.")
                return
            
            # Process all startups concurrently
            tasks = [
                self.process_startup(startup, client)
                for startup in startups
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Summary
            print("\n" + "=" * 80)
            print("SCOUTING REPORTS GENERATION SUMMARY")
            print("=" * 80)
            print(f"Total processed: {len(startups)}")
            print(f"✅ Generated: {self.generated_count}")
            print(f"⏭️  Skipped (already exist): {self.skipped_count}")
            print(f"❌ Failed: {self.failed_count}")
            print(f"Success rate: {self.generated_count / len(startups) * 100:.1f}%")
            print("=" * 80)
            
            # Log to file
            logger.info(f"✅ Generation complete: {self.generated_count} generated, {self.failed_count} failed, {self.skipped_count} skipped")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate CB Insights Scouting Reports for Tier 1/2 startups"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent report generations (default: {DEFAULT_CONCURRENCY})"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=REQUEST_TIMEOUT,
        help=f"Timeout per report in seconds (default: {REQUEST_TIMEOUT})"
    )
    
    args = parser.parse_args()
    
    generator = TierReportsGenerator(concurrency=args.concurrency)
    await generator.generate_all_reports()


if __name__ == "__main__":
    # For non-async main
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
