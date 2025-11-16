#!/usr/bin/env python3
"""
LLM-Enhanced AXA Fit Score Evaluation using Claude AI.

This script uses Claude LLM to intelligently evaluate startups based on:
- All startup database fields (funding, maturity, geography, team, tech stack, etc.)
- Insurance product owner perspective with IT expertise
- Scaling potential assessment
- Business knowledge and market context
- Provides scores with confidence levels and reasoning

Usage:
    python3 evaluator/llm_intelligent_scorer.py --dry-run      # Preview changes
    python3 evaluator/llm_intelligent_scorer.py                # Update database
    python3 evaluator/llm_intelligent_scorer.py --limit 10     # Evaluate first 10
"""

import sys
import json
import argparse
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

# Add parent and api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from database import SessionLocal
from models_startup import Startup
import anthropic

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Topic base scores for reference
TOPIC_BASE_SCORES = {
    "AI - Agentic": 40,
    "AI - Software Development": 35,
    "AI - Claims": 35,
    "AI - Underwriting": 35,
    "AI - Contact Centers": 35,
    "Health": 30,
    "Growth": 30,
    "Responsibility": 35,
    "Insurance Disruptor": 35,
    "DeepTech": 30,
    "Other": 30,
}


def format_startup_for_llm(startup: Startup) -> str:
    """Format startup data into a comprehensive prompt for LLM evaluation."""
    
    funding_info = ""
    if startup.total_funding:
        funding_info += f"  • Total Funding: ${startup.total_funding:.1f}M\n"
    if startup.funding_stage:
        funding_info += f"  • Funding Stage: {startup.funding_stage}\n"
    if startup.valuation:
        funding_info += f"  • Valuation: ${startup.valuation:.1f}M\n"
    
    geo_info = ""
    if startup.company_country:
        geo_info += f"  • Headquarters: {startup.company_city}, {startup.company_country}\n"
    
    maturity_info = ""
    if startup.maturity:
        maturity_info += f"  • Maturity: {startup.maturity}\n"
    if startup.maturity_score:
        maturity_info += f"  • Maturity Score: {startup.maturity_score}\n"
    
    team_info = ""
    if startup.enrichment:
        try:
            enrich = json.loads(startup.enrichment) if isinstance(startup.enrichment, str) else startup.enrichment
            if isinstance(enrich, dict) and 'team_members' in enrich:
                team_info += f"  • Team Size: {len(enrich.get('team_members', []))} members\n"
        except:
            pass
    
    tech_info = ""
    if startup.tech:
        try:
            tech_list = json.loads(startup.tech) if isinstance(startup.tech, str) else startup.tech
            if isinstance(tech_list, list):
                tech_info += f"  • Tech Stack: {', '.join(tech_list[:5])}\n"
        except:
            pass
    
    use_cases_info = ""
    if startup.axa_use_cases:
        try:
            uc = json.loads(startup.axa_use_cases) if isinstance(startup.axa_use_cases, str) else startup.axa_use_cases
            if isinstance(uc, list):
                use_cases_info += f"  • Use Cases: {', '.join(uc)}\n"
        except:
            pass
    
    business_info = ""
    if startup.business_model:
        business_info += f"  • Business Model: {startup.business_model}\n"
    if startup.extracted_product:
        business_info += f"  • Product: {startup.extracted_product[:100]}\n"
    if startup.extracted_market:
        business_info += f"  • Target Market: {startup.extracted_market[:100]}\n"
    
    prompt = f"""# Startup Evaluation Request

## Company: {startup.company_name}
### Current AXA Assessment: Score {startup.axa_overall_score or 0:.1f}/100 | {startup.axa_priority_tier or 'Unranked'}

## Core Information
{geo_info}
  • Type: {startup.company_type or 'Unknown'}
  • Founded: {startup.founding_year or 'Unknown'}
  • Industry: {startup.primary_industry or 'Unknown'}

## Financial Status
{funding_info if funding_info else "  • Funding: Not disclosed\n"}

## Stage & Maturity
{maturity_info if maturity_info else "  • Maturity: Not disclosed\n"}

## Technology & Capability
{tech_info if tech_info else "  • Tech Stack: Not specified\n"}

## Strategic Fit
{use_cases_info if use_cases_info else "  • Use Cases: Not specified\n"}
  • Primary Topic: {startup.axa_primary_topic or 'Not specified'}
  • Can Be Provider: {startup.axa_can_use_as_provider or 'Unknown'}

## Business Details
{business_info if business_info else ""}
  • Website: {startup.website or 'Not provided'}
  • Description: {startup.company_description[:200] if startup.company_description else 'N/A'}...

---

## Evaluation Task

You are evaluating this startup from the perspective of an experienced **AXA Insurance product owner with IT expertise and business knowledge**. 

Consider:
1. **Product-Market Fit with AXA**: How well does this solution address insurance operational challenges?
2. **Scaling Potential**: Given the team, tech, funding, and market position, can this solution scale to enterprise insurance requirements?
3. **Technology Readiness**: Is the technical architecture suitable for insurance-grade applications (security, compliance, reliability)?
4. **Business Viability**: Strong unit economics and go-to-market strategy?
5. **Integration Feasibility**: How easily could AXA integrate or partner with this solution?
6. **Risk Factors**: Key dependencies, market risks, or technical debt that would limit value delivery?

Provide your assessment in the following JSON format:

```json
{{
    "overall_score": <number 30-92>,
    "confidence": <"high" | "medium" | "low">,
    "scaling_potential": <"high" | "medium" | "low">,
    "scaling_margin": <adjustment -15 to +15>,
    "tier_recommendation": "<Tier 1: Critical Priority | Tier 2: High Priority | Tier 3: Medium Priority | Tier 4: Low Priority>",
    "key_strengths": [<up to 3 key strengths>],
    "key_concerns": [<up to 3 concerns/risks>],
    "scaling_assessment": "<brief explanation of scaling potential and recommended margin>",
    "recommendation_notes": "<2-3 sentence actionable recommendation for AXA>",
    "rationale": "<detailed reasoning for the score>"
}}
```

**Important Guidelines:**
- Scores should range from 30-92 (realistic distribution, no perfect 100s)
- Use scaling_margin to indicate if confidence adjustments are needed (-15 to +15)
- High confidence: margin ±5, Medium: ±10, Low: ±15
- Consider this startup's unique strengths and weaknesses
- Be realistic about scaling challenges in enterprise insurance
"""
    
    return prompt


def evaluate_startup_with_llm(startup: Startup) -> Optional[Dict]:
    """Use Claude LLM to evaluate a startup and return structured assessment."""
    
    try:
        prompt = format_startup_for_llm(startup)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to find JSON in the response
        try:
            # Look for JSON block
            import json as json_module
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                assessment = json_module.loads(json_str)
                return assessment
        except:
            logger.warning(f"Failed to parse JSON response for {startup.company_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error evaluating {startup.company_name}: {str(e)}")
        return None


def apply_margin_to_score(base_score: float, margin: float, confidence: str) -> float:
    """Apply scaling margin to base score with limits based on confidence."""
    
    # Clamp margin based on confidence level
    if confidence == "high":
        margin = max(-5, min(5, margin))
    elif confidence == "medium":
        margin = max(-10, min(10, margin))
    else:  # low
        margin = max(-15, min(15, margin))
    
    final_score = base_score + margin
    # Keep within realistic bounds
    return max(30, min(92, final_score))


def main():
    parser = argparse.ArgumentParser(description='LLM-powered intelligent AXA fit score evaluation')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without updating database')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of startups to evaluate')
    args = parser.parse_args()
    
    logger.info("=" * 90)
    logger.info("LLM-ENHANCED AXA FIT SCORE EVALUATION (CLAUDE INTELLIGENCE)")
    logger.info("=" * 90)
    logger.info("Methodology:")
    logger.info("  • Uses Claude 3.5 Sonnet for intelligent startup evaluation")
    logger.info("  • Perspective: Insurance product owner with IT & business expertise")
    logger.info("  • Considers: Product-market fit, scaling potential, tech readiness")
    logger.info("  • Includes: Confidence levels and scaling potential assessment")
    logger.info("  • Score range: 30-92 (realistic distribution)")
    logger.info("=" * 90)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be saved")
    
    db = SessionLocal()
    
    try:
        # Get startups to evaluate
        query = db.query(Startup).filter(Startup.axa_overall_score.isnot(None))
        
        if args.limit:
            startups = query.limit(args.limit).all()
        else:
            startups = query.all()
        
        logger.info(f"\nEvaluating {len(startups)} startups with LLM...\n")
        
        stats = {
            'total': len(startups),
            'evaluated': 0,
            'failed': 0,
            'score_increased': 0,
            'score_decreased': 0,
            'score_unchanged': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'high_scaling': 0,
            'medium_scaling': 0,
            'low_scaling': 0,
            'tier_improvements': 0,
        }
        
        changes = []
        
        for idx, startup in enumerate(startups, 1):
            old_score = startup.axa_overall_score or 0
            old_tier = startup.axa_priority_tier or "Tier 4: Low Priority"
            
            logger.info(f"[{idx}/{len(startups)}] Evaluating: {startup.company_name}...")
            
            assessment = evaluate_startup_with_llm(startup)
            
            if not assessment:
                logger.info(f"  ✗ FAILED to get LLM assessment")
                stats['failed'] += 1
                continue
            
            # Extract assessment data
            new_score = assessment.get('overall_score', old_score)
            confidence = assessment.get('confidence', 'medium')
            scaling_potential = assessment.get('scaling_potential', 'medium')
            scaling_margin = assessment.get('scaling_margin', 0)
            new_tier = assessment.get('tier_recommendation', old_tier)
            
            # Apply margin with confidence limits
            final_score = apply_margin_to_score(new_score, scaling_margin, confidence)
            
            # Track confidence levels
            if confidence == "high":
                stats['high_confidence'] += 1
            elif confidence == "medium":
                stats['medium_confidence'] += 1
            else:
                stats['low_confidence'] += 1
            
            # Track scaling potential
            if scaling_potential == "high":
                stats['high_scaling'] += 1
            elif scaling_potential == "medium":
                stats['medium_scaling'] += 1
            else:
                stats['low_scaling'] += 1
            
            # Track score changes
            score_diff = final_score - old_score
            if abs(score_diff) < 0.5:
                stats['score_unchanged'] += 1
            elif score_diff > 0:
                stats['score_increased'] += 1
            else:
                stats['score_decreased'] += 1
            
            # Check tier improvement
            old_tier_num = extract_tier_number(old_tier)
            new_tier_num = extract_tier_number(new_tier)
            if new_tier_num < old_tier_num:
                stats['tier_improvements'] += 1
            
            # Update database if not dry run
            if not args.dry_run:
                startup.axa_overall_score = final_score
                startup.axa_priority_tier = new_tier
                # Store LLM assessment as metadata
                startup.axa_fit_summary = json.dumps({
                    'llm_assessment': assessment,
                    'evaluation_method': 'Claude 3.5 Sonnet - Insurance Product Owner Perspective',
                    'confidence': confidence,
                    'scaling_potential': scaling_potential,
                    'scaling_margin_applied': scaling_margin
                })
            
            stats['evaluated'] += 1
            
            # Track significant changes
            if abs(score_diff) >= 3 or old_tier_num != new_tier_num:
                changes.append({
                    'name': startup.company_name,
                    'country': startup.company_country,
                    'old_score': round(old_score, 1),
                    'new_score': round(final_score, 1),
                    'diff': round(score_diff, 1),
                    'old_tier': old_tier,
                    'new_tier': new_tier,
                    'confidence': confidence,
                    'scaling': scaling_potential,
                    'strengths': assessment.get('key_strengths', []),
                    'concerns': assessment.get('key_concerns', []),
                })
            
            logger.info(f"  ✓ Score: {old_score:.1f} → {final_score:.1f} | Confidence: {confidence} | Scaling: {scaling_potential}")
        
        if not args.dry_run:
            db.commit()
            logger.info("\n✓ Database updated with LLM assessments")
        
        # Print detailed statistics
        logger.info("\n" + "=" * 90)
        logger.info("LLM EVALUATION SUMMARY")
        logger.info("=" * 90)
        
        logger.info(f"\nEvaluation Success: {stats['evaluated']}/{stats['total']} ({stats['evaluated']/stats['total']*100:.1f}%)")
        logger.info(f"Failed Evaluations: {stats['failed']}")
        
        logger.info(f"\nScore Changes:")
        logger.info(f"  ↑ Increased: {stats['score_increased']} ({stats['score_increased']/stats['total']*100:.1f}%)")
        logger.info(f"  ↓ Decreased: {stats['score_decreased']} ({stats['score_decreased']/stats['total']*100:.1f}%)")
        logger.info(f"  = Unchanged: {stats['score_unchanged']} ({stats['score_unchanged']/stats['total']*100:.1f}%)")
        
        logger.info(f"\nConfidence Distribution:")
        logger.info(f"  🟢 High: {stats['high_confidence']} ({stats['high_confidence']/stats['total']*100:.1f}%)")
        logger.info(f"  🟡 Medium: {stats['medium_confidence']} ({stats['medium_confidence']/stats['total']*100:.1f}%)")
        logger.info(f"  🔴 Low: {stats['low_confidence']} ({stats['low_confidence']/stats['total']*100:.1f}%)")
        
        logger.info(f"\nScaling Potential Assessment:")
        logger.info(f"  🚀 High: {stats['high_scaling']} ({stats['high_scaling']/stats['total']*100:.1f}%)")
        logger.info(f"  📈 Medium: {stats['medium_scaling']} ({stats['medium_scaling']/stats['total']*100:.1f}%)")
        logger.info(f"  📊 Low: {stats['low_scaling']} ({stats['low_scaling']/stats['total']*100:.1f}%)")
        
        logger.info(f"\nTier Improvements: {stats['tier_improvements']}")
        
        # Show sample of notable changes
        if changes:
            logger.info(f"\nTop Improvements (sample):")
            top_changes = sorted([c for c in changes if c['diff'] > 0], key=lambda x: x['diff'], reverse=True)[:5]
            for c in top_changes:
                logger.info(f"  • {c['name']} ({c['country']})")
                logger.info(f"    Score: {c['old_score']} → {c['new_score']} (+{c['diff']})")
                logger.info(f"    Confidence: {c['confidence']} | Scaling: {c['scaling']}")
                logger.info(f"    Strengths: {', '.join(c['strengths'][:2])}")
        
        logger.info("\n" + "=" * 90)
        
        if args.dry_run:
            logger.info("DRY RUN - No changes were saved to database")
        else:
            logger.info("✓ All LLM assessments saved to database")
        
    finally:
        db.close()


def extract_tier_number(tier_str: str) -> int:
    """Extract tier number from tier string."""
    if 'Tier 1' in tier_str or 'Critical' in tier_str:
        return 1
    elif 'Tier 2' in tier_str or 'High' in tier_str:
        return 2
    elif 'Tier 3' in tier_str or 'Medium' in tier_str:
        return 3
    else:
        return 4


if __name__ == "__main__":
    main()
