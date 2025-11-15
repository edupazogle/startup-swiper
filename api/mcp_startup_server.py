"""
MCP (Model Context Protocol) Server for Startup Information Extraction

This server provides tools to extract startup information from the database,
allowing Claude and other LLMs to query startup data when needed.

To run this server:
    python mcp_startup_server.py

The server will listen on stdio and provide startup search/lookup tools.
"""

import json
import logging
from typing import Any, Optional, List, Dict
from pathlib import Path
import sys
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
import mcp.types as types

# SQLAlchemy imports
from sqlalchemy.orm import Session
from database import SessionLocal
from models_startup import Startup


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StartupDatabaseServer:
    """MCP Server for querying startup database"""
    
    def __init__(self):
        self.server = Server("startup-db-server")
        self._setup_tools()
        self._db_session: Optional[Session] = None
    
    @asynccontextmanager
    async def get_db(self):
        """Get a database session context"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def _setup_tools(self):
        """Register all available tools with the MCP server"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="search_startups_by_name",
                    description="Search startups by company name. Returns matching startups with basic info.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Company name or partial name to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_startups_by_industry",
                    description="Search startups by industry/sector. Returns startups in specified industry.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "Industry name (e.g., AI, Fintech, Biotech, SaaS)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["industry"]
                    }
                ),
                Tool(
                    name="get_startup_details",
                    description="Get detailed information about a specific startup by ID or name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "startup_id": {
                                "type": "integer",
                                "description": "Startup database ID"
                            },
                            "company_name": {
                                "type": "string",
                                "description": "Company name (use this if ID not available)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="search_startups_by_funding",
                    description="Search startups by funding stage (e.g., Seed, Series A, Series B).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "stage": {
                                "type": "string",
                                "description": "Funding stage (Seed, Series A, Series B, Series C, etc.)"
                            },
                            "min_funding": {
                                "type": "number",
                                "description": "Minimum total funding in millions (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["stage"]
                    }
                ),
                Tool(
                    name="search_startups_by_location",
                    description="Search startups by country or city.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Country name (e.g., Finland, Sweden, USA)"
                            },
                            "city": {
                                "type": "string",
                                "description": "City name (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["country"]
                    }
                ),
                Tool(
                    name="get_startup_enrichment_data",
                    description="Get enriched data for a startup (team, tech stack, social media, etc.)",
                    inputSchema={
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
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_top_startups_by_funding",
                    description="Get top startups ranked by total funding amount.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of top startups to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="search_attendees_by_name",
                    description="Search attendees by name. Returns matching attendees with their details.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Attendee name or partial name to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="search_attendees_by_company",
                    description="Search attendees by company name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "Company name to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["company_name"]
                    }
                ),
                Tool(
                    name="search_attendees_by_country",
                    description="Search attendees by country.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Country name or code (e.g., Finland, FI, USA)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 20)",
                                "default": 20
                            }
                        },
                        "required": ["country"]
                    }
                ),
                Tool(
                    name="search_attendees_by_occupation",
                    description="Search attendees by occupation (e.g., CEO, Investor, Developer).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "occupation": {
                                "type": "string",
                                "description": "Occupation type (e.g., CEO, founder, investor, developer)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["occupation"]
                    }
                ),
                Tool(
                    name="get_attendee_details",
                    description="Get detailed information about a specific attendee.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "attendee_id": {
                                "type": "string",
                                "description": "Attendee unique ID"
                            },
                            "name": {
                                "type": "string",
                                "description": "Attendee name (use if ID not available)"
                            }
                        },
                        "required": []
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            try:
                if name == "search_startups_by_name":
                    return await self._search_by_name(arguments)
                elif name == "search_startups_by_industry":
                    return await self._search_by_industry(arguments)
                elif name == "get_startup_details":
                    return await self._get_startup_details(arguments)
                elif name == "search_startups_by_funding":
                    return await self._search_by_funding(arguments)
                elif name == "search_startups_by_location":
                    return await self._search_by_location(arguments)
                elif name == "get_startup_enrichment_data":
                    return await self._get_enrichment_data(arguments)
                elif name == "get_top_startups_by_funding":
                    return await self._get_top_by_funding(arguments)
                elif name == "search_attendees_by_name":
                    return await self._search_attendees_by_name(arguments)
                elif name == "search_attendees_by_company":
                    return await self._search_attendees_by_company(arguments)
                elif name == "search_attendees_by_country":
                    return await self._search_attendees_by_country(arguments)
                elif name == "search_attendees_by_occupation":
                    return await self._search_attendees_by_occupation(arguments)
                elif name == "get_attendee_details":
                    return await self._get_attendee_details(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _search_by_name(self, arguments: dict) -> list[TextContent]:
        """Search startups by name"""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            startups = db.query(Startup)\
                .filter(Startup.company_name.ilike(f"%{query}%"))\
                .limit(limit)\
                .all()
            
            if not startups:
                return [TextContent(type="text", text=f"No startups found matching '{query}'")]
            
            result = self._format_startup_list(startups)
            return [TextContent(type="text", text=result)]
    
    async def _search_by_industry(self, arguments: dict) -> list[TextContent]:
        """Search startups by industry"""
        industry = arguments.get("industry", "")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            startups = db.query(Startup)\
                .filter(
                    (Startup.primary_industry.ilike(f"%{industry}%")) |
                    (Startup.focus_industries.op('like')(f'%{industry}%'))
                )\
                .limit(limit)\
                .all()
            
            if not startups:
                return [TextContent(type="text", text=f"No startups found in industry '{industry}'")]
            
            result = self._format_startup_list(startups)
            return [TextContent(type="text", text=result)]
    
    async def _get_startup_details(self, arguments: dict) -> list[TextContent]:
        """Get detailed startup information"""
        startup_id = arguments.get("startup_id")
        company_name = arguments.get("company_name")
        
        async with self.get_db() as db:
            startup = None
            if startup_id:
                startup = db.query(Startup).filter(Startup.id == startup_id).first()
            elif company_name:
                startup = db.query(Startup).filter(Startup.company_name.ilike(company_name)).first()
            
            if not startup:
                return [TextContent(type="text", text="Startup not found")]
            
            result = self._format_startup_details(startup)
            return [TextContent(type="text", text=result)]
    
    async def _search_by_funding(self, arguments: dict) -> list[TextContent]:
        """Search startups by funding stage"""
        stage = arguments.get("stage", "")
        min_funding = arguments.get("min_funding")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            query = db.query(Startup).filter(
                Startup.currentInvestmentStage.ilike(f"%{stage}%")
            )
            
            if min_funding is not None:
                query = query.filter(Startup.totalFunding >= min_funding)
            
            startups = query.order_by(Startup.totalFunding.desc()).limit(limit).all()
            
            if not startups:
                return [TextContent(type="text", text=f"No startups found at stage '{stage}'")]
            
            result = self._format_startup_list(startups)
            return [TextContent(type="text", text=result)]
    
    async def _search_by_location(self, arguments: dict) -> list[TextContent]:
        """Search startups by location"""
        country = arguments.get("country", "")
        city = arguments.get("city")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            query = db.query(Startup).filter(
                Startup.company_country.ilike(f"%{country}%")
            )
            
            if city:
                query = query.filter(Startup.company_city.ilike(f"%{city}%"))
            
            startups = query.limit(limit).all()
            
            if not startups:
                location = f"{city}, {country}" if city else country
                return [TextContent(type="text", text=f"No startups found in {location}")]
            
            result = self._format_startup_list(startups)
            return [TextContent(type="text", text=result)]
    
    async def _get_enrichment_data(self, arguments: dict) -> list[TextContent]:
        """Get enriched startup data"""
        startup_id = arguments.get("startup_id")
        company_name = arguments.get("company_name")
        
        async with self.get_db() as db:
            startup = None
            if startup_id:
                startup = db.query(Startup).filter(Startup.id == startup_id).first()
            elif company_name:
                startup = db.query(Startup).filter(Startup.company_name.ilike(company_name)).first()
            
            if not startup or not startup.enrichment:
                return [TextContent(type="text", text="Enrichment data not found")]
            
            result = self._format_enrichment_data(startup)
            return [TextContent(type="text", text=result)]
    
    async def _get_top_by_funding(self, arguments: dict) -> list[TextContent]:
        """Get top startups by funding"""
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            startups = db.query(Startup)\
                .filter(Startup.totalFunding.isnot(None))\
                .order_by(Startup.totalFunding.desc())\
                .limit(limit)\
                .all()
            
            if not startups:
                return [TextContent(type="text", text="No funding data available")]
            
            result = self._format_startup_list(startups)
            return [TextContent(type="text", text=result)]
    
    async def _search_attendees_by_name(self, arguments: dict) -> list[TextContent]:
        """Search attendees by name"""
        from db_queries import search_attendees_by_name
        
        name = arguments.get("name", "")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            attendees = search_attendees_by_name(db, name, limit)
            
            if not attendees:
                return [TextContent(type="text", text=f"No attendees found matching '{name}'")]
            
            result = self._format_attendee_list(attendees)
            return [TextContent(type="text", text=result)]
    
    async def _search_attendees_by_company(self, arguments: dict) -> list[TextContent]:
        """Search attendees by company"""
        from db_queries import search_attendees_by_company
        
        company_name = arguments.get("company_name", "")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            attendees = search_attendees_by_company(db, company_name, limit)
            
            if not attendees:
                return [TextContent(type="text", text=f"No attendees found from company '{company_name}'")]
            
            result = self._format_attendee_list(attendees)
            return [TextContent(type="text", text=result)]
    
    async def _search_attendees_by_country(self, arguments: dict) -> list[TextContent]:
        """Search attendees by country"""
        from db_queries import search_attendees_by_country
        
        country = arguments.get("country", "")
        limit = arguments.get("limit", 20)
        
        async with self.get_db() as db:
            attendees = search_attendees_by_country(db, country, limit)
            
            if not attendees:
                return [TextContent(type="text", text=f"No attendees found from country '{country}'")]
            
            result = self._format_attendee_list(attendees)
            return [TextContent(type="text", text=result)]
    
    async def _search_attendees_by_occupation(self, arguments: dict) -> list[TextContent]:
        """Search attendees by occupation"""
        from db_queries import search_attendees_by_occupation
        
        occupation = arguments.get("occupation", "")
        limit = arguments.get("limit", 10)
        
        async with self.get_db() as db:
            attendees = search_attendees_by_occupation(db, occupation, limit)
            
            if not attendees:
                return [TextContent(type="text", text=f"No attendees found with occupation '{occupation}'")]
            
            result = self._format_attendee_list(attendees)
            return [TextContent(type="text", text=result)]
    
    async def _get_attendee_details(self, arguments: dict) -> list[TextContent]:
        """Get attendee details"""
        from db_queries import get_attendee_by_id, search_attendees_by_name
        
        attendee_id = arguments.get("attendee_id")
        name = arguments.get("name")
        
        async with self.get_db() as db:
            attendee = None
            
            if attendee_id:
                attendee = get_attendee_by_id(db, attendee_id)
            elif name:
                results = search_attendees_by_name(db, name, 1)
                attendee = results[0] if results else None
            
            if not attendee:
                return [TextContent(type="text", text="Attendee not found")]
            
            result = self._format_attendee_details(attendee)
            return [TextContent(type="text", text=result)]
    
    def _format_attendee_list(self, attendees: List[Dict]) -> str:
        """Format attendee list for display"""
        lines = []
        for attendee in attendees:
            name = attendee.get("name", "Unknown")
            title = attendee.get("title", "")
            company = attendee.get("company_name", "")
            country = attendee.get("country", "")
            
            title_str = f" - {title}" if title else ""
            company_str = f" @ {company}" if company else ""
            country_str = f" ({country})" if country else ""
            
            lines.append(f"• {name}{title_str}{company_str}{country_str}")
        
        return "\n".join(lines)
    
    def _format_attendee_details(self, attendee: Dict) -> str:
        """Format attendee details for display"""
        lines = []
        
        lines.append(f"**{attendee.get('name', 'Unknown')}**")
        
        if attendee.get("title"):
            lines.append(f"Title: {attendee['title']}")
        
        if attendee.get("bio"):
            lines.append(f"Bio: {attendee['bio']}")
        
        if attendee.get("company_name"):
            lines.append(f"Company: {attendee['company_name']} ({attendee.get('company_type', 'N/A')})")
        
        if attendee.get("country") or attendee.get("city"):
            location = f"{attendee.get('city', '')}, {attendee.get('country', '')}".strip(", ")
            lines.append(f"Location: {location}")
        
        if attendee.get("industry"):
            industries = attendee.get("industry")
            if isinstance(industries, list):
                lines.append(f"Industries: {', '.join(industries)}")
        
        if attendee.get("occupation"):
            occupations = attendee.get("occupation")
            if isinstance(occupations, list):
                lines.append(f"Occupations: {', '.join(occupations)}")
        
        if attendee.get("linkedin"):
            lines.append(f"LinkedIn: {attendee['linkedin']}")
        
        if attendee.get("profile_link"):
            lines.append(f"Profile: {attendee['profile_link']}")
        
        return "\n".join(lines)
    
    def _format_startup_list(self, startups: List[Startup]) -> str:
        """Format startup list for display"""
        lines = []
        for startup in startups:
            lines.append(f"• {startup.company_name}")
            if startup.shortDescription:
                lines.append(f"  {startup.shortDescription[:100]}...")
            if startup.primaryIndustry:
                lines.append(f"  Industry: {startup.primary_industry}")
            if startup.totalFunding:
                lines.append(f"  Funding: ${startup.totalFunding}M")
            if startup.currentInvestmentStage:
                lines.append(f"  Stage: {startup.currentInvestmentStage}")
            lines.append("")
        
        return "\n".join(lines) if lines else "No startups found"
    
    def _format_startup_details(self, startup: Startup) -> str:
        """Format detailed startup information"""
        lines = [f"**{startup.company_name}**"]
        
        if startup.company_description:
            lines.append(f"\nDescription: {startup.company_description}")
        
        if startup.website:
            lines.append(f"Website: {startup.website}")
        
        if startup.founding_year:
            lines.append(f"Founded: {startup.founding_year}")
        
        if startup.company_country:
            location = f"{startup.company_city}, {startup.company_country}" if startup.company_city else startup.company_country
            lines.append(f"Location: {location}")
        
        if startup.primary_industry:
            lines.append(f"Primary Industry: {startup.primary_industry}")
        
        if startup.totalFunding:
            lines.append(f"Total Funding: ${startup.totalFunding}M")
        
        if startup.currentInvestmentStage:
            lines.append(f"Current Stage: {startup.currentInvestmentStage}")
        
        if startup.employees:
            lines.append(f"Employees: {startup.employees}")
        
        if startup.company_linked_in:
            lines.append(f"LinkedIn: {startup.company_linked_in}")
        
        return "\n".join(lines)
    
    def _format_enrichment_data(self, startup: Startup) -> str:
        """Format enrichment data"""
        lines = [f"**{startup.company_name} - Enrichment Data**"]
        
        enrichment = startup.enrichment
        if not enrichment:
            return "No enrichment data available"
        
        if isinstance(enrichment, str):
            try:
                enrichment = json.loads(enrichment)
            except:
                return f"Enrichment data: {enrichment}"
        
        lines.append(f"\nEnrichment Date: {enrichment.get('enrichment_date', 'N/A')}")
        
        # Team members
        team = enrichment.get('team_members', [])
        if team:
            lines.append(f"\nTeam ({len(team)} members):")
            for member in team[:5]:  # Limit to 5
                lines.append(f"  - {member.get('name', 'N/A')} ({member.get('role', 'N/A')})")
        
        # Tech stack
        tech = enrichment.get('tech_stack', [])
        if tech:
            lines.append(f"\nTech Stack: {', '.join(tech[:10])}")
        
        # Social media
        social = enrichment.get('social_media', {})
        if social:
            lines.append("\nSocial Media:")
            for platform, url in social.items():
                if url:
                    lines.append(f"  {platform}: {url}")
        
        # Emails
        emails = enrichment.get('emails', [])
        if emails:
            lines.append(f"\nEmails: {', '.join(emails[:3])}")
        
        return "\n".join(lines)
    
    async def run(self):
        """Start the MCP server"""
        logger.info("Starting Startup Database MCP Server...")
        async with self.server:
            logger.info("Server running. Waiting for requests...")
            # Server will run indefinitely, handling incoming requests
            await self.server.wait()


async def main():
    """Main entry point"""
    server = StartupDatabaseServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
