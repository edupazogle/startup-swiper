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
    """Search startups with filters."""
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
            SUM(CASE WHEN totalFunding IS NOT NULL THEN 1 ELSE 0 END) as with_funding,
            SUM(CASE WHEN logoUrl IS NOT NULL THEN 1 ELSE 0 END) as with_logo
        FROM startups
    """)
    result = db.execute(query).first()
    
    return {
        "total_startups": result.total,
        "enriched_count": result.enriched,
        "with_funding": result.with_funding,
        "with_logo": result.with_logo,
        "enrichment_percentage": round(result.enriched / result.total * 100, 2) if result.total > 0 else 0
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
