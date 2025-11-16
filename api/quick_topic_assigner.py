#!/usr/bin/env python3
"""
Quick Topic Assigner - Assigns topics based on company data without external API
Uses existing fields: industries, description, extracted_product, company_type
"""

import sys
import json
sys.path.insert(0, '/home/akyo/startup_swiper/api')

from database import SessionLocal
from models_startup import Startup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOPIC_KEYWORDS = {
    "AI - Claims": ["claim", "insurance", "fraud", "detection", "risk", "loss"],
    "AI - Underwriting": ["underwriting", "risk assessment", "pricing", "credit", "lending"],
    "AI - Contact centers": ["contact center", "customer support", "call center", "chatbot", "customer service"],
    "AI - Software development": ["code generation", "developer tools", "IDE", "testing", "debugging", "development"],
    "AI - Agentic": ["agent", "workflow automation", "task automation", "autonomous", "multi-agent"],
    "Health": ["health", "healthcare", "medical", "wellness", "pharma", "biotech", "telemedicine"],
    "Growth": ["saas", "b2b", "marketplace", "e-commerce", "growth", "analytics", "crm"],
    "Insurance disruptor": ["insurance", "insurtech", "policy", "underwriting", "claims"],
    "DeepTech": ["quantum", "hardware", "semiconductor", "biotech", "deeptech", "research"],
    "Responsibility": ["sustainability", "esg", "climate", "renewable", "green", "social"],
}

def extract_keywords(startup: Startup) -> str:
    """Extract all relevant text from startup"""
    text_parts = []
    
    if startup.company_description:
        text_parts.append(startup.company_description)
    if startup.description:
        text_parts.append(startup.description)
    if startup.shortDescription:
        text_parts.append(startup.shortDescription)
    if startup.extracted_product:
        text_parts.append(startup.extracted_product)
    if startup.primary_industry:
        text_parts.append(startup.primary_industry)
    if startup.core_product:
        text_parts.append(startup.core_product)
    if startup.target_customers:
        text_parts.append(startup.target_customers)
    
    # Convert secondary industries list
    if startup.secondary_industry:
        try:
            if isinstance(startup.secondary_industry, str):
                text_parts.append(startup.secondary_industry)
            elif isinstance(startup.secondary_industry, list):
                text_parts.append(" ".join(startup.secondary_industry))
        except:
            pass
    
    combined = " ".join(text_parts).lower()
    return combined

def assign_topic(startup: Startup) -> str:
    """Assign primary topic based on company data"""
    content = extract_keywords(startup)
    
    if not content or len(content) < 10:
        return "Other"
    
    # Score each topic
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(content.count(kw) for kw in keywords)
        scores[topic] = score
    
    # Get topic with highest score
    best_topic = max(scores, key=scores.get)
    best_score = scores[best_topic]
    
    # Default to Other if no strong match
    if best_score == 0:
        return "Other"
    
    return best_topic

def main():
    db = SessionLocal()
    
    try:
        # Get startups without topics
        startups_without_topics = db.query(Startup).filter(
            (Startup.topics.is_(None)) | (Startup.topics == '') | (Startup.topics == '[]')
        ).all()
        
        total = len(startups_without_topics)
        logger.info(f"Found {total} startups without topics")
        
        # Assign topics
        updated = 0
        for i, startup in enumerate(startups_without_topics, 1):
            topic = assign_topic(startup)
            startup.topics = json.dumps([topic])  # Store as JSON array
            updated += 1
            
            if i % 100 == 0:
                logger.info(f"Processed {i}/{total} - assigning: {topic}")
        
        # Commit all changes
        db.commit()
        logger.info(f"✓ Successfully assigned topics to {updated} startups")
        
        # Verify
        with_topics = db.query(Startup).filter(Startup.topics.isnot(None)).count()
        logger.info(f"✓ Total startups with topics: {with_topics}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
