"""
Enhanced Qwen Concierge with Proper Function Calling and ChatCBI Integration

This implementation follows Qwen's recommended function calling patterns
and properly integrates CB Insights ChatCBI API with user confirmation.

Key Features:
- Native Qwen function calling (not ReAct text parsing)
- LangSmith tracing for observability
- ChatCBI integration with credential verification
- Tool results hidden from user, only final answers shown
"""

import os
import sys
import json
import logging
import asyncio
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
        print(f"✓ Enhanced Concierge: Loaded environment from: {env_path}")
        break

# LangSmith setup
from langsmith import traceable
from langsmith.run_helpers import tracing_context

# Local imports
from database import SessionLocal
import db_queries
from cb_insights_integration import cb_chat
from llm_config import llm_completion

logger = logging.getLogger(__name__)

# ====================
# Tool Definitions (JSON Schema Format for Qwen)
# ====================

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get tool definitions in Qwen-compatible JSON schema format"""
    return [
        {
            "type": "function",
            "function": {
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
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
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
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["industry"]
                }
            }
        },
        {
            "type": "function",
            "function": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_people",
                "description": "Search for people/attendees by name. Use this when looking for specific individuals like 'Eduardo Paz'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "advanced_research_request",
                "description": "Request to perform deep market research using CB Insights ChatCBI API. This requires user confirmation. Use ONLY when user explicitly asks for 'advanced research' or 'deep research' on a startup.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Company to research"
                        },
                        "focus": {
                            "type": "string",
                            "description": "Optional: Specific aspect (funding/competitors/technology/market)",
                            "default": ""
                        }
                    },
                    "required": ["company_name"]
                }
            }
        }
    ]


# ====================
# Tool Execution
# ====================

class ToolExecutor:
    """Executes tools and returns results"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @traceable(name="search_startups_by_name", tags=["tool", "database"])
    def search_startups_by_name(self, query: str, limit: int = 10) -> str:
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
            logger.error(f"Error searching startups: {e}")
            return f"Error: {str(e)}"
    
    @traceable(name="search_startups_by_industry", tags=["tool", "database"])
    def search_startups_by_industry(self, industry: str, limit: int = 10) -> str:
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
            logger.error(f"Error searching by industry: {e}")
            return f"Error: {str(e)}"
    
    @traceable(name="get_startup_details", tags=["tool", "database"])
    def get_startup_details(self, company_name: str) -> str:
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
            logger.error(f"Error getting startup details: {e}")
            return f"Error: {str(e)}"
    
    @traceable(name="search_people", tags=["tool", "database", "attendees"])
    def search_people(self, name: str, limit: int = 10) -> str:
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
            logger.error(f"Error searching people: {e}")
            return f"Error: {str(e)}"
    
    @traceable(name="advanced_research_request", tags=["tool", "chatcbi", "confirmation"])
    def advanced_research_request(self, company_name: str, focus: str = '') -> str:
        """Request advanced research - returns confirmation message"""
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
        
        # Return request for user confirmation
        focus_text = f", focusing on {focus}" if focus else ""
        return (
            f"🔍 **Advanced Research Request**\n\n"
            f"I can perform deep market intelligence research on **{company_name}**{focus_text} "
            f"using CB Insights ChatCBI API.\n\n"
            f"**This will:**\n"
            f"- Query CB Insights proprietary database\n"
            f"- Use CB Insights ChatCBI API (consumes credits)\n"
            f"- Provide business model analysis, competitive landscape, funding trends\n\n"
            f"**Next Step:** The user should use the `/advanced-research` endpoint "
            f"if they want to proceed with this research.\n\n"
            f"**Alternative:** I can provide basic information from our local database without "
            f"consuming CB Insights credits."
        )
    
    @traceable(name="execute_tool", tags=["tool-execution"])
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool with given parameters"""
        tool_map = {
            "search_startups_by_name": self.search_startups_by_name,
            "search_startups_by_industry": self.search_startups_by_industry,
            "get_startup_details": self.get_startup_details,
            "search_people": self.search_people,
            "advanced_research_request": self.advanced_research_request,
        }
        
        if tool_name not in tool_map:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            func = tool_map[tool_name]
            
            # Handle async functions
            if asyncio.iscoroutinefunction(func):
                return await func(**parameters)
            else:
                return func(**parameters)
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return f"Tool execution error: {str(e)}"


# ====================
# Qwen Function Calling Agent
# ====================

class QwenFunctionCallingAgent:
    """
    Qwen Agent using native function calling support
    
    Uses Qwen's tool use format as documented:
    https://github.com/QwenLM/Qwen-Agent/blob/main/docs/function_calling.md
    """
    
    def __init__(self, db: Session, model: str = None):
        self.db = db
        self.model = model or os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct')
        self.tools = ToolExecutor(db)
        self.max_iterations = 5
        self.tool_definitions = get_tool_definitions()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for function calling"""
        return """You are an elite AI Concierge for Slush 2025, the premier European startup conference in Helsinki.

You have access to tools to search for startups, attendees, and detailed information. 

**Your Role:**
- Help attendees discover interesting startups and connections
- Provide accurate information from the database using tools
- Be concise but comprehensive
- Format responses professionally with markdown
- Suggest relevant follow-up actions

**Important Guidelines:**
1. ALWAYS use tools to get real data - never make up information
2. Use multiple tools if needed for comprehensive answers
3. For people/attendee searches, use the `search_people` tool
4. For advanced/deep research requests:
   - Use `advanced_research_request` tool to check if credentials are configured
   - Inform user this requires CB Insights API access
   - DO NOT proceed with actual research without explicit user confirmation
5. Be conversational and helpful

**Tool Usage:**
- `search_startups_by_name`: Find startups by name
- `search_startups_by_industry`: Find startups by sector
- `get_startup_details`: Get comprehensive info about a startup
- `search_people`: Find attendees/people by name
- `advanced_research_request`: Request advanced market research (requires confirmation)

Remember: You're helping attendees make valuable connections at Slush 2025! 🚀"""
    
    @traceable(name="qwen_function_calling_iteration", tags=["agent", "function-calling"])
    async def _process_iteration(self, messages: List[Dict], iteration: int) -> tuple[str, List[Dict], bool]:
        """Process one iteration with function calling"""
        
        # Call LLM with tools
        response = await llm_completion(
            messages=messages,
            model=self.model,
            use_nvidia_nim=True,
            temperature=0.7,
            max_tokens=2000,
            tools=self.tool_definitions,
            tool_choice="auto",  # Let model decide
            metadata={"iteration": iteration}
        )
        
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        # Check if model wants to call tools
        if finish_reason == "tool_calls" and hasattr(message, 'tool_calls') and message.tool_calls:
            # Model wants to use tools
            logger.info(f"Iteration {iteration}: Model requested {len(message.tool_calls)} tool call(s)")
            
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    parameters = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    parameters = {}
                
                logger.info(f"Executing tool: {tool_name} with {parameters}")
                result = await self.tools.execute_tool(tool_name, parameters)
                logger.info(f"Tool result: {result[:200]}...")
                
                # Add tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result
                })
            
            # Continue to next iteration
            return "", messages, False
        
        else:
            # Model provided final answer
            final_answer = message.content or "No response generated."
            logger.info(f"Iteration {iteration}: Model provided final answer")
            return final_answer, messages, True
    
    @traceable(
        name="qwen_answer_question",
        run_type="chain",
        tags=["agent", "qwen", "function-calling"],
        metadata={"pattern": "function_calling", "model": "qwen"}
    )
    async def answer_question(self, question: str) -> str:
        """Answer a question using Qwen function calling"""
        system_prompt = self._build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        for iteration in range(self.max_iterations):
            logger.info(f"Function calling iteration {iteration + 1}/{self.max_iterations}")
            
            try:
                final_answer, messages, is_complete = await self._process_iteration(messages, iteration)
                
                if is_complete:
                    return final_answer
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                return f"I encountered an error while processing your question: {str(e)}"
        
        # Max iterations reached
        return "I apologize, but I'm having trouble formulating a complete answer. Please try rephrasing your question."


# ====================
# Main Enhanced Concierge
# ====================

class EnhancedQwenConcierge:
    """Enhanced concierge with proper Qwen function calling and ChatCBI integration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = QwenFunctionCallingAgent(db)
    
    @traceable(
        name="enhanced_concierge_answer",
        run_type="chain",
        tags=["concierge", "main-entry"],
        metadata={"service": "startup-swiper", "agent_type": "qwen-enhanced"}
    )
    async def answer_question(self, question: str) -> str:
        """Answer a question"""
        return await self.agent.answer_question(question)
    
    @traceable(name="advanced_research_chatcbi", tags=["chatcbi", "external-api"])
    async def perform_advanced_research(self, company_name: str, focus: str = '') -> str:
        """
        Perform actual advanced research using ChatCBI API
        This should only be called after user confirmation
        """
        # Check credentials
        creds = cb_chat.check_credentials()
        if not creds['configured']:
            return (
                "⚠️ **CB Insights API Not Configured**\n\n"
                f"Status: {creds['message']}\n\n"
                "Please configure credentials in `app/startup-swipe-schedu/.env`"
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
                model=self.agent.model,
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
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool["function"]["name"] for tool in self.agent.tool_definitions]


# ====================
# Factory Function
# ====================

def create_enhanced_qwen_concierge(db: Session = None) -> EnhancedQwenConcierge:
    """Factory function to create concierge instance"""
    if db is None:
        db = SessionLocal()
    
    return EnhancedQwenConcierge(db)


# ====================
# CLI Testing
# ====================

if __name__ == "__main__":
    import asyncio
    
    async def test():
        db = SessionLocal()
        concierge = create_enhanced_qwen_concierge(db)
        
        print("🤖 Enhanced Qwen Concierge Test\n")
        print("=" * 60)
        
        test_questions = [
            "Tell me about SimplifAI startup",
            "Find Eduardo Paz",
            "Perform advanced research on SimplifAI"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            print("-" * 60)
            answer = await concierge.answer_question(question)
            print(f"✅ Answer:\n{answer}\n")
            print("=" * 60)
    
    asyncio.run(test())
