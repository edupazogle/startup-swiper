"""
Topics and Use Cases API endpoints for hierarchical filtering.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text

router = APIRouter(prefix="/topics-usecases", tags=["topics-usecases"])


@router.get("/topics")
def get_all_topics(db: Session = Depends(get_db)):
    """
    Get all topics with their associated use cases.
    
    Returns:
    {
        "topics": [
            {
                "id": 1,
                "name": "AI - Software development",
                "use_cases": [
                    {"id": 1, "name": "Code Generation", "order_index": 1},
                    ...
                ]
            },
            ...
        ]
    }
    """
    try:
        # Get all topics ordered by order_index
        topics_result = db.execute(text(
            "SELECT id, name FROM topics ORDER BY order_index"
        )).fetchall()
        
        topics_with_usecases = []
        
        for topic_id, topic_name in topics_result:
            # Get use cases for this topic
            usecases_result = db.execute(text(
                "SELECT id, name FROM use_cases WHERE topic_id = :topic_id ORDER BY order_index"
            ), {"topic_id": topic_id}).fetchall()
            
            use_cases = [
                {"id": uc_id, "name": uc_name}
                for uc_id, uc_name in usecases_result
            ]
            
            topics_with_usecases.append({
                "id": topic_id,
                "name": topic_name,
                "use_cases": use_cases
            })
        
        return {
            "topics": topics_with_usecases,
            "total_topics": len(topics_with_usecases),
            "total_use_cases": sum(len(t["use_cases"]) for t in topics_with_usecases)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching topics: {str(e)}"
        )


@router.get("/topics/{topic_id}/use-cases")
def get_use_cases_for_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Get use cases for a specific topic.
    
    Returns:
    {
        "topic_id": 1,
        "topic_name": "AI - Software development",
        "use_cases": [
            {"id": 1, "name": "Code Generation"},
            ...
        ]
    }
    """
    try:
        # Verify topic exists
        topic_result = db.execute(text(
            "SELECT id, name FROM topics WHERE id = :topic_id"
        ), {"topic_id": topic_id}).fetchone()
        
        if not topic_result:
            raise HTTPException(
                status_code=404,
                detail=f"Topic {topic_id} not found"
            )
        
        topic_id, topic_name = topic_result
        
        # Get use cases for this topic
        usecases_result = db.execute(text(
            "SELECT id, name FROM use_cases WHERE topic_id = :topic_id ORDER BY order_index"
        ), {"topic_id": topic_id}).fetchall()
        
        use_cases = [
            {"id": uc_id, "name": uc_name}
            for uc_id, uc_name in usecases_result
        ]
        
        return {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "use_cases": use_cases,
            "count": len(use_cases)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching use cases: {str(e)}"
        )


@router.get("/quick-list")
def get_quick_list(db: Session = Depends(get_db)):
    """
    Get a quick list of just topic names for filtering dropdown.
    
    Returns:
    {
        "topics": ["AI - Software development", "AI - Agentic", ...]
    }
    """
    try:
        topics_result = db.execute(text(
            "SELECT name FROM topics ORDER BY order_index"
        )).fetchall()
        
        topics = [topic[0] for topic in topics_result]
        
        return {
            "topics": topics,
            "count": len(topics)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching quick list: {str(e)}"
        )
