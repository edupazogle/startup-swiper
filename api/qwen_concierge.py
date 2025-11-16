"""
Qwen-Agent Enhanced AI Concierge

This module provides a fully agentic AI Concierge using Qwen-Agent framework  
with advanced prompting, tool usage, and multi-turn conversations.

Based on: https://github.com/QwenLM/Qwen-Agent

Note: Uses LiteLLM for flexible model support including NVIDIA NIM
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Iterator
from pathlib import Path
from sqlalchemy.orm import Session

# Import Qwen-Agent components
try:
    from qwen_agent.agents import ReActChat  # Use ReAct agent for better tool use
    from qwen_agent.tools.base import BaseTool, register_tool
    HAS_QWEN_AGENT = True
except ImportError:
    HAS_QWEN_AGENT = False
    logger = logging.getLogger(__name__)
    logger.warning("Qwen-Agent not installed. Install with: pip install qwen-agent")

from database import SessionLocal
import models
import db_queries
from cb_insights_integration import cb_chat
from llm_config import llm_completion

logger = logging.getLogger(__name__)

# ====================
# Custom Tools for Qwen Agent
# ====================

@register_tool('search_startups_by_name')
class SearchStartupsByName(BaseTool):
    """Search for startups in the database by name"""
    
    description = (
        'Search for startups by company name. '
        'Use this when the user asks about a specific startup by name.'
    )
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': 'The company name to search for (partial matches allowed)',
        'required': True
    }, {
        'name': 'limit',
        'type': 'integer', 
        'description': 'Maximum number of results to return (default: 10)',
        'required': False
    }]
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Execute the search"""
        query = params.get('query', '')
        limit = params.get('limit', 10)
        
        db = kwargs.get('db')
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            results = db_queries.search_startups(db, query_text=query, limit=limit)
            
            if not results:
                return f"No startups found matching '{query}'"
            
            # Format results
            output = [f"Found {len(results)} startup(s):\n"]
            for startup in results:
                output.append(f"\n**{startup.get('company_name', 'Unknown')}**")
                output.append(f"Industry: {startup.get('primary_industry', 'N/A')}")
                output.append(f"Location: {startup.get('company_city', '')}, {startup.get('company_country', '')}")
                
                if startup.get('company_description'):
                    desc = startup['company_description'][:150]
                    output.append(f"Description: {desc}...")
                
                if startup.get('total_funding'):
                    output.append(f"Funding: ${startup['total_funding']}M")
            
            return '\n'.join(output)
            
        except Exception as e:
            logger.error(f"Error searching startups: {e}")
            return f"Error searching startups: {str(e)}"
        finally:
            if close_db:
                db.close()


@register_tool('search_startups_by_industry')
class SearchStartupsByIndustry(BaseTool):
    """Search for startups by industry"""
    
    description = (
        'Search for startups by industry or sector. '
        'Use this when the user asks about startups in a specific industry.'
    )
    parameters = [{
        'name': 'industry',
        'type': 'string',
        'description': 'The industry to search for (e.g., "AI", "FinTech", "HealthTech")',
        'required': True
    }, {
        'name': 'limit',
        'type': 'integer',
        'description': 'Maximum number of results (default: 10)',
        'required': False
    }]
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Execute the search"""
        industry = params.get('industry', '')
        limit = params.get('limit', 10)
        
        db = kwargs.get('db')
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            results = db_queries.search_startups_by_industry(db, industry, limit)
            
            if not results:
                return f"No startups found in '{industry}' industry"
            
            output = [f"Found {len(results)} startup(s) in {industry}:\n"]
            for startup in results:
                output.append(f"- {startup.get('company_name', 'Unknown')} ({startup.get('company_country', 'Global')})")
            
            return '\n'.join(output)
            
        except Exception as e:
            logger.error(f"Error searching by industry: {e}")
            return f"Error: {str(e)}"
        finally:
            if close_db:
                db.close()


@register_tool('get_startup_details')
class GetStartupDetails(BaseTool):
    """Get detailed information about a specific startup"""
    
    description = (
        'Get comprehensive details about a specific startup including '
        'team members, funding, technology, and social presence.'
    )
    parameters = [{
        'name': 'company_name',
        'type': 'string',
        'description': 'The exact company name',
        'required': True
    }]
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Get startup details"""
        company_name = params.get('company_name', '')
        
        db = kwargs.get('db')
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Search for the startup
            results = db_queries.search_startups(db, query_text=company_name, limit=1)
            
            if not results:
                return f"No startup found with name '{company_name}'"
            
            startup = results[0]
            
            # Build detailed response
            output = [f"# {startup.get('company_name', 'Unknown')}\n"]
            
            if startup.get('company_description'):
                output.append(f"**Description:** {startup['company_description']}\n")
            
            output.append(f"**Industry:** {startup.get('primary_industry', 'N/A')}")
            output.append(f"**Location:** {startup.get('company_city', '')}, {startup.get('company_country', '')}")
            output.append(f"**Founded:** {startup.get('founded_year', 'N/A')}")
            output.append(f"**Employees:** {startup.get('employee_count', 'N/A')}")
            
            if startup.get('total_funding'):
                output.append(f"\n**Funding:** ${startup['total_funding']}M")
                output.append(f"**Stage:** {startup.get('funding_stage', 'N/A')}")
            
            if startup.get('website'):
                output.append(f"\n**Website:** {startup['website']}")
            
            return '\n'.join(output)
            
        except Exception as e:
            logger.error(f"Error getting startup details: {e}")
            return f"Error: {str(e)}"
        finally:
            if close_db:
                db.close()


@register_tool('advanced_research_chatcbi')
class AdvancedResearchChatCBI(BaseTool):
    """Perform advanced research using CB Insights ChatCBI"""
    
    description = (
        'Use CB Insights ChatCBI API for comprehensive market research on a startup. '
        'Provides business model analysis, competitive landscape, funding trends, '
        'technology insights, and market positioning. Use this for deep analysis.'
    )
    parameters = [{
        'name': 'company_name',
        'type': 'string',
        'description': 'The company name to research',
        'required': True
    }, {
        'name': 'research_focus',
        'type': 'string',
        'description': 'Specific aspect to focus on (optional): "funding", "competitors", "technology", "market"',
        'required': False
    }]
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Execute ChatCBI research"""
        company_name = params.get('company_name', '')
        focus = params.get('research_focus', '')
        
        # Check credentials
        creds = cb_chat.check_credentials()
        if not creds['configured']:
            return (
                "⚠️ CB Insights API credentials required. "
                "Please configure CB_INSIGHTS_CLIENT_ID and CB_INSIGHTS_CLIENT_SECRET "
                "in app/startup-swipe-schedu/.env"
            )
        
        # Build research query
        if focus:
            query = f"Provide detailed analysis of {company_name}, focusing on {focus}"
        else:
            query = (
                f"Provide comprehensive analysis of {company_name} including: "
                f"business model, competitive landscape, funding history, "
                f"technology stack, and market position"
            )
        
        try:
            import asyncio
            # Run async ChatCBI call
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in event loop, create task
                import nest_asyncio
                nest_asyncio.apply()
            
            result = asyncio.run(cb_chat.ask_question(query))
            return f"## ChatCBI Research: {company_name}\n\n{result}"
            
        except Exception as e:
            logger.error(f"ChatCBI error: {e}")
            return f"Error performing advanced research: {str(e)}"


@register_tool('search_attendees')
class SearchAttendees(BaseTool):
    """Search for event attendees"""
    
    description = (
        'Search for attendees at Slush 2025 by name, company, or role. '
        'Use this when users ask about specific people or want to find attendees.'
    )
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': 'Search query (name, company, or role)',
        'required': True
    }, {
        'name': 'limit',
        'type': 'integer',
        'description': 'Maximum results (default: 10)',
        'required': False
    }]
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Search attendees"""
        query = params.get('query', '')
        limit = params.get('limit', 10)
        
        db = kwargs.get('db')
        if not db:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            # Try different search methods
            results = []
            
            # Search by name
            results.extend(db_queries.search_attendees_by_name(db, query, limit))
            
            # Search by company if no name results
            if not results:
                results.extend(db_queries.search_attendees_by_company(db, query, limit))
            
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
            logger.error(f"Error searching attendees: {e}")
            return f"Error: {str(e)}"
        finally:
            if close_db:
                db.close()


# ====================
# Qwen-Agent Concierge
# ====================

class QwenAIConcierge:
    """
    AI Concierge powered by Qwen-Agent framework
    
    Features:
    - Advanced agentic reasoning
    - Multi-turn conversations
    - Tool use with proper planning
    - Enhanced prompting
    - Memory across conversations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = None
        self._init_agent()
    
    def _init_agent(self):
        """Initialize the Qwen Agent with custom configuration"""
        
        # Get model configuration from environment
        model_name = os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct')
        api_key = os.getenv('NVIDIA_API_KEY')
        api_base = os.getenv('NVIDIA_NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')
        
        # Configure LLM for Qwen-Agent to use OpenAI-compatible API (NVIDIA NIM)
        llm_cfg = {
            'model_type': 'qwen-openai',  # Use OpenAI-compatible mode
            'model': model_name,
            'api_key': api_key,
            'base_url': api_base,  # NVIDIA NIM endpoint
            'generate_cfg': {
                'top_p': 0.8,
                'temperature': 0.7,
                'max_tokens': 2000,
            }
        }
        
        # System instructions with enhanced prompting
        system_message = """You are an elite AI Concierge for Slush 2025, the premier European startup conference in Helsinki.

## Your Role
You are a knowledgeable, proactive assistant helping attendees, investors, and startups maximize their conference experience. You have access to comprehensive tools to query startup data, attendee information, and perform advanced research.

## Core Capabilities
1. **Startup Intelligence**: Search startups by name, industry, location, or funding stage
2. **Deep Research**: Use CB Insights ChatCBI for comprehensive market analysis
3. **Attendee Networking**: Find and connect attendees by name, company, or role
4. **Event Navigation**: Help with schedules, venue directions, and meeting coordination

## Communication Guidelines
- **Be Proactive**: Anticipate needs and suggest relevant actions
- **Be Precise**: Use tools to get accurate, real-time data
- **Be Contextual**: Reference previous conversation turns
- **Be Professional**: Maintain enthusiasm while being informative
- **Be Helpful**: Offer alternatives when information isn't available

## Tool Usage Strategy
1. **Search First**: Always use tools to verify information before responding
2. **Comprehensive Queries**: When users ask about startups, search by name AND get details
3. **Advanced Research**: Suggest ChatCBI for competitive analysis, funding trends, or market insights
4. **Follow-up**: After providing information, suggest related actions

## Special Features
- **ChatCBI Advanced Research**: For deep startup analysis, use the `advanced_research_chatcbi` tool
  - Business model breakdown
  - Competitive landscape
  - Funding history and trends
  - Technology stack analysis
  - Market positioning

## Example Interactions

User: "Tell me about SimplifAI"
You: [Use search_startups_by_name → get_startup_details → Provide summary → Suggest advanced research if needed]

User: "Find AI startups"  
You: [Use search_startups_by_industry with "AI" → Present results → Offer to dive deeper on specific companies]

User: "Who from Google is attending?"
You: [Use search_attendees with "Google" → List attendees → Suggest networking opportunities]

## Response Format
- Use **bold** for company names and key terms
- Structure information with bullet points and headings
- Include actionable next steps
- Cite data sources when using ChatCBI

## Remember
- You have access to real data - ALWAYS use tools
- Don't make up information - if you don't know, say so and suggest alternatives
- Guide users to the most valuable insights and connections
- Make Slush 2025 an unforgettable experience for every attendee!

Let's make magic happen at Slush 2025! 🚀"""
        
        # Initialize the Assistant agent
        self.agent = Assistant(
            llm=llm_cfg,
            name='Slush2025Concierge',
            description='Elite AI Concierge for Slush 2025 startup conference',
            system_message=system_message,
            function_list=[
                'search_startups_by_name',
                'search_startups_by_industry', 
                'get_startup_details',
                'advanced_research_chatcbi',
                'search_attendees'
            ]
        )
        
        logger.info("✅ Qwen-Agent Concierge initialized successfully")
        logger.info(f"   Model: {model_name}")
        logger.info(f"   Tools: 5 tools registered")
    
    def answer_question(self, question: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Answer a question using Qwen-Agent with tool calling
        
        Args:
            question: User's question
            conversation_history: Optional previous conversation messages
            
        Returns:
            Agent's response with tool execution results
        """
        try:
            # Build messages
            messages = conversation_history or []
            messages.append({'role': 'user', 'content': question})
            
            # Run the agent with tools
            responses = []
            for response in self.agent.run(
                messages=messages,
                db=self.db,  # Pass DB session to tools
                lang='en'
            ):
                responses.append(response)
            
            # Extract final response
            if responses:
                final_response = responses[-1]
                
                # Handle different response types
                if isinstance(final_response, dict):
                    return final_response.get('content', final_response.get('response', str(final_response)))
                else:
                    return str(final_response)
            
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error in Qwen-Agent answer: {e}")
            import traceback
            traceback.print_exc()
            return f"I encountered an error processing your question: {str(e)}"
    
    def answer_question_streaming(
        self, 
        question: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> Iterator[str]:
        """
        Answer with streaming response
        
        Args:
            question: User's question
            conversation_history: Optional previous messages
            
        Yields:
            Response chunks as they're generated
        """
        try:
            messages = conversation_history or []
            messages.append({'role': 'user', 'content': question})
            
            # Stream responses
            for response in self.agent.run(
                messages=messages,
                db=self.db,
                lang='en'
            ):
                if isinstance(response, dict):
                    content = response.get('content', response.get('response', ''))
                    if content:
                        yield content
                else:
                    yield str(response)
                    
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"Error: {str(e)}"


# ====================
# Factory Function
# ====================

def create_qwen_concierge(db: Session) -> QwenAIConcierge:
    """
    Create a Qwen-Agent powered AI Concierge
    
    Args:
        db: Database session
        
    Returns:
        QwenAIConcierge instance ready to use
    """
    return QwenAIConcierge(db)


# ====================
# Convenience Function for Quick Testing
# ====================

async def quick_ask(question: str) -> str:
    """
    Quick way to ask a question without managing DB session
    
    Args:
        question: User's question
        
    Returns:
        Agent's response
    """
    db = SessionLocal()
    try:
        concierge = create_qwen_concierge(db)
        return concierge.answer_question(question)
    finally:
        db.close()


if __name__ == "__main__":
    # Test the Qwen Concierge
    import asyncio
    
    test_questions = [
        "Search for startups in AI industry",
        "Tell me about SimplifAI",
        "Who are the top investors attending?"
    ]
    
    db = SessionLocal()
    concierge = create_qwen_concierge(db)
    
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        print(f"{'='*60}")
        response = concierge.answer_question(q)
        print(response)
    
    db.close()
