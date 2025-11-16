#!/usr/bin/env python3
"""
AXA Enhanced Startup Evaluator - Simplified & Streamlined

Evaluates startups across 11 strategic topics:
- AI - Agentic, Software Development, Claims, Underwriting, Contact Centers
- Health, Growth, Responsibility, Insurance Disruptor, DeepTech, Other

Usage:
    python3 evaluator/axa_enhanced_evaluator.py --max-startups 10
    python3 evaluator/axa_enhanced_evaluator.py --workers 15 --batch-size 3
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
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

from database import SessionLocal
from models_startup import Startup
from llm_config import get_nvidia_nim_model
import os

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = get_nvidia_nim_model()


class UseCase(Enum):
    """AXA Use Cases organized by topic"""
    
    # AI - Agentic
    OBSERVABILITY = "Observability & Monitoring"
    ORCHESTRATION = "Agent Orchestration"
    LLM_OPS = "LLM Operations"
    FRAMEWORKS = "Agent Frameworks"
    DATA_INFRA = "Data Infrastructure"
    AGENT_TESTING = "Agent Testing"
    
    # AI - Software Development
    CODING = "Code Development"
    AUTO_TESTING = "Automated Testing"
    MIGRATION = "Legacy Migration"
    INTEGRATION = "System Integration"
    CODE_INTEL = "Code Intelligence"
    DEVOPS = "DevOps & CI/CD"
    
    # AI - Claims
    CLAIMS = "Claims Management"
    CLAIMS_FRAUD = "Claims Fraud Detection"
    
    # AI - Underwriting
    UNDERWRITING = "Underwriting & Risk Assessment"
    
    # AI - Contact Centers
    SUPPORT = "Customer Support Automation"
    CUSTOMER_EXP = "Digital Customer Experience"
    
    # Health
    HEALTH_ANALYTICS = "Health Data & Analytics"
    WELLNESS = "Wellness & Prevention"
    MONITORING = "Remote Monitoring & Wearables"
    TELEMEDICINE = "Telemedicine & Virtual Care"
    HEALTH_FRAUD = "Healthcare Fraud Detection"
    MENTAL_HEALTH = "Mental Health"
    
    # Growth
    MARKETING = "Marketing Automation"
    SALES = "Sales Enablement"
    ANALYTICS = "Data Analytics & BI"
    
    # Responsibility
    COMPLIANCE = "Compliance & Regulatory"
    INSURANCE_FRAUD = "Insurance Fraud Detection"
    
    # Insurance Disruptor
    POLICY = "Policy Administration"
    DISTRIBUTION = "Distribution & Agency Solutions"
    
    # DeepTech
    ADVANCED_AI = "Advanced AI & ML"
    EMERGING_TECH = "Emerging Technologies"
    
    # Other
    HR = "HR & Recruiting"
    FINANCE = "Finance & Procurement"
    WORKFLOW = "Workflow Automation"


# Topic to use cases mapping (for validation)
TOPIC_USECASES = {
    "AI - Agentic": ["Observability & Monitoring", "Agent Orchestration", "LLM Operations", "Agent Frameworks", "Data Infrastructure", "Agent Testing"],
    "AI - Software Development": ["Code Development", "Automated Testing", "Legacy Migration", "System Integration", "Code Intelligence", "DevOps & CI/CD"],
    "AI - Claims": ["Claims Management", "Claims Fraud Detection"],
    "AI - Underwriting": ["Underwriting & Risk Assessment"],
    "AI - Contact Centers": ["Customer Support Automation", "Digital Customer Experience"],
    "Health": ["Health Data & Analytics", "Wellness & Prevention", "Remote Monitoring & Wearables", "Telemedicine & Virtual Care", "Healthcare Fraud Detection", "Mental Health"],
    "Growth": ["Marketing Automation", "Sales Enablement", "Data Analytics & BI"],
    "Responsibility": ["Compliance & Regulatory", "Insurance Fraud Detection"],
    "Insurance Disruptor": ["Policy Administration", "Distribution & Agency Solutions"],
    "DeepTech": ["Advanced AI & ML", "Emerging Technologies"],
    "Other": ["HR & Recruiting", "Finance & Procurement", "Workflow Automation"],
}

# Keyword mappings
KEYWORDS = {
    UseCase.OBSERVABILITY: ["llm monitoring", "agent monitoring", "langsmith", "arize", "helicone"],
    UseCase.ORCHESTRATION: ["multi-agent", "orchestration", "crewai", "autogen", "langgraph"],
    UseCase.LLM_OPS: ["llm ops", "mlops", "humanloop", "vellum"],
    UseCase.FRAMEWORKS: ["agent framework", "langchain", "llamaindex", "agent sdk"],
    UseCase.DATA_INFRA: ["vector database", "pinecone", "weaviate", "qdrant", "rag"],
    UseCase.AGENT_TESTING: ["ai evaluation", "model testing", "agent testing"],
    
    UseCase.CODING: ["copilot", "code generation", "github copilot"],
    UseCase.AUTO_TESTING: ["test automation", "qa automation", "testim"],
    UseCase.MIGRATION: ["legacy migration", "mainframe", "cobol"],
    UseCase.INTEGRATION: ["api", "integration", "middleware"],
    UseCase.CODE_INTEL: ["code intelligence", "sourcegraph"],
    UseCase.DEVOPS: ["devops", "ci/cd", "jenkins", "gitlab"],
    
    UseCase.CLAIMS: ["claims", "fnol", "tractable"],
    UseCase.CLAIMS_FRAUD: ["claims fraud", "fraud detection"],
    UseCase.UNDERWRITING: ["underwriting", "risk assessment"],
    UseCase.SUPPORT: ["customer support", "chatbot", "zendesk"],
    UseCase.CUSTOMER_EXP: ["digital insurance", "policyholder portal"],
    
    UseCase.HEALTH_ANALYTICS: ["health analytics", "medical ai"],
    UseCase.WELLNESS: ["wellness", "preventive health"],
    UseCase.MONITORING: ["remote monitoring", "wearables"],
    UseCase.TELEMEDICINE: ["telemedicine", "telehealth"],
    UseCase.HEALTH_FRAUD: ["healthcare fraud", "medical fraud"],
    UseCase.MENTAL_HEALTH: ["mental health", "behavioral health"],
    
    UseCase.MARKETING: ["marketing", "content generation"],
    UseCase.SALES: ["sales", "crm", "lead generation"],
    UseCase.ANALYTICS: ["analytics", "business intelligence"],
    UseCase.COMPLIANCE: ["compliance", "regulatory", "kyc"],
    UseCase.INSURANCE_FRAUD: ["insurance fraud"],
    UseCase.POLICY: ["policy administration"],
    UseCase.DISTRIBUTION: ["distribution", "agency"],
    UseCase.ADVANCED_AI: ["deep learning", "neural network"],
    UseCase.EMERGING_TECH: ["blockchain", "iot", "quantum"],
    UseCase.HR: ["recruiting", "hr", "talent"],
    UseCase.FINANCE: ["finance", "invoice", "procurement"],
    UseCase.WORKFLOW: ["workflow", "automation", "rpa"],
}

TOPIC_SCORES = {
    "AI - Agentic": 40,
    "AI - Software Development": 35,
    "AI - Claims": 35,
    "AI - Underwriting": 35,
    "AI - Contact Centers": 35,
    "Health": 30,
    "Growth": 35,
    "Responsibility": 35,
    "Insurance Disruptor": 35,
    "DeepTech": 30,
    "Other": 30,
}


@dataclass
class EvaluationResult:
    startup_id: int
    startup_name: str
    evaluation_date: str
    primary_topic: str
    use_cases: List[str]
    overall_score: float
    priority_tier: str
    can_use_as_provider: bool
    business_leverage: str


class EvaluatedStartup:
    """Lightweight startup wrapper for evaluation"""
    
    def __init__(self, startup: Startup):
        self.id = startup.id
        self.name = startup.company_name
        self.desc = (startup.extracted_product or startup.company_description or startup.shortDescription or "").lower()
        self.industry = (startup.primary_industry or "").lower()
        self.text = f"{self.desc} {self.industry}".lower()
        self.maturity = startup.maturity
        self.funding_stage = startup.funding_stage
        self.total_funding = startup.total_funding
        self.country = startup.company_country


class Evaluator:
    """Simplified AXA startup evaluator"""
    
    def __init__(self, workers: int = 10, batch_size: int = 3, checkpoint_interval: int = 10):
        self.workers = workers
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.db = SessionLocal()
        self.checkpoint_file = Path("downloads/axa_enhanced_checkpoint.json")
        self.evaluated_ids = set()
        
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not configured!")
        
        logger.info(f"✓ Evaluator: {workers} workers, {batch_size} batch size, checkpoint every {checkpoint_interval} batches")
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                data = json.load(f)
                self.evaluated_ids = set(data.get('evaluated_ids', []))
                logger.info(f"✓ Loaded: {len(self.evaluated_ids)} already evaluated")
                return data
        return {'evaluated_ids': [], 'results': []}
    
    def _save_checkpoint(self, results: List[Dict]):
        checkpoint = {
            'evaluated_ids': list(self.evaluated_ids),
            'results': results,
            'last_updated': datetime.now().isoformat(),
            'total_evaluated': len(self.evaluated_ids),
        }
        temp_file = self.checkpoint_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            temp_file.replace(self.checkpoint_file)
        except Exception as e:
            logger.error(f"Checkpoint save failed: {e}")
            if temp_file.exists():
                temp_file.unlink()
    
    def _should_evaluate(self, startup: EvaluatedStartup) -> bool:
        """Quick pre-filter check"""
        if not startup.text:
            return False
        
        # Exclude irrelevant industries
        excluded = ['gaming', 'entertainment', 'food', 'restaurant', 'dating', 'fashion', 'beauty']
        for excl in excluded:
            if excl in startup.industry:
                return False
        
        # Include if relevant keywords present
        relevant = ['ai', 'insurance', 'health', 'software', 'automation', 'saas', 'platform']
        return any(kw in startup.text[:300] for kw in relevant)
    
    def _get_matching_usecases(self, startup: EvaluatedStartup) -> List[str]:
        """Find relevant use cases by keyword matching"""
        matches = []
        for usecase, keywords in KEYWORDS.items():
            if any(kw in startup.text for kw in keywords):
                matches.append(usecase.value)
        return list(set(matches))[:8] if matches else [UseCase.WORKFLOW.value, UseCase.FRAMEWORKS.value]
    
    def _build_prompt(self, startups: List[EvaluatedStartup]) -> str:
        """Streamlined evaluation prompt"""
        
        startup_profiles = []
        for i, startup in enumerate(startups, 1):
            usecases = self._get_matching_usecases(startup)
            startup_profiles.append(f"""
STARTUP {i}: {startup.name}
Industry: {startup.industry or 'Unknown'}
Description: {startup.desc[:400]}
Relevant Areas: {', '.join(usecases)}
Maturity: {startup.maturity or 'Unknown'} | Funding: {startup.funding_stage or 'Unknown'}
""")
        
        startups_section = "\n".join(startup_profiles)
        
        return f"""You are an insurance industry expert. Evaluate these {len(startups)} startups for AXA.

For each startup, determine:
1. PRIMARY TOPIC (exactly one): AI - Agentic, AI - Software Development, AI - Claims, AI - Underwriting, AI - Contact Centers, Health, Growth, Responsibility, Insurance Disruptor, DeepTech, or Other
2. CORE USE CASES: Only those that are central to their primary business (2-3 max)
3. PROVIDER STATUS: Can AXA buy their core product/service as a B2B customer? (true/false)
4. BUSINESS LEVERAGE: How this benefits AXA insurance operations specifically (if true), or why not relevant (if false)

CRITICAL: Distinguish WHAT THEY SELL from what they USE internally. Classify based on revenue model, not technology stack.

Startups:
{startups_section}

Return JSON array with objects: startup_name, primary_topic, use_cases (array), overall_score (0-100), priority_tier (Tier 1-4), can_use_as_provider (bool), business_leverage (text)

Topics and valid use cases:
- AI - Agentic: Observability & Monitoring, Agent Orchestration, LLM Operations, Agent Frameworks, Data Infrastructure, Agent Testing
- AI - Software Development: Code Development, Automated Testing, Legacy Migration, System Integration, Code Intelligence, DevOps & CI/CD
- AI - Claims: Claims Management, Claims Fraud Detection
- AI - Underwriting: Underwriting & Risk Assessment
- AI - Contact Centers: Customer Support Automation, Digital Customer Experience
- Health: Health Data & Analytics, Wellness & Prevention, Remote Monitoring & Wearables, Telemedicine & Virtual Care, Healthcare Fraud Detection, Mental Health
- Growth: Marketing Automation, Sales Enablement, Data Analytics & BI
- Responsibility: Compliance & Regulatory, Insurance Fraud Detection
- Insurance Disruptor: Policy Administration, Distribution & Agency Solutions
- DeepTech: Advanced AI & ML, Emerging Technologies
- Other: HR & Recruiting, Finance & Procurement, Workflow Automation

RESPOND WITH JSON ARRAY ONLY."""
    
    async def _call_llm(self, prompt: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Call NVIDIA LLM API"""
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        for attempt in range(3):
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
                        logger.warning(f"API error {response.status}, retry {attempt+1}/3")
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"LLM error: {e}, retry {attempt+1}/3")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
        return None
    
    async def _evaluate_batch(self, startups: List[EvaluatedStartup], session: aiohttp.ClientSession) -> List[Dict]:
        """Evaluate a batch of startups"""
        try:
            prompt = self._build_prompt(startups)
            response = await self._call_llm(prompt, session)
            
            if not response:
                logger.error(f"Failed to evaluate batch of {len(startups)}")
                return []
            
            # Extract JSON
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end] if json_start >= 0 else response
            results = json.loads(json_str)
            
            # Validate and score results
            evaluated = []
            for startup, result in zip(startups, results):
                topic = result.get('primary_topic', 'Other')
                usecases = result.get('use_cases', [])
                provider = result.get('can_use_as_provider', False)
                
                # Validate and filter use cases to match topic
                if topic in TOPIC_USECASES:
                    valid_uc = set(TOPIC_USECASES[topic])
                    usecases = [uc for uc in usecases if uc in valid_uc]
                    # If no valid use cases, add a default one for the topic
                    if not usecases and valid_uc:
                        usecases = [list(valid_uc)[0]]
                else:
                    topic = 'Other'
                    usecases = [uc for uc in usecases if uc in TOPIC_USECASES.get(topic, [])]
                    if not usecases:
                        usecases = ['Workflow Automation']
                
                # Calculate score
                base = TOPIC_SCORES.get(topic, 30)
                confidence = min(100, len(usecases) * 30)
                maturity_bonus = {"Scaleup": 15, "Growth": 10, "Startup": 8}.get(startup.maturity, 0)
                
                funding_bonus = 0
                if startup.total_funding:
                    funding_bonus = min(5, max(0, (startup.total_funding / 10_000_000) * 2))
                
                geo_bonus = 10 if startup.country and startup.country.upper() in ["DE", "FR", "GB", "ES", "IT", "NL", "BE", "CH"] else 0
                
                score = base + (confidence * 0.2) + maturity_bonus + funding_bonus + geo_bonus
                score = min(100, max(0, score))
                
                if not provider:
                    score *= 0.25
                
                tier = "Tier 1: Critical" if score >= 80 else "Tier 2: High" if score >= 60 else "Tier 3: Medium" if score >= 40 else "Tier 4: Low"
                
                evaluated.append({
                    'startup_id': startup.id,
                    'startup_name': startup.name,
                    'evaluation_date': datetime.now().isoformat(),
                    'primary_topic': topic,
                    'use_cases': usecases,
                    'overall_score': score,
                    'priority_tier': tier,
                    'can_use_as_provider': provider,
                    'business_leverage': result.get('business_leverage', ''),
                })
                self.evaluated_ids.add(startup.id)
            
            return evaluated
            
        except Exception as e:
            logger.error(f"Batch evaluation error: {e}")
            return []
    
    async def _worker(self, queue: asyncio.Queue, session: aiohttp.ClientSession, results: List[Dict], worker_id: int):
        """Worker process for evaluating batches"""
        batches_processed = 0
        
        while True:
            batch = await queue.get()
            if batch is None:
                break
            
            batch_results = await self._evaluate_batch(batch, session)
            results.extend(batch_results)
            batches_processed += 1
            
            if batches_processed % self.checkpoint_interval == 0:
                self._save_checkpoint(results)
                logger.info(f"Worker {worker_id}: Saved checkpoint ({len(self.evaluated_ids)} total)")
            else:
                logger.info(f"Worker {worker_id}: Batch done ({len(self.evaluated_ids)} total)")
            
            queue.task_done()
    
    async def evaluate_all(self, resume: bool = False, max_startups: Optional[int] = None, startup_ids: Optional[List[int]] = None) -> List[Dict]:
        """Main evaluation loop"""
        
        # Load checkpoint
        checkpoint = self._load_checkpoint() if resume else {'results': []}
        results = checkpoint.get('results', [])
        
        # Get startups from DB
        try:
            if startup_ids:
                startups = self.db.query(Startup).filter(Startup.id.in_(startup_ids)).all()
            else:
                startups = self.db.query(Startup).filter(Startup.company_name.isnot(None)).all()
        except Exception as e:
            logger.error(f"Database error: {e}")
            return results
        
        logger.info(f"📊 Total: {len(startups)}")
        
        # Filter
        if not startup_ids:
            startups = [s for s in startups if self._should_evaluate(EvaluatedStartup(s)) and s.id not in self.evaluated_ids]
            logger.info(f"📊 After filter: {len(startups)}")
        
        if max_startups and not startup_ids:
            startups = startups[:max_startups]
            logger.info(f"📊 Limited to: {max_startups}")
        
        # Convert to lightweight objects and batch
        evaluated_startups = [EvaluatedStartup(s) for s in startups]
        batches = [evaluated_startups[i:i+self.batch_size] for i in range(0, len(evaluated_startups), self.batch_size)]
        
        logger.info(f"🚀 Starting: {len(batches)} batches × {self.workers} workers")
        
        # Queue setup
        queue = asyncio.Queue()
        for batch in batches:
            await queue.put(batch)
        for _ in range(self.workers):
            await queue.put(None)
        
        # Run workers
        start = datetime.now()
        connector = aiohttp.TCPConnector(limit=self.workers * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            workers = [asyncio.create_task(self._worker(queue, session, results, i)) for i in range(self.workers)]
            try:
                await asyncio.gather(*workers)
            except KeyboardInterrupt:
                logger.warning("Interrupted! Saving checkpoint...")
                self._save_checkpoint(results)
                raise
        
        self._save_checkpoint(results)
        elapsed = (datetime.now() - start).total_seconds()
        
        logger.info(f"\n{'='*60}\n✅ Complete! {int(elapsed//60)}m {int(elapsed%60)}s | {len(self.evaluated_ids)} evaluated\n{'='*60}")
        
        return results
    
    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='AXA Startup Evaluator')
    parser.add_argument('--workers', type=int, default=10, help='Concurrent workers')
    parser.add_argument('--batch-size', type=int, default=3, help='Startups per batch')
    parser.add_argument('--checkpoint-interval', type=int, default=10, help='Checkpoint interval')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--max-startups', type=int, help='Limit for testing')
    parser.add_argument('--startup-ids', type=str, help='Comma-separated startup IDs')
    parser.add_argument('--output', type=str, default='downloads/axa_enhanced_results.json')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🚀 AXA ENHANCED EVALUATOR")
    print("="*80)
    
    evaluator = Evaluator(workers=args.workers, batch_size=args.batch_size, checkpoint_interval=args.checkpoint_interval)
    
    try:
        startup_ids = None
        if args.startup_ids:
            startup_ids = [int(x.strip()) for x in args.startup_ids.split(',')]
            logger.info(f"🎯 Specific startups: {startup_ids}")
        
        results = asyncio.run(evaluator.evaluate_all(resume=args.resume, max_startups=args.max_startups, startup_ids=startup_ids))
        
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Results: {args.output}")
        
        if results:
            tiers = {}
            for r in results:
                tier = r['priority_tier'].split(':')[0]
                tiers[tier] = tiers.get(tier, 0) + 1
            
            print("\n📊 Summary:")
            for tier in sorted(tiers.keys()):
                print(f"  {tier}: {tiers[tier]}")
    
    finally:
        evaluator.close()


if __name__ == '__main__':
    main()
