"""
Enhanced Agentic AI Concierge with ReAct Pattern and LangSmith Tracing

This module implements a ReAct (Reasoning + Acting) agent for the AI Concierge
using Qwen model via NVIDIA NIM, with advanced tool use and reasoning.

Inspired by Qwen-Agent design patterns but using our LiteLLM infrastructure.
Includes LangSmith tracing for observability and debugging.

CRITICAL: Environment variables MUST be loaded BEFORE importing langsmith!
"""

import os
import sys
from pathlib import Path

# ====================
# STEP 1: Load environment FIRST (before langsmith imports!)
# ====================
from dotenv import load_dotenv

# Try multiple .env locations
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✓ Qwen Concierge: Loaded environment from: {env_path}")
        break

# Verify tracing config
tracing_enabled = os.getenv("LANGSMITH_TRACING", "false")
tracing_project = os.getenv("LANGSMITH_PROJECT", "default")
print(f"✓ LangSmith Tracing: {tracing_enabled}")
print(f"✓ LangSmith Project: {tracing_project}")

# ====================
# STEP 2: Now import everything else (including langsmith)
# ====================
import json
import logging
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

# LangSmith tracing (imported AFTER environment is loaded)
from langsmith import traceable
from langsmith.run_helpers import tracing_context

from database import SessionLocal
import db_queries
from cb_insights_integration import cb_chat
from llm_config import llm_completion

logger = logging.getLogger(__name__)

# ====================
# Tool Definitions
# ====================

class ToolRegistry:
    """Registry of available tools for the agent"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available tools"""
        return {
            'search_startups_by_name': {
                'description': 'Search for startups in the database by company name. Returns basic info about matching startups.',
                'parameters': {
                    'query': 'The company name to search for (partial matches allowed)',
                    'limit': 'Maximum number of results (default: 10)'
                },
                'function': self._search_startups_by_name
            },
            'search_startups_by_industry': {
                'description': 'Search for startups by industry or sector (e.g., "AI", "FinTech", "HealthTech").',
                'parameters': {
                    'industry': 'The industry to search for',
                    'limit': 'Maximum number of results (default: 10)'
                },
                'function': self._search_startups_by_industry
            },
            'get_startup_details': {
                'description': 'Get comprehensive details about a specific startup including team, funding, and technology.',
                'parameters': {
                    'company_name': 'The exact company name'
                },
                'function': self._get_startup_details
            },
            'search_attendees': {
                'description': 'Search for event attendees by name, company, or role.',
                'parameters': {
                    'query': 'Search query (name, company, or role)',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_attendees
            },
            'search_people': {
                'description': 'Search for people/attendees by name. Use this when looking for specific individuals like "Eduardo Paz".',
                'parameters': {
                    'name': 'Name of the person to search for',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_people
            },
            'advanced_research': {
                'description': 'Perform deep market research using CB Insights ChatCBI API. Provides business model analysis, competitive landscape, funding trends, and technology insights.',
                'parameters': {
                    'company_name': 'Company to research',
                    'focus': 'Optional: Specific aspect (funding/competitors/technology/market)'
                },
                'function': self._advanced_research
            },
            'search_events': {
                'description': 'Search for Slush events by title or organizer name. Use this to find specific events or events hosted by companies.',
                'parameters': {
                    'query': 'Search query for event title or organizer',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_events
            },
            'search_events_by_organizer': {
                'description': 'Find all events organized by a specific company or organization.',
                'parameters': {
                    'organizer': 'Company/organization name hosting events',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_events_by_organizer
            },
            'search_events_by_date': {
                'description': 'Find events happening on a specific date (e.g., "Nov 19", "Nov 20", "November 19").',
                'parameters': {
                    'date_query': 'Date string to search for',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_events_by_date
            },
            'search_events_by_category': {
                'description': 'Find events by category or topic (e.g., "AI", "Demo", "Networking", "Fintech").',
                'parameters': {
                    'category': 'Category or topic name',
                    'limit': 'Maximum results (default: 10)'
                },
                'function': self._search_events_by_category
            },
            'get_event_details': {
                'description': 'Get comprehensive details about a specific Slush event including location, time, status, and categories.',
                'parameters': {
                    'title': 'Event title or partial title'
                },
                'function': self._get_event_details
            },
            'get_all_event_organizers': {
                'description': 'Get a list of all companies/organizations hosting events at Slush, with event counts.',
                'parameters': {
                    'limit': 'Maximum organizers to return (default: 20)'
                },
                'function': self._get_all_event_organizers
            }
        }
    
    # Tool implementations
    
    @traceable(name="search_startups_by_name", tags=["tool", "database"])
    def _search_startups_by_name(self, query: str, limit: int = 10) -> str:
        """Search startups by name"""
        try:
            results = db_queries.search_startups(self.db, query_text=query, limit=limit)
            if not results:
                return f"No startups found matching '{query}'"
            
            output = [f"Found {len(results)} startup(s):\n"]
            for startup in results:
                name = startup.get('company_name', 'Unknown')
                industry = startup.get('primary_industry', 'N/A')
                location = f"{startup.get('company_city', '')}, {startup.get('company_country', '')}"
                output.append(f"- **{name}** | {industry} | {location}")
                
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_startups_by_industry", tags=["tool", "database"])
    def _search_startups_by_industry(self, industry: str, limit: int = 10) -> str:
        """Search startups by industry"""
        try:
            results = db_queries.search_startups_by_industry(self.db, industry, limit)
            if not results:
                return f"No startups found in '{industry}' industry"
            
            output = [f"Found {len(results)} startup(s) in {industry}:\n"]
            for startup in results:
                name = startup.get('company_name', 'Unknown')
                country = startup.get('company_country', 'Global')
                output.append(f"- {name} ({country})")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="get_startup_details", tags=["tool", "database"])
    def _get_startup_details(self, company_name: str) -> str:
        """Get detailed startup information"""
        try:
            results = db_queries.search_startups(self.db, query_text=company_name, limit=1)
            if not results:
                return f"No startup found: '{company_name}'"
            
            startup = results[0]
            output = [f"# {startup.get('company_name', 'Unknown')}\n"]
            
            if startup.get('company_description'):
                output.append(f"**Description:** {startup['company_description']}\n")
            
            output.append(f"**Industry:** {startup.get('primary_industry', 'N/A')}")
            output.append(f"**Location:** {startup.get('company_city', '')}, {startup.get('company_country', '')}")
            output.append(f"**Founded:** {startup.get('founded_year', 'N/A')}")
            
            if startup.get('total_funding'):
                output.append(f"**Funding:** ${startup['total_funding']}M ({startup.get('funding_stage', 'N/A')})")
            
            if startup.get('website'):
                output.append(f"**Website:** {startup['website']}")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_attendees", tags=["tool", "database"])
    def _search_attendees(self, query: str, limit: int = 10) -> str:
        """Search attendees"""
        try:
            results = []
            results.extend(db_queries.search_attendees_by_name(self.db, query, limit))
            
            if not results:
                results.extend(db_queries.search_attendees_by_company(self.db, query, limit))
            
            if not results:
                return f"No attendees found matching '{query}'"
            
            output = [f"Found {len(results)} attendee(s):\n"]
            for attendee in results[:limit]:
                name = attendee.get('name', 'Unknown')
                title = attendee.get('title', '')
                company = attendee.get('company_name', '')
                
                line = f"- **{name}**"
                if title:
                    line += f" - {title}"
                if company:
                    line += f" @ {company}"
                output.append(line)
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_people", tags=["tool", "database", "attendees"])
    def _search_people(self, name: str, limit: int = 10) -> str:
        """Search for people/attendees by name"""
        try:
            results = db_queries.search_attendees_by_name(self.db, name, limit)
            
            if not results:
                return f"No people found matching '{name}'"
            
            output = [f"Found {len(results)} person(s):\n"]
            for person in results:
                pname = person.get('name', 'Unknown')
                title = person.get('title', '')
                company = person.get('company_name', '')
                country = person.get('country', '')
                linkedin = person.get('linkedin', '')
                
                line = f"- **{pname}**"
                if title:
                    line += f" - {title}"
                if company:
                    line += f" @ {company}"
                if country:
                    line += f" ({country})"
                if linkedin:
                    line += f"\n  LinkedIn: {linkedin}"
                output.append(line)
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="advanced_research_chatcbi", tags=["tool", "chatcbi", "external-api"])
    async def _advanced_research(self, company_name: str, focus: str = '') -> str:
        """Perform advanced research via ChatCBI with LLM-optimized queries"""
        # Check credentials using cb_chat
        creds = cb_chat.check_credentials()
        if not creds['configured']:
            return (
                "⚠️ **CB Insights API Credentials Required**\n\n"
                "To use advanced research, please configure credentials in:\n"
                "`app/startup-swipe-schedu/.env`\n\n"
                "Required variables:\n"
                "- CBINSIGHTS_CLIENT_ID=your-client-id\n"
                "- CBINSIGHTS_CLIENT_SECRET=your-secret\n\n"
                f"Status: {creds['message']}\n\n"
                "Contact your CB Insights rep or CSM to obtain credentials."
            )
        
        # Build optimized research query using Qwen LLM
        if focus:
            user_query = f"Provide detailed analysis of {company_name}, focusing on {focus}"
        else:
            user_query = (
                f"Provide comprehensive market intelligence on {company_name} including: "
                f"business model, competitive positioning, funding history, technology stack, "
                f"market trends, and strategic opportunities."
            )
        
        # Optimize query with LLM
        optimization_prompt = f"""You are an expert at formulating precise CB Insights ChatCBI queries.

User wants to research: {company_name}
User's specific interest: {focus if focus else "comprehensive analysis"}

Generate an optimized ChatCBI query that will yield the most relevant and actionable insights.
The query should be specific, focused, and leverage CB Insights' capabilities for market intelligence.

Optimized query:"""
        
        try:
            # Get optimized query from LLM
            opt_response = await llm_completion(
                messages=[{"role": "user", "content": optimization_prompt}],
                model=os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct'),
                use_nvidia_nim=True,
                temperature=0.3,
                max_tokens=200,
                metadata={"purpose": "chatcbi_query_optimization"}
            )
            
            optimized_query = opt_response.choices[0].message.content.strip()
            logger.info(f"Optimized ChatCBI query: {optimized_query}")
            
            # Call ChatCBI API
            result = await cb_chat.ask_question(optimized_query)
            
            return f"## 🔍 ChatCBI Research: {company_name}\n\n{result}\n\n---\n*Source: CB Insights ChatCBI*"
            
        except Exception as e:
            logger.error(f"ChatCBI error: {e}")
            return f"❌ Error performing advanced research: {str(e)}\n\nPlease verify CB Insights credentials."
    
    @traceable(name="search_events", tags=["tool", "database", "events"])
    def _search_events(self, query: str, limit: int = 10) -> str:
        """Search Slush events by title or organizer"""
        from models import SlushEvent
        
        try:
            events = self.db.query(SlushEvent).filter(
                (SlushEvent.title.ilike(f"%{query}%")) |
                (SlushEvent.organizer.ilike(f"%{query}%"))
            ).limit(limit).all()
            
            if not events:
                return f"No events found matching '{query}'"
            
            output = [f"Found {len(events)} event(s):\n"]
            for event in events:
                title = event.title
                organizer = event.organizer
                datetime = event.datetime
                location = event.location or "Location TBA"
                status = ", ".join(event.status) if event.status else "Open"
                
                output.append(f"- **{title}**")
                output.append(f"  Organized by: {organizer}")
                output.append(f"  When: {datetime}")
                output.append(f"  Where: {location}")
                output.append(f"  Status: {status}\n")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_events_by_organizer", tags=["tool", "database", "events"])
    def _search_events_by_organizer(self, organizer: str, limit: int = 10) -> str:
        """Search Slush events by organizer"""
        from models import SlushEvent
        
        try:
            events = self.db.query(SlushEvent).filter(
                SlushEvent.organizer.ilike(f"%{organizer}%")
            ).limit(limit).all()
            
            if not events:
                return f"No events found organized by '{organizer}'"
            
            output = [f"Found {len(events)} event(s) organized by {organizer}:\n"]
            for event in events:
                title = event.title
                datetime = event.datetime
                location = event.location or "Location TBA"
                status = ", ".join(event.status) if event.status else "Open"
                
                output.append(f"- **{title}**")
                output.append(f"  When: {datetime}")
                output.append(f"  Where: {location}")
                output.append(f"  Status: {status}\n")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_events_by_date", tags=["tool", "database", "events"])
    def _search_events_by_date(self, date_query: str, limit: int = 10) -> str:
        """Search Slush events by date"""
        from models import SlushEvent
        
        try:
            events = self.db.query(SlushEvent).filter(
                SlushEvent.datetime.ilike(f"%{date_query}%")
            ).limit(limit).all()
            
            if not events:
                return f"No events found for '{date_query}'"
            
            output = [f"Found {len(events)} event(s) on {date_query}:\n"]
            for event in events:
                title = event.title
                organizer = event.organizer
                datetime = event.datetime
                location = event.location or "Location TBA"
                categories = ", ".join(event.categories) if event.categories else "General"
                
                output.append(f"- **{title}**")
                output.append(f"  By: {organizer}")
                output.append(f"  Time: {datetime}")
                output.append(f"  Location: {location}")
                output.append(f"  Categories: {categories}\n")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="search_events_by_category", tags=["tool", "database", "events"])
    def _search_events_by_category(self, category: str, limit: int = 10) -> str:
        """Search Slush events by category"""
        from models import SlushEvent
        from sqlalchemy import cast, String
        
        try:
            events = self.db.query(SlushEvent).filter(
                cast(SlushEvent.categories, String).ilike(f"%{category}%")
            ).limit(limit).all()
            
            if not events:
                return f"No events found in category '{category}'"
            
            output = [f"Found {len(events)} event(s) in category {category}:\n"]
            for event in events:
                title = event.title
                organizer = event.organizer
                datetime = event.datetime
                location = event.location or "Location TBA"
                
                output.append(f"- **{title}**")
                output.append(f"  By: {organizer}")
                output.append(f"  When: {datetime}")
                output.append(f"  Where: {location}\n")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="get_event_details", tags=["tool", "database", "events"])
    def _get_event_details(self, title: str) -> str:
        """Get detailed information about a Slush event"""
        from models import SlushEvent
        
        try:
            event = self.db.query(SlushEvent).filter(
                SlushEvent.title.ilike(f"%{title}%")
            ).first()
            
            if not event:
                return f"No event found: '{title}'"
            
            output = [f"# {event.title}\n"]
            output.append(f"**Organized by:** {event.organizer}")
            output.append(f"**Date & Time:** {event.datetime}")
            output.append(f"**Location:** {event.location or 'Location TBA'}")
            
            if event.categories and len(event.categories) > 0:
                output.append(f"**Categories:** {', '.join(event.categories)}")
            
            if event.status and len(event.status) > 0:
                output.append(f"**Status:** {', '.join(event.status)}")
            
            if event.insight:
                output.append(f"\n**Insights:** {event.insight}")
            
            if event.tags and len(event.tags) > 0:
                output.append(f"**Tags:** {', '.join(event.tags)}")
            
            if event.rating:
                output.append(f"**Rating:** {'⭐' * event.rating}")
            
            if event.followUp:
                output.append("**Follow-up:** Yes ✓")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @traceable(name="get_all_event_organizers", tags=["tool", "database", "events"])
    def _get_all_event_organizers(self, limit: int = 20) -> str:
        """Get list of all event organizers at Slush"""
        from models import SlushEvent
        from sqlalchemy import func
        
        try:
            organizers = self.db.query(
                SlushEvent.organizer,
                func.count(SlushEvent.id).label('event_count')
            ).group_by(SlushEvent.organizer)\
             .order_by(func.count(SlushEvent.id).desc())\
             .limit(limit)\
             .all()
            
            if not organizers:
                return "No event organizers found"
            
            output = [f"Found {len(organizers)} event organizer(s):\n"]
            for org, count in organizers:
                plural = "event" if count == 1 else "events"
                output.append(f"- **{org}** ({count} {plural})")
            
            return '\n'.join(output)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_tools_description(self) -> str:
        """Get formatted description of all tools"""
        lines = ["**Available Tools:**\n"]
        for name, info in self.tools.items():
            lines.append(f"\n{name}")
            lines.append(f"  Description: {info['description']}")
            lines.append(f"  Parameters:")
            for param, desc in info['parameters'].items():
                lines.append(f"    - {param}: {desc}")
        
        return '\n'.join(lines)
    
    @traceable(name="execute_tool", tags=["tool-execution"])
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            func = self.tools[tool_name]['function']
            
            # Handle async functions
            if asyncio.iscoroutinefunction(func):
                return await func(**parameters)
            else:
                return func(**parameters)
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return f"Tool execution error: {str(e)}"


# ====================
# ReAct Agent
# ====================

class ReActAgent:
    """
    ReAct (Reasoning + Acting) Agent for AI Concierge
    
    This agent follows the ReAct pattern:
    1. Thought: Reason about what to do
    2. Action: Use a tool
    3. Observation: Process tool result
    4. Repeat until answer is ready
    """
    
    def __init__(self, db: Session, model: str = None):
        self.db = db
        self.model = model or os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct')
        self.tools = ToolRegistry(db)
        self.max_iterations = 5
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with ReAct instructions"""
        tools_desc = self.tools.get_tools_description()
        
        return f"""You are an elite AI Concierge for Slush 2025, the premier European startup conference in Helsinki.

{tools_desc}

## ReAct Protocol
You follow the ReAct (Reasoning + Acting) pattern to answer questions:

1. **Thought:** Analyze the question and decide what action to take
2. **Action:** Choose a tool and specify parameters in JSON format
3. **Observation:** Review the tool result (provided by the system)
4. **Repeat** until you have enough information
5. **Final Answer:** Provide a comprehensive response to the user

## Response Format
Use this EXACT format:

Thought: I need to search for information about...
Action: search_startups_by_name
Action Input: {{"query": "company name", "limit": 5}}

STOP HERE. Do not continue beyond this point. Do not write "Observation:" yourself.

⚠️ CRITICAL RULES:
- NEVER write or predict "Observation:" yourself - only the system provides observations
- After writing "Action Input:", you MUST stop immediately
- Do NOT make up or fabricate any data
- Wait for the ACTUAL observation from the tool execution
- If you see "Observation:" it means the tool has run - analyze that REAL data
- ONLY provide "Final Answer:" when you have gathered sufficient REAL observations
- For advanced/deep research, use the `advanced_research` tool which calls CB Insights ChatCBI

When you receive an observation and are ready to answer:
Thought: I now have enough information to answer
Final Answer: [Your comprehensive response based on REAL observations]

## Tool Usage Strategy
- **Basic queries**: Use `search_startups_by_name` or `search_startups_by_industry`
- **Detailed info**: Use `get_startup_details` for comprehensive startup data
- **People search**: 
  - Use `search_people` to find specific individuals by name (e.g., "Eduardo Paz")
  - Use `search_attendees` for broader searches by company or role
- **Event search**: 
  - Use `search_events` to find events by title or organizer
  - Use `search_events_by_organizer` to see all events hosted by a company
  - Use `search_events_by_date` to find events on specific dates (e.g., "Nov 19", "Nov 20")
  - Use `search_events_by_category` to find events by topic (AI, Demo, Networking, etc.)
  - Use `get_event_details` for comprehensive information about a specific event
  - Use `get_all_event_organizers` to see which companies are hosting events
- **Advanced research**: Use `advanced_research` for deep market intelligence via CB Insights ChatCBI:
  - Competitive analysis
  - Market intelligence
  - Funding trends and financial analysis
  - Technology assessment
  - Strategic opportunities
  - Business model analysis
  - When user explicitly asks for "advanced research" or "deep research"

## Rules
- ALWAYS use tools to get real data - never make up information
- Be concise in thoughts, detailed in final answers
- Use multiple tools if needed for comprehensive answers
- Format final answers professionally with markdown
- Suggest relevant follow-up actions
- If data is not available (Observation says "not found"), acknowledge it honestly

## Example Interaction

Question: Tell me about SimplifAI startup

Thought: I should search for this startup in the database
Action: search_startups_by_name
Action Input: {{"query": "SimplifAI", "limit": 1}}

STOP

Observation: Found 1 startup:
- SimplifAI | AI/ML | San Francisco, USA

Thought: Now I should get detailed information
Action: get_startup_details
Action Input: {{"company_name": "SimplifAI"}}

STOP

Observation: [Detailed info...]

Thought: I have comprehensive information now
Final Answer: **SimplifAI** is an AI/ML startup based in San Francisco...

## Example with Advanced Research

Question: Perform advanced research on SimplifAI

Thought: The user wants deep market intelligence. I should use advanced_research tool
Action: advanced_research
Action Input: {{"company_name": "SimplifAI", "focus": ""}}

STOP

Observation: [CB Insights comprehensive analysis...]

Thought: I received detailed ChatCBI research
Final Answer: Based on CB Insights market intelligence...

Remember: YOU are at Slush 2025 helping attendees make valuable connections! 🚀"""

    async def _react_iteration(self, conversation: List[Dict], iteration: int) -> tuple[str, List[Dict]]:
        """Single ReAct iteration with tracing"""
        # Get agent's response
        response = await llm_completion(
            messages=conversation,
            model=self.model,
            use_nvidia_nim=True,
            temperature=0.7,
            max_tokens=2000,
            metadata={"iteration": iteration, "step": "reasoning"}
        )
        
        agent_response = response.choices[0].message.content
        logger.info(f"Iteration {iteration} - Agent response: {agent_response[:200]}...")
        
        # Add to conversation
        conversation.append({"role": "assistant", "content": agent_response})
        
        return agent_response, conversation
    
    @traceable(
        name="react_agent_answer",
        run_type="chain",
        tags=["agent", "react", "qwen"],
        metadata={"pattern": "ReAct", "model": "qwen"}
    )
    async def answer_question(self, question: str) -> str:
        """
        Answer a question using ReAct pattern
        
        Args:
            question: User's question
            
        Returns:
            Agent's response
        """
        system_prompt = self._build_system_prompt()
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        for iteration in range(self.max_iterations):
            logger.info(f"ReAct iteration {iteration + 1}/{self.max_iterations}")
            
            try:
                # Run iteration with tracing
                agent_response, conversation = await self._react_iteration(conversation, iteration)
                
                # Check if this is a final answer
                if "Final Answer:" in agent_response:
                    # Extract final answer
                    final_answer = agent_response.split("Final Answer:")[-1].strip()
                    return final_answer
                
                # Extract action and parameters - strip any hallucinated observations
                # Split at "STOP" or "Observation:" to ignore anything the model added after
                clean_response = agent_response
                if "Observation:" in clean_response:
                    # Agent hallucinated an observation - truncate before it
                    clean_response = clean_response.split("Observation:")[0]
                    logger.warning("Agent hallucinated an observation - removed it")
                
                action_match = re.search(r'Action:\s*(\w+)', clean_response)
                action_input_match = re.search(r'Action Input:\s*({.*?})', clean_response, re.DOTALL)
                
                if action_match and action_input_match:
                    tool_name = action_match.group(1)
                    try:
                        parameters = json.loads(action_input_match.group(1))
                    except json.JSONDecodeError:
                        parameters = {}
                    
                    # Execute tool
                    logger.info(f"Executing tool: {tool_name} with {parameters}")
                    observation = await self.tools.execute_tool(tool_name, parameters)
                    logger.info(f"Tool result: {observation[:200]}...")
                    
                    # Add observation to conversation
                    conversation.append({
                        "role": "user",
                        "content": f"Observation: {observation}\n\nContinue your reasoning or provide Final Answer."
                    })
                else:
                    # No clear action found, prompt for final answer
                    if iteration == self.max_iterations - 1:
                        # Last iteration, force final answer
                        conversation.append({
                            "role": "user",
                            "content": "Please provide your Final Answer now based on the information gathered."
                        })
                    else:
                        # Model might have made an error, give it another chance
                        conversation.append({
                            "role": "user",
                            "content": "Please specify your next Action and Action Input, or provide your Final Answer."
                        })
                
            except Exception as e:
                logger.error(f"Error in ReAct iteration: {e}")
                return f"I encountered an error while processing your question: {str(e)}"
        
        # Max iterations reached without final answer
        return "I apologize, but I'm having trouble formulating a complete answer. Please try rephrasing your question."


# ====================
# Main Concierge Class
# ====================

class QwenAgenticConcierge:
    """Main concierge class using ReAct agent with LangSmith tracing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = ReActAgent(db)
    
    @traceable(
        name="concierge_answer_question",
        run_type="chain",
        tags=["concierge", "main-entry"],
        metadata={"service": "startup-swiper", "agent_type": "qwen-react"}
    )
    async def answer_question(self, question: str) -> str:
        """Answer a question"""
        return await self.agent.answer_question(question)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.agent.tools.tools.keys())


# ====================
# Factory Function
# ====================

def create_qwen_concierge(db: Session) -> QwenAgenticConcierge:
    """
    Create a Qwen-powered agentic AI Concierge
    
    Args:
        db: Database session
        
    Returns:
        QwenAgenticConcierge instance
    """
    return QwenAgenticConcierge(db)


# ====================
# Quick Test
# ====================

if __name__ == "__main__":
    async def test():
        db = SessionLocal()
        try:
            concierge = create_qwen_concierge(db)
            
            questions = [
                "Search for SimplifAI startup",
                "Find AI startups"
            ]
            
            for q in questions:
                print(f"\n{'='*60}")
                print(f"Q: {q}")
                print('='*60)
                answer = await concierge.answer_question(q)
                print(answer)
        finally:
            db.close()
    
    asyncio.run(test())
