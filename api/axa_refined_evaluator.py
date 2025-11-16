#!/usr/bin/env python3
"""
AXA REFINED Startup Evaluator - STRICT PROVIDER ASSESSMENT

Key Improvements:
1. STRICT provider assessment - must sell TO enterprises as provider
2. ONE primary rule focus (not multiple)
3. Core value proposition alignment
4. Maturity scoring included (60% fit + 40% maturity)
5. Insurance expert perspective
6. Venture clienting analysis

Usage:
    python3 api/axa_refined_evaluator.py --test 10
    python3 api/axa_refined_evaluator.py --full
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import aiohttp
import os
from datetime import datetime

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
from llm_config import get_nvidia_nim_model

# Get NVIDIA API config
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = get_nvidia_nim_model()

# Maturity scoring configuration
FUNDING_STAGE_SCORES = {
    'series_d': 100, 'series_c': 95, 'series_b': 85, 'series_a': 70,
    'seed': 50, 'pre_seed': 30, 'angel': 25, 'grant': 20,
    'bootstrapped': 40, 'unknown': 35
}

EMPLOYEE_BRACKETS = [
    (1000, 100), (500, 95), (250, 90), (100, 85), (50, 75),
    (25, 65), (10, 50), (5, 35), (1, 20)
]

FUNDING_BRACKETS = [
    (100, 100), (50, 95), (25, 90), (10, 85), (5, 75),
    (2, 65), (1, 50), (0.5, 40), (0.1, 25), (0, 10)
]

AGE_BRACKETS = [
    (15, 100), (10, 95), (7, 85), (5, 75), (3, 65),
    (2, 50), (1, 35), (0, 20)
]

GROWTH_STAGES = {
    'hypergrowth': 100, 'growth': 85, 'established': 70,
    'emerging': 50, 'startup': 35, 'unknown': 40
}


# STRICT evaluation prompt
EVALUATION_PROMPT = """You are an insurance industry expert evaluating startups for AXA, a global insurance company, for SLUSH 2025 meetings.

CRITICAL: This is a VENTURE CLIENTING analysis. AXA wants to USE these startups as PROVIDERS/VENDORS.

STARTUP INFORMATION:
Name: {company_name}
Description: {description}
Industry: {industry}
Funding: ${funding}M at {funding_stage}
Employees: {employees}
Founded: {founded_year}
Website: {website}

YOUR TASK:
1. Determine if AXA can USE this startup as a PROVIDER (buy their solution/service)
2. Identify ONE primary rule that matches their CORE VALUE PROPOSITION
3. Assess specific categories within that rule
4. Explain venture clienting opportunity

AXA'S 5 RULES (Choose ONE primary):

**RULE 1: AGENTIC PLATFORM ENABLERS** (Infrastructure for building agents)
- Only if they SELL platform tools (not consulting)
- Examples: LangSmith, Pinecone, Arize, CrewAI
- Categories: F1.1_observability, F1.2_orchestration, F1.3_llm_ops, F1.4_frameworks, F1.5_data_infrastructure, F1.6_testing

**RULE 2: AGENTIC SERVICE PROVIDERS** (Ready-made enterprise solutions)
- Must SELL to enterprises (not just consulting)
- NOT insurance-specific (that's Rule 3)
- Examples: Intercom (support), Gong (sales), Jasper (marketing)
- Categories: F2.1_marketing, F2.2_sales, F2.3_support, F2.4_hr, F2.5_finance, F2.6_analytics, F2.7_workflow

**RULE 3: INSURANCE-SPECIFIC SOLUTIONS**
- MUST be for insurance companies
- Examples: Tractable (claims), Shift Technology (fraud), Zelros (underwriting)
- Categories: F3.1_claims, F3.2_underwriting, F3.3_policy, F3.4_distribution, F3.5_customer_experience, F3.6_compliance

**RULE 4: HEALTH INNOVATIONS** (For health/life insurance)
- Health tech applicable to insurance
- Examples: Komodo Health, Omada Health, Lyra Health
- Categories: F4.1_health_analytics, F4.2_wellness, F4.3_monitoring, F4.4_telemedicine, F4.5_fraud

**RULE 5: DEVELOPMENT & LEGACY MODERNIZATION**
- Dev tools, testing, migration, DevOps
- Examples: GitHub Copilot, Harness, Heirloom (mainframe)
- Categories: F5.1_coding, F5.2_testing, F5.3_migration, F5.4_integration, F5.5_intelligence, F5.6_devops

STRICT EXCLUSIONS:
❌ Consulting firms (not providers)
❌ Agencies (not product companies)
❌ Insurance carriers (competitors)
❌ Banking/fintech NOT applicable to insurance (e.g., debt collections for banks)
❌ Generic B2C apps
❌ Companies targeting wrong industry

RESPOND IN JSON:
{{
  "can_use_as_provider": true/false,
  "provider_reasoning": "Clear explanation of why they can/cannot be used as provider by AXA",
  "primary_rule": "Rule 1/2/3/4/5 or null",
  "primary_rule_name": "Platform Enablers/Service Providers/Insurance/Health/Dev",
  "rule_confidence": 0-100,
  "matched_categories": [
    {{
      "category": "F1.1_observability",
      "matches": true/false,
      "confidence": 0-100,
      "reasoning": "Why this category matches/doesn't match"
    }}
  ],
  "axa_fit_summary": "2-3 sentence summary from insurance perspective",
  "business_leverage": "Specific ways AXA can use this startup (be concrete)",
  "venture_clienting_analysis": {{
    "use_case": "Primary use case for AXA",
    "integration_complexity": "low/medium/high",
    "expected_value": "Cost savings, efficiency, innovation, etc.",
    "timeline": "Immediate/6-12 months/12+ months"
  }},
  "overall_fit_score": 0-100
}}

IMPORTANT:
- If not a provider (consultant, agency, wrong industry) → can_use_as_provider: false, overall_fit_score: 0
- If banking/fintech but NOT insurance-applicable → can_use_as_provider: false
- Choose ONE primary rule that matches CORE business
- Be strict: must be real provider/vendor AXA can buy from"""


def parse_employee_count(emp_str: Optional[str]) -> int:
    """Parse employee count from various formats"""
    if not emp_str:
        return 0
    emp_str = str(emp_str).strip().lower()
    if '-' in emp_str:
        try:
            return int(emp_str.split('-')[1])
        except:
            pass
    if '+' in emp_str:
        try:
            return int(emp_str.replace('+', ''))
        except:
            pass
    try:
        return int(emp_str)
    except:
        return 0


def score_bracket(value: float, brackets: list) -> int:
    """Score value against bracket thresholds"""
    if value <= 0:
        return brackets[-1][1]
    for threshold, score in brackets:
        if value >= threshold:
            return score
    return brackets[-1][1]


def score_funding_stage(stage: Optional[str]) -> int:
    """Score funding stage"""
    if not stage:
        return FUNDING_STAGE_SCORES['unknown']
    stage_lower = str(stage).lower().replace(' ', '_')
    for key, score in FUNDING_STAGE_SCORES.items():
        if key in stage_lower:
            return score
    return FUNDING_STAGE_SCORES['unknown']


def calculate_maturity_score(startup: Startup) -> Tuple[float, Dict]:
    """Calculate maturity score from startup data"""
    
    # Parse components
    emp_count = parse_employee_count(startup.employees)
    current_year = datetime.now().year
    age = current_year - startup.founding_year if startup.founding_year else 0
    
    # Score individual components
    funding_stage_score = score_funding_stage(startup.funding_stage)
    funding_amount_score = score_bracket(startup.total_funding or 0, FUNDING_BRACKETS)
    team_score = score_bracket(emp_count, EMPLOYEE_BRACKETS)
    age_score = score_bracket(age, AGE_BRACKETS)
    
    # Revenue scoring
    if startup.latest_revenue_min or startup.latest_revenue_max:
        revenue = ((startup.latest_revenue_min or 0) + (startup.latest_revenue_max or 0)) / 2
        rev_millions = revenue / 1_000_000 if revenue > 1_000_000 else revenue
        if rev_millions >= 100:
            revenue_score = 100
        elif rev_millions >= 50:
            revenue_score = 95
        elif rev_millions >= 25:
            revenue_score = 90
        elif rev_millions >= 10:
            revenue_score = 85
        elif rev_millions >= 5:
            revenue_score = 75
        elif rev_millions >= 1:
            revenue_score = 60
        else:
            revenue_score = 45
    else:
        revenue_score = 40
    
    # Determine growth stage
    total_funding = startup.total_funding or 0
    if (total_funding >= 50) or emp_count >= 250:
        growth_stage = 'hypergrowth'
    elif (total_funding >= 10) or emp_count >= 50:
        growth_stage = 'growth'
    elif age >= 10 or emp_count >= 100:
        growth_stage = 'established'
    elif age >= 2 and age < 5:
        growth_stage = 'emerging'
    elif age < 2:
        growth_stage = 'startup'
    else:
        growth_stage = 'unknown'
    
    growth_score = GROWTH_STAGES[growth_stage]
    
    # Weighted maturity score
    maturity_score = (
        funding_stage_score * 0.25 +
        funding_amount_score * 0.20 +
        revenue_score * 0.20 +
        team_score * 0.15 +
        age_score * 0.10 +
        growth_score * 0.10
    )
    
    maturity_details = {
        'maturity_score': round(maturity_score, 2),
        'growth_stage': growth_stage,
        'components': {
            'funding_stage': {'value': startup.funding_stage, 'score': funding_stage_score},
            'funding_amount': {'value': total_funding, 'score': funding_amount_score},
            'revenue': {'score': revenue_score},
            'team_size': {'value': startup.employees, 'parsed': emp_count, 'score': team_score},
            'company_age': {'founding_year': startup.founding_year, 'age': age, 'score': age_score},
            'growth_stage': {'stage': growth_stage, 'score': growth_score}
        }
    }
    
    return maturity_score, maturity_details


async def evaluate_startup_with_llm(
    session: aiohttp.ClientSession,
    startup: Startup,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """Evaluate a single startup using LLM"""
    
    async with semaphore:
        try:
            # Prepare startup info
            description = (startup.company_description or startup.description or 
                         startup.shortDescription or "No description available")
            
            prompt = EVALUATION_PROMPT.format(
                company_name=startup.company_name,
                description=description,
                industry=startup.primary_industry or "Not specified",
                funding=startup.total_funding or 0,
                funding_stage=startup.funding_stage or "Unknown",
                employees=startup.employees or "Not specified",
                founded_year=startup.founding_year or "Unknown",
                website=startup.website or "Not available"
            )
            
            # Call NVIDIA NIM API
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": NVIDIA_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an insurance industry expert evaluating startups for venture clienting opportunities."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            async with session.post(
                f"{NVIDIA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    logger.error(f"API error for {startup.company_name}: {response.status}")
                    return None
                
                result = await response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON from response
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                evaluation = json.loads(content.strip())
                
                # Calculate maturity score
                maturity_score, maturity_details = calculate_maturity_score(startup)
                
                # Combine scores: 60% fit + 40% maturity
                fit_score = evaluation.get('overall_fit_score', 0)
                
                # If not a provider, heavily penalize
                if not evaluation.get('can_use_as_provider', False):
                    combined_score = fit_score * 0.3 + maturity_score * 0.2  # Max 50%
                else:
                    combined_score = fit_score * 0.60 + maturity_score * 0.40
                
                # Determine tier
                if combined_score >= 80:
                    tier = "Tier 1: Critical Priority"
                elif combined_score >= 65:
                    tier = "Tier 2: High Priority"
                elif combined_score >= 45:
                    tier = "Tier 3: Medium Priority"
                else:
                    tier = "Tier 4: Low Priority"
                
                # Build result
                result_data = {
                    'startup_id': startup.id,
                    'startup_name': startup.company_name,
                    'evaluation_date': datetime.utcnow().isoformat(),
                    
                    # LLM evaluation
                    'can_use_as_provider': evaluation.get('can_use_as_provider', False),
                    'provider_reasoning': evaluation.get('provider_reasoning', ''),
                    'primary_rule': evaluation.get('primary_rule'),
                    'primary_rule_name': evaluation.get('primary_rule_name'),
                    'rule_confidence': evaluation.get('rule_confidence', 0),
                    'matched_categories': evaluation.get('matched_categories', []),
                    'axa_fit_summary': evaluation.get('axa_fit_summary', ''),
                    'business_leverage': evaluation.get('business_leverage', ''),
                    'venture_clienting_analysis': evaluation.get('venture_clienting_analysis', {}),
                    'fit_score': fit_score,
                    
                    # Maturity scoring
                    'maturity_analysis': maturity_details,
                    
                    # Combined scoring
                    'overall_score': round(combined_score, 2),
                    'priority_tier': tier,
                    
                    # Metadata
                    'funding': startup.total_funding,
                    'funding_stage': startup.funding_stage,
                    'employees': startup.employees,
                    'founded': startup.founding_year
                }
                
                logger.info(f"✓ {startup.company_name}: {tier} (Score: {combined_score:.1f}, Provider: {evaluation.get('can_use_as_provider')})")
                
                return result_data
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {startup.company_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error evaluating {startup.company_name}: {e}")
            return None


async def process_batch(
    startups: List[Startup],
    batch_size: int = 5,
    max_workers: int = 10
) -> List[Dict]:
    """Process startups in batches"""
    
    semaphore = asyncio.Semaphore(max_workers)
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Process in batches
        for i in range(0, len(startups), batch_size):
            batch = startups[i:i + batch_size]
            logger.info(f"\n📦 Processing batch {i//batch_size + 1} ({len(batch)} startups)")
            
            tasks = [
                evaluate_startup_with_llm(session, startup, semaphore)
                for startup in batch
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend([r for r in batch_results if r is not None])
            
            # Save checkpoint after each batch
            checkpoint_path = Path("downloads/axa_refined_checkpoint.json")
            checkpoint_path.parent.mkdir(exist_ok=True)
            with open(checkpoint_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"💾 Checkpoint saved: {len(results)} evaluations")
            
            # Small delay between batches
            await asyncio.sleep(1)
    
    return results


def save_to_database(results: List[Dict]):
    """Save evaluation results to database"""
    
    db = SessionLocal()
    try:
        for result in results:
            startup = db.query(Startup).filter(Startup.id == result['startup_id']).first()
            if startup:
                # Update AXA evaluation fields
                startup.axa_evaluation_date = datetime.utcnow()
                startup.axa_overall_score = result['overall_score']
                startup.axa_priority_tier = result['priority_tier']
                startup.axa_can_use_as_provider = result['can_use_as_provider']
                startup.axa_business_leverage = result['business_leverage']
                startup.axa_fit_summary = result['axa_fit_summary']
                startup.axa_matched_rules = json.dumps([result['primary_rule']] if result['primary_rule'] else [])
                startup.axa_categories_matched = json.dumps(result['matched_categories'])
        
        db.commit()
        logger.info(f"✅ Saved {len(results)} evaluations to database")
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()


async def main():
    parser = argparse.ArgumentParser(description='AXA Refined Startup Evaluator')
    parser.add_argument('--test', type=int, help='Test with N startups')
    parser.add_argument('--full', action='store_true', help='Evaluate all startups')
    parser.add_argument('--batch-size', type=int, default=5, help='Batch size')
    parser.add_argument('--workers', type=int, default=10, help='Max concurrent workers')
    parser.add_argument('--output', default='downloads/axa_refined_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Get startups from database using raw SQL to avoid JSON parsing issues
    import sqlite3
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    
    try:
        limit_clause = f"LIMIT {args.test}" if args.test else ""
        
        cursor.execute(f'''
            SELECT 
                id, company_name, company_description, description, shortDescription,
                primary_industry, total_funding, funding_stage, employees,
                founding_year, website, latest_revenue_min, latest_revenue_max
            FROM startups
            WHERE company_name IS NOT NULL
            {limit_clause}
        ''')
        
        rows = cursor.fetchall()
        
        if args.test:
            logger.info(f"🧪 TEST MODE: Evaluating {len(rows)} startups")
        elif args.full:
            logger.info(f"🚀 FULL MODE: Evaluating {len(rows)} startups")
        else:
            logger.error("❌ Specify --test N or --full")
            return
        
        # Create minimal startup objects
        from dataclasses import dataclass
        
        @dataclass
        class MinimalStartup:
            id: int
            company_name: str
            company_description: str
            description: str
            shortDescription: str
            primary_industry: str
            total_funding: float
            funding_stage: str
            employees: str
            founding_year: int
            website: str
            latest_revenue_min: float
            latest_revenue_max: float
        
        startups = [MinimalStartup(*row) for row in rows]
        
    finally:
        conn.close()
    
    # Process evaluations
    logger.info(f"⚙️  Settings: batch_size={args.batch_size}, workers={args.workers}")
    results = await process_batch(startups, args.batch_size, args.workers)
    
    # Save final results
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\n✅ COMPLETE: {len(results)} evaluations saved to {output_path}")
    
    # Save to database
    save_to_database(results)
    
    # Print summary
    tier_counts = {}
    provider_count = sum(1 for r in results if r['can_use_as_provider'])
    
    for r in results:
        tier = r['priority_tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    print("\n" + "="*80)
    print("📊 EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Evaluated: {len(results)}")
    print(f"Viable Providers: {provider_count} ({provider_count*100/len(results):.1f}%)")
    print("\nTier Distribution:")
    for tier in sorted(tier_counts.keys()):
        count = tier_counts[tier]
        print(f"  {tier}: {count} ({count*100/len(results):.1f}%)")
    print()


if __name__ == '__main__':
    asyncio.run(main())
