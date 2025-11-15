"""
MCP (Model Context Protocol) Client Integration for AI Concierge

This module provides tools for the AI Concierge to interact with MCP servers,
particularly for extracting startup information from the database when needed.

The MCP client allows the LLM to use tool calls that query the database,
making the AI concierge more intelligent and context-aware.
"""

import json
import subprocess
import os
import sys
from typing import Any, Optional, Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self, server_type: str = "startup_db", config: Optional[Dict[str, Any]] = None):
        """
        Initialize MCP Client
        
        Args:
            server_type: Type of server ("startup_db", "web", etc.)
            config: Configuration dictionary for the server
        """
        self.server_type = server_type
        self.config = config or {}
        self.process = None
        self._startup_tool_cache = {}
    
    def start_server(self) -> bool:
        """Start the MCP server process"""
        try:
            api_dir = Path(__file__).parent
            
            if self.server_type == "startup_db":
                script = api_dir / "mcp_startup_server.py"
                
                if not script.exists():
                    logger.error(f"MCP server script not found: {script}")
                    return False
                
                # Start the server process
                self.process = subprocess.Popen(
                    [sys.executable, str(script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(api_dir),
                    env={**os.environ, "PYTHONPATH": str(api_dir)}
                )
                
                logger.info(f"Started MCP {self.server_type} server (PID: {self.process.pid})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("MCP server stopped")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
                if self.process.poll() is None:
                    self.process.kill()


class StartupDatabaseMCPTools:
    """
    Tools for querying startup information via MCP
    
    These tools can be used by the LLM to extract startup data
    when needed for context in conversations.
    """
    
    def __init__(self):
        self.mcp_client = MCPClient("startup_db")
        self.tools_definition = self._get_tools_definition()
    
    def _get_tools_definition(self) -> List[Dict[str, Any]]:
        """Get the list of available tools for LLM function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_startups_by_name",
                    "description": "Search for startups by company name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Company name or partial name to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
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
                    "description": "Search for startups in a specific industry or sector",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Industry name (AI, Fintech, Biotech, SaaS, etc.)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
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
                    "description": "Get detailed information about a specific startup",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "startup_id": {
                                "type": "integer",
                                "description": "Startup database ID"
                            },
                            "company_name": {
                                "type": "string",
                                "description": "Company name (use if ID not available)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_startups_by_funding",
                    "description": "Search for startups by funding stage or amount",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stage": {
                                "type": "string",
                                "description": "Funding stage (Seed, Series A, Series B, Series C, etc.)"
                            },
                            "min_funding": {
                                "type": "number",
                                "description": "Minimum total funding in millions"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["stage"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_startups_by_location",
                    "description": "Search for startups by country or city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Country name"
                            },
                            "city": {
                                "type": "string",
                                "description": "City name (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["country"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_startup_enrichment_data",
                    "description": "Get enriched data for a startup (team, tech stack, social media)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "startup_id": {
                                "type": "integer",
                                "description": "Startup database ID"
                            },
                            "company_name": {
                                "type": "string",
                                "description": "Company name (use if ID not available)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_startups_by_funding",
                    "description": "Get the top funded startups",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of top startups to return",
                                "default": 10
                            }
                        }
                    }
                }
            }
        ]
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Get tools formatted for LLM function calling (Claude, GPT, etc.)
        
        Returns:
            List of tool definitions
        """
        return self.tools_definition
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a startup database tool
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments for the tool
        
        Returns:
            Result dictionary with tool output
        """
        try:
            # For now, we'll mock the tool calls since MCP integration is async
            # In production, these would call the actual MCP server
            
            if tool_name == "search_startups_by_name":
                return await self._search_startups_by_name(**kwargs)
            elif tool_name == "search_startups_by_industry":
                return await self._search_startups_by_industry(**kwargs)
            elif tool_name == "get_startup_details":
                return await self._get_startup_details(**kwargs)
            elif tool_name == "search_startups_by_funding":
                return await self._search_startups_by_funding(**kwargs)
            elif tool_name == "search_startups_by_location":
                return await self._search_startups_by_location(**kwargs)
            elif tool_name == "get_startup_enrichment_data":
                return await self._get_startup_enrichment_data(**kwargs)
            elif tool_name == "get_top_startups_by_funding":
                return await self._get_top_startups_by_funding(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Direct database access methods (bypassing MCP for now)
    async def _search_startups_by_name(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search startups by name"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            startups = db.query(Startup)\
                .filter(Startup.company_name.ilike(f"%{query}%"))\
                .limit(limit)\
                .all()
            
            results = [
                {
                    "id": s.id,
                    "name": s.company_name,
                    "description": s.shortDescription,
                    "industry": s.primary_industry,
                    "funding": s.totalFunding,
                    "stage": s.currentInvestmentStage,
                    "website": s.website
                }
                for s in startups
            ]
            
            db.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error searching startups: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_startups_by_industry(self, industry: str, limit: int = 10) -> Dict[str, Any]:
        """Search startups by industry"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            startups = db.query(Startup)\
                .filter(Startup.primary_industry.ilike(f"%{industry}%"))\
                .limit(limit)\
                .all()
            
            results = [
                {
                    "id": s.id,
                    "name": s.company_name,
                    "description": s.shortDescription,
                    "industry": s.primary_industry,
                    "funding": s.totalFunding,
                    "stage": s.currentInvestmentStage,
                    "website": s.website
                }
                for s in startups
            ]
            
            db.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error searching by industry: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_startup_details(self, startup_id: Optional[int] = None, 
                                   company_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed startup information"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            startup = None
            
            if startup_id:
                startup = db.query(Startup).filter(Startup.id == startup_id).first()
            elif company_name:
                startup = db.query(Startup).filter(Startup.company_name.ilike(company_name)).first()
            
            db.close()
            
            if not startup:
                return {
                    "success": False,
                    "error": "Startup not found"
                }
            
            return {
                "success": True,
                "startup": {
                    "id": startup.id,
                    "name": startup.company_name,
                    "description": startup.company_description,
                    "shortDescription": startup.shortDescription,
                    "website": startup.website,
                    "founded": startup.founding_year,
                    "location": f"{startup.company_city}, {startup.company_country}",
                    "industry": startup.primary_industry,
                    "totalFunding": startup.totalFunding,
                    "stage": startup.currentInvestmentStage,
                    "employees": startup.employees,
                    "linkedIn": startup.company_linked_in,
                    "logo": startup.logoUrl
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting startup details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_startups_by_funding(self, stage: str, min_funding: Optional[float] = None,
                                          limit: int = 10) -> Dict[str, Any]:
        """Search startups by funding stage"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            query = db.query(Startup).filter(Startup.currentInvestmentStage.ilike(f"%{stage}%"))
            
            if min_funding is not None:
                query = query.filter(Startup.totalFunding >= min_funding)
            
            startups = query.order_by(Startup.totalFunding.desc()).limit(limit).all()
            
            results = [
                {
                    "id": s.id,
                    "name": s.company_name,
                    "funding": s.totalFunding,
                    "stage": s.currentInvestmentStage,
                    "industry": s.primary_industry,
                    "description": s.shortDescription
                }
                for s in startups
            ]
            
            db.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error searching by funding: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_startups_by_location(self, country: str, city: Optional[str] = None,
                                           limit: int = 10) -> Dict[str, Any]:
        """Search startups by location"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            query = db.query(Startup).filter(Startup.company_country.ilike(f"%{country}%"))
            
            if city:
                query = query.filter(Startup.company_city.ilike(f"%{city}%"))
            
            startups = query.limit(limit).all()
            
            results = [
                {
                    "id": s.id,
                    "name": s.company_name,
                    "location": f"{s.company_city}, {s.company_country}",
                    "industry": s.primary_industry,
                    "funding": s.totalFunding,
                    "website": s.website
                }
                for s in startups
            ]
            
            db.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error searching by location: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_startup_enrichment_data(self, startup_id: Optional[int] = None,
                                           company_name: Optional[str] = None) -> Dict[str, Any]:
        """Get enriched startup data"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            startup = None
            
            if startup_id:
                startup = db.query(Startup).filter(Startup.id == startup_id).first()
            elif company_name:
                startup = db.query(Startup).filter(Startup.company_name.ilike(company_name)).first()
            
            db.close()
            
            if not startup or not startup.enrichment:
                return {
                    "success": False,
                    "error": "Enrichment data not found"
                }
            
            enrichment = startup.enrichment
            if isinstance(enrichment, str):
                enrichment = json.loads(enrichment)
            
            return {
                "success": True,
                "startup_name": startup.company_name,
                "enrichment_date": enrichment.get("enrichment_date"),
                "team": enrichment.get("team_members", [])[:5],
                "tech_stack": enrichment.get("tech_stack", [])[:10],
                "social_media": enrichment.get("social_media", {}),
                "emails": enrichment.get("emails", [])[:3]
            }
        
        except Exception as e:
            logger.error(f"Error getting enrichment data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_top_startups_by_funding(self, limit: int = 10) -> Dict[str, Any]:
        """Get top startups by funding"""
        from database import SessionLocal
        from models_startup import Startup
        
        try:
            db = SessionLocal()
            startups = db.query(Startup)\
                .filter(Startup.totalFunding.isnot(None))\
                .order_by(Startup.totalFunding.desc())\
                .limit(limit)\
                .all()
            
            results = [
                {
                    "id": s.id,
                    "name": s.company_name,
                    "funding": s.totalFunding,
                    "stage": s.currentInvestmentStage,
                    "industry": s.primary_industry,
                    "website": s.website
                }
                for s in startups
            ]
            
            db.close()
            
            return {
                "success": True,
                "count": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error getting top startups: {e}")
            return {
                "success": False,
                "error": str(e)
            }
