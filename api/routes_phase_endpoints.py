"""
Phase 1 & Phase 2 Recommendation Endpoints

Phase 1 (0-20 swipes): Show 20 top-funded Tier 2 startups with category variety
Phase 2 (20+ swipes): Show 100 recommendations (70% preference-based + 30% diverse)
"""

import random
import json
from typing import List, Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

from database import get_db
from models_startup import Startup
from models import Vote

router = APIRouter(prefix="/startups", tags=["startups"])


def parse_array(value):
    """Parse JSON array from database"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except:
            return [x.strip() for x in value.split(',')]
    return []


def parse_topics(value):
    """Parse AXA topics/use cases from JSON"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            topics = json.loads(value)
            return topics if isinstance(topics, list) else []
        except:
            return []
    return []


def startup_to_dict(startup: Startup) -> dict:
    """Convert Startup ORM object to dict for JSON serialization"""
    return {
        'id': startup.id,
        'name': startup.company_name,
        'shortDescription': startup.shortDescription,
        'description': startup.description,
        'logoUrl': startup.logoUrl,
        'website': startup.website,
        'topics': parse_array(startup.topics),
        'tech': parse_array(startup.tech),
        'maturity': startup.maturity,
        'maturity_score': startup.maturity_score,
        'totalFunding': startup.total_funding,
        'total_funding': startup.total_funding,
        'employees': startup.employees,
        'billingCity': startup.billingCity,
        'billingCountry': startup.billingCountry,
        'dateFounded': startup.dateFounded.isoformat() if startup.dateFounded else None,
        'currentInvestmentStage': startup.funding_stage,
        'funding_stage': startup.funding_stage,
        'company_name': startup.company_name,
        'Company Name': startup.company_name,
        'Company Description': startup.company_description,
        'Headquarter Country': startup.company_country,
        'value_proposition': startup.value_proposition,
        'core_product': startup.core_product,
        'target_customers': startup.target_customers,
        'problem_solved': startup.problem_solved,
        'key_differentiator': startup.key_differentiator,
        'business_model': startup.business_model,
        'vp_competitors': startup.vp_competitors,
        'extracted_product': startup.extracted_product,
        'extracted_market': startup.extracted_market,
        'extracted_competitors': startup.extracted_competitors,
        'axa_evaluation_date': startup.axa_evaluation_date,
        'axa_overall_score': startup.axa_overall_score,
        'axa_priority_tier': startup.axa_priority_tier,
        'axa_can_use_as_provider': startup.axa_can_use_as_provider,
        'axa_business_leverage': startup.axa_business_leverage,
        'axa_primary_topic': startup.axa_primary_topic,
        'axa_use_cases': parse_array(startup.axa_use_cases),
    }


def calculate_recommendation_score(
    candidate: Startup,
    preference_topics: Set[str],
    preference_maturity: dict,
    preference_use_cases: Set[str]
) -> float:
    """
    Score a startup candidate based on quality and user preferences
    
    Scoring hierarchy (in order of importance):
    1. AXA Overall Score: Foundation quality (0-100 scale)
    2. Topic match: +20 per match
    3. Use case match: +10 per match
    4. Maturity match: +5
    
    Final score = axa_overall_score * 100 + preference_bonus
    This ensures highest quality startups always ranked first
    """
    # Foundation: AXA overall score (most important)
    base_score = (candidate.axa_overall_score or 0) * 100
    
    # Preference bonuses (secondary factors)
    preference_bonus = 0
    
    # Topic matching
    candidate_topics = set(parse_array(candidate.topics))
    topic_matches = len(candidate_topics & preference_topics)
    preference_bonus += topic_matches * 20
    
    # Use case matching
    candidate_use_cases = set(parse_array(candidate.axa_use_cases))
    use_case_matches = len(candidate_use_cases & preference_use_cases)
    preference_bonus += use_case_matches * 10
    
    # Maturity matching
    if candidate.maturity and candidate.maturity in preference_maturity:
        preference_bonus += 5
    
    return base_score + preference_bonus


@router.get("/phase1")
def get_phase1_startups(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get Phase 1 startups: 10 Agentic with highest rise score + 10 random from other topics
    
    Rules:
    - 10 startups: Agentic topic, sorted by rise_score descending
    - 10 startups: Random from all other topics
    - Exclude: Any startup user has already voted on
    
    Returns:
    {
        "startups": [Startup, ...],
        "phase": 1,
        "total_count": 20,
        "phase_transition_at": 20
    }
    """
    import random
    
    # Get user's voted IDs
    user_votes = db.query(Vote).filter(Vote.userId == user_id).all()
    voted_ids = {v.startupId for v in user_votes}
    
    # Get all startups, excluding voted ones
    query = db.query(Startup)
    if voted_ids:
        query = query.filter(~Startup.id.in_(voted_ids))
    
    all_startups = query.all()
    
    if not all_startups:
        raise HTTPException(status_code=404, detail="No startups available")
    
    # Separate Agentic from others
    agentic_startups = []
    other_startups = []
    
    for startup in all_startups:
        topics = parse_array(startup.topics)
        if any('agentic' in t.lower() or 'ai' in t.lower() and 'agent' in t.lower() for t in topics):
            agentic_startups.append(startup)
        else:
            other_startups.append(startup)
    
    # Get top 10 Agentic by axa_overall_score (highest first)
    agentic_sorted = sorted(
        agentic_startups,
        key=lambda s: s.axa_overall_score or 0,
        reverse=True
    )[:10]
    
    # Get 10 other topics, sorted by axa_overall_score (highest first)
    other_sorted = sorted(
        other_startups,
        key=lambda s: s.axa_overall_score or 0,
        reverse=True
    )[:10]
    
    result = agentic_sorted + other_sorted
    
    return {
        "startups": [startup_to_dict(s) for s in result[:limit]],
        "phase": 1,
        "total_count": len(result[:limit]),
        "phase_transition_at": 20,
        "description": "10 Agentic (highest rise_score) + 10 random from other topics"
    }


@router.get("/phase2")
def get_phase2_startups(
    user_id: str,
    exclude_ids: Optional[str] = Query(None),
    diversity_ratio: float = 0.3,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get Phase 2 startups: Personalized recommendations with balanced variety
    
    Rules:
    - Base: All available startups (Tier 2, 3, 4, Unrated)
    - Filtering: Exclude startups user has already voted on
    - Recommendation Strategy: 50/50 Balance
        * 50% Preference-based: Highest scored matches to user's topics/use-cases/maturity
        * 50% Diverse: Variety grouped by topic/use-case/maturity (highest scored in each group)
    - Scoring algorithm for preference-based:
        * axa_overall_score * 100 (foundation)
        * Topic match: +20 per match
        * Use case match: +10 per match
        * Maturity match: +5 per match
    
    Returns:
    {
        "startups": [Startup, ...],
        "phase": 2,
        "total_count": 100,
        "tier_used": "Tier 2: High" | "Tier 3: Medium" | "Tier 4: Low" | "Unrated",
        "breakdown": {
            "preference_based": 50,
            "diverse": 50
        }
    }
    """
    
    # Parse exclude IDs
    excluded_ids = set()
    if exclude_ids:
        try:
            excluded_ids = {int(x) for x in exclude_ids.split(',') if x.strip()}
        except ValueError:
            pass
    
    # Add user's voted IDs to excluded
    user_votes = db.query(Vote).filter(Vote.userId == user_id).all()
    for vote in user_votes:
        excluded_ids.add(vote.startupId)
    
    # Get user's interested startups to extract preferences
    interested_votes = [v for v in user_votes if v.interested]
    interested_startups = []
    
    if interested_votes:
        interested_ids = {v.startupId for v in interested_votes}
        interested_startups = db.query(Startup).filter(
            Startup.id.in_(interested_ids)
        ).all()
    
    # Extract preference signals
    preference_topics = set()
    preference_maturity = {}
    preference_use_cases = set()
    
    for startup in interested_startups:
        # Topics
        topics = parse_array(startup.topics)
        preference_topics.update(topics)
        
        # Maturity
        if startup.maturity:
            preference_maturity[startup.maturity] = \
                preference_maturity.get(startup.maturity, 0) + 1
        
        # Use cases
        use_cases = parse_array(startup.axa_use_cases)
        preference_use_cases.update(use_cases)
    
    # Get all unseen Tier 2 startups, or fallback to Tier 3 if Tier 2 is exhausted
    unseen_startups = db.query(Startup).filter(
        and_(
            Startup.axa_priority_tier.like('%Tier 2%'),
            ~Startup.id.in_(excluded_ids) if excluded_ids else True
        )
    ).all()
    
    # If no Tier 2 available, fallback to Tier 3
    if not unseen_startups:
        unseen_startups = db.query(Startup).filter(
            and_(
                Startup.axa_priority_tier.like('%Tier 3%'),
                ~Startup.id.in_(excluded_ids) if excluded_ids else True
            )
        ).all()
    
    # Final fallback to Tier 4 if needed
    if not unseen_startups:
        unseen_startups = db.query(Startup).filter(
            and_(
                Startup.axa_priority_tier.like('%Tier 4%'),
                ~Startup.id.in_(excluded_ids) if excluded_ids else True
            )
        ).all()
    
    # Last resort fallback to unrated startups
    if not unseen_startups:
        unseen_startups = db.query(Startup).filter(
            and_(
                Startup.axa_priority_tier == None,
                ~Startup.id.in_(excluded_ids) if excluded_ids else True
            )
        ).all()
    
    if not unseen_startups:
        raise HTTPException(status_code=404, detail="No more startups available")
    
    # Score candidates (if user has preferences)
    if interested_startups:
        # Split: 50% preference-based (high scores) + 50% diverse (variety)
        pref_count = max(1, int(limit * 0.5))
        
        # 1. GET PREFERENCE-BASED (50%): Highest scored matches to user preferences
        scored = []
        for candidate in unseen_startups:
            score = calculate_recommendation_score(
                candidate,
                preference_topics,
                preference_maturity,
                preference_use_cases
            )
            scored.append((candidate, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        preference_based = [s[0] for s in scored[:pref_count]]
        
        # 2. GET DIVERSE (50%): Balanced variety grouped by topic/use-case/maturity
        # Exclude startups already in preference_based
        remaining = [s for s in unseen_startups if s not in preference_based]
        
        if remaining:
            # Group remaining startups by different dimensions for variety
            diverse_pool = []
            
            # Group by topic - pick top scored from each unique topic
            topics_seen = {}
            for startup in remaining:
                topics = parse_array(startup.topics)
                for topic in topics:
                    if topic not in topics_seen:
                        topics_seen[topic] = []
                    topics_seen[topic].append(startup)
            
            # Sort each topic group by score, take top 1 from each
            for topic in sorted(topics_seen.keys()):
                group = topics_seen[topic]
                # Sort by axa_overall_score (highest first)
                group.sort(key=lambda s: s.axa_overall_score or 0, reverse=True)
                if group and group[0] not in diverse_pool:
                    diverse_pool.append(group[0])
            
            # If we need more variety, add high-scoring startups from different use cases
            use_cases_seen = {}
            for startup in remaining:
                if startup not in diverse_pool:
                    use_cases = parse_array(startup.axa_use_cases)
                    for uc in use_cases:
                        if uc not in use_cases_seen:
                            use_cases_seen[uc] = []
                        use_cases_seen[uc].append(startup)
            
            # Sort each use case group by score, take top 1 from each
            for uc in sorted(use_cases_seen.keys()):
                group = use_cases_seen[uc]
                group.sort(key=lambda s: s.axa_overall_score or 0, reverse=True)
                if group and group[0] not in diverse_pool and len(diverse_pool) < pref_count:
                    diverse_pool.append(group[0])
            
            # If still need more, add from different maturity levels
            maturity_seen = {}
            for startup in remaining:
                if startup not in diverse_pool:
                    if startup.maturity not in maturity_seen:
                        maturity_seen[startup.maturity] = []
                    maturity_seen[startup.maturity].append(startup)
            
            # Sort each maturity group by score, take top 1 from each
            for maturity in sorted(maturity_seen.keys()):
                group = maturity_seen[maturity]
                group.sort(key=lambda s: s.axa_overall_score or 0, reverse=True)
                if group and group[0] not in diverse_pool and len(diverse_pool) < pref_count:
                    diverse_pool.append(group[0])
            
            # If still need more, just add remaining high-scored startups
            if len(diverse_pool) < pref_count:
                remaining_sorted = [s for s in remaining if s not in diverse_pool]
                remaining_sorted.sort(key=lambda s: s.axa_overall_score or 0, reverse=True)
                diverse_pool.extend(remaining_sorted[:pref_count - len(diverse_pool)])
            
            diverse = diverse_pool[:pref_count]
        else:
            diverse = []
    else:
        # No preferences yet, return balanced mix: 50% highest scored, 50% variety
        unseen_sorted = sorted(unseen_startups, key=lambda s: s.axa_overall_score or 0, reverse=True)
        pref_count = max(1, int(limit * 0.5))
        preference_based = unseen_sorted[:pref_count]
        
        # For diverse, group by topic and take top from each
        diverse_pool = []
        topics_seen = {}
        for startup in unseen_startups:
            if startup not in preference_based:
                topics = parse_array(startup.topics)
                for topic in topics:
                    if topic not in topics_seen:
                        topics_seen[topic] = []
                    topics_seen[topic].append(startup)
        
        for topic in sorted(topics_seen.keys()):
            group = topics_seen[topic]
            group.sort(key=lambda s: s.axa_overall_score or 0, reverse=True)
            if group and group[0] not in diverse_pool and len(diverse_pool) < pref_count:
                diverse_pool.append(group[0])
        
        if len(diverse_pool) < pref_count:
            remaining_sorted = [s for s in unseen_sorted if s not in preference_based and s not in diverse_pool]
            diverse_pool.extend(remaining_sorted[:pref_count - len(diverse_pool)])
        
        diverse = diverse_pool[:pref_count]
    
    # Combine and return
    result = preference_based + diverse
    
    # Determine which tier was used
    tier_used = "Tier 2: High"
    if not db.query(Startup).filter(
        and_(
            Startup.axa_priority_tier.like('%Tier 2%'),
            ~Startup.id.in_(excluded_ids) if excluded_ids else True
        )
    ).count():
        if db.query(Startup).filter(
            and_(
                Startup.axa_priority_tier.like('%Tier 3%'),
                ~Startup.id.in_(excluded_ids) if excluded_ids else True
            )
        ).count():
            tier_used = "Tier 3: Medium"
        elif db.query(Startup).filter(
            and_(
                Startup.axa_priority_tier.like('%Tier 4%'),
                ~Startup.id.in_(excluded_ids) if excluded_ids else True
            )
        ).count():
            tier_used = "Tier 4: Low"
        else:
            tier_used = "Unrated"
    
    return {
        "startups": [startup_to_dict(s) for s in result[:limit]],
        "phase": 2,
        "total_count": len(result[:limit]),
        "tier_used": tier_used,
        "breakdown": {
            "preference_based": len(preference_based),
            "diverse": len(diverse)
        },
        "user_preference_signals": {
            "topics": list(preference_topics),
            "maturity_levels": list(preference_maturity.keys()),
            "use_cases": list(preference_use_cases)
        }
    }


@router.get("/stats")
def get_startup_stats(db: Session = Depends(get_db)) -> dict:
    """Get overall startup statistics"""
    
    total = db.query(Startup).count()
    tier2 = db.query(Startup).filter(
        Startup.axa_priority_tier.like('%Tier 2%')
    ).count()
    
    # Use cases distribution
    tier2_startups = db.query(Startup).filter(
        Startup.axa_priority_tier.like('%Tier 2%')
    ).all()
    
    use_cases_count = {}
    for startup in tier2_startups:
        use_cases = parse_array(startup.axa_use_cases)
        for use_case in use_cases:
            use_cases_count[use_case] = use_cases_count.get(use_case, 0) + 1
    
    return {
        "total_startups": total,
        "tier2_startups": tier2,
        "use_cases_distribution": use_cases_count,
        "data_completeness": {
            "have_extracted_product": db.query(Startup).filter(
                Startup.extracted_product.isnot(None)
            ).count(),
            "have_extracted_market": db.query(Startup).filter(
                Startup.extracted_market.isnot(None)
            ).count(),
            "have_funding": db.query(Startup).filter(
                Startup.total_funding.isnot(None)
            ).count()
        }
    }
