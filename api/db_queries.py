"""
Database query layer for normalized tables.
Replaces JSON file reads with SQL queries.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# ============================================
# Startup Queries
# ============================================

def get_all_startups(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all startups from database."""
    query = text("""
        SELECT * FROM startups 
        ORDER BY id 
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"limit": limit, "skip": skip})
    return [dict(row._mapping) for row in result]

def get_startup_by_id(db: Session, startup_id: str) -> Optional[Dict]:
    """Get startup by ID."""
    query = text("""
        SELECT * FROM startups 
        WHERE id = :id OR company_name = :id
        LIMIT 1
    """)
    result = db.execute(query, {"id": startup_id}).first()
    return dict(result._mapping) if result else None

def get_startup_by_name(db: Session, company_name: str) -> Optional[Dict]:
    """Get startup by company name (exact match or fuzzy)."""
    # Try exact match first
    query = text("""
        SELECT * FROM startups 
        WHERE company_name = :name
        LIMIT 1
    """)
    result = db.execute(query, {"name": company_name}).first()
    
    if result:
        return dict(result._mapping)
    
    # Try fuzzy match
    query = text("""
        SELECT * FROM startups 
        WHERE company_name LIKE :name
        ORDER BY company_name
        LIMIT 1
    """)
    result = db.execute(query, {"name": f"%{company_name}%"}).first()
    return dict(result._mapping) if result else None

def get_enriched_startups(db: Session, limit: int = 100) -> List[Dict]:
    """Get only enriched startups."""
    query = text("""
        SELECT * FROM startups 
        WHERE is_enriched = 1 
        ORDER BY last_enriched_date DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]

def search_startups(
    db: Session,
    query_text: Optional[str] = None,
    country: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Search startups with flexible filters.
    
    Args:
        db: Database session
        query_text: Search in company name and description
        country: Filter by country
        industry: Filter by industry
        limit: Maximum results
        
    Returns:
        List of matching startups
    """
    conditions = []
    params = {"limit": limit}
    
    if query_text:
        conditions.append("""
            (company_name LIKE :query 
             OR company_description LIKE :query
             OR primary_industry LIKE :query)
        """)
        params["query"] = f"%{query_text}%"
    
    if country:
        conditions.append("company_country LIKE :country")
        params["country"] = f"%{country}%"
    
    if industry:
        conditions.append("primary_industry LIKE :industry")
        params["industry"] = f"%{industry}%"
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = text(f"""
        SELECT * FROM startups 
        WHERE {where_clause}
        ORDER BY company_name
        LIMIT :limit
    """)
    
    result = db.execute(query, params)
    return [dict(row._mapping) for row in result]


def search_startups_by_industry(
    db: Session,
    industry: str,
    limit: int = 100
) -> List[Dict]:
    """
    Search startups by industry/sector
    
    Args:
        db: Database session
        industry: Industry to search for (e.g., "AI", "FinTech", "HealthTech")
        limit: Maximum results
        
    Returns:
        List of startups in that industry
    """
    query = text("""
        SELECT * FROM startups 
        WHERE primary_industry LIKE :industry
           OR secondary_industry LIKE :industry
           OR company_description LIKE :industry
        ORDER BY company_name
        LIMIT :limit
    """)
    
    params = {"industry": f"%{industry}%", "limit": limit}
    result = db.execute(query, params)
    return [dict(row._mapping) for row in result]


def count_startups(db: Session) -> int:
    conditions = []
    params = {"limit": limit}
    
    if query_text:
        conditions.append("(company_name LIKE :query OR company_description LIKE :query)")
        params["query"] = f"%{query_text}%"
    
    if country:
        conditions.append("company_country = :country")
        params["country"] = country
    
    if industry:
        conditions.append("primary_industry = :industry")
        params["industry"] = industry
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = text(f"""
        SELECT * FROM startups 
        WHERE {where_clause}
        LIMIT :limit
    """)
    result = db.execute(query, params)
    return [dict(row._mapping) for row in result]

def count_startups(db: Session) -> int:
    """Get total startup count."""
    result = db.execute(text("SELECT COUNT(*) as count FROM startups")).first()
    return result.count if result else 0

def get_enrichment_stats(db: Session) -> Dict[str, Any]:
    """Get enrichment statistics."""
    query = text("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_enriched = 1 THEN 1 ELSE 0 END) as enriched,
            SUM(CASE WHEN logoUrl IS NOT NULL THEN 1 ELSE 0 END) as with_logo,
            SUM(CASE WHEN total_funding IS NOT NULL THEN 1 ELSE 0 END) as with_cb_insights_funding
        FROM startups
    """)
    result = db.execute(query).first()
    
    return {
        "total_startups": result.total,
        "enriched_count": result.enriched,
        "with_logo": result.with_logo,
        "with_cb_insights_funding": result.with_cb_insights_funding,
        "enrichment_percentage": round(result.enriched / result.total * 100, 2) if result.total > 0 else 0,
        "funding_coverage": round(result.with_cb_insights_funding / result.total * 100, 2) if result.total > 0 else 0
    }

def get_funding_stats(db: Session) -> Dict[str, Any]:
    """Get funding statistics from CB Insights data."""
    query = text("""
        SELECT 
            COUNT(*) as total_with_funding,
            AVG(total_funding) as avg_funding,
            MAX(total_funding) as max_funding,
            MIN(total_funding) as min_funding,
            SUM(total_funding) as total_capital_raised,
            COUNT(DISTINCT simplified_round) as unique_round_types
        FROM startups
        WHERE total_funding IS NOT NULL
    """)
    result = db.execute(query).first()
    
    return {
        "total_with_funding": result.total_with_funding or 0,
        "avg_funding_millions": round(result.avg_funding, 2) if result.avg_funding else None,
        "max_funding_millions": round(result.max_funding, 2) if result.max_funding else None,
        "min_funding_millions": round(result.min_funding, 2) if result.min_funding else None,
        "total_capital_raised_millions": round(result.total_capital_raised, 2) if result.total_capital_raised else None,
    }

def get_funding_by_stage(db: Session) -> Dict[str, Any]:
    """Get funding statistics by stage."""
    query = text("""
        SELECT 
            simplified_round,
            COUNT(*) as count,
            AVG(amount_millions) as avg_amount,
            SUM(amount_millions) as total_amount
        FROM funding_rounds
        WHERE amount_millions IS NOT NULL
        GROUP BY simplified_round
        ORDER BY total_amount DESC
    """)
    
    results = db.execute(query).fetchall()
    
    return {
        "by_stage": [
            {
                "stage": row.simplified_round,
                "count": row.count,
                "avg_amount_millions": round(row.avg_amount, 2) if row.avg_amount else None,
                "total_amount_millions": round(row.total_amount, 2) if row.total_amount else None,
            }
            for row in results
        ]
    }

# ============================================
# Calendar Event Queries
# ============================================

def get_calendar_events(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get calendar events."""
    query = text("""
        SELECT 
            e.*,
            GROUP_CONCAT(ea.attendee) as attendees
        FROM calendar_events e
        LEFT JOIN calendar_event_attendees ea ON e.id = ea.event_id
        GROUP BY e.id
        ORDER BY e.start_time
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"limit": limit, "skip": skip})
    
    events = []
    for row in result:
        event_dict = dict(row._mapping)
        # Convert attendees string to list
        if event_dict.get('attendees'):
            event_dict['attendees'] = event_dict['attendees'].split(',')
        else:
            event_dict['attendees'] = []
        events.append(event_dict)
    
    return events

def get_events_by_date_range(
    db: Session,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """Get events in date range."""
    query = text("""
        SELECT 
            e.*,
            GROUP_CONCAT(ea.attendee) as attendees
        FROM calendar_events e
        LEFT JOIN calendar_event_attendees ea ON e.id = ea.event_id
        WHERE e.start_time BETWEEN :start_date AND :end_date
        GROUP BY e.id
        ORDER BY e.start_time
    """)
    result = db.execute(query, {"start_date": start_date, "end_date": end_date})
    
    events = []
    for row in result:
        event_dict = dict(row._mapping)
        if event_dict.get('attendees'):
            event_dict['attendees'] = event_dict['attendees'].split(',')
        else:
            event_dict['attendees'] = []
        events.append(event_dict)
    
    return events

# ============================================
# Rating Queries
# ============================================

def get_startup_ratings(db: Session, user_id: Optional[str] = None) -> List[Dict]:
    """Get startup ratings, optionally filtered by user."""
    if user_id:
        query = text("""
            SELECT * FROM startup_ratings 
            WHERE user_id = :user_id
        """)
        result = db.execute(query, {"user_id": user_id})
    else:
        query = text("SELECT * FROM startup_ratings")
        result = db.execute(query)
    
    return [dict(row._mapping) for row in result]

def add_startup_rating(
    db: Session,
    startup_id: str,
    user_id: str,
    rating: int
):
    """Add or update startup rating."""
    query = text("""
        INSERT INTO startup_ratings (startup_id, user_id, rating)
        VALUES (:startup_id, :user_id, :rating)
        ON CONFLICT(startup_id, user_id) 
        DO UPDATE SET rating = :rating
    """)
    db.execute(query, {
        "startup_id": startup_id,
        "user_id": user_id,
        "rating": rating
    })
    db.commit()

def get_average_ratings(db: Session, limit: int = 100) -> List[Dict]:
    """Get average ratings per startup."""
    query = text("""
        SELECT 
            startup_id,
            AVG(rating) as avg_rating,
            COUNT(user_id) as num_ratings
        FROM startup_ratings
        GROUP BY startup_id
        ORDER BY avg_rating DESC, num_ratings DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]

# ============================================
# Message Queries
# ============================================

def get_ai_assistant_messages(db: Session, limit: int = 100) -> List[Dict]:
    """Get AI assistant messages."""
    query = text("""
        SELECT * FROM ai_assistant_messages 
        ORDER BY timestamp DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]

def add_ai_message(
    db: Session,
    message_id: str,
    role: str,
    content: str,
    timestamp: int,
    table: str = "ai_assistant_messages"
):
    """Add message to AI chat tables."""
    query = text(f"""
        INSERT OR REPLACE INTO {table} (id, role, content, timestamp)
        VALUES (:id, :role, :content, :timestamp)
    """)
    db.execute(query, {
        "id": message_id,
        "role": role,
        "content": content,
        "timestamp": timestamp
    })
    db.commit()

# ============================================
# Idea Queries
# ============================================

def get_ideas(db: Session) -> List[Dict]:
    """Get all ideas with tags."""
    query = text("""
        SELECT 
            i.*,
            GROUP_CONCAT(it.tag) as tags
        FROM ideas i
        LEFT JOIN idea_tags it ON i.id = it.idea_id
        GROUP BY i.id
        ORDER BY i.timestamp DESC
    """)
    result = db.execute(query)
    
    ideas = []
    for row in result:
        idea_dict = dict(row._mapping)
        if idea_dict.get('tags'):
            idea_dict['tags'] = idea_dict['tags'].split(',')
        else:
            idea_dict['tags'] = []
        ideas.append(idea_dict)
    
    return ideas

def add_idea(
    db: Session,
    idea_id: str,
    name: str,
    title: str,
    category: str,
    description: str,
    tags: List[str],
    timestamp: int
):
    """Add new idea."""
    # Insert idea
    query = text("""
        INSERT INTO ideas (id, name, title, category, description, timestamp)
        VALUES (:id, :name, :title, :category, :description, :timestamp)
    """)
    db.execute(query, {
        "id": idea_id,
        "name": name,
        "title": title,
        "category": category,
        "description": description,
        "timestamp": timestamp
    })
    
    # Insert tags
    for tag in tags:
        tag_query = text("""
            INSERT OR IGNORE INTO idea_tags (idea_id, tag)
            VALUES (:idea_id, :tag)
        """)
        db.execute(tag_query, {"idea_id": idea_id, "tag": tag})
    
    db.commit()

# ============================================
# Metadata Queries
# ============================================

def get_current_user(db: Session) -> Optional[str]:
    """Get current user ID."""
    query = text("SELECT id FROM current_user LIMIT 1")
    result = db.execute(query).first()
    return result.id if result else None

def set_current_user(db: Session, user_id: str):
    """Set current user ID."""
    query = text("""
        INSERT OR REPLACE INTO current_user (id, updated_at)
        VALUES (:id, :updated_at)
    """)
    db.execute(query, {
        "id": user_id,
        "updated_at": datetime.utcnow().isoformat()
    })
    db.commit()

def get_data_version(db: Session) -> Optional[str]:
    """Get data version."""
    query = text("SELECT version FROM data_version LIMIT 1")
    result = db.execute(query).first()
    return result.version if result else None

def get_finished_users(db: Session) -> List[str]:
    """Get list of finished user IDs."""
    query = text("SELECT user_id FROM finished_users")
    result = db.execute(query)
    return [row.user_id for row in result]

def add_finished_user(db: Session, user_id: str):
    """Mark user as finished."""
    query = text("""
        INSERT OR IGNORE INTO finished_users (user_id)
        VALUES (:user_id)
    """)
    db.execute(query, {"user_id": user_id})
    db.commit()

# ============================================
# Auroral Theme Queries
# ============================================

def get_auroral_themes(db: Session) -> Dict:
    """Get auroral theme configuration."""
    # Get main info
    info_query = text("SELECT * FROM auroral_info WHERE id = 1")
    info = db.execute(info_query).first()
    
    # Get themes with colors
    themes_query = text("""
        SELECT 
            t.id,
            t.name,
            t.hours,
            t.mood,
            GROUP_CONCAT(tc.color) as colors
        FROM auroral_themes t
        LEFT JOIN auroral_theme_colors tc ON t.id = tc.theme_id
        GROUP BY t.id
        ORDER BY t.id
    """)
    themes_result = db.execute(themes_query)
    
    themes = []
    for row in themes_result:
        theme_dict = dict(row._mapping)
        if theme_dict.get('colors'):
            theme_dict['colors'] = theme_dict['colors'].split(',')
        else:
            theme_dict['colors'] = []
        themes.append(theme_dict)
    
    return {
        "description": info.description if info else None,
        "last_viewed": info.last_viewed if info else None,
        "themes": themes
    }

# ============================================
# Attendee Queries
# ============================================

def search_attendees_by_name(db: Session, name: str, limit: int = 10) -> List[Dict]:
    """Search attendees by name"""
    from models import Attendee
    
    results = db.query(Attendee).filter(
        Attendee.name.ilike(f"%{name}%")
    ).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "title": a.title,
            "country": a.country,
            "city": a.city,
            "company_name": a.company_name,
            "company_type": a.company_type,
            "bio": a.bio,
            "linkedin": a.linkedin,
            "profile_link": a.profile_link,
            "industry": a.industry,
            "occupation": a.occupation,
        }
        for a in results
    ]

def search_attendees_by_company(db: Session, company_name: str, limit: int = 10) -> List[Dict]:
    """Search attendees by company name"""
    from models import Attendee
    
    results = db.query(Attendee).filter(
        Attendee.company_name.ilike(f"%{company_name}%")
    ).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "title": a.title,
            "country": a.country,
            "company_name": a.company_name,
            "company_type": a.company_type,
            "bio": a.bio,
            "linkedin": a.linkedin,
            "profile_link": a.profile_link,
        }
        for a in results
    ]

def search_attendees_by_country(db: Session, country: str, limit: int = 20) -> List[Dict]:
    """Search attendees by country"""
    from models import Attendee
    
    results = db.query(Attendee).filter(
        Attendee.country.ilike(f"%{country}%")
    ).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "title": a.title,
            "country": a.country,
            "city": a.city,
            "company_name": a.company_name,
            "linkedin": a.linkedin,
        }
        for a in results
    ]

def search_attendees_by_occupation(db: Session, occupation: str, limit: int = 10) -> List[Dict]:
    """Search attendees by occupation"""
    from models import Attendee
    
    # Search in occupation JSON array
    results = db.query(Attendee).filter(
        Attendee.occupation.astext.ilike(f"%{occupation}%")
    ).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "title": a.title,
            "country": a.country,
            "company_name": a.company_name,
            "occupation": a.occupation,
            "linkedin": a.linkedin,
        }
        for a in results
    ]

def get_attendee_by_id(db: Session, attendee_id: str) -> Optional[Dict]:
    """Get attendee by ID"""
    from models import Attendee
    
    attendee = db.query(Attendee).filter(Attendee.id == attendee_id).first()
    
    if not attendee:
        return None
    
    return {
        "id": attendee.id,
        "name": attendee.name,
        "title": attendee.title,
        "country": attendee.country,
        "city": attendee.city,
        "linkedin": attendee.linkedin,
        "twitter": attendee.twitter,
        "bio": attendee.bio,
        "industry": attendee.industry,
        "occupation": attendee.occupation,
        "company_name": attendee.company_name,
        "company_type": attendee.company_type,
        "company_country": attendee.company_country,
        "company_city": attendee.company_city,
        "website": attendee.website,
        "company_linkedin": attendee.company_linkedin,
        "company_description": attendee.company_description,
        "profile_link": attendee.profile_link,
    }

def get_all_attendees(db: Session, skip: int = 0, limit: int = 100) -> List[Dict]:
    """Get all attendees"""
    from models import Attendee
    
    results = db.query(Attendee).offset(skip).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "name": a.name,
            "title": a.title,
            "country": a.country,
            "city": a.city,
            "company_name": a.company_name,
            "company_type": a.company_type,
            "linkedin": a.linkedin,
        }
        for a in results
    ]

def count_attendees(db: Session) -> int:
    """Count total attendees"""
    from models import Attendee
    
    return db.query(Attendee).count()


# ============================================
# AXA Evaluation Queries
# ============================================

def get_startups_by_axa_tier(db: Session, tier: str, limit: int = 100, skip: int = 0) -> List[Dict]:
    """Get startups by AXA priority tier (Tier 1, Tier 2, Tier 3, Tier 4)"""
    query = text("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier, 
               axa_primary_topic, axa_use_cases, axa_can_use_as_provider
        FROM startups
        WHERE axa_priority_tier LIKE :tier
        ORDER BY axa_overall_score DESC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {"tier": f"%{tier}%", "limit": limit, "skip": skip})
    return [dict(row._mapping) for row in result]

def get_startups_by_axa_score_range(
    db: Session, 
    min_score: float = 0, 
    max_score: float = 100, 
    limit: int = 100,
    skip: int = 0
) -> List[Dict]:
    """Get startups within an AXA score range"""
    query = text("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier, 
               axa_primary_topic, axa_use_cases, axa_can_use_as_provider
        FROM startups
        WHERE axa_overall_score BETWEEN :min_score AND :max_score
        ORDER BY axa_overall_score DESC
        LIMIT :limit OFFSET :skip
    """)
    result = db.execute(query, {
        "min_score": min_score, 
        "max_score": max_score, 
        "limit": limit, 
        "skip": skip
    })
    return [dict(row._mapping) for row in result]

def get_startup_axa_evaluation(db: Session, startup_id: int) -> Optional[Dict]:
    """Get full AXA evaluation for a startup"""
    query = text("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier,
               axa_evaluation_date, axa_primary_topic, axa_use_cases,
               axa_can_use_as_provider, axa_business_leverage
        FROM startups
        WHERE id = :id
    """)
    result = db.execute(query, {"id": startup_id}).first()
    
    if not result:
        return None
    
    return dict(result._mapping)

def get_axa_tier_statistics(db: Session) -> Dict[str, Any]:
    """Get statistics about AXA evaluations by tier"""
    query = text("""
        SELECT 
            axa_priority_tier as tier,
            COUNT(*) as total_startups,
            ROUND(AVG(axa_overall_score), 1) as avg_score,
            MIN(axa_overall_score) as min_score,
            MAX(axa_overall_score) as max_score,
            SUM(CASE WHEN cb_insights_id IS NOT NULL THEN 1 ELSE 0 END) as with_cb_id,
            ROUND(100.0 * SUM(CASE WHEN cb_insights_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as cb_id_coverage
        FROM startups
        WHERE axa_priority_tier IS NOT NULL
        GROUP BY axa_priority_tier
        ORDER BY tier
    """)
    
    result = db.execute(query)
    stats = {}
    
    for row in result:
        tier = dict(row._mapping)['tier']
        stats[tier] = {
            'total_startups': dict(row._mapping)['total_startups'],
            'avg_score': dict(row._mapping)['avg_score'],
            'min_score': dict(row._mapping)['min_score'],
            'max_score': dict(row._mapping)['max_score'],
            'with_cb_insights_id': dict(row._mapping)['with_cb_id'],
            'cb_insights_coverage_pct': dict(row._mapping)['cb_id_coverage']
        }
    
    return stats

def search_startups_by_axa_category(
    db: Session, 
    category: str, 
    matched_only: bool = True,
    limit: int = 100,
    skip: int = 0
) -> List[Dict]:
    """Search startups by AXA primary topic or use cases"""
    query = text("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier,
               axa_primary_topic, axa_use_cases, axa_can_use_as_provider
        FROM startups
        WHERE axa_primary_topic LIKE :category_pattern
           OR axa_use_cases LIKE :category_pattern
        ORDER BY axa_overall_score DESC
        LIMIT :limit OFFSET :skip
    """)
    
    category_pattern = f'%{category}%'
    
    result = db.execute(query, {
        "category_pattern": category_pattern,
        "limit": limit,
        "skip": skip
    })
    
    return [dict(row._mapping) for row in result]

def count_tier_1_with_cb_insights(db: Session) -> Dict[str, int]:
    """Count Tier 1 startups with and without CB Insights IDs"""
    query = text("""
        SELECT 
            SUM(CASE WHEN cb_insights_id IS NOT NULL THEN 1 ELSE 0 END) as with_id,
            SUM(CASE WHEN cb_insights_id IS NULL THEN 1 ELSE 0 END) as without_id,
            COUNT(*) as total
        FROM startups
        WHERE axa_priority_tier LIKE '%Tier 1%'
    """)
    
    result = db.execute(query).first()
    return {
        'with_cb_insights_id': result[0] or 0,
        'without_cb_insights_id': result[1] or 0,
        'total': result[2] or 0
    }
