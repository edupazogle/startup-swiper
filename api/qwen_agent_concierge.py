"""
Qwen-Agent Based Concierge with Proper Function Calling

This implementation uses qwen-agent framework for proper agentic behavior,
includes LangSmith tracing, ChatCBI integration, and comprehensive tool support.

Features:
- Qwen-Agent framework for proper tool calling (not text-based ReAct)
- LangSmith tracing for observability
- ChatCBI integration with credential verification
- People search functionality
- Proper tool execution hidden from users
- Uses qwen/qwen3-next-80b-a3b-instruct model
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

# Load environment FIRST
from dotenv import load_dotenv

env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✓ Qwen-Agent Concierge: Loaded environment from: {env_path}")
        break

# Verify key environment variables
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "startup-swiper-concierge")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CBINSIGHTS_CLIENT_ID = os.getenv("CBINSIGHTS_CLIENT_ID")
CBINSIGHTS_CLIENT_SECRET = os.getenv("CBINSIGHTS_CLIENT_SECRET")

print(f"✓ LangSmith Tracing: {LANGSMITH_TRACING}")
print(f"✓ LangSmith Project: {LANGSMITH_PROJECT}")
print(f"✓ NVIDIA API Key: {'Set' if NVIDIA_API_KEY else 'Missing'}")
print(f"✓ CB Insights Credentials: {'Set' if CBINSIGHTS_CLIENT_ID and CBINSIGHTS_CLIENT_SECRET else 'Missing'}")

# LangSmith tracing
from langsmith import traceable
from langsmith.run_helpers import tracing_context

# Qwen-Agent imports
from qwen_agent.llm import get_chat_model

# Local imports
from database import SessionLocal
import db_queries
from cb_insights_integration import cb_chat

logger = logging.getLogger(__name__)

# ====================
# Tool Functions
# ====================

class QwenConciergeTools:
    """Tools available to the Qwen agent"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @traceable(name="search_startups_by_name")
    def search_startups_by_name(self, query: str, limit: int = 10) -> str:
        """Search for startups by company name"""
        try:
            results = db_queries.search_startups_by_name(self.db, query, limit)
            
            if not results:
                return f"No startups found matching '{query}'"
            
            output = []
            for startup in results:
                output.append(f"**{startup.get('name', 'N/A')}**")
                if startup.get('description'):
                    output.append(f"  Description: {startup['description'][:200]}...")
                if startup.get('industry'):
                    output.append(f"  Industry: {startup['industry']}")
                if startup.get('city') and startup.get('country'):
                    output.append(f"  Location: {startup['city']}, {startup['country']}")
                output.append("")
            
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error searching startups: {e}")
            return f"Error searching startups: {str(e)}"
    
    @traceable(name="search_people")
    def search_people(self, name: str, limit: int = 10) -> str:
        """Search for people/attendees by name"""
        try:
            query = f"%{name}%"
            results = self.db.execute(
                "SELECT * FROM attendees WHERE name LIKE :query LIMIT :limit",
                {"query": query, "limit": limit}
            ).fetchall()
            
            if not results:
                return f"No people found matching '{name}'"
            
            output = []
            for person in results:
                output.append(f"**{person.name}**")
                if person.title:
                    output.append(f"  Title: {person.title}")
                if person.company_name:
                    output.append(f"  Company: {person.company_name}")
                if person.city and person.country:
                    output.append(f"  Location: {person.city}, {person.country}")
                if person.bio:
                    output.append(f"  Bio: {person.bio[:150]}...")
                if person.linkedin:
                    output.append(f"  LinkedIn: {person.linkedin}")
                output.append("")
            
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error searching people: {e}")
            return f"Error searching people: {str(e)}"
    
    @traceable(name="get_startup_details")
    def get_startup_details(self, company_name: str) -> str:
        """Get detailed information about a specific startup"""
        try:
            startup = db_queries.get_startup_by_name(self.db, company_name)
            
            if not startup:
                return f"Startup '{company_name}' not found in database"
            
            output = [f"# {startup.get('name', 'N/A')}"]
            
            if startup.get('description'):
                output.append(f"\n**Description:** {startup['description']}")
            
            if startup.get('industry'):
                output.append(f"\n**Industry:** {startup['industry']}")
            
            if startup.get('city') or startup.get('country'):
                location = f"{startup.get('city', '')}, {startup.get('country', '')}".strip(', ')
                output.append(f"**Location:** {location}")
            
            if startup.get('website'):
                output.append(f"**Website:** {startup['website']}")
            
            # Funding information
            if startup.get('funding_stage'):
                output.append(f"\n**Funding Stage:** {startup['funding_stage']}")
            
            if startup.get('total_funding'):
                output.append(f"**Total Funding:** ${startup['total_funding']:,.0f}")
            
            # Team information
            if startup.get('team_members'):
                output.append("\n**Team:**")
                for member in startup.get('team_members', [])[:5]:  # Show first 5
                    output.append(f"  - {member.get('name')}: {member.get('role')}")
            
            # Technology/Topics
            if startup.get('topics'):
                output.append(f"\n**Technology:** {', '.join(startup['topics'][:10])}")
            
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error getting startup details: {e}")
            return f"Error getting startup details: {str(e)}"
    
    @traceable(name="search_startups_by_industry")
    def search_startups_by_industry(self, industry: str, limit: int = 10) -> str:
        """Search for startups by industry"""
        try:
            results = db_queries.search_startups_by_industry(self.db, industry, limit)
            
            if not results:
                return f"No startups found in '{industry}' industry"
            
            output = [f"Found {len(results)} startups in {industry}:\n"]
            for startup in results:
                output.append(f"**{startup.get('name', 'N/A')}**")
                if startup.get('description'):
                    output.append(f"  {startup['description'][:150]}...")
                output.append("")
            
            return "\n".join(output)
        except Exception as e:
            logger.error(f"Error searching by industry: {e}")
            return f"Error searching by industry: {str(e)}"
    
    @traceable(name="advanced_research_chatcbi")
    async def advanced_research_chatcbi(self, company_name: str) -> str:
        """
        Perform advanced research using CB Insights ChatCBI API.
        This requires valid CB Insights credentials in the environment.
        """
        try:
            # Check credentials
            if not CBINSIGHTS_CLIENT_ID or not CBINSIGHTS_CLIENT_SECRET:
                return (
                    "⚠️ CB Insights API credentials are not configured.\n\n"
                    "To use advanced research, please ensure the following environment variables are set:\n"
                    "- CBINSIGHTS_CLIENT_ID\n"
                    "- CBINSIGHTS_CLIENT_SECRET\n\n"
                    "These should be added to: app/startup-swipe-schedu/.env"
                )
            
            # Craft optimized research query
            research_query = f"""Provide a comprehensive analysis of {company_name} including:
1. Business model and value proposition
2. Market position and competitive landscape
3. Recent funding and financial health
4. Key strengths and growth opportunities
5. Technology and innovation focus
6. Strategic partnerships and customers
7. Leadership team and expertise"""
            
            logger.info(f"Performing ChatCBI research on: {company_name}")
            
            # Call ChatCBI API
            response = await cb_chat(research_query)
            
            if response.get("error"):
                return f"❌ ChatCBI API Error: {response['error']}"
            
            # Format the response
            output = [
                f"# Advanced Research: {company_name}",
                "",
                response.get("message", "No response from ChatCBI"),
                "",
                "---",
                "*Research powered by CB Insights ChatCBI API*"
            ]
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error in ChatCBI research: {e}")
            return f"Error performing advanced research: {str(e)}"
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Return function definitions for Qwen-Agent"""
        return [
            {
                "name": "search_startups_by_name",
                "description": "Search for startups in the database by company name. Returns basic info about matching startups.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The company name to search for (partial matches allowed)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_people",
                "description": "Search for people/attendees by name. Use this when looking for specific individuals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 10
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_startup_details",
                "description": "Get comprehensive details about a specific startup including team, funding, and technology.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "The exact company name"
                        }
                    },
                    "required": ["company_name"]
                }
            },
            {
                "name": "search_startups_by_industry",
                "description": "Search for startups by industry or sector (e.g., 'AI', 'FinTech', 'HealthTech').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "The industry to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 10
                        }
                    },
                    "required": ["industry"]
                }
            },
            {
                "name": "advanced_research_chatcbi",
                "description": "Perform deep market research using CB Insights ChatCBI API. Use ONLY when user explicitly asks for 'advanced research' or 'deep research' on a startup. Requires CB Insights API credentials.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Company to research"
                        }
                    },
                    "required": ["company_name"]
                }
            }
        ]

# ====================
# Qwen-Agent Concierge
# ====================

class QwenAgentConcierge:
    """Qwen-Agent based concierge with proper function calling"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = QwenConciergeTools(db)
        
        # Initialize Qwen model via qwen-agent
        self.llm = get_chat_model({
            "model": "qwen/qwen3-next-80b-a3b-instruct",
            "model_server": os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            "api_key": NVIDIA_API_KEY,
            "generate_cfg": {
                "temperature": 0.7,
                "top_p": 0.8,
                "max_tokens": 2048,
                "extra_body": {
                    "chat_template_kwargs": {"enable_thinking": False}  # Disable thinking mode
                }
            }
        })
        
        # Get function definitions
        self.functions = self.tools.get_function_definitions()
        
        logger.info(f"✓ Qwen-Agent Concierge initialized with {len(self.functions)} tools")
    
    def _get_function_by_name(self, function_name: str):
        """Get the actual function object by name"""
        function_map = {
            "search_startups_by_name": self.tools.search_startups_by_name,
            "search_people": self.tools.search_people,
            "get_startup_details": self.tools.get_startup_details,
            "search_startups_by_industry": self.tools.search_startups_by_industry,
            "advanced_research_chatcbi": self.tools.advanced_research_chatcbi,
        }
        return function_map.get(function_name)
    
    @traceable(name="qwen_agent_answer_question")
    async def answer_question(self, question: str) -> str:
        """
        Answer a question using Qwen-Agent with proper function calling.
        
        This follows the Qwen-Agent pattern:
        1. Send question with available functions
        2. Model decides which functions to call
        3. Execute functions and collect results
        4. Send results back to model for final answer
        5. Return only the final answer to user (hide tool execution)
        """
        try:
            # Prepare messages with system prompt
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful AI concierge assistant for a startup event platform.

You have access to tools to search for startups, people, and get detailed information.

CRITICAL RULES:
1. When user asks about a person (e.g., "Who is Eduardo Paz?"), use search_people tool
2. When user asks for startup information, use search_startups_by_name or get_startup_details
3. When user asks for industry insights, use search_startups_by_industry
4. Use advanced_research_chatcbi ONLY when user explicitly requests "advanced research" or "deep research"
5. Provide clear, concise answers based on tool results
6. If no results found, say so clearly

Format your responses professionally and conversationally."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            # Step 1: Initial call with functions available
            logger.info(f"Step 1: Sending question to Qwen-Agent: {question}")
            
            response_stream = self.llm.chat(
                messages=messages,
                functions=self.functions
            )
            
            # Collect all responses
            responses = []
            for response_list in response_stream:
                responses.extend(response_list)
            
            # Step 2: Check for function calls
            tool_calls = [r for r in responses if r.get("function_call")]
            
            if not tool_calls:
                # No tool calls, return direct answer
                final_response = next((r.get("content") for r in responses if r.get("content")), None)
                if final_response:
                    logger.info("No tool calls needed, returning direct answer")
                    return final_response
                return "I apologize, I couldn't process that request. Could you rephrase your question?"
            
            # Step 3: Execute tool calls
            logger.info(f"Step 3: Executing {len(tool_calls)} tool calls")
            
            messages.extend(responses)
            
            for tool_call in tool_calls:
                fn_call = tool_call.get("function_call")
                if not fn_call:
                    continue
                
                fn_name = fn_call.get("name")
                fn_args = json.loads(fn_call.get("arguments", "{}"))
                
                logger.info(f"Executing tool: {fn_name} with args: {fn_args}")
                
                # Get and execute the function
                fn = self._get_function_by_name(fn_name)
                if fn:
                    try:
                        # Handle async functions
                        if fn_name == "advanced_research_chatcbi":
                            result = await fn(**fn_args)
                        else:
                            result = fn(**fn_args)
                        
                        result_str = str(result) if not isinstance(result, str) else result
                        
                        # Add function result to messages
                        messages.append({
                            "role": "function",
                            "name": fn_name,
                            "content": result_str
                        })
                        
                        logger.info(f"Tool {fn_name} executed successfully")
                    except Exception as e:
                        error_msg = f"Error executing {fn_name}: {str(e)}"
                        logger.error(error_msg)
                        messages.append({
                            "role": "function",
                            "name": fn_name,
                            "content": error_msg
                        })
            
            # Step 4: Get final answer from model
            logger.info("Step 4: Getting final answer from model")
            
            final_stream = self.llm.chat(
                messages=messages,
                functions=self.functions
            )
            
            final_responses = []
            for response_list in final_stream:
                final_responses.extend(response_list)
            
            # Extract final answer (only content, not tool calls)
            final_answer = next(
                (r.get("content") for r in final_responses if r.get("content") and not r.get("function_call")),
                None
            )
            
            if final_answer:
                logger.info("Final answer generated successfully")
                return final_answer
            
            return "I processed your request but couldn't generate a final answer. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error in answer_question: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}. Please try again."


def create_qwen_agent_concierge(db: Session) -> QwenAgentConcierge:
    """Factory function to create Qwen-Agent concierge"""
    return QwenAgentConcierge(db)
