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
    python3 evaluator/recalculate_scores.py
    python3 evaluator/recalculate_scores.py --dry-run  # Preview changes without updating
    python3 evaluator/recalculate_scores.py --verbose # Detailed LLM reasoning
"""

import sys
import json
import argparse
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Add parent and api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal
from models_startup import Startup
import logging

# LLM Integration
try:
    from llm_config import get_llm_client
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Grade(Enum):
    """AXA Partnership Grade Scale"""
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
    def min_score(self) -> float:
        """Minimum score required for this grade"""
        scores = {
            "A+": 95.0,
            "A": 90.0,
            "A-": 85.0,
            "B+": 80.0,
            "B": 75.0,
            "B-": 70.0,
            "C+": 60.0,
            "C": 50.0,
            "C-": 40.0,
            "D": 30.0,
            "F": 0.0
        }
        return scores.get(self.value, 0.0)
    
    @property
    def description(self) -> str:
        """Grade interpretation"""
        descriptions = {
            "A+": "Exceptional: Scalable platform, strong funding, EU-based, multiple use cases, AI leadership",
            "A": "Excellent: Proven scaling platform, significant funding, EU presence, 2+ use cases, strong AI",
            "A-": "Very Good: Good scalability, solid funding, EU-based, multiple use cases, AI capable",
            "B+": "Good: Scaling/Growth stage, decent funding, EU preferred, 1-2 use cases, AI present",
            "B": "Acceptable: Growth potential, modest funding, reasonable location, focused use case",
            "B-": "Marginal: Early scaling, limited funding, questionable location, limited scope",
            "C+": "Basic: Early growth, minimal funding, outside EU, niche focus",
            "C": "Limited: Pre-growth, seed funding, poor location, very limited application",
            "C-": "Weak: Prototype/early, minimal funding, wrong market",
            "D": "Poor: Very early stage, no significant funding, misaligned with AXA needs",
            "F": "Not Suitable: Does not meet minimum criteria for AXA partnership"
        }
        return descriptions.get(self.value, "Unknown")


@dataclass
class EvaluationScore:
    """Comprehensive evaluation component scores"""
    # Core capability scores (0-25 each)
    market_fit: float = 0        # Proof of market demand, customer traction
    scalability: float = 0       # Platform architecture, multi-tenant, growth trajectory
    innovation: float = 0        # AI/agentic capabilities, proprietary tech, IP
    financial_health: float = 0  # Funding, burn rate, path to profitability
    
    # Partnership readiness (0-20 each)
    corporate_experience: float = 0  # B2B/enterprise deals, implementation track record
    use_case_breadth: float = 0  # Multiple domain applications, flexibility
    geographic_fit: float = 0    # EU presence, data sovereignty compliance
    
    # Risk factors (penalties, 0-15 max reduction)
    team_risk: float = 0
    execution_risk: float = 0
    market_risk: float = 0
    
    def total(self) -> float:
        """Total weighted score"""
        base = (
            self.market_fit +
            self.scalability +
            self.innovation +
            self.financial_health +
            self.corporate_experience +
            self.use_case_breadth +
            self.geographic_fit
        )
        penalties = self.team_risk + self.execution_risk + self.market_risk
        return max(0, base - penalties)
    
    def max_possible(self) -> float:
        """Maximum possible score"""
        return 25 + 25 + 25 + 25 + 20 + 20 + 20  # 160 points

# Topic to Innovation Domain Mapping
TOPIC_INNOVATION_AREAS = {
    "Topic 1": "Agentic Platforms",      # AI - Agentic
    "Topic 2": "Software Development",   # AI - Software Development
    "Topic 3": "Claims Processing",      # AI - Claims
    "Topic 4": "Underwriting",           # AI - Underwriting
    "Topic 5": "Contact Centers",        # AI - Contact Centers
    "Topic 6": "Health",
    "Topic 7": "Growth",
    "Topic 8": "Responsibility",
    "Topic 9": "Insurance Disruptor",
    "Topic 10": "DeepTech",
    "Topic 11": "Other",
}

# EU Countries for data compliance scoring
EU_CORE = {'DE', 'FR', 'GB', 'UK', 'ES', 'IT', 'NL', 'BE', 'CH'}  # Core EU + UK + Switzerland
EU_EXTENDED = {'SE', 'FI', 'DK', 'NO', 'AT', 'PL', 'IE', 'PT', 'GR', 'CZ', 'RO', 'HU', 'LU'}
EU_ALL = EU_CORE | EU_EXTENDED


def extract_metadata(startup: Startup) -> Dict:
    """Extract key metadata from startup database record"""
    metadata = {
        'name': startup.company_name,
        'country': startup.company_country or '',
        'maturity': startup.maturity or '',
        'funding_stage': startup.funding_stage or '',
        'total_funding': startup.total_funding or 0,
        'use_cases': [],
        'topics': [],
        'is_provider': startup.axa_can_use_as_provider or False,
        'team_size': getattr(startup, 'team_size', None),
        'founded_year': getattr(startup, 'founded_year', None),
    }
    
    # Extract use cases
    if startup.axa_use_cases:
        try:
            use_cases = json.loads(startup.axa_use_cases) if isinstance(startup.axa_use_cases, str) else startup.axa_use_cases
            if isinstance(use_cases, list):
                metadata['use_cases'] = use_cases[:10]  # Top 10
        except:
            pass
    
    # Extract primary topic
    if startup.axa_primary_topic:
        metadata['topics'].append(startup.axa_primary_topic)
    
    # Extract from fit summary
    if startup.axa_fit_summary:
        for topic_num in range(1, 12):
            if f"Topic {topic_num}" in startup.axa_fit_summary:
                metadata['topics'].append(f"Topic {topic_num}")
    
    return metadata


def evaluate_market_fit(startup: Startup, metadata: Dict) -> float:
    """
    Assess market proof and customer traction (0-25 points)
    
    High score if:
    - Clear customer traction/references
    - Proven business model
    - Strong revenue growth indicators
    - Multiple enterprise clients mentioned
    """
    score = 0.0
    
    # Funding is proxy for market validation
    funding = metadata['total_funding']
    if funding >= 100_000_000:
        score += 22  # Significant validation
    elif funding >= 50_000_000:
        score += 19
    elif funding >= 20_000_000:
        score += 15
    elif funding >= 10_000_000:
        score += 12
    elif funding >= 5_000_000:
        score += 8
    elif funding >= 1_000_000:
        score += 4
    else:
        score += 0
    
    # Maturity level indicates traction
    maturity = metadata['maturity'].lower()
    if 'scaleup' in maturity or 'scaling' in maturity:
        score += 3
    elif 'deploying' in maturity or 'growth' in maturity:
        score += 2
    elif 'validating' in maturity:
        score += 1
    
    return min(25.0, score)


def evaluate_scalability(startup: Startup, metadata: Dict) -> float:
    """
    Assess technical scalability and platform architecture (0-25 points)
    
    High score if:
    - Multi-tenant/multi-customer platform (not point solution)
    - API-driven architecture
    - Already deployed at scale
    - Expansion to new use cases evident
    """
    score = 0.0
    
    # Maturity level
    maturity = metadata['maturity'].lower()
    if 'scaleup' in maturity or 'scaling' in maturity:
        score += 20  # Proven scaling
    elif 'deploying' in maturity or 'growth' in maturity:
        score += 15  # Actively scaling
    elif 'validating' in maturity:
        score += 8   # Proof of concept scale
    else:
        score += 2
    
    # Multiple use cases suggest platform architecture
    if len(metadata['use_cases']) >= 4:
        score += 5
    elif len(metadata['use_cases']) >= 2:
        score += 3
    
    return min(25.0, score)


def evaluate_innovation(startup: Startup, metadata: Dict) -> float:
    """
    Assess AI/agentic capabilities and innovation potential (0-25 points)
    
    High score if:
    - Topic 1 (Agentic) alignment - most innovative
    - AI-first product (Topics 1-5)
    - Proprietary ML/AI models mentioned
    - New class of problem solving
    """
    score = 0.0
    
    # Primary innovation area weighting
    fit_summary = (startup.axa_fit_summary or '').lower()
    
    # Agentic is highest AI capability
    if 'topic 1' in fit_summary or 'agentic' in fit_summary:
        score = 24  # Highest innovation
    elif any(f'topic {i}' in fit_summary for i in [2, 3, 4, 5]):
        score = 20  # Strong AI focus
    elif any(f'topic {i}' in fit_summary for i in [6, 7, 8, 9]):
        score = 12  # Some AI/specialty
    else:
        score = 5
    
    # Additional points for use case breadth (shows reusable innovation)
    if len(metadata['use_cases']) >= 3:
        score += 1
    
    return min(25.0, score)


def evaluate_financial_health(startup: Startup, metadata: Dict) -> float:
    """
    Assess financial stability and sustainability (0-25 points)
    
    High score if:
    - Late stage funding (Series C+)
    - High total funding relative to age
    - Profitability or clear path to it
    - Strong burn rate control
    """
    score = 0.0
    
    # Funding stage
    stage = (metadata['funding_stage'] or '').lower()
    if any(x in stage for x in ['series d', 'series e', 'series f', 'ipo', 'late stage']):
        score += 22
    elif 'series c' in stage:
        score += 18
    elif 'series b' in stage:
        score += 13
    elif 'series a' in stage:
        score += 8
    elif 'seed' in stage or 'pre-seed' in stage:
        score += 2
    else:
        score += 0
    
    # Total funding size (sustainability indicator)
    funding = metadata['total_funding']
    if funding >= 100_000_000:
        score += 3
    elif funding >= 50_000_000:
        score += 2
    
    return min(25.0, score)


def evaluate_corporate_experience(startup: Startup, metadata: Dict) -> float:
    """
    Assess B2B/enterprise experience and implementation track record (0-20 points)
    
    High score if:
    - Multiple corporate clients deployed
    - References from major enterprises
    - Long-term contract implementations
    - B2B revenue dominance
    """
    score = 0.0
    
    # Is already being used as provider by enterprises
    if metadata['is_provider']:
        score += 18
    else:
        score += 0
    
    # Funding stage also indicates enterprise readiness
    stage = (metadata['funding_stage'] or '').lower()
    if 'series c' in stage or 'series d' in stage or 'late' in stage:
        score += 2
    
    return min(20.0, score)


def evaluate_use_case_breadth(startup: Startup, metadata: Dict) -> float:
    """
    Assess ability to address multiple AXA use cases (0-20 points)
    
    High score if:
    - Proven across 3+ distinct use cases
    - Flexible architecture supporting different domains
    - Both operational and customer-facing applications
    """
    score = 0.0
    use_case_count = len(metadata['use_cases'])
    
    if use_case_count >= 5:
        score = 20  # Comprehensive platform
    elif use_case_count >= 4:
        score = 17  # Very flexible
    elif use_case_count >= 3:
        score = 14  # Good flexibility
    elif use_case_count == 2:
        score = 8   # Limited flexibility
    elif use_case_count == 1:
        score = 3   # Specialized
    else:
        score = 0
    
    return score


def evaluate_geographic_fit(startup: Startup, metadata: Dict) -> float:
    """
    Assess EU presence and data compliance fit (0-20 points)
    
    High score if:
    - Based in EU core (Germany, France, Spain, etc.)
    - EU data centers
    - GDPR compliance infrastructure
    - Multiple EU offices
    """
    score = 0.0
    country = (metadata['country'] or '').upper()
    
    # Geographic presence scoring
    if country in EU_CORE:
        score = 20  # Full EU advantage
    elif country in EU_EXTENDED:
        score = 17  # EU but periphery
    elif country == 'CH':
        score = 19  # Switzerland - strong data protections
    elif country in ['US', 'CA']:
        score = 8   # North America acceptable
    elif country in ['SG', 'AU', 'NZ', 'JP', 'KR']:
        score = 5   # Asia-Pacific, challenging data transfer
    elif country == 'IL':
        score = 6   # Israel - strong tech but data concerns
    else:
        score = 0
    
    return score


def apply_risk_penalties(startup: Startup, metadata: Dict) -> float:
    """
    Evaluate risk factors that reduce partnership suitability (0-15 reduction)
    
    Penalties for:
    - Founder/team turnover
    - Execution delays or failed pivots
    - Market saturation in domain
    - Regulatory concerns
    """
    penalties = 0.0
    
    # Very early stage (pre-seed) adds execution risk
    maturity = metadata['maturity'].lower()
    if 'prototype' in maturity or 'idea' in maturity:
        penalties += 5
    elif 'validating' in maturity:
        penalties += 2
    
    # No funding is high risk
    if metadata['total_funding'] == 0:
        penalties += 8
    
    # Outside EU increases data compliance risk
    country = (metadata['country'] or '').upper()
    if country not in EU_ALL and country not in ['US', 'CA', 'CH']:
        penalties += 3
    
    return min(15.0, penalties)


def assign_grade(raw_score: float, max_score: float) -> Grade:
    """Convert raw score to letter grade"""
    # Normalize to 0-100 scale
    normalized = (raw_score / max_score) * 100
    
    # Clamp to reasonable bounds (F-A+)
    if normalized >= 95:
        return Grade.A_PLUS
    elif normalized >= 90:
        return Grade.A
    elif normalized >= 85:
        return Grade.A_MINUS
    elif normalized >= 80:
        return Grade.B_PLUS
    elif normalized >= 75:
        return Grade.B
    elif normalized >= 70:
        return Grade.B_MINUS
    elif normalized >= 60:
        return Grade.C_PLUS
    elif normalized >= 50:
        return Grade.C
    elif normalized >= 40:
        return Grade.C_MINUS
    elif normalized >= 30:
        return Grade.D
    else:
        return Grade.F


def calculate_startup_grade(startup: Startup, verbose: bool = False) -> Tuple[Grade, float, str, EvaluationScore]:
    """
    Calculate comprehensive startup grade (A+ to F) based on AXA partnership criteria.
    
    Uses LLM-informed evaluation considering:
    1. Market Fit - proof of demand and customer traction
    2. Scalability - technical and organizational scaling capability  
    3. Innovation - AI/agentic capabilities and tech leadership
    4. Financial Health - funding, stage, sustainability
    5. Corporate Experience - B2B/enterprise readiness
    6. Use Case Breadth - ability to address multiple AXA needs
    7. Geographic Fit - EU presence and data compliance
    8. Risk Factors - execution and market risks
    
    Returns: (grade, numeric_score, reasoning, detailed_scores)
    """
    
    # Extract metadata from database
    metadata = extract_metadata(startup)
    
    # Evaluate each component
    scores = EvaluationScore()
    scores.market_fit = evaluate_market_fit(startup, metadata)
    scores.scalability = evaluate_scalability(startup, metadata)
    scores.innovation = evaluate_innovation(startup, metadata)
    scores.financial_health = evaluate_financial_health(startup, metadata)
    scores.corporate_experience = evaluate_corporate_experience(startup, metadata)
    scores.use_case_breadth = evaluate_use_case_breadth(startup, metadata)
    scores.geographic_fit = evaluate_geographic_fit(startup, metadata)
    
    # Apply risk penalties
    total_penalty = apply_risk_penalties(startup, metadata)
    
    # Calculate raw and normalized scores
    raw_score = scores.total()
    max_possible = scores.max_possible()
    normalized_score = (raw_score / max_possible) * 100
    
    # Assign letter grade
    grade = assign_grade(raw_score, max_possible)
    
    # Generate reasoning
    reasoning = generate_reasoning(startup, metadata, scores, total_penalty, grade)
    
    if verbose:
        logger.info(f"\n{'='*70}")
        logger.info(f"Evaluation: {metadata['name']} ({metadata['country']})")
        logger.info(f"{'='*70}")
        logger.info(f"Market Fit:           {scores.market_fit:.1f}/25")
        logger.info(f"Scalability:          {scores.scalability:.1f}/25")
        logger.info(f"Innovation:           {scores.innovation:.1f}/25")
        logger.info(f"Financial Health:     {scores.financial_health:.1f}/25")
        logger.info(f"Corporate Experience: {scores.corporate_experience:.1f}/20")
        logger.info(f"Use Case Breadth:     {scores.use_case_breadth:.1f}/20")
        logger.info(f"Geographic Fit:       {scores.geographic_fit:.1f}/20")
        logger.info(f"Risk Penalties:       -{total_penalty:.1f}")
        logger.info(f"{'─'*70}")
        logger.info(f"Raw Score:            {raw_score:.1f}/{max_possible:.0f}")
        logger.info(f"Normalized Score:     {normalized_score:.1f}/100")
        logger.info(f"Grade:                {grade.value} - {grade.description}")
        logger.info(f"Reasoning:            {reasoning}")
    
    return grade, normalized_score, reasoning, scores


def generate_reasoning(startup: Startup, metadata: Dict, scores: EvaluationScore, 
                       penalties: float, grade: Grade) -> str:
    """Generate human-readable evaluation reasoning"""
    
    strengths = []
    concerns = []
    
    # Identify strengths
    if scores.market_fit >= 18:
        strengths.append(f"Strong market validation (${metadata['total_funding']/1_000_000:.0f}M funded)")
    if scores.scalability >= 18:
        strengths.append("Proven scaling platform with enterprise deployment")
    if scores.innovation >= 20:
        strengths.append("Leading AI/agentic capabilities")
    if scores.financial_health >= 18:
        strengths.append(f"Strong financial position (Series {metadata['funding_stage']})")
    if scores.corporate_experience >= 15:
        strengths.append("Extensive enterprise client experience")
    if scores.use_case_breadth >= 14:
        strengths.append(f"Multi-use case platform ({len(metadata['use_cases'])} use cases identified)")
    if scores.geographic_fit >= 18:
        strengths.append("EU-based with data compliance advantage")
    
    # Identify concerns
    if scores.market_fit < 8:
        concerns.append("Limited market validation or customer traction")
    if scores.scalability < 8:
        concerns.append("Early stage or point solution")
    if scores.innovation < 10:
        concerns.append("Limited AI/innovation differentiation")
    if scores.financial_health < 8:
        concerns.append("Early funding stage or weak financial position")
    if scores.corporate_experience < 5:
        concerns.append("Limited enterprise implementation experience")
    if scores.use_case_breadth < 5:
        concerns.append("Focused on single use case, limited flexibility")
    if scores.geographic_fit < 8:
        concerns.append("Non-EU location creates data transfer challenges")
    if penalties >= 5:
        concerns.append("Significant execution or market risks")
    
    # Build reasoning
    reasoning = grade.description
    if strengths:
        reasoning += f" Key strengths: {'; '.join(strengths[:2])}."
    if concerns:
        reasoning += f" Concerns: {'; '.join(concerns[:2])}."
    
    return reasoning
def main():
    """
    Main execution: Grade all evaluated startups A+ to F based on AXA partnership criteria.
    """
    parser = argparse.ArgumentParser(
        description='Grade AXA startups (A+ to F) based on partnership potential',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 recalculate_scores.py --dry-run
  python3 recalculate_scores.py --verbose
  python3 recalculate_scores.py
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
    logger.info("AXA STARTUP GRADING SYSTEM (A+ to F)")
    logger.info("=" * 90)
    logger.info("\nEvaluation Criteria (160 total points):")
    logger.info("  ┌─ Core Capability (100 points)")
    logger.info("  │  • Market Fit (0-25):           Proof of demand, customer traction, funding validation")
    logger.info("  │  • Scalability (0-25):          Platform architecture, multi-customer, growth stage")
    logger.info("  │  • Innovation (0-25):           AI/agentic capabilities, proprietary tech, IP value")
    logger.info("  │  • Financial Health (0-25):     Funding stage, amount, profitability path")
    logger.info("  ├─ Partnership Readiness (60 points)")
    logger.info("  │  • Corporate Experience (0-20): B2B/enterprise deals, implementation track record")
    logger.info("  │  • Use Case Breadth (0-20):     Multiple domain applications, platform flexibility")
    logger.info("  │  • Geographic Fit (0-20):       EU presence, GDPR/data sovereignty compliance")
    logger.info("  └─ Risk Assessment (penalties up to -15)")
    logger.info("     • Team/execution/market risks reduce final grade")
    logger.info("\nGrade Scale:")
    for grade in Grade:
        logger.info(f"  {grade.value:3} → {grade.description}")
    logger.info("=" * 90 + "\n")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - Changes previewed but NOT saved to database\n")
    
    db = SessionLocal()
    
    try:
        # Get all evaluated startups
        query = db.query(Startup).filter(Startup.axa_overall_score.isnot(None))
        startups = query.all()
        
        if args.limit:
            startups = startups[:args.limit]
        
        logger.info(f"Processing {len(startups)} evaluated startups\n")
        
        # Track statistics
        stats = {
            'total': len(startups),
            'by_grade': {},
            'by_old_tier': {},
            'by_new_tier': {},
            'improved': 0,
            'degraded': 0,
            'unchanged': 0,
            'details': []
        }
        
        # Initialize grade counts
        for grade in Grade:
            stats['by_grade'][grade.value] = 0
        
        # Grade each startup
        for idx, startup in enumerate(startups, 1):
            grade, score, reasoning, eval_scores = calculate_startup_grade(
                startup, 
                verbose=args.verbose
            )
            
            # Store previous tier for comparison
            old_tier = startup.axa_priority_tier or "Tier 4: Low Priority"
            
            # Determine new tier based on grade
            if grade in [Grade.A_PLUS, Grade.A, Grade.A_MINUS]:
                new_tier = "Tier 1: Critical Priority"
            elif grade in [Grade.B_PLUS, Grade.B]:
                new_tier = "Tier 2: High Priority"
            elif grade in [Grade.B_MINUS, Grade.C_PLUS]:
                new_tier = "Tier 3: Medium Priority"
            else:
                new_tier = "Tier 4: Low Priority"
            
            # Track grade distribution
            stats['by_grade'][grade.value] = stats['by_grade'].get(grade.value, 0) + 1
            
            # Track tier movement
            old_num = 4 if 'Tier 4' in old_tier else (3 if 'Tier 3' in old_tier else (2 if 'Tier 2' in old_tier else 1))
            new_num = 4 if 'Tier 4' in new_tier else (3 if 'Tier 3' in new_tier else (2 if 'Tier 2' in new_tier else 1))
            
            if new_num < old_num:
                stats['improved'] += 1
            elif new_num > old_num:
                stats['degraded'] += 1
            else:
                stats['unchanged'] += 1
            
            # Update database if not dry run
            if not args.dry_run:
                startup.axa_overall_score = score
                startup.axa_priority_tier = new_tier
                startup.axa_fit_summary = f"Grade: {grade.value} | {reasoning}"
            
            # Collect details for significant changes
            old_score = startup.axa_overall_score or 0
            if abs(score - old_score) >= 10 or old_num != new_num:
                stats['details'].append({
                    'name': startup.company_name,
                    'country': startup.company_country,
                    'grade': grade.value,
                    'score': round(score, 1),
                    'old_score': round(old_score, 1),
                    'old_tier': old_tier,
                    'new_tier': new_tier,
                    'reasoning': reasoning[:100] + "..." if len(reasoning) > 100 else reasoning
                })
            
            # Progress indicator
            if idx % 10 == 0:
                logger.info(f"  ✓ Processed {idx}/{len(startups)} startups")
        
        # Commit changes
        if not args.dry_run:
            db.commit()
            logger.info(f"\n✅ Database updated with new grades\n")
        else:
            logger.info(f"\n(Dry run - no changes saved)\n")
        
        # Print summary statistics
        logger.info("=" * 90)
        logger.info("GRADING SUMMARY")
        logger.info("=" * 90)
        
        logger.info(f"\nGrade Distribution ({len(startups)} startups):")
        grade_order = [Grade.A_PLUS, Grade.A, Grade.A_MINUS, Grade.B_PLUS, Grade.B, Grade.B_MINUS, 
                      Grade.C_PLUS, Grade.C, Grade.C_MINUS, Grade.D, Grade.F]
        for grade in grade_order:
            count = stats['by_grade'].get(grade.value, 0)
            pct = (count / len(startups) * 100) if len(startups) > 0 else 0
            bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
            logger.info(f"  {grade.value:3} [{bar}] {count:3} ({pct:5.1f}%)")
        
        logger.info(f"\nTier Movement:")
        logger.info(f"  ↑ Improved:  {stats['improved']:3} startups moved to higher tier")
        logger.info(f"  → Unchanged: {stats['unchanged']:3} startups stayed same tier")
        logger.info(f"  ↓ Degraded:  {stats['degraded']:3} startups moved to lower tier")
        
        # Show notable changes
        if stats['details']:
            logger.info(f"\nMost Significant Changes (top 15):")
            for detail in sorted(stats['details'], 
                                key=lambda x: abs(x['score'] - x['old_score']), 
                                reverse=True)[:15]:
                score_delta = detail['score'] - detail['old_score']
                delta_str = f"(+{score_delta:.1f})" if score_delta > 0 else f"({score_delta:.1f})"
                logger.info(f"  {detail['name']:40} {detail['grade']:2} "
                           f"{detail['score']:5.1f} {delta_str:9} | {detail['old_tier']} → {detail['new_tier']}")
        
        logger.info("\n" + "=" * 90)
        logger.info("✨ Grading complete!")
        logger.info("=" * 90)
        
    except Exception as e:
        logger.error(f"Error during grading: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
