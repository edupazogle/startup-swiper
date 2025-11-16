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
                return f"No startups found matching '{query}'"
            
            output = [f"Found {len(results)} startup(s):\n"]
            for startup in results:
                name = startup.get('company_name', 'Unknown')
                industry = startup.get('primary_industry', 'N/A')
                location = f"{startup.get('company_city', '')}, {startup.get('company_country', '')}"
                output.append(f"- **{name}** | {industry} | {location}")
                
            return '\n'.join(output)
        except Exception as e:
            logger.error(f"Error in search_startups_by_name: {e}")
            return f"Error: {str(e)}"


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
            logger.error(f"Error in get_startup_details: {e}")
            return f"Error: {str(e)}"


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
            logger.error(f"Error in search_people: {e}")
            return f"Error: {str(e)}"


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
                return f"No startups found in '{industry}' industry"
            
            output = [f"Found {len(results)} startup(s) in {industry}:\n"]
            for startup in results:
                name = startup.get('company_name', 'Unknown')
                country = startup.get('company_country', 'Global')
                output.append(f"- {name} ({country})")
            
            return '\n'.join(output)
        except Exception as e:
            logger.error(f"Error in search_startups_by_industry: {e}")
            return f"Error: {str(e)}"


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
                "⚠️ **CB Insights API Credentials Required**\n\n"
                "To use advanced research, please configure credentials in:\n"
                "`app/startup-swipe-schedu/.env`\n\n"
                "Required variables:\n"
                "- CBINSIGHTS_CLIENT_ID=your-client-id\n"
                "- CBINSIGHTS_CLIENT_SECRET=your-secret\n\n"
                f"Status: {creds['message']}\n\n"
                "Contact your CB Insights rep or CSM to obtain credentials."
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
            
            return f"## 🔍 ChatCBI Research: {company_name}\n\n{result}\n\n---\n*Source: CB Insights ChatCBI*"
            
        except Exception as e:
            logger.error(f"ChatCBI error: {e}")
            return f"❌ Error performing advanced research: {str(e)}\n\nPlease verify CB Insights credentials."
    
    def call(self, params: Dict[str, Any], **kwargs) -> str:
        """Synchronous wrapper"""
        return asyncio.run(self.call_async(params, **kwargs))


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
                "max_tokens": 2000,
                "extra_body": {
                    "chat_template_kwargs": {
                        "enable_thinking": False  # Disable think mode by default (can be enabled per request)
                    }
                }
            }
        })
        
        # Initialize tools with database session
        self.tools = [
            SearchStartupsByName(db),
            GetStartupDetails(db),
            SearchPeople(db),
            SearchStartupsByIndustry(db),
            AdvancedResearchChatCBI(db),
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
        return """You are the Startup Swiper AI Concierge, an expert assistant for startup discovery and market research.

Your capabilities:
1. **Startup Search**: Find startups by name or industry in our curated database
2. **Attendee Lookup**: Search for event attendees and networking contacts
3. **Startup Details**: Provide comprehensive information about specific companies
4. **Advanced Research**: Deep market analysis via CB Insights (ONLY when explicitly requested)

**IMPORTANT**: 
- ONLY use the 'advanced_research_chatcbi' tool when the user EXPLICITLY asks for:
  - "advanced research"
  - "deep dive"
  - "comprehensive market analysis"
  - "CB Insights research"
- For general questions about startups, use the database tools first
- Be conversational and helpful
- Provide structured, actionable insights
- If you don't know something, say so - don't make up information

Remember: You have access to tools. Use them to provide accurate, real-time information."""
    
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
