"""
Enhanced Qwen Agent Concierge with LangSmith Tracing and ChatCBI Integration

This implements a production-ready AI concierge using:
- Qwen-Agent framework for robust tool calling
- LangSmith for observability and tracing
- ChatCBI for advanced startup research
- Proper function calling patterns (not ReAct with stopwords)

References:
- Qwen Function Calling: https://qwen.readthedocs.io/en/latest/framework/function_call.html
- LangSmith Tracing: https://docs.smith.langchain.com/
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
import asyncio

# Load environment FIRST
from dotenv import load_dotenv

env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✓ Enhanced Concierge: Loaded environment from: {env_path}")
        break

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify configuration
print(f"✓ Model: {os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct')}")
print(f"✓ LangSmith Tracing: {os.getenv('LANGSMITH_TRACING', 'false')}")
print(f"✓ LangSmith Project: {os.getenv('LANGSMITH_PROJECT', 'default')}")
print(f"✓ CBInsights Client ID: {'Configured' if os.getenv('CBINSIGHTS_CLIENT_ID') else 'Missing'}")

# Import after env is loaded
from sqlalchemy.orm import Session
from qwen_agent.llm import get_chat_model
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

# LangSmith tracing
from langsmith import traceable
from langsmith.run_helpers import tracing_context

# Local imports
from database import SessionLocal
import db_queries
from cb_insights_integration import cb_chat
from llm_config import llm_completion


# ====================
# Tool Implementations using Qwen-Agent Pattern
# ====================

@register_tool('search_startups_by_name')
class SearchStartupsByName(BaseTool):
    """Search for startups in the database by company name"""
    
    description = 'Search for startups in the database by company name. Returns basic info about matching startups.'
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'The company name to search for (partial matches allowed)',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum number of results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_startups_by_name", tags=["tool", "database"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        # Handle both dict and JSON string
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        query = params.get('query', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups(self.db, query_text=query, limit=limit)
            if not results:
                return f"Hmm, no matches for '{query}'. Want to try a different search term or maybe search by industry?"
            
            if len(results) == 1:
                s = results[0]
                name = s.get('company_name', 'Unknown')
                industry = s.get('primary_industry', 'N/A')
                city = s.get('company_city', '')
                country = s.get('company_country', '')
                location = f"{city}, {country}" if city else country
                return f"{name} - they're in {industry}, based in {location}. Want more details about them?"
            
            if len(results) <= 3:
                names = [s.get('company_name', 'Unknown') for s in results]
                industries = [s.get('primary_industry', 'N/A') for s in results]
                details = ', '.join([f"{n} ({i})" for n, i in zip(names, industries)])
                return f"Found {details}. Which one are you most interested in?"
            
            # Many results
            top_three = [s.get('company_name', 'Unknown') for s in results[:3]]
            top_names = f"{top_three[0]}, {top_three[1]}, and {top_three[2]}"
            return f"There are {len(results)} matches. Top ones are {top_names}... Want me to narrow this down by industry or location?"
                
        except Exception as e:
            logger.error(f"Error in search_startups_by_name: {e}")
            return f"Having trouble with that search. Can you try rephrasing it?"


@register_tool('get_startup_details')
class GetStartupDetails(BaseTool):
    """Get comprehensive details about a specific startup"""
    
    description = 'Get comprehensive details about a specific startup including team, funding, and technology.'
    parameters = [
        {
            'name': 'company_name',
            'type': 'string',
            'description': 'The exact company name',
            'required': True
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_startup_details", tags=["tool", "database"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        # Handle both dict and JSON string
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        company_name = params.get('company_name', '')
        
        try:
            results = db_queries.search_startups(self.db, query_text=company_name, limit=1)
            if not results:
                return f"Not finding '{company_name}' in our database. Maybe try searching by industry or a different name?"
            
            startup = results[0]
            name = startup.get('company_name', 'Unknown')
            parts = []
            
            # Build natural description
            industry = startup.get('primary_industry', 'N/A')
            city = startup.get('company_city', '')
            country = startup.get('company_country', '')
            location = f"{city}, {country}" if city else country
            
            parts.append(f"{name} is in {industry}, based in {location}.")
            
            if startup.get('company_description'):
                desc = startup['company_description'][:150]
                if len(startup['company_description']) > 150:
                    desc += "..."
                parts.append(desc)
            
            founded = startup.get('founded_year')
            funding = startup.get('total_funding')
            stage = startup.get('funding_stage', '')
            
            if founded and funding:
                parts.append(f"Founded in {founded}, they've raised ${funding}M ({stage}).")
            elif founded:
                parts.append(f"Founded in {founded}.")
            elif funding:
                parts.append(f"They've raised ${funding}M ({stage}).")
            
            if startup.get('website'):
                parts.append(f"Website: {startup['website']}")
            
            return ' '.join(parts)
        except Exception as e:
            logger.error(f"Error in get_startup_details: {e}")
            return f"Having trouble getting those details. Try searching for them by name first?"


@register_tool('search_people')
class SearchPeople(BaseTool):
    """Search for event attendees/people by name"""
    
    description = 'Search for people/attendees by name. Use this when looking for specific individuals like "Eduardo Paz".'
    parameters = [
        {
            'name': 'name',
            'type': 'string',
            'description': 'Name of the person to search for',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_people", tags=["tool", "database", "attendees"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        # Handle both dict and JSON string
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        name = params.get('name', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_attendees_by_name(self.db, name, limit)
            
            if not results:
                return f"Not finding anyone named '{name}'. Want to try a different spelling or search by company instead?"
            
            if len(results) == 1:
                p = results[0]
                pname = p.get('name', 'Unknown')
                title = p.get('title', '')
                company = p.get('company_name', '')
                linkedin = p.get('linkedin', '')
                
                parts = [f"Found {pname}"]
                if title and company:
                    parts.append(f"- {title} at {company}")
                elif title:
                    parts.append(f"- {title}")
                elif company:
                    parts.append(f"- works at {company}")
                
                if linkedin:
                    parts.append(f"LinkedIn: {linkedin}")
                
                return '. '.join(parts) + '.'
            
            # Multiple results
            names = []
            for person in results[:3]:
                pname = person.get('name', 'Unknown')
                company = person.get('company_name', '')
                if company:
                    names.append(f"{pname} ({company})")
                else:
                    names.append(pname)
            
            if len(results) <= 3:
                return f"Found {', '.join(names[:-1])} and {names[-1]}. Which one were you looking for?"
            else:
                return f"Found {len(results)} people named {name}. Top matches: {', '.join(names)}. Need more details to narrow it down?"
            
        except Exception as e:
            logger.error(f"Error in search_people: {e}")
            return f"Having trouble with that search. Try a different name?"


@register_tool('search_startups_by_industry')
class SearchStartupsByIndustry(BaseTool):
    """Search for startups by industry or sector"""
    
    description = 'Search for startups by industry or sector (e.g., "AI", "FinTech", "HealthTech").'
    parameters = [
        {
            'name': 'industry',
            'type': 'string',
            'description': 'The industry to search for',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum number of results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_startups_by_industry", tags=["tool", "database"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        # Handle both dict and JSON string
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        industry = params.get('industry', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups_by_industry(self.db, industry, limit)
            if not results:
                return f"Not finding any startups in '{industry}'. Want to try a related industry or different search term?"
            
            if len(results) <= 3:
                details = []
                for s in results:
                    name = s.get('company_name', 'Unknown')
                    country = s.get('company_country', '')
                    if country:
                        details.append(f"{name} from {country}")
                    else:
                        details.append(name)
                return f"In {industry}: {', '.join(details)}. Want details on any of these?"
            
            # Many results
            top_names = [s.get('company_name', 'Unknown') for s in results[:3]]
            return f"Found {len(results)} startups in {industry}. Top ones: {', '.join(top_names)}. Want me to narrow this down by location or funding stage?"
            
        except Exception as e:
            logger.error(f"Error in search_startups_by_industry: {e}")
            return f"Having trouble searching that industry. Try rephrasing it?"


@register_tool('search_events')
class SearchEvents(BaseTool):
    """Search for Slush events by title or organizer"""
    
    description = 'Search for Slush events by title or organizer name. Use this to find specific events or events hosted by companies.'
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'Search query for event title or organizer',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_events", tags=["tool", "database", "events"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        from models import SlushEvent
        
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        query = params.get('query', '')
        limit = params.get('limit', 10)
        
        try:
            events = self.db.query(SlushEvent).filter(
                (SlushEvent.title.ilike(f"%{query}%")) |
                (SlushEvent.organizer.ilike(f"%{query}%"))
            ).limit(limit).all()
            
            if not events:
                return f"Not finding any events for '{query}'. Want to try a different search or look by organizer?"
            
            if len(events) == 1:
                e = events[0]
                status = ', '.join(e.status) if e.status else 'Open'
                return f"{e.title} by {e.organizer} - {e.datetime} at {e.location or 'venue TBA'}. Status: {status}"
            
            if len(events) <= 3:
                titles = [e.title for e in events]
                return f"Found {', '.join(titles[:-1])} and {titles[-1]}. Which one interests you?"
            
            # Many events
            top_three = [f"{e.title} by {e.organizer}" for e in events[:3]]
            return f"There are {len(events)} events matching '{query}'. Top ones: {top_three[0]}, {top_three[1]}, and {top_three[2]}. Want details on any of these?"
            
        except Exception as e:
            logger.error(f"Error in search_events: {e}")
            return f"Having trouble with that search. Try rephrasing it?"


@register_tool('search_events_by_organizer')
class SearchEventsByOrganizer(BaseTool):
    """Find all events organized by a specific company"""
    
    description = 'Find all events organized by a specific company or organization.'
    parameters = [
        {
            'name': 'organizer',
            'type': 'string',
            'description': 'Company/organization name hosting events',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_events_by_organizer", tags=["tool", "database", "events"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        from models import SlushEvent
        
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        organizer = params.get('organizer', '')
        limit = params.get('limit', 10)
        
        try:
            events = self.db.query(SlushEvent).filter(
                SlushEvent.organizer.ilike(f"%{organizer}%")
            ).limit(limit).all()
            
            if not events:
                return f"Not finding any events organized by '{organizer}'. Maybe try a different company name?"
            
            if len(events) == 1:
                e = events[0]
                return f"{organizer} is hosting '{e.title}' on {e.datetime} at {e.location or 'venue TBA'}. Want more details?"
            
            if len(events) <= 3:
                titles = [f"'{e.title}' ({e.datetime.split(',')[0]})" for e in events]  # Just the date part
                return f"{organizer} has {len(events)} events: {', '.join(titles)}. Which one interests you?"
            
            # Many events
            main_event = events[0]
            return f"{organizer}'s pretty active - they've got {len(events)} events. The main one is '{main_event.title}' on {main_event.datetime}. Want the full list or interested in something specific?"
            
        except Exception as e:
            logger.error(f"Error in search_events_by_organizer: {e}")
            return f"Having trouble with that search. Try a different organizer?"


@register_tool('search_events_by_date')
class SearchEventsByDate(BaseTool):
    """Find events happening on specific dates"""
    
    description = 'Find events happening on a specific date (e.g., "Nov 19", "Nov 20", "November 19").'
    parameters = [
        {
            'name': 'date_query',
            'type': 'string',
            'description': 'Date string to search for',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_events_by_date", tags=["tool", "database", "events"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        from models import SlushEvent
        
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        date_query = params.get('date_query', '')
        limit = params.get('limit', 10)
        
        try:
            events = self.db.query(SlushEvent).filter(
                SlushEvent.datetime.ilike(f"%{date_query}%")
            ).limit(limit).all()
            
            if not events:
                return f"Not finding events for '{date_query}'. Maybe try 'Nov 19' or 'Nov 20'?"
            
            if len(events) <= 3:
                event_list = [f"{e.title} by {e.organizer}" for e in events]
                return f"On {date_query}: {', '.join(event_list)}. Want details on any?"
            
            # Many events
            return f"There are {len(events)} events on {date_query}. Want me to narrow it down by organizer, topic, or time of day?"
            
        except Exception as e:
            logger.error(f"Error in search_events_by_date: {e}")
            return f"Having trouble with that search. Try a different date format?"


@register_tool('get_event_details')
class GetEventDetails(BaseTool):
    """Get comprehensive details about a specific event"""
    
    description = 'Get comprehensive details about a specific Slush event including location, time, status, and categories.'
    parameters = [
        {
            'name': 'title',
            'type': 'string',
            'description': 'Event title or partial title',
            'required': True
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_event_details", tags=["tool", "database", "events"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        from models import SlushEvent
        
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        title = params.get('title', '')
        
        try:
            event = self.db.query(SlushEvent).filter(
                SlushEvent.title.ilike(f"%{title}%")
            ).first()
            
            if not event:
                return f"Not finding an event called '{title}'. Want to search by organizer instead?"
            
            parts = [f"{event.title} - organized by {event.organizer}. "]
            parts.append(f"It's on {event.datetime} at {event.location or 'venue TBA'}.")
            
            if event.status and len(event.status) > 0:
                parts.append(f"Status: {', '.join(event.status)}.")
            
            if event.categories and len(event.categories) > 0:
                parts.append(f"Categories: {', '.join(event.categories)}.")
            
            return ' '.join(parts)
        except Exception as e:
            logger.error(f"Error in get_event_details: {e}")
            return f"Having trouble getting those details. Try searching for it first?"


@register_tool('advanced_research_chatcbi')
class AdvancedResearchChatCBI(BaseTool):
    """Perform deep market research using CB Insights ChatCBI API"""
    
    description = 'Perform deep market research using CB Insights ChatCBI API. ONLY use when user explicitly requests "advanced research" or "deep dive". Provides business model analysis, competitive landscape, funding trends, and technology insights. Requires CB Insights API credentials.'
    parameters = [
        {
            'name': 'company_name',
            'type': 'string',
            'description': 'Company to research',
            'required': True
        },
        {
            'name': 'focus',
            'type': 'string',
            'description': 'Optional: Specific aspect (funding/competitors/technology/market)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="advanced_research_chatcbi", tags=["tool", "chatcbi", "external-api"])
    async def call_async(self, params: Dict[str, Any], **kwargs) -> str:
        """Async version for ChatCBI API calls"""
        # Handle both dict and JSON string
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        company_name = params.get('company_name', '')
        focus = params.get('focus', '')
        
        # Check credentials
        creds = cb_chat.check_credentials()
        if not creds['configured']:
            return (
                "Looks like CB Insights isn't set up yet. You'll need API credentials for advanced research. "
                "Want to try a regular database search instead?"
            )
        
        # Build research query
        if focus:
            user_query = f"Provide detailed analysis of {company_name}, focusing on {focus}"
        else:
            user_query = (
                f"Provide comprehensive market intelligence on {company_name} including: "
                f"business model, competitive positioning, funding history, technology stack, "
                f"market trends, and strategic opportunities."
            )
        
        try:
            # Call ChatCBI API (with built-in LLM query optimization)
            result = await cb_chat.ask_question(user_query, company_name=company_name)
            
            return f"Here's what CB Insights has on {company_name}:\n\n{result}\n\nSource: CB Insights ChatCBI"
            
        except Exception as e:
            logger.error(f"ChatCBI error: {e}")
            return f"Having trouble reaching CB Insights right now. Want to try a regular database search instead?"
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Synchronous wrapper"""
        return asyncio.run(self.call_async(params, **kwargs))


# ====================
# Phase 1: Enhanced Startup Search Tools
# ====================

@register_tool('search_by_funding_stage')
class SearchByFundingStage(BaseTool):
    """Search startups by funding stage and/or minimum funding amount"""
    
    description = 'Search for startups by funding stage (seed, Series A, B, C, etc.) and/or minimum funding amount in millions USD.'
    parameters = [
        {
            'name': 'stage',
            'type': 'string',
            'description': 'Funding stage (e.g., "seed", "Series A", "Series B")',
            'required': False
        },
        {
            'name': 'min_amount',
            'type': 'number',
            'description': 'Minimum funding amount in millions USD',
            'required': False
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_by_funding_stage", tags=["tool", "database", "funding"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        stage = params.get('stage')
        min_amount = params.get('min_amount')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups_by_funding_stage(
                self.db, stage=stage, min_amount=min_amount, limit=limit
            )
            
            if not results:
                filter_desc = []
                if stage:
                    filter_desc.append(f"at {stage}")
                if min_amount:
                    filter_desc.append(f"with ${min_amount}M+ funding")
                return f"Not finding startups {' '.join(filter_desc)}. Want to try different criteria?"
            
            if len(results) <= 3:
                details = []
                for s in results:
                    name = s.get('company_name', 'Unknown')
                    funding = s.get('total_funding', 0)
                    stage_info = s.get('funding_stage', 'N/A')
                    details.append(f"{name} (${funding}M, {stage_info})")
                return f"Found {', '.join(details)}. Want more info on any?"
            
            top_names = [f"{s.get('company_name')} (${s.get('total_funding', 0)}M)" 
                        for s in results[:3]]
            return f"Found {len(results)} startups. Top funded: {', '.join(top_names)}. Want to see more or narrow it down?"
            
        except Exception as e:
            logger.error(f"Error in search_by_funding_stage: {e}")
            return "Having trouble with that search. Try different funding criteria?"


@register_tool('search_by_axa_grade')
class SearchByAXAGrade(BaseTool):
    """Search startups by AXA partnership grade and/or priority tier"""
    
    description = 'Search for startups by AXA partnership grade (A+, A, A-, B+, etc.) and/or priority tier (Tier 1, 2, 3, 4).'
    parameters = [
        {
            'name': 'min_grade',
            'type': 'string',
            'description': 'Minimum grade (e.g., "A+", "A", "B+")',
            'required': False
        },
        {
            'name': 'tier',
            'type': 'string',
            'description': 'Priority tier (e.g., "Tier 1", "Tier 2")',
            'required': False
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_by_axa_grade", tags=["tool", "database", "axa-grade"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        min_grade = params.get('min_grade')
        tier = params.get('tier')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups_by_axa_grade(
                self.db, min_grade=min_grade, tier=tier, limit=limit
            )
            
            if not results:
                filter_desc = []
                if min_grade:
                    filter_desc.append(f"graded {min_grade}+")
                if tier:
                    filter_desc.append(f"in {tier}")
                return f"Not finding startups {' '.join(filter_desc)}. Want to broaden the search?"
            
            if len(results) <= 3:
                details = []
                for s in results:
                    name = s.get('company_name', 'Unknown')
                    grade = s.get('axa_grade', 'N/A')
                    tier_info = s.get('axa_priority_tier', 'N/A')
                    details.append(f"{name} ({grade}, {tier_info})")
                return f"Found {', '.join(details)}. Want details on any?"
            
            top_names = [f"{s.get('company_name')} ({s.get('axa_grade')})" 
                        for s in results[:3]]
            return f"Found {len(results)} high-priority startups. Top rated: {', '.join(top_names)}. Want to see more?"
            
        except Exception as e:
            logger.error(f"Error in search_by_axa_grade: {e}")
            return "Having trouble with that search. Try different grade criteria?"


@register_tool('search_by_location')
class SearchByLocation(BaseTool):
    """Search startups by country and/or city"""
    
    description = 'Search for startups by location (country and/or city).'
    parameters = [
        {
            'name': 'country',
            'type': 'string',
            'description': 'Country name',
            'required': False
        },
        {
            'name': 'city',
            'type': 'string',
            'description': 'City name',
            'required': False
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_by_location", tags=["tool", "database", "location"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        country = params.get('country')
        city = params.get('city')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups_by_location(
                self.db, country=country, city=city, limit=limit
            )
            
            if not results:
                location = city if city else country
                return f"Not finding startups in {location}. Want to try a nearby city or country?"
            
            if len(results) <= 3:
                names = [s.get('company_name', 'Unknown') for s in results]
                location = f"{city}, {country}" if city and country else (city or country)
                return f"In {location}: {', '.join(names)}. Want details on any?"
            
            top_names = [s.get('company_name') for s in results[:3]]
            location = f"{city}, {country}" if city and country else (city or country)
            return f"Found {len(results)} startups in {location}. Top ones: {', '.join(top_names)}. Want to filter by industry?"
            
        except Exception as e:
            logger.error(f"Error in search_by_location: {e}")
            return "Having trouble with that location search. Try a different place?"


@register_tool('search_by_value_prop')
class SearchByValueProp(BaseTool):
    """Search startups by value proposition, problem solved, or target customers"""
    
    description = 'Search for startups by what they do, problems they solve, or who their customers are. Use natural language queries.'
    parameters = [
        {
            'name': 'query',
            'type': 'string',
            'description': 'Search query (e.g., "claims automation", "SMB customers", "workflow optimization")',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_by_value_prop", tags=["tool", "database", "value-prop"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        query = params.get('query', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_startups_by_value_prop(self.db, query, limit)
            
            if not results:
                return f"Not finding startups focused on '{query}'. Want to try related keywords?"
            
            if len(results) <= 3:
                details = []
                for s in results:
                    name = s.get('company_name', 'Unknown')
                    prop = s.get('value_proposition', '')[:60]
                    details.append(f"{name} - {prop}...")
                return f"Found {', '.join(details)}. Want full details?"
            
            top_names = [s.get('company_name') for s in results[:3]]
            return f"Found {len(results)} startups working on '{query}'. Top ones: {', '.join(top_names)}. Want to see their value props?"
            
        except Exception as e:
            logger.error(f"Error in search_by_value_prop: {e}")
            return "Having trouble with that search. Try different keywords?"


@register_tool('get_funding_details')
class GetFundingDetails(BaseTool):
    """Get detailed funding information for a specific startup"""
    
    description = 'Get comprehensive funding information including rounds, amounts, valuation, and revenue data for a specific startup.'
    parameters = [
        {
            'name': 'startup_name',
            'type': 'string',
            'description': 'Startup name',
            'required': True
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_funding_details", tags=["tool", "database", "funding"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        startup_name = params.get('startup_name', '')
        
        try:
            result = db_queries.get_startup_funding_details(self.db, startup_name)
            
            if not result:
                return f"Not finding funding data for '{startup_name}'. Want to search for similar names?"
            
            name = result.get('company_name', 'Unknown')
            total = result.get('total_funding', 0)
            stage = result.get('funding_stage', 'Unknown')
            last_date = result.get('last_funding_date_str', 'Unknown')
            valuation = result.get('valuation')
            
            parts = [f"{name} has raised ${total}M total"]
            if stage and stage != 'Unknown':
                parts.append(f"currently at {stage}")
            if last_date and last_date != 'Unknown':
                parts.append(f"Last round: {last_date}")
            if valuation:
                parts.append(f"Valued at ${valuation}M")
            
            return '. '.join(parts) + '. Want more details or comparisons?'
            
        except Exception as e:
            logger.error(f"Error in get_funding_details: {e}")
            return "Having trouble getting funding data. Try a different startup?"


# ====================
# Phase 2: Meeting Context Tools
# ====================

@register_tool('get_meeting_prep')
class GetMeetingPrep(BaseTool):
    """Get existing meeting prep outline for a startup"""
    
    description = 'Retrieve saved meeting preparation outline including talking points and critical questions for a specific startup.'
    parameters = [
        {
            'name': 'startup_id',
            'type': 'string',
            'description': 'Startup ID or name',
            'required': True
        },
        {
            'name': 'user_id',
            'type': 'string',
            'description': 'User ID',
            'required': True
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_meeting_prep", tags=["tool", "database", "meeting-prep"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        startup_id = params.get('startup_id', '')
        user_id = params.get('user_id', '')
        
        try:
            result = db_queries.get_meeting_prep_outline(self.db, startup_id, user_id)
            
            if not result:
                return f"No meeting prep found for that startup. Want me to help generate one?"
            
            name = result.get('startup_name', 'Unknown')
            outline = result.get('outline', '')
            
            if outline:
                # Return first 300 chars of outline
                preview = outline[:300] + ('...' if len(outline) > 300 else '')
                return f"Here's your prep for {name}:\n\n{preview}\n\nWant the full outline?"
            
            return f"Found prep for {name} but it's empty. Want to regenerate it?"
            
        except Exception as e:
            logger.error(f"Error in get_meeting_prep: {e}")
            return "Having trouble loading that prep. Try a different startup?"


@register_tool('get_user_votes')
class GetUserVotes(BaseTool):
    """Get all startups a user has voted for"""
    
    description = 'Retrieve all startups that a user has voted as interested or not interested in.'
    parameters = [
        {
            'name': 'user_id',
            'type': 'string',
            'description': 'User ID',
            'required': True
        },
        {
            'name': 'interested_only',
            'type': 'boolean',
            'description': 'Show only interested votes (default: true)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_user_votes", tags=["tool", "database", "votes"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        user_id = params.get('user_id', '')
        interested_only = params.get('interested_only', True)
        
        try:
            votes = db_queries.get_user_votes(self.db, user_id, limit=100)
            
            if not votes:
                return "You haven't voted on any startups yet. Want to browse some?"
            
            if interested_only:
                votes = [v for v in votes if v['interested']]
            
            if not votes:
                return "No interested votes found. Want to see all your votes?"
            
            if len(votes) <= 5:
                startup_ids = [v['startup_id'] for v in votes]
                return f"You're interested in: {', '.join(startup_ids)}. Want details on any?"
            
            count = len(votes)
            recent = [v['startup_id'] for v in votes[:3]]
            return f"You've voted interested in {count} startups. Most recent: {', '.join(recent)}. Want the full list?"
            
        except Exception as e:
            logger.error(f"Error in get_user_votes: {e}")
            return "Having trouble loading your votes. Try again?"


@register_tool('get_startup_rating')
class GetStartupRating(BaseTool):
    """Get rating and feedback for a startup"""
    
    description = 'Get average rating, total number of ratings, and feedback for a specific startup.'
    parameters = [
        {
            'name': 'startup_id',
            'type': 'string',
            'description': 'Startup ID or name',
            'required': True
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_startup_rating", tags=["tool", "database", "ratings"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        startup_id = params.get('startup_id', '')
        
        try:
            result = db_queries.get_startup_rating(self.db, startup_id)
            
            if not result:
                return f"No ratings yet for '{startup_id}'. Want to be the first to rate them?"
            
            avg = result.get('average_rating', 0)
            total = result.get('total_ratings', 0)
            trending = result.get('trending_score', 0)
            
            if total == 0:
                return f"No ratings yet for '{startup_id}'. Want to rate them?"
            
            rating_str = f"{avg}/5 stars from {total} rating{'s' if total != 1 else ''}"
            
            if trending > 50:
                return f"{startup_id}: {rating_str}. Pretty hot right now! Want to see feedback?"
            elif trending > 20:
                return f"{startup_id}: {rating_str}. Getting some attention. Want details?"
            else:
                return f"{startup_id}: {rating_str}. Want to see what people said?"
            
        except Exception as e:
            logger.error(f"Error in get_startup_rating: {e}")
            return "Having trouble loading ratings. Try a different startup?"


# ====================
# Phase 3: People Intelligence Tools
# ====================

@register_tool('search_people_by_role')
class SearchPeopleByRole(BaseTool):
    """Search attendees by job title or role"""
    
    description = 'Search for Slush attendees by job title or role (e.g., "CTO", "founder", "VP Innovation").'
    parameters = [
        {
            'name': 'title_query',
            'type': 'string',
            'description': 'Job title or role to search for',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_people_by_role", tags=["tool", "database", "people"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        title_query = params.get('title_query', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_people_by_role(self.db, title_query, limit)
            
            if not results:
                return f"Not finding anyone with '{title_query}' in their title. Want to try a related role?"
            
            if len(results) <= 3:
                details = []
                for p in results:
                    name = p.get('name', 'Unknown')
                    title = p.get('title', '')
                    company = p.get('company_name', '')
                    if company:
                        details.append(f"{name} ({title} at {company})")
                    else:
                        details.append(f"{name} ({title})")
                return f"Found {', '.join(details)}. Want to connect with any?"
            
            top_people = [f"{p.get('name')} ({p.get('company_name', 'N/A')})" 
                         for p in results[:3]]
            return f"Found {len(results)} people with '{title_query}' roles. Top matches: {', '.join(top_people)}. Want more?"
            
        except Exception as e:
            logger.error(f"Error in search_people_by_role: {e}")
            return "Having trouble with that search. Try a different job title?"


@register_tool('search_people_by_company')
class SearchPeopleByCompany(BaseTool):
    """Search attendees by company name"""
    
    description = 'Find all attendees from a specific company at Slush.'
    parameters = [
        {
            'name': 'company_name',
            'type': 'string',
            'description': 'Company name',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_people_by_company", tags=["tool", "database", "people"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        company_name = params.get('company_name', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_people_by_company(self.db, company_name, limit)
            
            if not results:
                return f"Not finding anyone from {company_name}. Want to check a different company?"
            
            if len(results) <= 3:
                details = []
                for p in results:
                    name = p.get('name', 'Unknown')
                    title = p.get('title', 'N/A')
                    details.append(f"{name} ({title})")
                return f"From {company_name}: {', '.join(details)}. Want their contact info?"
            
            names = [p.get('name') for p in results[:3]]
            return f"{company_name} has {len(results)} people here. Key attendees: {', '.join(names)}. Want the full list?"
            
        except Exception as e:
            logger.error(f"Error in search_people_by_company: {e}")
            return "Having trouble with that search. Try a different company?"


@register_tool('search_people_by_country')
class SearchPeopleByCountry(BaseTool):
    """Search attendees by country"""
    
    description = 'Find attendees from a specific country at Slush.'
    parameters = [
        {
            'name': 'country',
            'type': 'string',
            'description': 'Country name',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="search_people_by_country", tags=["tool", "database", "people"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        country = params.get('country', '')
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.search_people_by_country(self.db, country, limit)
            
            if not results:
                return f"Not finding attendees from {country}. Want to try a neighboring country?"
            
            if len(results) <= 5:
                names = [p.get('name') for p in results]
                return f"From {country}: {', '.join(names)}. Want details on any?"
            
            top_names = [p.get('name') for p in results[:3]]
            return f"Found {len(results)} attendees from {country}. Notable ones: {', '.join(top_names)}. Want to filter by role?"
            
        except Exception as e:
            logger.error(f"Error in search_people_by_country: {e}")
            return "Having trouble with that search. Try a different country?"


# ====================
# Phase 4: Smart Recommendations Tools
# ====================

@register_tool('recommend_similar_startups')
class RecommendSimilarStartups(BaseTool):
    """Find similar startups based on industry, technology, and stage"""
    
    description = 'Get recommendations for similar startups based on a reference startup. Useful for finding alternatives or comparisons.'
    parameters = [
        {
            'name': 'startup_id',
            'type': 'string',
            'description': 'Reference startup ID or name',
            'required': True
        },
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 5)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="recommend_similar_startups", tags=["tool", "database", "recommendations"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        startup_id = params.get('startup_id', '')
        limit = params.get('limit', 5)
        
        try:
            results = db_queries.get_similar_startups(self.db, startup_id, limit)
            
            if not results:
                return f"Can't find similar startups to '{startup_id}'. Want to search by industry instead?"
            
            if len(results) <= 3:
                details = []
                for s in results:
                    name = s.get('company_name', 'Unknown')
                    industry = s.get('primary_industry', 'N/A')
                    details.append(f"{name} ({industry})")
                return f"Similar to {startup_id}: {', '.join(details)}. Want comparisons?"
            
            names = [s.get('company_name') for s in results[:3]]
            return f"Found {len(results)} similar startups. Check out: {', '.join(names)}. Want full details or comparisons?"
            
        except Exception as e:
            logger.error(f"Error in recommend_similar_startups: {e}")
            return "Having trouble finding similar startups. Try a different reference?"


@register_tool('get_trending_startups')
class GetTrendingStartups(BaseTool):
    """Get currently trending startups based on voting activity"""
    
    description = 'Get the most popular/trending startups based on recent voting and rating activity at Slush.'
    parameters = [
        {
            'name': 'limit',
            'type': 'integer',
            'description': 'Maximum results (default: 10)',
            'required': False
        }
    ]
    
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
    
    @traceable(name="get_trending_startups", tags=["tool", "database", "trending"])
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        if isinstance(params, str):
            import json
            params = json.loads(params)
        
        limit = params.get('limit', 10)
        
        try:
            results = db_queries.get_trending_startups(self.db, limit)
            
            if not results:
                return "No trending data available yet. Want to search by industry or funding stage?"
            
            if len(results) <= 3:
                names = [s.get('company_name', 'Unknown') for s in results]
                return f"Trending right now: {', '.join(names)}. Want to know why they're hot?"
            
            top_names = [s.get('company_name') for s in results[:3]]
            return f"Top {len(results)} trending startups: {', '.join(top_names)}... Everyone's checking these out. Want details?"
            
        except Exception as e:
            logger.error(f"Error in get_trending_startups: {e}")
            return "Having trouble loading trending startups. Want to search by industry?"


# ====================
# Qwen Agent Concierge
# ====================

class QwenAgentConcierge:
    """
    Production-ready AI Concierge using Qwen-Agent framework
    
    Features:
    - Proper function calling (Hermes-style, not ReAct with stopwords)
    - LangSmith tracing for observability
    - ChatCBI integration for advanced research
    - Database tool integrations
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize Qwen model via OpenAI-compatible API
        self.llm = get_chat_model({
            "model": os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct'),
            "model_server": os.getenv('NVIDIA_NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1'),
            "api_key": os.getenv('NVIDIA_API_KEY'),
            "generate_cfg": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500,  # Reduced from 2000 to encourage brevity
                "extra_body": {
                    "chat_template_kwargs": {
                        "enable_thinking": False  # Disable think mode by default (can be enabled per request)
                    }
                }
            }
        })
        
        # Initialize tools with database session
        self.tools = [
            # Original tools
            SearchStartupsByName(db),
            GetStartupDetails(db),
            SearchPeople(db),
            SearchStartupsByIndustry(db),
            SearchEvents(db),
            SearchEventsByOrganizer(db),
            SearchEventsByDate(db),
            GetEventDetails(db),
            AdvancedResearchChatCBI(db),
            # Phase 1: Enhanced Startup Search
            SearchByFundingStage(db),
            SearchByAXAGrade(db),
            SearchByLocation(db),
            SearchByValueProp(db),
            GetFundingDetails(db),
            # Phase 2: Meeting Context
            GetMeetingPrep(db),
            GetUserVotes(db),
            GetStartupRating(db),
            # Phase 3: People Intelligence
            SearchPeopleByRole(db),
            SearchPeopleByCompany(db),
            SearchPeopleByCountry(db),
            # Phase 4: Smart Recommendations
            RecommendSimilarStartups(db),
            GetTrendingStartups(db),
        ]
        
        # Create Qwen Agent Assistant
        self.agent = Assistant(
            llm=self.llm,
            name="Startup Swiper Concierge",
            description="AI assistant for startup discovery, attendee search, and market research",
            function_list=self.tools,
            system_message=self._get_system_message()
        )
        
        logger.info("✅ Qwen Agent Concierge initialized successfully")
    
    def _get_system_message(self) -> str:
        """Get the system message for the agent"""
        return """You're a helpful colleague at Slush 2025 who knows the startup scene really well. You've been here before, you know the players, and you love helping people make connections.

Talk like a real person:
- Keep responses short and conversational (2-3 sentences usually does it)
- Ask questions when you need more context instead of guessing
- Share information like you're chatting, not giving a presentation
- If you don't know something, just say "Not sure about that one" - no need to apologize profusely
- No markdown formatting like **bold**, bullet lists, or ## headers - just natural sentences

You have access to powerful search tools:
- Startups: Search by name, industry, location, funding stage, AXA grade, value proposition
- People: Find attendees by name, company, role, or country
- Events: Search by title, organizer, date, or get full details
- Intelligence: Get funding details, meeting preps, user votes, ratings, trending startups
- Recommendations: Find similar startups based on what someone's interested in
- Research: Deep market research via CB Insights (only when they explicitly ask for "advanced research")

When you use tools to look things up:
- Don't just dump the data - tell them what's actually useful
- If there are many results, show the top few and offer to narrow down
- End with a natural question like "Want more details?" or "Which one interests you?"
- Keep it conversational

Important: You're helpful, knowledgeable, and straightforward. Not formal, not robotic, not overly enthusiastic. Just someone who knows their stuff and wants to help.

Remember: Brief and useful beats comprehensive and overwhelming."""
    
    @traceable(name="concierge_chat", tags=["concierge", "qwen-agent"])
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Process a user message and return a response
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Agent's response
        """
        try:
            # Build messages list
            messages = conversation_history or []
            messages.append({"role": "user", "content": message})
            
            # Run agent with LangSmith tracing
            with tracing_context(enabled=True, project_name=os.getenv('LANGSMITH_PROJECT', 'startup-swiper-concierge')):
                # Qwen-Agent returns a generator of message lists
                responses = []
                for response_batch in self.agent.run(messages=messages):
                    responses.extend(response_batch)
                
                # Extract final response
                if responses:
                    # Get the last assistant message
                    for msg in reversed(responses):
                        if msg.get('role') == 'assistant' and msg.get('content'):
                            return msg['content']
                    
                    # Fallback to last message
                    return responses[-1].get('content', 'I apologize, but I was unable to generate a response.')
                else:
                    return 'I apologize, but I was unable to generate a response.'
                    
        except Exception as e:
            logger.error(f"Error in concierge chat: {e}", exc_info=True)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    @traceable(name="concierge_chat_sync", tags=["concierge", "qwen-agent"])
    def chat_sync(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Synchronous version of chat for compatibility
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Agent's response
        """
        return asyncio.run(self.chat(message, conversation_history))


# ====================
# Factory Functions
# ====================

def create_qwen_agent_concierge(db: Session) -> QwenAgentConcierge:
    """
    Create a Qwen Agent Concierge instance
    
    Args:
        db: Database session
        
    Returns:
        QwenAgentConcierge instance
    """
    return QwenAgentConcierge(db)


# ====================
# CLI Test Interface
# ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Qwen Agent Concierge Test Interface")
    print("="*60 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize concierge
        concierge = create_qwen_agent_concierge(db)
        
        print("✅ Concierge initialized successfully!")
        print("\nTest queries:")
        print("1. 'Find startups in AI'")
        print("2. 'Tell me about SimplifAI'")
        print("3. 'Search for Eduardo Paz'")
        print("4. 'Perform advanced research on SimplifAI' (requires CB Insights credentials)")
        print("\nType 'quit' to exit\n")
        
        conversation_history = []
        
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end='', flush=True)
            response = concierge.chat_sync(user_input, conversation_history)
            print(response)
            
            # Update history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
    finally:
        db.close()
