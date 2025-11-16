#!/usr/bin/env python3
"""
AXA Enhanced Batch Evaluator - Optimized Performance
Batch processing with Nvidia NIM API for intelligent startup evaluation.

Features:
- Optimized batch size for Nvidia NIM API
- Parallel batch processing with configurable workers
- Smart checkpointing and recovery
- Progress tracking with ETA estimation
- Scaling potential assessment using all database fields

Usage:
    source .venv/bin/activate
    python3 api/axa_enhanced_batch_evaluator.py --batch-size 15 --workers 8
    python3 api/axa_enhanced_batch_evaluator.py --limit 100 --dry-run
"""

import json
import argparse
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import aiohttp
from dataclasses import dataclass
import time
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models_startup import Startup
from llm_config import get_nvidia_nim_model

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get NVIDIA NIM configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = get_nvidia_nim_model()

# Validation
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not set in .env file")


@dataclass
class BatchStats:
    """Statistics for batch processing"""
    total_startups: int
    processed: int = 0
    failed: int = 0
    batch_count: int = 0
    start_time: float = 0
    total_api_calls: int = 0
    successful_api_calls: int = 0
    avg_batch_time: float = 0
    estimated_completion: Optional[datetime] = None
    
    def get_progress_percent(self) -> float:
        return (self.processed / self.total_startups * 100) if self.total_startups > 0 else 0
    
    def get_eta(self) -> Optional[timedelta]:
        if self.processed == 0 or self.start_time == 0:
            return None
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed
        remaining = self.total_startups - self.processed
        if rate > 0:
            return timedelta(seconds=remaining / rate)
        return None


class OptimizedBatchEvaluator:
    """Optimized batch evaluator for Nvidia NIM API"""
    
    def __init__(
        self,
        batch_size: int = 15,
        workers: int = 8,
        checkpoint_dir: str = "downloads",
        timeout: int = 120
    ):
        self.batch_size = batch_size
        self.workers = workers
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.db = SessionLocal()
        
        self.checkpoint_file = self.checkpoint_dir / "axa_batch_checkpoint.json"
        self.results_file = self.checkpoint_dir / "axa_batch_results.jsonl"
        
        self.evaluated_ids = set()
        self.results = []
        self.stats = BatchStats(total_startups=0)
        
        logger.info(f"✓ Batch Evaluator initialized:")
        logger.info(f"  Batch Size: {batch_size} startups/batch")
        logger.info(f"  Workers: {workers} parallel workers")
        logger.info(f"  Model: {NVIDIA_MODEL}")
        logger.info(f"  Checkpoint: {self.checkpoint_file}")
    
    def load_checkpoint(self) -> Tuple[set, int]:
        """Load checkpoint if exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file) as f:
                    data = json.load(f)
                    evaluated_ids = set(data.get('evaluated_ids', []))
                    batch_count = data.get('batch_count', 0)
                    logger.info(f"✓ Loaded checkpoint: {len(evaluated_ids)} evaluated, {batch_count} batches")
                    return evaluated_ids, batch_count
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return set(), 0
    
    def save_checkpoint(self):
        """Save progress checkpoint"""
        try:
            checkpoint_data = {
                'timestamp': datetime.now().isoformat(),
                'evaluated_ids': list(self.evaluated_ids),
                'batch_count': self.stats.batch_count,
                'processed': self.stats.processed,
                'failed': self.stats.failed
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    async def call_nvidia_nim_api(
        self,
        startups: List[Startup],
        session: aiohttp.ClientSession
    ) -> Optional[Dict]:
        """Call Nvidia NIM API with batch of startups"""
        
        prompt = self._build_batch_prompt(startups)
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 8000
        }
        
        self.stats.total_api_calls += 1
        
        try:
            async with session.post(
                f"{NVIDIA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.stats.successful_api_calls += 1
                    return data['choices'][0]['message']['content']
                else:
                    logger.error(f"API returned status {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error: {error_text[:200]}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling API (batch size {len(startups)})")
            return None
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return None
    
    def _build_batch_prompt(self, startups: List[Startup]) -> str:
        """Build prompt for batch evaluation"""
        
        startup_blocks = []
        for startup in startups:
            block = self._format_startup_data(startup)
            startup_blocks.append(block)
        
        startups_text = "\n" + "=" * 80 + "\n".join(startup_blocks)
        
        prompt = f"""You are an INSURANCE INDUSTRY EXPERT evaluating {len(startups)} startups for AXA.

TASK: For each startup, provide:
1. Primary Rule matching (Rule 1-5)
2. Matching feature categories
3. Overall fit score (30-92)
4. Confidence level (high/medium/low)
5. Scaling potential assessment
6. Key strengths and concerns
7. Can be used as provider (yes/no)

EVALUATION CONTEXT:
- Consider ALL available data fields (funding, maturity, location, tech stack, team, market, etc.)
- Perspective: Insurance product owner with IT expertise and business knowledge
- Focus on SCALING POTENTIAL given company stage, funding, geography, and capabilities
- Realistic scoring with high confidence in differentiation

STARTUPS TO EVALUATE:
{startups_text}

Return a JSON array with format:
[
  {{
    "startup_id": <id>,
    "startup_name": "<name>",
    "rule": "Rule X",
    "feature_categories": ["F#.#", ...],
    "score": <30-92>,
    "confidence": "high|medium|low",
    "scaling_potential": "high|medium|low",
    "scaling_margin": <-15 to +15>,
    "strengths": [<3 key strengths>],
    "concerns": [<3 key concerns>],
    "can_be_provider": <true|false>,
    "reasoning": "<2-3 sentence justification>"
  }},
  ...
]

Only return valid JSON array, no markdown, no explanations."""
        
        return prompt
    
    def _format_startup_data(self, startup: Startup) -> str:
        """Format single startup data for prompt"""
        
        # Build comprehensive data summary
        sections = []
        
        # Basic info
        sections.append(f"Company: {startup.company_name} (ID: {startup.id})")
        
        if startup.company_country:
            sections.append(f"Location: {startup.company_city or 'N/A'}, {startup.company_country}")
        
        if startup.founding_year:
            sections.append(f"Founded: {startup.founding_year}")
        
        # Industry/Business
        if startup.primary_industry:
            sections.append(f"Industry: {startup.primary_industry}")
        
        if startup.company_description:
            sections.append(f"Description: {startup.company_description[:300]}")
        
        # Stage & Maturity
        if startup.maturity:
            sections.append(f"Maturity: {startup.maturity}")
        
        if startup.company_type:
            sections.append(f"Type: {startup.company_type}")
        
        # Funding
        if startup.total_funding:
            sections.append(f"Funding: ${startup.total_funding:.1f}M total")
        
        if startup.funding_stage:
            sections.append(f"Funding Stage: {startup.funding_stage}")
        
        if startup.valuation:
            sections.append(f"Valuation: ${startup.valuation:.1f}M")
        
        # Team
        if startup.employees:
            sections.append(f"Employees: {startup.employees}")
        
        # Tech
        if startup.tech:
            try:
                tech_list = json.loads(startup.tech) if isinstance(startup.tech, str) else startup.tech
                if isinstance(tech_list, list) and tech_list:
                    sections.append(f"Tech: {', '.join(tech_list[:8])}")
            except:
                pass
        
        # Business model
        if startup.business_model:
            sections.append(f"Business Model: {startup.business_model}")
        
        # Product & market
        if startup.extracted_product:
            sections.append(f"Product: {startup.extracted_product[:150]}")
        
        if startup.extracted_market:
            sections.append(f"Market: {startup.extracted_market[:150]}")
        
        # Current AXA assessment
        if startup.axa_primary_topic:
            sections.append(f"Current Topic: {startup.axa_primary_topic}")
        
        if startup.axa_overall_score:
            sections.append(f"Current Score: {startup.axa_overall_score:.1f}")
        
        return "\n".join(sections)
    
    async def _process_batch(self, batch: List[Startup], session: aiohttp.ClientSession) -> Tuple[int, int]:
        """Process single batch of startups"""
        
        batch_start = time.time()
        
        response_text = await self.call_nvidia_nim_api(batch, session)
        
        if not response_text:
            logger.error(f"Batch of {len(batch)} failed - API error")
            self.stats.failed += len(batch)
            return 0, len(batch)
        
        # Parse JSON response
        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                evaluations = json.loads(json_str)
            else:
                evaluations = json.loads(response_text)
            
            # Process and save results
            success_count = 0
            for eval_data in evaluations:
                try:
                    startup_id = eval_data.get('startup_id')
                    if startup_id:
                        self.evaluated_ids.add(startup_id)
                        self.results.append(eval_data)
                        
                        # Save to results file
                        with open(self.results_file, 'a') as f:
                            f.write(json.dumps(eval_data) + '\n')
                        
                        success_count += 1
                except Exception as e:
                    logger.error(f"Failed to process evaluation: {e}")
            
            self.stats.processed += success_count
            self.stats.failed += (len(batch) - success_count)
            self.stats.batch_count += 1
            
            batch_time = time.time() - batch_start
            self.stats.avg_batch_time = (self.stats.avg_batch_time * (self.stats.batch_count - 1) + batch_time) / self.stats.batch_count
            
            return success_count, len(batch) - success_count
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response preview: {response_text[:200]}")
            self.stats.failed += len(batch)
            return 0, len(batch)
    
    async def _worker(self, worker_id: int, queue: asyncio.Queue):
        """Worker coroutine for batch processing"""
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    batch = await asyncio.wait_for(queue.get(), timeout=5.0)
                    
                    if batch is None:  # Poison pill
                        break
                    
                    success, failed = await self._process_batch(batch, session)
                    
                    # Save checkpoint every 10 batches
                    if self.stats.batch_count % 10 == 0:
                        self.save_checkpoint()
                    
                    # Log progress
                    progress = self.stats.get_progress_percent()
                    eta = self.stats.get_eta()
                    eta_str = f" ETA: {eta}" if eta else ""
                    
                    logger.info(
                        f"[Worker {worker_id}] Batch {self.stats.batch_count}: "
                        f"{success}✓/{failed}✗ | "
                        f"Progress: {self.stats.processed}/{self.stats.total_startups} "
                        f"({progress:.1f}%){eta_str}"
                    )
                    
                    queue.task_done()
                    
                except asyncio.TimeoutError:
                    if queue.empty():
                        continue
                except Exception as e:
                    logger.error(f"Worker {worker_id} error: {e}")
    
    async def evaluate_all_async(self, limit: int = None, dry_run: bool = False) -> List[Dict]:
        """Evaluate all startups asynchronously with batch processing"""
        
        # Load checkpoint
        self.evaluated_ids, last_batch_count = self.load_checkpoint()
        
        # Get startups to evaluate
        query = self.db.query(Startup).filter(Startup.axa_overall_score.isnot(None))
        
        if limit:
            startups = query.limit(limit).all()
        else:
            startups = query.all()
        
        # Filter already evaluated
        remaining_startups = [s for s in startups if s.id not in self.evaluated_ids]
        
        self.stats.total_startups = len(remaining_startups)
        self.stats.start_time = time.time()
        
        logger.info(f"\n{'=' * 90}")
        logger.info(f"AXA ENHANCED BATCH EVALUATOR - PERFORMANCE OPTIMIZED")
        logger.info(f"{'=' * 90}")
        logger.info(f"Total startups to evaluate: {self.stats.total_startups}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Workers: {self.workers}")
        logger.info(f"Dry run: {dry_run}\n")
        
        if dry_run:
            logger.info("DRY RUN MODE - No results will be saved")
            return []
        
        if self.stats.total_startups == 0:
            logger.info("No startups to evaluate")
            return []
        
        # Create batches
        batches = [
            remaining_startups[i:i + self.batch_size]
            for i in range(0, len(remaining_startups), self.batch_size)
        ]
        
        logger.info(f"Created {len(batches)} batches\n")
        
        # Create work queue
        queue = asyncio.Queue()
        
        # Add batches to queue
        for batch in batches:
            await queue.put(batch)
        
        # Add poison pills for workers
        for _ in range(self.workers):
            await queue.put(None)
        
        # Start workers
        workers = [
            asyncio.create_task(self._worker(i, queue))
            for i in range(self.workers)
        ]
        
        # Wait for all work to complete
        await asyncio.gather(*workers)
        
        # Final checkpoint
        self.save_checkpoint()
        
        # Summary
        elapsed = time.time() - self.stats.start_time
        
        logger.info(f"\n{'=' * 90}")
        logger.info(f"BATCH EVALUATION COMPLETE")
        logger.info(f"{'=' * 90}")
        logger.info(f"Total Time: {timedelta(seconds=int(elapsed))}")
        logger.info(f"Processed: {self.stats.processed}")
        logger.info(f"Failed: {self.stats.failed}")
        logger.info(f"Success Rate: {self.stats.successful_api_calls}/{self.stats.total_api_calls} API calls")
        logger.info(f"Avg Batch Time: {self.stats.avg_batch_time:.2f}s")
        logger.info(f"Throughput: {self.stats.processed/elapsed:.1f} startups/sec")
        logger.info(f"Results saved: {self.results_file}\n")
        
        return self.results


async def main():
    parser = argparse.ArgumentParser(
        description='AXA Enhanced Batch Evaluator - Optimized Performance'
    )
    parser.add_argument('--batch-size', type=int, default=15, help='Startups per batch')
    parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of startups')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--timeout', type=int, default=120, help='API timeout in seconds')
    
    args = parser.parse_args()
    
    evaluator = OptimizedBatchEvaluator(
        batch_size=args.batch_size,
        workers=args.workers,
        timeout=args.timeout
    )
    
    results = await evaluator.evaluate_all_async(
        limit=args.limit,
        dry_run=args.dry_run
    )
    
    if results and not args.dry_run:
        logger.info(f"✓ Evaluation complete. {len(results)} startups processed.")


if __name__ == "__main__":
    asyncio.run(main())
