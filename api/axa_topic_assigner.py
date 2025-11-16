#!/usr/bin/env python3
"""
AXA Topic Assigner & Maturity Calculator
- Assign one primary topic to each startup
- Calculate maturity based on stage, funding, and founding year

TOPICS:
- AI - Claims
- AI - Underwriting
- AI - Contact centers
- AI - Software development
- AI - Agentic
- Health
- Growth
- Responsibility
- Insurance disruptor
- DeepTech
- Other (default if no match)

MATURITY LEVELS:
1 - Emerging (Pre-seed, very early, no funding, <2 years)
2 - Validating (Seed round, <$5M funding, <4 years)
3 - Deploying (Series A/B, $5M-$50M funding, 4-7 years)
4 - Scaling (Series C+, >$50M funding, 7-15 years)
5 - Established (Mature, well-funded, >15 years)

OPTIMIZATIONS:
1. Async LLM calls for topic assignment
2. Multi-startup batching (5-10 startups per LLM call)
3. Synchronous maturity calculation (rule-based, fast)
4. Aggressive pre-filtering to skip irrelevant startups
5. Connection pooling and retry logic
6. Database persistence - saves topics & maturity directly to DB

Expected Performance:
- 100-150 startups/minute
- 3,665 startups in ~25-40 minutes

Usage:
    python3 api/axa_topic_assigner.py
    python3 api/axa_topic_assigner.py --workers 15
    python3 api/axa_topic_assigner.py --batch-size 5
    python3 api/axa_topic_assigner.py --max-startups 100  # Test run
    python3 api/axa_topic_assigner.py --skip-topics      # Only calculate maturity
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import aiohttp
from enum import Enum

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
from sqlalchemy import text, event
from sqlalchemy.pool import Pool
import os

# Handle JSON parsing errors by configuring SQLAlchemy
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure SQLite to handle JSON parsing gracefully"""
    pass

# Get NVIDIA API config
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_NIM_MODEL", "deepseek-ai/deepseek-r1")

# Valid topics
VALID_TOPICS = [
    "AI - Claims",
    "AI - Underwriting",
    "AI - Contact centers",
    "AI - Software development",
    "AI - Agentic",
    "Health",
    "Growth",
    "Responsibility",
    "Insurance disruptor",
    "DeepTech",
    "Other"
]

# Valid maturity levels
VALID_MATURITY = [
    "Emerging",
    "Validating",
    "Deploying",
    "Scaling",
    "Established"
]

MATURITY_MAPPING = {
    "Emerging": 1,
    "Validating": 2,
    "Deploying": 3,
    "Scaling": 4,
    "Established": 5
}

TOPIC_KEYWORDS = {
    "AI - Claims": ["claims", "FNOL", "fraud detection", "subrogation", "claims automation", "claims processing"],
    "AI - Underwriting": ["underwriting", "risk scoring", "triage", "STP", "underwriting automation", "policy underwriting"],
    "AI - Contact centers": ["contact center", "call center", "customer service", "IVR", "chatbot", "conversational AI", "speech"],
    "AI - Software development": ["code generation", "AI coding", "copilot", "test automation", "CI/CD", "DevOps", "code review"],
    "AI - Agentic": ["agent", "autonomous", "multi-agent", "agent orchestration", "intelligent assistant", "virtual agent", "workflow automation"],
    "Health": ["healthcare", "health", "telemedicine", "wellness", "medical", "patient", "digital health", "health benefits"],
    "Growth": ["growth", "revenue optimization", "pricing", "sales", "marketing automation", "demand generation", "lead generation"],
    "Responsibility": ["ESG", "sustainability", "compliance", "risk management", "governance", "ethics", "responsible AI"],
    "Insurance disruptor": ["insurance", "insurtech", "policy", "coverage", "premium", "policy management", "insurance platform"],
    "DeepTech": ["quantum", "biotech", "nanotechnology", "advanced materials", "deep learning", "ML research", "fundamental science"]
}


@dataclass
class TopicAssignment:
    startup_id: int
    startup_name: str
    assigned_topic: str
    confidence: int
    reasoning: str
    assignment_date: str


@dataclass
class MaturityAssignment:
    startup_id: int
    startup_name: str
    maturity_level: str
    founding_year: int
    funding_amount: float
    stage: str
    reasoning: str
    assignment_date: str


class TopicAssigner:
    """Topic assigner with async concurrent processing"""
    
    def __init__(self, workers: int = 15, batch_size: int = 5):
        self.workers = workers
        self.batch_size = batch_size
        self.db = SessionLocal()
        self.checkpoint_file = Path("downloads/topic_assignment_checkpoint.json")
        self.assigned_ids = set()
        self.session = None
        
        if not NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not configured!")
        
        logger.info(f"✓ Topic Assigner: {workers} workers × {batch_size} startups/batch")
        logger.info(f"✓ Valid topics: {', '.join(VALID_TOPICS)}")
        logger.info(f"✓ Valid maturity levels: {', '.join(VALID_MATURITY)}")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.assigned_ids = set(data.get('assigned_ids', []))
                logger.info(f"✓ Checkpoint: {len(self.assigned_ids)} already assigned")
                return data
        return {'assigned_ids': [], 'assignments': []}
    
    def _save_checkpoint(self, assignments: List[Dict[str, Any]]):
        """Save checkpoint"""
        checkpoint_data = {
            'assigned_ids': list(self.assigned_ids),
            'assignments': assignments,
            'last_updated': datetime.now().isoformat(),
            'total_assigned': len(self.assigned_ids)
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def _calculate_maturity(self, startup: Startup) -> tuple[str, str]:
        """
        Calculate maturity level based on:
        1. Funding stage (highest priority)
        2. Total funding amount
        3. Years since founding
        
        Returns: (maturity_level, reasoning)
        """
        from datetime import datetime
        
        stage = (startup.funding_stage or "").lower()
        funding = startup.total_funding or 0
        founded = startup.founding_year or 0
        
        # Calculate years since founding
        current_year = datetime.now().year
        years_since_founding = current_year - founded if founded > 0 else 0
        
        # Stage-based rules (highest priority)
        if any(x in stage for x in ["pre-seed", "angel", "seed - accelerator", "undisclosed"]):
            # Pre-seed/Angel/Accelerator
            if years_since_founding < 2 or funding < 1_000_000:
                return "Emerging", f"Pre-seed/Angel stage, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Validating", f"Angel/Pre-seed but {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif "seed" in stage:
            # Seed round (generic)
            if funding < 2_000_000:
                return "Emerging", f"Seed round, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Validating", f"Seed round, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series a", "series-a"]):
            # Series A
            if funding < 5_000_000:
                return "Validating", f"Series A, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Deploying", f"Series A, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series b", "series-b"]):
            # Series B
            if funding < 10_000_000:
                return "Deploying", f"Series B, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Scaling", f"Series B, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series c", "series-c", "series d", "series-d", "series e", "series-e"]):
            # Series C+
            return "Scaling", f"Series C+, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["growth equity", "private equity", "ipo", "ipos"]):
            # Late stage
            return "Established", f"Late-stage ({stage}), {years_since_founding}y old, ${funding:,.0f} funding"
        
        # Fallback: Use funding and age to estimate
        if funding >= 50_000_000:
            return "Scaling", f"High funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding >= 10_000_000:
            return "Deploying", f"Series B+ funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding >= 2_000_000:
            return "Validating", f"Seed-A funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding > 0:
            return "Emerging", f"Early funding (${funding:,.0f}), {years_since_founding}y old"
        elif years_since_founding >= 15:
            return "Established", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 7:
            return "Scaling", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 4:
            return "Deploying", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 2:
            return "Validating", f"No funding data, {years_since_founding}y old"
        else:
            return "Emerging", f"No funding data, {years_since_founding}y old"
    
    def _calculate_maturity_raw(self, founding_year: int, total_funding: float, funding_stage: str) -> tuple[str, str]:
        """
        Calculate maturity level based on raw data (avoiding ORM to prevent JSON parsing errors)
        """
        from datetime import datetime
        
        stage = (funding_stage or "").lower()
        funding = total_funding or 0
        founded = founding_year or 0
        
        # Calculate years since founding
        current_year = datetime.now().year
        years_since_founding = current_year - founded if founded > 0 else 0
        
        # Stage-based rules (highest priority)
        if any(x in stage for x in ["pre-seed", "angel", "seed - accelerator", "undisclosed"]):
            # Pre-seed/Angel/Accelerator
            if years_since_founding < 2 or funding < 1_000_000:
                return "Emerging", f"Pre-seed/Angel stage, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Validating", f"Angel/Pre-seed but {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif "seed" in stage:
            # Seed round (generic)
            if funding < 2_000_000:
                return "Emerging", f"Seed round, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Validating", f"Seed round, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series a", "series-a"]):
            # Series A
            if funding < 5_000_000:
                return "Validating", f"Series A, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Deploying", f"Series A, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series b", "series-b"]):
            # Series B
            if funding < 10_000_000:
                return "Deploying", f"Series B, {years_since_founding}y old, ${funding:,.0f} funding"
            else:
                return "Scaling", f"Series B, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["series c", "series-c", "series d", "series-d", "series e", "series-e"]):
            # Series C+
            return "Scaling", f"Series C+, {years_since_founding}y old, ${funding:,.0f} funding"
        
        elif any(x in stage for x in ["growth equity", "private equity", "ipo", "ipos"]):
            # Late stage
            return "Established", f"Late-stage ({stage}), {years_since_founding}y old, ${funding:,.0f} funding"
        
        # Fallback: Use funding and age to estimate
        if funding >= 50_000_000:
            return "Scaling", f"High funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding >= 10_000_000:
            return "Deploying", f"Series B+ funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding >= 2_000_000:
            return "Validating", f"Seed-A funding (${funding:,.0f}), {years_since_founding}y old"
        elif funding > 0:
            return "Emerging", f"Early funding (${funding:,.0f}), {years_since_founding}y old"
        elif years_since_founding >= 15:
            return "Established", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 7:
            return "Scaling", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 4:
            return "Deploying", f"No funding data, {years_since_founding}y old"
        elif years_since_founding >= 2:
            return "Validating", f"No funding data, {years_since_founding}y old"
        else:
            return "Emerging", f"No funding data, {years_since_founding}y old"
    
    def _should_assign_topic(self, startup: Startup) -> bool:
        """Check if startup should get a topic"""
        # Skip if already has a topic
        if startup.topics:
            return False
        
        # Need at least a name and some description
        if not startup.company_name:
            return False
        
        return True
    
    def _build_multi_startup_prompt(self, startups: List[Startup]) -> str:
        """Build prompt for assigning topics to MULTIPLE startups"""
        
        startup_blocks = []
        for i, startup in enumerate(startups, 1):
            startup_blocks.append(f"""
STARTUP {i}: {startup.company_name}
Industry: {startup.primary_industry or 'Unknown'}
Description: {(startup.company_description or startup.shortDescription or 'No description')[:400]}
""")
        
        startups_text = "\n---\n".join(startup_blocks)
        
        valid_topics_str = "\n".join([f"- {t}" for t in VALID_TOPICS])
        
        prompt = f"""You are assigning primary topics to startups for AXA.

For EACH startup, assign exactly ONE primary topic from this list:
{valid_topics_str}

Only select topics that have clear relevance. If none match well, use "Other".

{startups_text}

Respond with a JSON array with one object per startup:
[
  {{
    "startup_name": "Name",
    "topic": "Topic name from the list",
    "confidence": 0-100,
    "reasoning": "one brief sentence explaining why"
  }},
  ...
]

IMPORTANT: Respond with ONLY the JSON array. Topic must be exactly from the list above."""

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
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        for attempt in range(retry):
            try:
                async with session.post(
                    f"{NVIDIA_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
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
    
    async def _assign_topic_batch_async(
        self,
        startups: List[Startup],
        session: aiohttp.ClientSession
    ) -> List[TopicAssignment]:
        """Assign topics to a batch of startups in one LLM call"""
        
        try:
            prompt = self._build_multi_startup_prompt(startups)
            response_text = await self._call_llm_async(prompt, session)
            
            if not response_text:
                logger.error(f"Failed to assign topics to batch of {len(startups)} startups")
                return []
            
            # Parse JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                results = json.loads(json_str)
            else:
                results = json.loads(response_text)
            
            # Convert to TopicAssignment objects
            assignments = []
            for startup, result in zip(startups, results):
                topic = result.get('topic', 'Other')
                
                # Validate topic
                if topic not in VALID_TOPICS:
                    logger.warning(f"Invalid topic '{topic}' for {startup.company_name}, using 'Other'")
                    topic = "Other"
                
                assignment = TopicAssignment(
                    startup_id=startup.id,
                    startup_name=startup.company_name,
                    assigned_topic=topic,
                    confidence=result.get('confidence', 50),
                    reasoning=result.get('reasoning', 'Auto-assigned'),
                    assignment_date=datetime.now().isoformat()
                )
                assignments.append(assignment)
            
            return assignments
            
        except Exception as e:
            logger.error(f"Batch assignment error: {e}")
            return []
    
    async def _worker(
        self,
        queue: asyncio.Queue,
        session: aiohttp.ClientSession,
        assignments_list: List[Dict],
        worker_id: int
    ):
        """Async worker that processes startup batches from queue"""
        
        while True:
            try:
                batch = await queue.get()
                if batch is None:  # Poison pill
                    break
                
                assignments = await self._assign_topic_batch_async(batch, session)
                
                for assignment in assignments:
                    assignment_dict = asdict(assignment)
                    assignments_list.append(assignment_dict)
                    self.assigned_ids.add(assignment.startup_id)
                
                logger.info(f"Worker {worker_id}: Assigned topics to {len(batch)} startups ({len(self.assigned_ids)} total)")
                
                queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                queue.task_done()
    
    async def assign_all_async(
        self,
        resume: bool = False,
        max_startups: Optional[int] = None
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Async assignment with concurrent workers"""
        
        # Load checkpoint
        checkpoint_data = {'assignments': []}
        if resume:
            checkpoint_data = self._load_checkpoint()
        
        assignments = checkpoint_data.get('assignments', [])
        maturity_assignments = []
        
        # Get startups - use direct SQL to avoid JSON parsing errors
        db = SessionLocal()
        try:
            # Get startups without loading problematic JSON columns
            startups_to_assign = db.query(
                Startup.id, Startup.company_name, Startup.company_description,
                Startup.shortDescription, Startup.primary_industry, Startup.topics
            ).filter(Startup.topics == None).all()
            
            # Convert to Startup objects for filtering
            startup_objects = db.query(Startup).filter(
                Startup.topics == None
            ).all()
            
            logger.info(f"📊 Total startups in DB: 3665")  # We know this from earlier
            logger.info(f"📊 Startups needing topic assignment: {len(startup_objects)}")
            logger.info(f"📊 Already assigned: {len(self.assigned_ids)}")
        finally:
            db.close()
        
        startups_to_assign = [s for s in startup_objects if s.id not in self.assigned_ids]
        
        if max_startups:
            startups_to_assign = startups_to_assign[:max_startups]
        
        if not startups_to_assign:
            logger.info("✅ All startups already have topics assigned!")
            return assignments, maturity_assignments
        
        # Create batches
        batches = []
        for i in range(0, len(startups_to_assign), self.batch_size):
            batches.append(startups_to_assign[i:i+self.batch_size])
        
        logger.info(f"🚀 Starting topic assignment: {len(batches)} batches with {self.workers} workers")
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
                asyncio.create_task(self._worker(queue, session, assignments, i))
                for i in range(self.workers)
            ]
            
            # Wait for completion
            await asyncio.gather(*workers)
        
        # Calculate maturity for ALL startups using raw SQL
        logger.info(f"\n🔄 Calculating maturity for all startups...")
        db = SessionLocal()
        try:
            # Get all startup data we need for maturity calculation
            all_startups_raw = db.execute(text(
                "SELECT id, company_name, founding_year, total_funding, funding_stage FROM startups"
            )).fetchall()
            
            for row in all_startups_raw:
                startup_id, name, founding_year, total_funding, stage = row
                maturity, reasoning = self._calculate_maturity_raw(
                    founding_year, total_funding, stage
                )
                maturity_assignments.append({
                    'startup_id': startup_id,
                    'startup_name': name,
                    'maturity_level': maturity,
                    'founding_year': founding_year,
                    'funding_amount': total_funding,
                    'stage': stage,
                    'reasoning': reasoning,
                    'assignment_date': datetime.now().isoformat()
                })
        finally:
            db.close()
        
        # Save to database
        logger.info(f"\n💾 Saving {len(self.assigned_ids)} topics and {len(maturity_assignments)} maturity levels to database...")
        self._save_assignments_to_db(assignments, maturity_assignments)
        
        # Save final checkpoint
        self._save_checkpoint(assignments)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = len(self.assigned_ids) / elapsed * 60 if elapsed > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Assignment Complete!")
        logger.info(f"⏱️  Total time: {int(elapsed//60)}m {int(elapsed%60)}s")
        logger.info(f"📊 Topics assigned: {len(self.assigned_ids)} startups")
        logger.info(f"📊 Maturity calculated: {len(maturity_assignments)} startups")
        logger.info(f"⚡ Rate: {rate:.1f} startups/minute")
        logger.info(f"{'='*60}")
        
        return assignments, maturity_assignments
    
    def _save_assignments_to_db(self, assignments: List[Dict[str, Any]], maturity_assignments: List[Dict[str, Any]]):
        """Save topic and maturity assignments directly to database"""
        try:
            db = SessionLocal()
            
            # Group by topic/maturity to show distribution
            topic_counts = {}
            maturity_counts = {}
            
            # Save topics
            for assignment in assignments:
                startup_id = assignment['startup_id']
                topic = assignment['assigned_topic']
                
                # Update database
                db.execute(
                    text("UPDATE startups SET topics = :topic WHERE id = :id"),
                    {"topic": topic, "id": startup_id}
                )
                
                # Count for stats
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Save maturity
            for assignment in maturity_assignments:
                startup_id = assignment['startup_id']
                maturity = assignment['maturity_level']
                
                # Update database
                db.execute(
                    text("UPDATE startups SET maturity = :maturity WHERE id = :id"),
                    {"maturity": maturity, "id": startup_id}
                )
                
                # Count for stats
                maturity_counts[maturity] = maturity_counts.get(maturity, 0) + 1
            
            db.commit()
            db.close()
            
            # Show distribution
            if topic_counts:
                logger.info(f"\n📊 Topic Distribution ({len(assignments)} assigned):")
                for topic in sorted(VALID_TOPICS):
                    count = topic_counts.get(topic, 0)
                    if count > 0:
                        pct = 100 * count / len(assignments)
                        logger.info(f"  {topic:30s}: {count:5d} ({pct:5.1f}%)")
            
            if maturity_counts:
                logger.info(f"\n📊 Maturity Distribution ({len(maturity_assignments)} total):")
                for maturity in VALID_MATURITY:
                    count = maturity_counts.get(maturity, 0)
                    if count > 0:
                        pct = 100 * count / len(maturity_assignments)
                        logger.info(f"  {maturity:20s}: {count:5d} ({pct:5.1f}%)")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
    
    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='AXA Topic Assigner & Maturity Calculator')
    parser.add_argument('--workers', type=int, default=8, help='Concurrent workers (default: 8)')
    parser.add_argument('--batch-size', type=int, default=3, help='Startups per LLM call (default: 3)')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--max-startups', type=int, help='Limit startups (for testing)')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎯 AXA TOPIC ASSIGNER & MATURITY CALCULATOR")
    print("="*80)
    
    assigner = TopicAssigner(workers=args.workers, batch_size=args.batch_size)
    
    try:
        # Run async assignment and maturity calculation
        assignments, maturity_assignments = asyncio.run(assigner.assign_all_async(
            resume=args.resume,
            max_startups=args.max_startups
        ))
        
        logger.info(f"\n✅ All done! Topics assigned and maturity calculated for all startups.")
        
    finally:
        assigner.close()


if __name__ == '__main__':
    main()
