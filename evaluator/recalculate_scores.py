#!/usr/bin/env python3
"""
AXA Startup Grading System (A+ to F) - LLM-Enhanced Evaluation.

This script recalculates startup grades (A+ to F) based on realistic AXA partnership criteria:
- **Scaling Platforms**: Proven multi-use case, multi-customer architecture
- **Funding & Market Fit**: Strong funding history with corporate experience  
- **European Presence**: Based in EU for data transfer compliance and proximity
- **AI/Agentic Innovation**: Core AI capabilities, especially agentic solutions
- **Enterprise Value Delivery**: Ability to solve real business problems at scale

The system uses LLM analysis of enriched startup data to synthesize a holistic grade
reflecting realistic partnership quality, implementation potential, and business value.

Only axa_overall_score is updated in the database upon completion.

Usage:
    python3 evaluator/recalculate_scores_llm.py
    python3 evaluator/recalculate_scores_llm.py --dry-run  # Preview without updating
    python3 evaluator/recalculate_scores_llm.py --verbose # Detailed LLM reasoning
    python3 evaluator/recalculate_scores_llm.py --limit 10 # Process 10 startups
"""

import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from enum import Enum
from datetime import datetime

# Add parent and api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal
from models_startup import Startup
import logging

# LLM Integration
try:
    from llm_config import llm_completion_sync, is_nvidia_nim_configured
    HAS_LLM = is_nvidia_nim_configured()
except ImportError:
    HAS_LLM = False
    logger_init = logging.getLogger(__name__)
    logger_init.warning("LLM config not available - using heuristic evaluation")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Grade(Enum):
    """AXA Partnership Grade Scale (A+ to F)"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D = "D"
    F = "F"
    
    @property
    def description(self) -> str:
        """Grade interpretation for AXA context"""
        descriptions = {
            "A+": "Exceptional Partner: Scalable platform, strong funding (>$50M), EU-based, 3+ use cases, AI leadership. Ready for deep strategic partnership.",
            "A": "Excellent Partner: Proven scaling platform, significant funding ($20M+), EU presence, 2+ use cases, strong AI. High confidence deployment.",
            "A-": "Very Good: Good scalability, solid funding ($10M+), EU-based, 2+ use cases, AI capable. Strong partnership potential.",
            "B+": "Good: Scaling/Growth stage, decent funding ($5M+), EU preferred, 1-2 use cases, AI present. Viable partnership with planning.",
            "B": "Acceptable: Growth potential, modest funding, reasonable location, focused use case. Workable if actively managed.",
            "B-": "Marginal: Early scaling, limited funding (<$5M), questionable location, limited scope. High execution risk.",
            "C+": "Basic: Early growth, minimal funding, outside EU, niche focus. Significant gaps require mitigation.",
            "C": "Limited: Pre-growth, seed funding, poor location, very limited application. Not recommended.",
            "C-": "Weak: Prototype/early, minimal funding, wrong market. Does not meet partnership threshold.",
            "D": "Poor: Very early stage, no significant funding, misaligned with AXA needs. Not suitable.",
            "F": "Not Suitable: Critical gaps in scalability, funding, location, or AI capability. Not recommended for partnership."
        }
        return descriptions.get(self.value, "Unknown")


def extract_startup_profile(startup: Startup) -> Dict:
    """Extract comprehensive startup profile for evaluation - using ALL available database fields"""
    
    # Parse use cases
    use_cases = []
    if startup.axa_use_cases:
        try:
            uc = json.loads(startup.axa_use_cases) if isinstance(startup.axa_use_cases, str) else startup.axa_use_cases
            use_cases = uc if isinstance(uc, list) else []
        except:
            pass
    
    # Parse technology tags from multiple sources
    tech_focus = []
    if startup.tech:
        try:
            tf = json.loads(startup.tech) if isinstance(startup.tech, str) else startup.tech
            tech_focus = tf if isinstance(tf, list) else []
        except:
            pass
    
    # Extract enrichment data
    enrichment_data = {}
    social_media = {}
    key_pages = {}
    if startup.enrichment:
        try:
            enrich = json.loads(startup.enrichment) if isinstance(startup.enrichment, str) else startup.enrichment
            if isinstance(enrich, dict):
                enrichment_data = enrich
                if 'tech_stack' in enrich and not tech_focus:
                    tech_focus = enrich.get('tech_stack', [])
                social_media = enrich.get('social_media', {})
                key_pages = enrich.get('key_pages', {})
        except:
            pass
    
    # Extract founding year
    founded_year = None
    if startup.founding_year:
        founded_year = startup.founding_year
    elif startup.dateFounded:
        founded_year = startup.dateFounded.year
    
    # Parse employee count as team size
    team_size = None
    if startup.employees:
        try:
            if '-' in str(startup.employees):
                parts = str(startup.employees).split('-')
                team_size = int(parts[0]) if parts else None
            else:
                team_size = int(startup.employees)
        except:
            team_size = None
    
    # Extract industries
    industries = []
    if startup.primary_industry:
        industries.append(startup.primary_industry)
    if startup.secondary_industry:
        try:
            sec = json.loads(startup.secondary_industry) if isinstance(startup.secondary_industry, str) else startup.secondary_industry
            if isinstance(sec, list):
                industries.extend(sec)
        except:
            pass
    
    # Extract business types
    business_types = []
    if startup.business_types:
        try:
            bt = json.loads(startup.business_types) if isinstance(startup.business_types, str) else startup.business_types
            business_types = bt if isinstance(bt, list) else []
        except:
            pass
    
    # Parse topics
    topics = []
    if startup.topics:
        try:
            t = json.loads(startup.topics) if isinstance(startup.topics, str) else startup.topics
            topics = t if isinstance(t, list) else []
        except:
            pass
    
    # Get value proposition data
    value_prop = {
        'statement': startup.value_proposition or '',
        'core_product': startup.core_product or '',
        'target_customers': startup.target_customers or '',
        'problem_solved': startup.problem_solved or '',
        'differentiator': startup.key_differentiator or '',
        'competitors': startup.vp_competitors or '',
        'confidence': startup.vp_confidence or 'unknown'
    }
    
    # Extract product and market info
    extracted_info = {
        'product': startup.extracted_product or '',
        'market': startup.extracted_market or '',
        'technologies': startup.extracted_technologies or '',
        'competitors': startup.extracted_competitors or ''
    }
    
    # Revenue data
    revenue_range = None
    if startup.latest_revenue_min and startup.latest_revenue_max:
        revenue_range = f"${startup.latest_revenue_min/1_000_000:.1f}M - ${startup.latest_revenue_max/1_000_000:.1f}M"
    elif startup.latest_revenue_min:
        revenue_range = f"${startup.latest_revenue_min/1_000_000:.1f}M+"
    
    profile = {
        'name': startup.company_name or 'Unknown',
        'country': startup.company_country or 'Unknown',
        'city': startup.company_city or '',
        'founded_year': founded_year,
        'company_type': startup.company_type or '',
        'maturity': startup.maturity or 'Unknown',
        'maturity_score': startup.maturity_score or 0,
        'funding_stage': startup.funding_stage or 'Unknown',
        'total_funding': startup.total_funding or 0,
        'total_equity_funding': startup.total_equity_funding or 0,
        'last_funding_date': startup.last_funding_date.strftime('%Y-%m-%d') if startup.last_funding_date else None,
        'valuation': startup.valuation or 0,
        'revenue_range': revenue_range,
        'team_size': team_size,
        'is_provider': startup.axa_can_use_as_provider or False,
        'use_cases': use_cases[:10],
        'use_case_count': len(use_cases),
        'primary_topic': startup.axa_primary_topic or 'Not specified',
        'fit_summary': startup.axa_fit_summary or '',
        'description': startup.company_description or startup.description or startup.shortDescription or '',
        'technology_focus': tech_focus,
        'business_model': startup.business_model or '',
        'pricing_model': startup.pricingModel or '',
        'tech_readiness': startup.technologyReadiness or '',
        'industries': industries,
        'business_types': business_types,
        'topics': topics,
        'value_proposition': value_prop,
        'extracted_info': extracted_info,
        'website': startup.website or '',
        'linkedin': startup.company_linked_in or '',
        'has_enrichment': startup.is_enriched or False,
        'social_media': social_media,
        'cb_insights_id': startup.cb_insights_id,
        'axa_business_leverage': startup.axa_business_leverage or ''
    }
    
    return profile


def build_evaluation_prompt(profile: Dict) -> str:
    """Build comprehensive evaluation prompt for LLM using all available data"""
    
    years_old = 2025 - (profile['founded_year'] or 2025) if profile['founded_year'] else 'Unknown'
    funding_millions = profile['total_funding'] / 1_000_000 if profile['total_funding'] else 0
    equity_millions = profile['total_equity_funding'] / 1_000_000 if profile['total_equity_funding'] else 0
    valuation_millions = profile['valuation'] / 1_000_000 if profile['valuation'] else 0
    
    prompt = f"""
You are an expert venture evaluator for AXA, a global insurance company evaluating technology startups for partnership potential.

## EVALUATION CRITERIA - AXA Partnership Grade (A+ to F)

Grade based on these critical factors (in priority order):

1. **Scaling Platform** (25% weight): Multi-use case, multi-customer platform capability
   - 3+ use cases with proven deployment = Excellent (A range)
   - 2 use cases with corporate traction = Good (B range)
   - 1 use case or niche = Limited (C-D range)
   - No clear use cases = Poor (F)

2. **Market Validation & Funding** (25% weight): Financial health and investor confidence
   - $50M+ / Series C+ / Valuation $200M+ = Exceptional (A+/A)
   - $20M+ / Series B / Strong revenue = Very Good (A-/B+)
   - $10M+ / Series A = Good (B)
   - $5M+ / Seed = Acceptable (B-/C+)
   - <$5M = Early/Risky (C-/D/F)

3. **Enterprise Deployment Experience** (20% weight): Proven corporate implementation
   - Currently serving enterprise clients = Essential for A/B grades
   - No corporate deployment = Maximum B-, likely C range

4. **Use Case Breadth & AXA Fit** (15% weight): Solves multiple AXA problems
   - Primary topic relevance + multiple use cases = Higher score
   - Clear business leverage identified = Strong indicator

5. **Geographic & Regulatory Fit** (10% weight): Data compliance
   - EU/UK = Optimal (GDPR native)
   - US/CA = Workable (transfer frameworks exist)
   - Other = Challenging (data residency issues)

6. **AI/Technology Innovation** (5% weight): Modern capabilities
   - Agentic AI / Advanced ML = Premium
   - Strong AI capability = Good
   - Traditional tech = Acceptable
   - No innovation = Concerning

## STARTUP PROFILE TO EVALUATE

### Core Information
**Company**: {profile['name']}
**Location**: {profile['city']}, {profile['country']}
**Founded**: {profile['founded_year']} ({years_old} years old)
**Type**: {profile['company_type']} | **Maturity**: {profile['maturity']} (Score: {profile['maturity_score']})
**Website**: {profile['website']}

### Financial Position & Validation
**Funding Stage**: {profile['funding_stage']}
**Total Funding**: ${funding_millions:.1f}M (Equity: ${equity_millions:.1f}M)
**Last Funding**: {profile['last_funding_date'] or 'Not disclosed'}
**Valuation**: ${valuation_millions:.1f}M
**Revenue**: {profile['revenue_range'] or 'Not disclosed'}
**Team Size**: {profile['team_size'] or 'Not disclosed'}

### AXA Fit Assessment
**Provider Status**: {'✓ YES - Deployed with corporate/enterprise clients' if profile['is_provider'] else '✗ NO - No corporate deployments yet'}
**Primary Topic**: {profile['primary_topic']}
**Identified Use Cases** ({profile['use_case_count']}): {', '.join(profile['use_cases'][:5])}{'...' if len(profile['use_cases']) > 5 else ''}
**Business Leverage**: {profile['axa_business_leverage'] or 'Not specified'}
**Fit Summary**: {profile['fit_summary']}

### Business Model & Market
**Industries**: {', '.join(profile['industries']) if profile['industries'] else 'Not specified'}
**Business Types**: {', '.join(profile['business_types']) if profile['business_types'] else 'Not specified'}
**Business Model**: {profile['business_model'] or 'Not specified'}
**Pricing Model**: {profile['pricing_model'] or 'Not specified'}
**Technology Readiness**: {profile['tech_readiness'] or 'Not specified'}

### Value Proposition
{f"**Statement**: {profile['value_proposition']['statement']}" if profile['value_proposition']['statement'] else ''}
**Core Product**: {profile['value_proposition']['core_product'] or profile['extracted_info']['product'] or 'Not specified'}
**Target Customers**: {profile['value_proposition']['target_customers'] or profile['extracted_info']['market'] or 'Not specified'}
**Problem Solved**: {profile['value_proposition']['problem_solved'] or 'Not specified'}
**Key Differentiator**: {profile['value_proposition']['differentiator'] or 'Not specified'}
**Competitors**: {profile['value_proposition']['competitors'] or profile['extracted_info']['competitors'] or 'Not specified'}

### Technology & Innovation
**Technology Focus**: {', '.join(profile['technology_focus']) if profile['technology_focus'] else profile['extracted_info']['technologies'] or 'Not specified'}
**Topics**: {', '.join(profile['topics'][:5]) if profile['topics'] else 'Not specified'}

### Company Description
{profile['description'][:500] + '...' if len(profile['description']) > 500 else profile['description']}

### Data Quality
**Enrichment Status**: {'✓ Enriched' if profile['has_enrichment'] else '✗ Not enriched'}
**CB Insights**: {'✓ Available' if profile['cb_insights_id'] else '✗ Not available'}

## YOUR TASK

Provide a realistic, critical grade (A+ to F) reflecting actual partnership viability for AXA.

**Be pragmatic and demanding:**
- A+/A grades require EXCEPTIONAL proof: $50M+, 3+ use cases, enterprise clients, EU location
- Most startups should receive B-C grades (realistic assessment)
- Early stage (<$5M) or no corporate deployment = C or below
- Missing critical data = Lower confidence, grade accordingly
- No use cases or poor AXA fit = D/F

**Consider implementation reality:**
- Can they handle AXA's scale and compliance requirements?
- Do they have the team/funding to deliver?
- What could realistically go wrong?
- Is the technology production-ready?

**Output ONLY a JSON object with this exact structure:**
{{
    "grade": "B+",
    "score": 82,
    "reasoning": "2-3 sentence critical assessment explaining the grade based on concrete evidence",
    "strengths": ["Specific strength 1", "Specific strength 2"],
    "concerns": ["Specific concern 1", "Specific concern 2"],
    "recommendation": "Clear actionable recommendation (e.g., 'Schedule POC with risk mitigation' or 'Monitor until Series B')"
}}

**Grade Scale (be realistic - most startups are B/C range):**
- A+ (95-100): Exceptional strategic priority - Series C+, $50M+, 3+ use cases, EU, enterprise proven
- A (90-94): Excellent high-confidence - Series B+, $20M+, 2+ use cases, strong traction
- A- (85-89): Very good potential - Series B, $15M+, proven use cases
- B+ (80-84): Good viable option - Series A+, $10M+, 1-2 use cases, planning needed
- B (75-79): Acceptable with risks - Series A, $5-10M, manageable execution risk
- B- (70-74): Marginal fit - Early Series A, limited funding/cases, high execution risk
- C+ (60-69): Basic/gaps - Seed stage, <$5M, significant limitations
- C (50-59): Limited viability - Early seed, minimal validation, not recommended
- C- (40-49): Weak - Pre-seed, major gaps, below partnership threshold
- D (30-39): Poor - Very early, insufficient capabilities
- F (<30): Not suitable - Critical failures in funding, location, capability, or fit

Be critical. Real partnerships require proven capability, not just potential.
"""
    
    return prompt


def evaluate_with_llm(profile: Dict, verbose: bool = False) -> Tuple[Grade, float, str]:
    """Use LLM to evaluate startup and assign grade with enhanced error handling"""
    
    if not HAS_LLM:
        logger.debug(f"LLM not available for {profile['name']}, using heuristic")
        return evaluate_heuristic(profile)
    
    try:
        prompt = build_evaluation_prompt(profile)
        
        if verbose:
            logger.debug(f"\n{'='*80}")
            logger.debug(f"LLM Evaluation Request: {profile['name']}")
            logger.debug(f"{'='*80}")
        
        # Call LLM using the configured NVIDIA NIM model
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = llm_completion_sync(
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            metadata={"startup_name": profile['name'], "evaluation_type": "grading"}
        )
        
        response_text = response.strip()
        
        if verbose:
            logger.debug(f"LLM Response:\n{response_text}\n")
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                eval_result = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response for {profile['name']}: {e}")
            if verbose:
                logger.debug(f"Problematic response: {response_text[:200]}")
            return evaluate_heuristic(profile)
        
        # Extract and validate grade and score
        grade_str = eval_result.get('grade', 'C').upper().strip()
        score = float(eval_result.get('score', 50))
        reasoning = eval_result.get('reasoning', 'LLM evaluation completed')
        strengths = eval_result.get('strengths', [])
        concerns = eval_result.get('concerns', [])
        recommendation = eval_result.get('recommendation', '')
        
        # Validate score range
        if not (0 <= score <= 100):
            logger.warning(f"Invalid score {score} for {profile['name']}, clamping to 0-100")
            score = max(0, min(100, score))
        
        # Convert to Grade enum
        try:
            # Handle grade format variations
            grade_normalized = grade_str.replace('+', '_PLUS').replace('-', '_MINUS')
            if not grade_normalized.startswith('_'):
                grade = Grade[grade_normalized]
            else:
                raise KeyError(f"Invalid grade format: {grade_str}")
        except KeyError:
            logger.warning(f"Invalid grade '{grade_str}' for {profile['name']}, using score-based grade")
            # Derive grade from score
            if score >= 95:
                grade = Grade.A_PLUS
            elif score >= 90:
                grade = Grade.A
            elif score >= 85:
                grade = Grade.A_MINUS
            elif score >= 80:
                grade = Grade.B_PLUS
            elif score >= 75:
                grade = Grade.B
            elif score >= 70:
                grade = Grade.B_MINUS
            elif score >= 60:
                grade = Grade.C_PLUS
            elif score >= 50:
                grade = Grade.C
            elif score >= 40:
                grade = Grade.C_MINUS
            elif score >= 30:
                grade = Grade.D
            else:
                grade = Grade.F
        
        # Build enhanced reasoning
        full_reasoning = reasoning
        if strengths and verbose:
            full_reasoning += f" | Strengths: {'; '.join(strengths[:2])}"
        if concerns and verbose:
            full_reasoning += f" | Concerns: {'; '.join(concerns[:2])}"
        
        if verbose:
            logger.debug(f"Final Grade: {grade.value} ({score:.1f})")
            logger.debug(f"Reasoning: {reasoning}")
            if strengths:
                logger.debug(f"Strengths: {', '.join(strengths)}")
            if concerns:
                logger.debug(f"Concerns: {', '.join(concerns)}")
            if recommendation:
                logger.debug(f"Recommendation: {recommendation}")
        
        return grade, score, full_reasoning if verbose else reasoning
        
    except Exception as e:
        logger.warning(f"LLM evaluation failed for {profile['name']}: {str(e)[:100]}")
        if verbose:
            import traceback
            logger.debug(f"Full error: {traceback.format_exc()}")
        return evaluate_heuristic(profile)


def evaluate_heuristic(profile: Dict) -> Tuple[Grade, float, str]:
    """Enhanced heuristic-based evaluation leveraging all available data"""
    
    score = 50  # Base score
    name = profile['name']
    insights = []
    
    # 1. Scaling platform assessment (20 points max)
    if profile['use_case_count'] >= 5:
        score += 20
        insights.append("Comprehensive platform (5+ use cases)")
    elif profile['use_case_count'] >= 3:
        score += 16
        insights.append(f"Multi-use case platform ({profile['use_case_count']} use cases)")
    elif profile['use_case_count'] >= 2:
        score += 11
        insights.append(f"Dual-purpose solution ({profile['use_case_count']} use cases)")
    elif profile['use_case_count'] == 1:
        score += 5
        insights.append("Single use case")
    else:
        score -= 5
        insights.append("No clear use cases")
    
    # 2. Funding & market validation (25 points max)
    funding = profile['total_funding']
    valuation = profile['valuation']
    
    if funding >= 50_000_000:
        score += 25
        insights.append(f"Exceptional funding (${funding/1_000_000:.0f}M - highly validated)")
    elif funding >= 20_000_000:
        score += 20
        insights.append(f"Strong funding (${funding/1_000_000:.0f}M)")
    elif funding >= 10_000_000:
        score += 15
        insights.append(f"Good funding (${funding/1_000_000:.0f}M)")
    elif funding >= 5_000_000:
        score += 10
        insights.append(f"Acceptable funding (${funding/1_000_000:.0f}M)")
    elif funding >= 1_000_000:
        score += 4
        insights.append(f"Early funding (${funding/1_000_000:.1f}M)")
    else:
        score -= 10
        insights.append("Minimal/no disclosed funding - very high risk")
    
    # Valuation boost
    if valuation >= 200_000_000:
        score += 5
        insights.append(f"High valuation (${valuation/1_000_000:.0f}M)")
    elif valuation >= 100_000_000:
        score += 3
    
    # 3. Enterprise deployment experience (15 points max) - CRITICAL
    if profile['is_provider']:
        score += 15
        insights.append("✓ Enterprise deployment proven")
    else:
        score -= 8
        insights.append("✗ No corporate deployment experience")
    
    # 4. Maturity & stage assessment (10 points max)
    maturity_lower = profile['maturity'].lower()
    maturity_score = profile['maturity_score']
    
    if maturity_score >= 80 or 'scaleup' in maturity_lower:
        score += 10
        insights.append("Scaling stage (proven)")
    elif maturity_score >= 60 or 'growth' in maturity_lower or 'deploying' in maturity_lower:
        score += 7
        insights.append("Growth stage")
    elif maturity_score >= 40 or 'validating' in maturity_lower:
        score += 4
        insights.append("Validation phase")
    elif maturity_score >= 20:
        score += 1
        insights.append("Early stage")
    else:
        score -= 5
        insights.append("Prototype/idea stage")
    
    # 5. Geographic & regulatory fit (10 points max)
    country = (profile['country'] or '').upper()
    eu_core = {'DE', 'FR', 'GB', 'UK', 'ES', 'IT', 'NL', 'BE', 'CH'}
    eu_extended = {'SE', 'FI', 'DK', 'NO', 'AT', 'PL', 'IE', 'PT', 'GR', 'CZ', 'RO', 'HU', 'LU'}
    
    if country in eu_core:
        score += 10
        insights.append(f"EU core ({country}) - optimal compliance")
    elif country in eu_extended:
        score += 7
        insights.append(f"EU extended ({country})")
    elif country in ['US', 'CA']:
        score += 3
        insights.append(f"North America ({country})")
    elif country in ['AU', 'NZ', 'SG', 'JP', 'KR']:
        score += 2
        insights.append(f"Developed market ({country})")
    else:
        score -= 8
        insights.append(f"Challenging location ({country}) - data transfer issues")
    
    # 6. AI/Innovation assessment (10 points max)
    fit_lower = (profile['fit_summary'] or '').lower()
    tech_lower = ' '.join(profile['technology_focus']).lower() if profile['technology_focus'] else ''
    primary_topic = (profile['primary_topic'] or '').lower()
    
    if 'agentic' in fit_lower or 'agentic' in tech_lower or 'agentic ai' in primary_topic:
        score += 10
        insights.append("Agentic AI leadership")
    elif 'topic 1' in fit_lower or 'ai' in primary_topic or 'machine learning' in tech_lower:
        score += 7
        insights.append("Strong AI capabilities")
    elif any(ai_term in tech_lower for ai_term in ['ml', 'nlp', 'computer vision', 'deep learning']):
        score += 5
        insights.append("AI/ML capability")
    elif 'automation' in primary_topic or 'workflow' in primary_topic:
        score += 3
        insights.append("Automation focus")
    
    # 7. Team size indicator (5 points max)
    if profile['team_size']:
        if profile['team_size'] >= 200:
            score += 5
            insights.append(f"Large team ({profile['team_size']}+)")
        elif profile['team_size'] >= 100:
            score += 4
            insights.append(f"Substantial team ({profile['team_size']})")
        elif profile['team_size'] >= 50:
            score += 3
            insights.append(f"Growing team ({profile['team_size']})")
        elif profile['team_size'] >= 20:
            score += 2
        elif profile['team_size'] < 10:
            score -= 3
            insights.append("Very small team")
    
    # 8. Revenue indicator (5 points max)
    if profile['revenue_range']:
        score += 5
        insights.append(f"Revenue: {profile['revenue_range']}")
    
    # 9. Value proposition clarity (bonus)
    if profile['value_proposition']['statement'] and profile['value_proposition']['confidence'] == 'high':
        score += 3
        insights.append("Clear value proposition")
    
    # 10. Data enrichment quality
    if profile['has_enrichment'] and profile['cb_insights_id']:
        score += 2
    elif not profile['has_enrichment'] and not profile['cb_insights_id']:
        score -= 3
        insights.append("Limited data availability")
    
    # 11. Business leverage clarity
    if profile['axa_business_leverage'] and len(profile['axa_business_leverage']) > 50:
        score += 2
    
    # Clamp score to 0-100
    score = max(0, min(100, score))
    
    # Assign grade based on score with realistic distribution
    if score >= 95:
        grade = Grade.A_PLUS
    elif score >= 90:
        grade = Grade.A
    elif score >= 85:
        grade = Grade.A_MINUS
    elif score >= 80:
        grade = Grade.B_PLUS
    elif score >= 75:
        grade = Grade.B
    elif score >= 70:
        grade = Grade.B_MINUS
    elif score >= 60:
        grade = Grade.C_PLUS
    elif score >= 50:
        grade = Grade.C
    elif score >= 40:
        grade = Grade.C_MINUS
    elif score >= 30:
        grade = Grade.D
    else:
        grade = Grade.F
    
    # Build reasoning from top insights
    reasoning = f"{grade.value} - " + "; ".join(insights[:4])
    
    return grade, score, reasoning


def calculate_startup_grade(startup: Startup, verbose: bool = False) -> Tuple[Grade, float, str]:
    """Calculate comprehensive startup grade using LLM analysis"""
    
    profile = extract_startup_profile(startup)
    grade, score, reasoning = evaluate_with_llm(profile, verbose=verbose)
    
    if verbose:
        logger.info(f"\n{'='*80}")
        logger.info(f"Final Evaluation: {profile['name']} ({profile['country']})")
        logger.info(f"{'='*80}")
        logger.info(f"Grade: {grade.value} | Score: {score:.1f}/100")
        logger.info(f"Reasoning: {reasoning}")
        logger.info(f"\nKey Metrics:")
        logger.info(f"  • Use Cases: {profile['use_case_count']}")
        logger.info(f"  • Funding: ${profile['total_funding']/1_000_000:.1f}M ({profile['funding_stage']})")
        logger.info(f"  • Valuation: ${profile['valuation']/1_000_000:.1f}M" if profile['valuation'] else "  • Valuation: Not disclosed")
        logger.info(f"  • Provider Status: {'✓ YES' if profile['is_provider'] else '✗ NO'}")
        logger.info(f"  • Maturity: {profile['maturity']} (score: {profile['maturity_score']})")
        logger.info(f"  • Team Size: {profile['team_size'] or 'Not disclosed'}")
        logger.info(f"  • Location: {profile['city']}, {profile['country']}")
        logger.info(f"{'='*80}\n")
    
    return grade, score, reasoning


def main():
    """Main execution: Grade all evaluated startups A+ to F"""
    
    parser = argparse.ArgumentParser(
        description='Grade AXA startups (A+ to F) using LLM-enhanced evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 recalculate_scores_llm.py              # Grade all startups
  python3 recalculate_scores_llm.py --dry-run    # Preview without saving
  python3 recalculate_scores_llm.py --verbose    # Show detailed reasoning
  python3 recalculate_scores_llm.py --limit 5    # Test with 5 startups
        """
    )
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview grades without updating database')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed evaluation reasoning for each startup')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit processing to N startups')
    args = parser.parse_args()
    
    # Banner
    logger.info("=" * 90)
    logger.info("AXA STARTUP GRADING SYSTEM (A+ to F) - LLM-ENHANCED")
    logger.info("=" * 90)
    logger.info(f"\nEvaluation Mode: {'LLM' if HAS_LLM else 'HEURISTIC'}")
    logger.info("\nCriteria:")
    logger.info("  • Scaling Platform: Multi-use case, multi-customer architecture")
    logger.info("  • Funding & Market: Strong validation ($5M+), proven customer traction")
    logger.info("  • Corporate Experience: Ability to deploy in enterprise environment")
    logger.info("  • Use Case Breadth: Multiple AXA business problems solved")
    logger.info("  • EU Presence: GDPR compliance and data residency")
    logger.info("  • AI Innovation: Especially agentic capabilities")
    logger.info("\nGrade Scale:")
    for grade in [Grade.A_PLUS, Grade.A, Grade.A_MINUS, Grade.B_PLUS, Grade.B, 
                  Grade.B_MINUS, Grade.C_PLUS, Grade.C, Grade.C_MINUS, Grade.D, Grade.F]:
        logger.info(f"  {grade.value:3} - {grade.description[:70]}...")
    logger.info("=" * 90 + "\n")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be saved to database\n")
    
    db = SessionLocal()
    
    try:
        # Get all evaluated startups
        query = db.query(Startup).filter(Startup.axa_overall_score.isnot(None))
        startups = query.all()
        
        if args.limit:
            startups = startups[:args.limit]
        
        logger.info(f"Processing {len(startups)} evaluated startups\n")
        
        # Grade statistics
        grade_counts = {g.value: 0 for g in Grade}
        score_details = []
        
        # Evaluate each startup
        for idx, startup in enumerate(startups, 1):
            try:
                grade, score, reasoning = calculate_startup_grade(startup, verbose=args.verbose)
                
                grade_counts[grade.value] += 1
                
                # Update database only if not dry-run
                if not args.dry_run:
                    startup.axa_overall_score = score
                
                score_details.append({
                    'name': startup.company_name,
                    'country': startup.company_country,
                    'grade': grade.value,
                    'score': score,
                    'reasoning': reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
                })
                
                # Progress
                if idx % max(1, len(startups) // 20) == 0:
                    logger.info(f"  ✓ Processed {idx}/{len(startups)} startups")
                    
            except Exception as e:
                logger.error(f"Error evaluating {startup.company_name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Commit changes ONLY if not dry-run
        if not args.dry_run:
            db.commit()
            logger.info(f"\n✅ Database updated - axa_overall_score saved\n")
        else:
            db.rollback()
            logger.info(f"\n(Dry run - no changes committed)\n")
        
        # Summary
        logger.info("=" * 90)
        logger.info("GRADING SUMMARY")
        logger.info("=" * 90)
        
        logger.info(f"\nGrade Distribution ({len(startups)} startups):")
        for grade in [Grade.A_PLUS, Grade.A, Grade.A_MINUS, Grade.B_PLUS, Grade.B, 
                      Grade.B_MINUS, Grade.C_PLUS, Grade.C, Grade.C_MINUS, Grade.D, Grade.F]:
            count = grade_counts[grade.value]
            pct = (count / len(startups) * 100) if len(startups) > 0 else 0
            bar = "█" * int(pct / 3) + "░" * (30 - int(pct / 3))
            logger.info(f"  {grade.value:3} [{bar}] {count:4} startups  {grade.description[:50]}")
        
        
        # Show top performers
        if score_details:
            logger.info(f"\nTop 10 Performers:")
            for detail in sorted(score_details, key=lambda x: x['score'], reverse=True)[:10]:
                logger.info(f"  {detail['grade']:3} {detail['name']:40} ({detail['country']})")
        
        logger.info("\n" + "=" * 90)
        logger.info("✨ Grading complete!")
        logger.info("=" * 90)
        
    except Exception as e:
        logger.error(f"Fatal error during grading: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
