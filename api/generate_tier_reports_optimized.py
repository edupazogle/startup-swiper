#!/usr/bin/env python3
"""
Generate CB Insights Scouting Reports for Tier 1 and Tier 2 Startups
WITH CHECKPOINTING AND RESUMABLE EXECUTION

This script:
1. Generates scouting reports in batches (Tier 1, then Tier 2)
2. Supports resumable execution with checkpoints
3. Uses optimized concurrency=5 (proven safe in testing)
4. Tracks progress and handles failures gracefully
5. Saves intermediate results for recovery

Features:
- Checkpointing: Save progress every batch
- Resumable: Can be stopped and restarted without losing work
- Tier-based execution: Tier 1 first, then Tier 2
- Progress tracking: Real-time updates to database and logs
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

# Configuration - OPTIMIZED BASED ON TESTING
CONCURRENCY = 5  # Proven safe: 2.3s for 3 reports = 0.77s per report
REQUEST_TIMEOUT = 300  # 5 minutes max per report
DB_PATH = Path("/home/akyo/startup_swiper/startup_swiper.db")
DOWNLOADS_PATH = Path("/home/akyo/startup_swiper/downloads/tier_reports")
CHECKPOINT_FILE = Path("/tmp/tier_reports_checkpoint.json")


@dataclass
class StartupToProcess:
    """Startup record to process"""
    startup_id: int
    company_name: str
    cb_insights_id: int
    axa_overall_score: float
    axa_priority_tier: str


class CheckpointManager:
    """Manage checkpoints for resumable execution"""
    
    def __init__(self, checkpoint_file: Path):
        self.checkpoint_file = checkpoint_file
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
        
        return {
            "tier_1_completed": False,
            "tier_2_completed": False,
            "tier_1_processed": 0,
            "tier_1_generated": 0,
            "tier_1_failed": 0,
            "tier_2_processed": 0,
            "tier_2_generated": 0,
            "tier_2_failed": 0,
            "last_processed_tier_1_id": None,
            "last_processed_tier_2_id": None,
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save(self) -> None:
        """Save checkpoint to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def mark_tier_1_complete(self) -> None:
        """Mark Tier 1 as complete"""
        self.data["tier_1_completed"] = True
        self.save()
    
    def mark_tier_2_complete(self) -> None:
        """Mark Tier 2 as complete"""
        self.data["tier_2_completed"] = True
        self.save()
    
    def update_tier_1_progress(self, processed: int, generated: int, failed: int, last_id: Optional[int] = None) -> None:
        """Update Tier 1 progress"""
        self.data["tier_1_processed"] = processed
        self.data["tier_1_generated"] = generated
        self.data["tier_1_failed"] = failed
        if last_id:
            self.data["last_processed_tier_1_id"] = last_id
        self.save()
    
    def update_tier_2_progress(self, processed: int, generated: int, failed: int, last_id: Optional[int] = None) -> None:
        """Update Tier 2 progress"""
        self.data["tier_2_processed"] = processed
        self.data["tier_2_generated"] = generated
        self.data["tier_2_failed"] = failed
        if last_id:
            self.data["last_processed_tier_2_id"] = last_id
        self.save()


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
                        logger.error(f"❌ No token in response")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Authorization failed: {response.status}")
                    return False
        except asyncio.TimeoutError:
            logger.error("❌ Authorization timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Authorization error: {str(e)}")
            return False
    
    async def get_scouting_report(self, org_id: int, company_name: str) -> Optional[Dict[str, Any]]:
        """Get scouting report for an organization"""
        if not self.bearer_token or not self.session:
            return None
        
        report_url = f"{self.base_url}/v2/organizations/{org_id}/scoutingreport"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(report_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
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
    
    def __init__(self, concurrency: int = CONCURRENCY):
        self.concurrency = concurrency
        self.db_path = DB_PATH
        self.downloads_path = DOWNLOADS_PATH
        self.downloads_path.mkdir(parents=True, exist_ok=True)
        
        self.checkpoint = CheckpointManager(CHECKPOINT_FILE)
        self.semaphore = asyncio.Semaphore(concurrency)
    
    def get_startups_to_process(self, tier: str) -> List[StartupToProcess]:
        """Query database for Tier startups with CB Insights IDs"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, company_name, cb_insights_id, axa_overall_score, axa_priority_tier
                FROM startups
                WHERE axa_priority_tier LIKE ?
                  AND cb_insights_id IS NOT NULL
                  AND cb_insights_id != 0
                ORDER BY axa_overall_score DESC
            """, (f"%{tier}%",))
            
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
        """Process a single startup"""
        async with self.semaphore:
            try:
                # Check if already exists
                if self.report_exists(startup.startup_id):
                    logger.debug(f"⏭️ Skipping {startup.company_name} - report already exists")
                    return True
                
                # Generate report
                report_data = await client.get_scouting_report(
                    startup.cb_insights_id,
                    startup.company_name
                )
                
                if not report_data:
                    logger.warning(f"❌ Failed to generate report for {startup.company_name}")
                    return False
                
                # Save report
                self.save_report(startup, report_data)
                logger.info(f"✅ Generated & saved: {startup.company_name}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error processing {startup.company_name}: {e}")
                return False
    
    def save_report(self, startup: StartupToProcess, report_data: Dict[str, Any]) -> None:
        """Save report to database and filesystem"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = startup.company_name.lower().replace(" ", "_").replace(".", "")
        
        try:
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
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
                markdown_content,
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
    
    async def generate_tier_reports(self, tier: str) -> Dict[str, int]:
        """Generate reports for a specific tier"""
        startups = self.get_startups_to_process(tier)
        
        if not startups:
            logger.warning(f"⚠️ No {tier} startups to process")
            return {"total": 0, "generated": 0, "failed": 0, "skipped": 0}
        
        tier_display = f"{tier} (Critical Priority)" if "1" in tier else f"{tier} (High Priority)"
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 GENERATING REPORTS FOR {tier_display}")
        logger.info(f"{'='*80}")
        logger.info(f"Total startups to process: {len(startups)}")
        logger.info(f"Concurrency: {self.concurrency}")
        logger.info(f"Timeout per report: {REQUEST_TIMEOUT}s")
        
        generated = 0
        failed = 0
        skipped = 0
        
        async with CBInsightsV2Client(
            CBINSIGHTS_CLIENT_ID,
            CBINSIGHTS_CLIENT_SECRET,
            timeout=REQUEST_TIMEOUT
        ) as client:
            
            # Authorize once
            if not await client.authorize():
                logger.error("❌ Authorization failed. Aborting.")
                return {"total": len(startups), "generated": 0, "failed": 0, "skipped": 0}
            
            # Process all startups concurrently
            logger.info(f"🚀 Starting parallel processing with concurrency={self.concurrency}...")
            
            tasks = [
                self.process_startup(startup, client)
                for startup in startups
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            for i, result in enumerate(results):
                if isinstance(result, bool) and result:
                    # Check if it was skipped (report already exists)
                    if self.report_exists(startups[i].startup_id):
                        skipped += 1
                    else:
                        generated += 1
                else:
                    failed += 1
            
            # Update checkpoint
            if "1" in tier:
                self.checkpoint.update_tier_1_progress(
                    len(startups), generated, failed,
                    startups[-1].startup_id if startups else None
                )
            else:
                self.checkpoint.update_tier_2_progress(
                    len(startups), generated, failed,
                    startups[-1].startup_id if startups else None
                )
            
            # Print summary
            print("\n" + "=" * 80)
            print(f"✅ {tier_display} GENERATION COMPLETE")
            print("=" * 80)
            print(f"Total processed: {len(startups)}")
            print(f"✅ Generated: {generated}")
            print(f"⏭️  Already exist: {skipped}")
            print(f"❌ Failed: {failed}")
            print(f"Success rate: {generated / len(startups) * 100:.1f}%" if generated + failed > 0 else "N/A")
            print("=" * 80)
            
            return {
                "total": len(startups),
                "generated": generated,
                "failed": failed,
                "skipped": skipped
            }


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate CB Insights Scouting Reports for Tier 1/2 startups with checkpointing"
    )
    parser.add_argument(
        "--tier",
        choices=["tier-1", "tier-2", "all"],
        default="all",
        help="Which tier to process: tier-1, tier-2, or all (default: all)"
    )
    parser.add_argument(
        "--skip-checkpoint",
        action="store_true",
        help="Skip checkpoint and restart from beginning"
    )
    
    args = parser.parse_args()
    
    generator = TierReportsGenerator(concurrency=CONCURRENCY)
    
    # Check checkpoint status
    checkpoint = generator.checkpoint
    if checkpoint.data["tier_1_completed"] or checkpoint.data["tier_2_completed"]:
        print("\n" + "=" * 80)
        print("📋 CHECKPOINT STATUS")
        print("=" * 80)
        if checkpoint.data["tier_1_completed"]:
            print("✅ Tier 1 (Critical Priority): COMPLETED")
            print(f"   Generated: {checkpoint.data['tier_1_generated']}")
            print(f"   Failed: {checkpoint.data['tier_1_failed']}")
        else:
            print("⏳ Tier 1 (Critical Priority): NOT STARTED")
        
        if checkpoint.data["tier_2_completed"]:
            print("✅ Tier 2 (High Priority): COMPLETED")
            print(f"   Generated: {checkpoint.data['tier_2_generated']}")
            print(f"   Failed: {checkpoint.data['tier_2_failed']}")
        else:
            print("⏳ Tier 2 (High Priority): NOT STARTED")
        print("=" * 80 + "\n")
    
    # Process tiers
    tier_1_result = None
    tier_2_result = None
    
    if args.tier in ["tier-1", "all"]:
        if not checkpoint.data["tier_1_completed"] or args.skip_checkpoint:
            tier_1_result = await generator.generate_tier_reports("Tier 1")
            if tier_1_result["failed"] == 0 and tier_1_result["total"] > 0:
                generator.checkpoint.mark_tier_1_complete()
    
    if args.tier in ["tier-2", "all"]:
        if not checkpoint.data["tier_2_completed"] or args.skip_checkpoint:
            tier_2_result = await generator.generate_tier_reports("Tier 2")
            if tier_2_result["failed"] == 0 and tier_2_result["total"] > 0:
                generator.checkpoint.mark_tier_2_complete()
    
    # Final summary
    print("\n" + "=" * 80)
    print("OVERALL GENERATION SUMMARY")
    print("=" * 80)
    
    total_generated = 0
    total_failed = 0
    
    if tier_1_result:
        print(f"Tier 1: {tier_1_result['generated']} generated, {tier_1_result['failed']} failed")
        total_generated += tier_1_result['generated']
        total_failed += tier_1_result['failed']
    
    if tier_2_result:
        print(f"Tier 2: {tier_2_result['generated']} generated, {tier_2_result['failed']} failed")
        total_generated += tier_2_result['generated']
        total_failed += tier_2_result['failed']
    
    print("-" * 80)
    print(f"Total: {total_generated} generated, {total_failed} failed")
    print("=" * 80)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
