#!/usr/bin/env python3
"""
AXA ULTRA-FAST Startup Evaluator with Async + Concurrent Processing

OPTIMIZATIONS:
1. Async LLM calls with concurrent workers (10x faster)
2. Multi-startup batching (3-5 startups per LLM call)
3. Aggressive pre-filtering to skip irrelevant startups
4. Connection pooling and retry logic

Expected Performance:
- 100-150 startups/minute
- 6045 startups in ~40-60 minutes (vs 6-8 hours)

Usage:
    python3 api/axa_ultra_fast_evaluator.py
    python3 api/axa_ultra_fast_evaluator.py --workers 20  # More parallelism
    python3 api/axa_ultra_fast_evaluator.py --batch-size 5  # Larger batches
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Imports
from database import SessionLocal
from models_startup import Startup
from llm_config import is_nvidia_nim_configured, get_nvidia_nim_model
import os

# Get NVIDIA API config
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = get_nvidia_nim_model() if hasattr(__builtins__, 'get_nvidia_nim_model') else "deepseek-ai/deepseek-r1"


class CategoryType(Enum):
    """AXA Strategic Categories"""
    AGENTIC_PLATFORM = "agentic_platform"
    AGENTIC_SOLUTIONS = "agentic_solutions"
    WORKFLOW_AUTOMATION = "workflow_automation"
    SALES_TRAINING = "sales_training"
    INSURANCE_GENERAL = "insurance"
    UNDERWRITING_TRIAGE = "underwriting"
    CLAIMS_RECOVERY = "claims"
    CODING_AUTOMATION = "coding"
    HEALTH_WELLNESS = "health"
    AI_EVALS = "ai_evals"
    LLM_OBSERVABILITY = "llm_observability"
    CONTACT_CENTER = "contact_center"


CATEGORY_KEYWORDS = {
    CategoryType.AGENTIC_PLATFORM: ["agent orchestration", "multi-agent", "vector database", "RAG", "LangChain"],
    CategoryType.AGENTIC_SOLUTIONS: ["AI agent", "autonomous", "intelligent assistant", "virtual agent"],
    CategoryType.WORKFLOW_AUTOMATION: ["workflow automation", "RPA", "process automation", "BPA"],
    CategoryType.SALES_TRAINING: ["sales coaching", "sales training", "sales enablement"],
    CategoryType.INSURANCE_GENERAL: ["insurance", "insurtech", "policy", "claims management"],
    CategoryType.UNDERWRITING_TRIAGE: ["underwriting", "risk scoring", "triage", "STP"],
    CategoryType.CLAIMS_RECOVERY: ["claims automation", "FNOL", "fraud detection", "subrogation"],
    CategoryType.CODING_AUTOMATION: ["code generation", "AI coding", "copilot", "test automation"],
    CategoryType.HEALTH_WELLNESS: ["digital health", "telemedicine", "wellness", "health benefits"],
    CategoryType.AI_EVALS: ["AI evaluation", "LLM testing", "model evaluation"],
    CategoryType.LLM_OBSERVABILITY: ["LLM monitoring", "observability", "LLMOps"],
    CategoryType.CONTACT_CENTER: ["contact center", "call center", "customer service AI"]
}


@dataclass
class CategoryMatch:
    category: str
    matches: bool
    confidence: int
    reasoning: str


@dataclass
class StartupEvaluation:
    startup_id: int
    startup_name: str
    evaluation_date: str
    categories_matched: List[CategoryMatch]
    overall_score: float
    priority_tier: str
    axa_fit_summary: str


class UltraFastEvaluator:
    """Ultra-optimized evaluator with async + concurrent processing"""
    
    def __init__(self, workers: int = 10, batch_size: int = 3):
        self.workers = workers  # Concurrent LLM calls
        self.batch_size = batch_size  # Startups per LLM call
        self.db = SessionLocal()
        self.checkpoint_file = Path("downloads/axa_evaluation_checkpoint.json")
        self.evaluated_ids = set()
        self.session = None
        
        if not NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not configured!")
        
        logger.info(f"✓ Ultra-Fast Mode: {workers} workers × {batch_size} startups/batch")
        logger.info(f"✓ Theoretical max: {workers * batch_size * 60 / 5} startups/minute")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.evaluated_ids = set(data.get('evaluated_ids', []))
                logger.info(f"✓ Checkpoint: {len(self.evaluated_ids)} already evaluated")
                return data
        return {'evaluated_ids': [], 'results': []}
    
    def _save_checkpoint(self, results: List[Dict[str, Any]]):
        """Save checkpoint"""
        checkpoint_data = {
            'evaluated_ids': list(self.evaluated_ids),
            'results': results,
            'last_updated': datetime.now().isoformat(),
            'total_evaluated': len(self.evaluated_ids)
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _should_evaluate(self, startup: Startup) -> bool:
        """Aggressive pre-filtering - skip obvious non-matches"""
        
        # Skip if no description
        if not startup.company_description and not startup.shortDescription:
            return False
        
        text = f"{startup.company_description or ''} {startup.shortDescription or ''} {startup.primary_industry or ''}".lower()
        industry = (startup.primary_industry or '').lower()
        
        # EXCLUDE these industries completely
        excluded_industries = ['gaming', 'game', 'entertainment', 'food', 'restaurant', 
                              'hospitality', 'dating', 'fashion', 'beauty', 'cosmetics',
                              'luxury', 'jewelry', 'travel', 'tourism', 'event']
        
        for excl in excluded_industries:
            if excl in industry or excl in text[:100]:
                return False
        
        # INCLUDE if matches any relevant keywords
        relevant_keywords = [
            'ai', 'insurance', 'health', 'enterprise', 'software', 'automation',
            'agent', 'workflow', 'saas', 'platform', 'analytics', 'data',
            'fintech', 'insurtech', 'healthtech', 'developer', 'code',
            'claims', 'underwriting', 'policy', 'risk', 'medical'
        ]
        
        for keyword in relevant_keywords:
            if keyword in text[:300]:
                return True
        
        # If no matches and generic, skip
        if 'b2c' in str(startup.business_types).lower() and 'b2b' not in str(startup.business_types).lower():
            return False
        
        return True  # Default: evaluate
    
    def _get_relevant_categories(self, startup: Startup) -> List[CategoryType]:
        """Smart category selection"""
        text = f"{startup.company_description or ''} {startup.shortDescription or ''} {startup.primary_industry or ''}".lower()
        industry = (startup.primary_industry or '').lower()
        
        relevant = []
        
        # Industry-based
        if 'ai' in industry or 'ai' in text[:200]:
            relevant.extend([CategoryType.AGENTIC_PLATFORM, CategoryType.AGENTIC_SOLUTIONS, 
                           CategoryType.WORKFLOW_AUTOMATION, CategoryType.LLM_OBSERVABILITY, CategoryType.AI_EVALS])
        
        if 'insurance' in text or 'insurtech' in text:
            relevant.extend([CategoryType.INSURANCE_GENERAL, CategoryType.UNDERWRITING_TRIAGE, CategoryType.CLAIMS_RECOVERY])
        
        if 'health' in industry or 'health' in text or 'medical' in text:
            relevant.append(CategoryType.HEALTH_WELLNESS)
        
        if 'enterprise' in industry or 'software' in industry:
            relevant.extend([CategoryType.WORKFLOW_AUTOMATION, CategoryType.CONTACT_CENTER])
        
        if any(x in text for x in ['developer', 'code', 'coding', 'devops']):
            relevant.append(CategoryType.CODING_AUTOMATION)
        
        if any(x in text for x in ['sales', 'crm']):
            relevant.append(CategoryType.SALES_TRAINING)
        
        # Deduplicate
        return list(set(relevant)) if relevant else [CategoryType.AGENTIC_SOLUTIONS, CategoryType.WORKFLOW_AUTOMATION]
    
    def _build_multi_startup_prompt(self, startups: List[Startup]) -> str:
        """Build prompt for evaluating MULTIPLE startups at once"""
        
        startup_blocks = []
        for i, startup in enumerate(startups, 1):
            cats = self._get_relevant_categories(startup)
            cat_names = [c.value for c in cats]
            
            startup_blocks.append(f"""
STARTUP {i}: {startup.company_name}
Industry: {startup.primary_industry or 'Unknown'}
Business: {startup.business_types or 'Unknown'}
Description: {(startup.company_description or startup.shortDescription or 'No description')[:400]}
Categories to evaluate: {', '.join(cat_names)}
""")
        
        startups_text = "\n---\n".join(startup_blocks)
        
        prompt = f"""You are evaluating {len(startups)} startups for AXA (insurance company).

For EACH startup, evaluate ONLY its listed categories and determine:
- Does it match? (yes/no)
- Confidence (0-100)
- Why? (one brief sentence)

{startups_text}

Respond with a JSON array with one object per startup:
[
  {{
    "startup_name": "Name",
    "evaluations": [
      {{"category": "cat_name", "matches": true/false, "confidence": 0-100, "reasoning": "brief reason"}},
      ...
    ]
  }},
  ...
]

Be strict: Only match if clear B2B/enterprise alignment exists.
IMPORTANT: Respond with ONLY the JSON array."""

        return prompt
    
    async def _call_llm_async(self, prompt: str, session: aiohttp.ClientSession, retry: int = 3) -> Optional[str]:
        """Async LLM API call with retry logic"""
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 3000
        }
        
        for attempt in range(retry):
            try:
                async with session.post(
                    f"{NVIDIA_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.warning(f"API error {response.status}, attempt {attempt+1}/{retry}")
                        if attempt < retry - 1:
                            await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"LLM call error: {e}, attempt {attempt+1}/{retry}")
                if attempt < retry - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def _evaluate_startup_batch_async(
        self,
        startups: List[Startup],
        session: aiohttp.ClientSession
    ) -> List[StartupEvaluation]:
        """Evaluate a batch of startups in one LLM call"""
        
        try:
            prompt = self._build_multi_startup_prompt(startups)
            response_text = await self._call_llm_async(prompt, session)
            
            if not response_text:
                logger.error(f"Failed to evaluate batch of {len(startups)} startups")
                return []
            
            # Parse JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                results = json.loads(json_str)
            else:
                results = json.loads(response_text)
            
            # Convert to StartupEvaluation objects
            evaluations = []
            for startup, result in zip(startups, results):
                category_matches = []
                for eval_data in result.get('evaluations', []):
                    category_matches.append(CategoryMatch(
                        category=eval_data['category'],
                        matches=eval_data['matches'],
                        confidence=eval_data['confidence'],
                        reasoning=eval_data['reasoning']
                    ))
                
                matched = [m for m in category_matches if m.matches]
                overall_score = sum(m.confidence for m in matched) / len(matched) if matched else 0
                
                if overall_score >= 75 and len(matched) >= 2:
                    tier = "Tier 1: Critical Priority"
                elif overall_score >= 60 or len(matched) >= 2:
                    tier = "Tier 2: High Priority"
                elif overall_score >= 40 or len(matched) >= 1:
                    tier = "Tier 3: Medium Priority"
                else:
                    tier = "Tier 4: Low Priority"
                
                summary = f"Matches {len(matched)} categories. Score: {overall_score:.0f}%." if matched else "No matches."
                
                evaluations.append(StartupEvaluation(
                    startup_id=startup.id,
                    startup_name=startup.company_name,
                    evaluation_date=datetime.now().isoformat(),
                    categories_matched=category_matches,
                    overall_score=overall_score,
                    priority_tier=tier,
                    axa_fit_summary=summary
                ))
            
            return evaluations
            
        except Exception as e:
            logger.error(f"Batch evaluation error: {e}")
            return []
    
    async def _worker(
        self,
        queue: asyncio.Queue,
        session: aiohttp.ClientSession,
        results_list: List[Dict],
        worker_id: int
    ):
        """Async worker that processes startup batches from queue"""
        
        while True:
            try:
                batch = await queue.get()
                if batch is None:  # Poison pill
                    break
                
                evaluations = await self._evaluate_startup_batch_async(batch, session)
                
                for eval in evaluations:
                    eval_dict = asdict(eval)
                    results_list.append(eval_dict)
                    self.evaluated_ids.add(eval.startup_id)
                
                logger.info(f"Worker {worker_id}: Completed batch of {len(batch)} startups ({len(self.evaluated_ids)} total)")
                
                queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                queue.task_done()
    
    async def evaluate_all_async(
        self,
        resume: bool = False,
        max_startups: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Async evaluation with concurrent workers"""
        
        # Load checkpoint
        checkpoint_data = {'results': []}
        if resume:
            checkpoint_data = self._load_checkpoint()
        
        results = checkpoint_data.get('results', [])
        
        # Get startups
        all_startups = self.db.query(Startup).all()
        logger.info(f"📊 Total startups in DB: {len(all_startups)}")
        
        # Pre-filter
        filtered_startups = [s for s in all_startups if self._should_evaluate(s) and s.id not in self.evaluated_ids]
        logger.info(f"📊 After pre-filtering: {len(filtered_startups)} startups to evaluate")
        logger.info(f"📊 Skipped {len(all_startups) - len(filtered_startups)} irrelevant startups")
        
        if max_startups:
            filtered_startups = filtered_startups[:max_startups]
        
        # Create batches
        batches = []
        for i in range(0, len(filtered_startups), self.batch_size):
            batches.append(filtered_startups[i:i+self.batch_size])
        
        logger.info(f"🚀 Starting evaluation: {len(batches)} batches with {self.workers} workers")
        logger.info(f"⚡ Estimated time: {len(batches) / self.workers / 12:.1f} minutes")
        
        start_time = datetime.now()
        
        # Create queue and workers
        queue = asyncio.Queue()
        for batch in batches:
            await queue.put(batch)
        
        # Add poison pills
        for _ in range(self.workers):
            await queue.put(None)
        
        # Create HTTP session
        connector = aiohttp.TCPConnector(limit=self.workers * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Start workers
            workers = [
                asyncio.create_task(self._worker(queue, session, results, i))
                for i in range(self.workers)
            ]
            
            # Wait for completion
            await asyncio.gather(*workers)
        
        # Save final checkpoint
        self._save_checkpoint(results)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = len(self.evaluated_ids) / elapsed * 60
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Evaluation Complete!")
        logger.info(f"⏱️  Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
        logger.info(f"📊 Evaluated: {len(self.evaluated_ids)} startups")
        logger.info(f"⚡ Rate: {rate:.1f} startups/minute")
        logger.info(f"{'='*60}")
        
        return results
    
    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='Ultra-Fast AXA Evaluator')
    parser.add_argument('--workers', type=int, default=10, help='Concurrent workers (default: 10)')
    parser.add_argument('--batch-size', type=int, default=3, help='Startups per LLM call (default: 3)')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--max-startups', type=int, help='Limit startups (for testing)')
    parser.add_argument('--output', type=str, default='downloads/axa_evaluation_results.json')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🚀 AXA ULTRA-FAST EVALUATOR")
    print("="*80)
    
    evaluator = UltraFastEvaluator(workers=args.workers, batch_size=args.batch_size)
    
    try:
        # Run async evaluation
        results = asyncio.run(evaluator.evaluate_all_async(
            resume=args.resume,
            max_startups=args.max_startups
        ))
        
        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to: {output_path}")
        
    finally:
        evaluator.close()


if __name__ == '__main__':
    main()
