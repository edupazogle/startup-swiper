"""
CB Insights API Integration

This module provides integration with CB Insights API for startup data retrieval.
Updated with ChatCBI v2 and Qwen LLM query optimization.
"""

import os
import aiohttp
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Configure logging
logger = logging.getLogger(__name__)

class CBInsightsAPI:
    """CB Insights API client for fetching startup information"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CB_INSIGHTS_API_KEY")
        self.base_url = "https://api.cbinsights.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
    
    async def search_company(self, query: str) -> Dict[str, Any]:
        """
        Search for companies in CB Insights
        
        Args:
            query: Company name or search term
            
        Returns:
            Company data from CB Insights
        """
        if not self.api_key:
            return {"error": "CB Insights API key not configured", "results": []}
        
        url = f"{self.base_url}/companies/search"
        params = {"query": query, "limit": 5}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API error: {response.status}", "results": []}
        except Exception as e:
            return {"error": str(e), "results": []}
    
    async def get_company_details(self, company_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific company
        
        Args:
            company_id: CB Insights company ID
            
        Returns:
            Detailed company data
        """
        if not self.api_key:
            return {"error": "CB Insights API key not configured"}
        
        url = f"{self.base_url}/companies/{company_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_company_news(self, company_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent news about a company
        
        Args:
            company_id: CB Insights company ID
            limit: Number of news items to fetch
            
        Returns:
            List of news articles
        """
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/companies/{company_id}/news"
        params = {"limit": limit}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("news", [])
                    else:
                        return []
        except Exception as e:
            return []
    
    async def get_company_funding(self, company_id: str) -> Dict[str, Any]:
        """
        Get funding information for a company
        
        Args:
            company_id: CB Insights company ID
            
        Returns:
            Funding data
        """
        if not self.api_key:
            return {"error": "CB Insights API key not configured"}
        
        url = f"{self.base_url}/companies/{company_id}/funding"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"API error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}


class CBChat:
    """CB Insights Chat API for advanced research using ChatCBI v2"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        # Load from .env - try both naming conventions
        self.client_id = (
            client_id or 
            os.getenv("CBINSIGHTS_CLIENT_ID") or 
            os.getenv("CB_INSIGHTS_CLIENT_ID")
        )
        self.client_secret = (
            client_secret or 
            os.getenv("CBINSIGHTS_CLIENT_SECRET") or 
            os.getenv("CB_INSIGHTS_CLIENT_SECRET")
        )
        self.base_url = "https://api.cbinsights.com"
        self.access_token = None
        self.chat_id = None
    
    def check_credentials(self) -> Dict[str, Any]:
        """
        Check if CB Insights API credentials are configured
        
        Returns:
            Dict with status and message
        """
        if not self.client_id or not self.client_secret:
            return {
                "configured": False,
                "message": "CB Insights API credentials not found. Please configure CBINSIGHTS_CLIENT_ID and CBINSIGHTS_CLIENT_SECRET in app/startup-swipe-schedu/.env"
            }
        return {
            "configured": True,
            "message": "CB Insights API credentials are configured",
            "client_id": self.client_id[:10] + "..." if self.client_id else None
        }
    
    async def authorize(self) -> bool:
        """
        Authorize with CB Insights API v2 to get access token
        
        Returns:
            True if authorization successful
        """
        if not self.client_id or not self.client_secret:
            return False
        
        url = f"{self.base_url}/v2/authorize"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data.get("accessToken")
                        logger.info("✅ Successfully authorized with CB Insights API")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"CB Insights authorization failed ({response.status}): {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Error authorizing with CB Insights: {e}")
            return False
    
    async def optimize_query_with_llm(self, user_query: str, company_name: Optional[str] = None) -> str:
        """
        Optimize the user's query using Qwen LLM before sending to ChatCBI
        
        This ensures the query is well-structured and gets the best results from ChatCBI.
        
        Args:
            user_query: Original user query
            company_name: Optional company name for focused research
            
        Returns:
            Optimized query for ChatCBI
        """
        from llm_config import llm_completion
        
        system_prompt = """You are a query optimization expert for CB Insights ChatCBI.

Your task: Transform user questions into optimal ChatCBI queries that will get comprehensive, actionable market intelligence.

Guidelines for optimal ChatCBI queries:
1. Be specific and focused
2. Include relevant context (industry, geography, time period)
3. Ask for actionable insights (market trends, competitive analysis, funding patterns)
4. Request specific data points (funding rounds, key players, growth metrics)
5. Keep queries clear and concise (1-3 sentences)

Examples:

User: "Tell me about SimplifAI"
Optimized: "Provide a comprehensive analysis of SimplifAI including: business model, competitive landscape, funding history, technology stack, market positioning, and growth trajectory."

User: "AI startups"
Optimized: "What are the top AI startups in terms of funding and innovation? Include their business models, key differentiators, recent funding rounds, and market opportunities."

User: "Research this company for investment"
Optimized: "Analyze [company] for investment potential: funding history, valuation trends, competitive advantages, market size, growth metrics, key risks, and investment thesis."

Now optimize this query:"""

        user_prompt = f"User Query: {user_query}"
        if company_name:
            user_prompt += f"\nCompany Focus: {company_name}"
        
        user_prompt += "\n\nOptimized ChatCBI Query:"
        
        try:
            response = await llm_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=os.getenv('NVIDIA_DEFAULT_MODEL', 'qwen/qwen3-next-80b-a3b-instruct'),
                use_nvidia_nim=True,
                temperature=0.3,  # Lower temperature for focused optimization
                max_tokens=200
            )
            
            optimized = response.choices[0].message.content.strip()
            logger.info(f"Query optimized:\n  Original: {user_query}\n  Optimized: {optimized}")
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing query with LLM: {e}")
            # Fallback to original query
            return user_query
    
    async def ask_question(self, question: str, company_name: Optional[str] = None, 
                          optimize_query: bool = True) -> str:
        """
        Ask CB Insights ChatCBI a research question using v2 API
        
        Args:
            question: Research question
            company_name: Optional company name for focused research
            optimize_query: Whether to optimize the query with LLM (default: True)
            
        Returns:
            Research answer from ChatCBI
        """
        creds = self.check_credentials()
        if not creds["configured"]:
            return creds["message"]
        
        # Authorize if we don't have a token
        if not self.access_token:
            authorized = await self.authorize()
            if not authorized:
                return "Failed to authorize with CB Insights API. Please check your credentials in app/startup-swipe-schedu/.env"
        
        # Optimize the query with Qwen LLM
        if optimize_query:
            optimized_message = await self.optimize_query_with_llm(question, company_name)
        else:
            optimized_message = question
        
        url = f"{self.base_url}/v2/chatcbi"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": optimized_message
        }
        
        # Include chatID for multi-turn conversations
        if self.chat_id:
            payload["chatID"] = self.chat_id
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Store chat ID for future turns
                        self.chat_id = data.get("chatID")
                        
                        # Extract message and sources
                        message = data.get("message", "No answer available")
                        sources = data.get("sources", [])
                        suggestions = data.get("suggestions", [])
                        
                        # Format response with sources
                        formatted_response = f"**Query sent to ChatCBI:** {optimized_message}\n\n---\n\n{message}"
                        
                        if sources:
                            formatted_response += "\n\n**Sources:**\n"
                            for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
                                title = source.get("title", "Unknown")
                                url = source.get("url", "")
                                if url:
                                    formatted_response += f"{i}. [{title}]({url})\n"
                                else:
                                    formatted_response += f"{i}. {title}\n"
                        
                        if suggestions:
                            formatted_response += "\n\n**Follow-up questions:**\n"
                            for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                                formatted_response += f"- {suggestion}\n"
                        
                        return formatted_response
                        
                    elif response.status == 401:
                        # Token expired, re-authorize
                        logger.info("Access token expired, re-authorizing...")
                        self.access_token = None
                        return await self.ask_question(question, company_name, optimize_query=False)  # Don't re-optimize
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"ChatCBI API error ({response.status}): {error_text}")
                        return f"ChatCBI API error ({response.status}): {error_text}"
                        
        except Exception as e:
            logger.error(f"Error communicating with ChatCBI: {e}")
            return f"Error communicating with ChatCBI: {str(e)}"
    
    async def research_company(self, company_name: str, aspect: str) -> str:
        """
        Research a specific aspect of a company using CB Chat
        
        Args:
            company_name: Name of the company
            aspect: What to research (e.g., "competitors", "market position", "technology")
            
        Returns:
            Research findings
        """
        question = f"Tell me about {company_name}'s {aspect}. Provide detailed insights."
        return await self.ask_question(question)
    
    async def compare_companies(self, company1: str, company2: str) -> str:
        """
        Compare two companies using CB Chat
        
        Args:
            company1: First company name
            company2: Second company name
            
        Returns:
            Comparison analysis
        """
        question = f"Compare {company1} and {company2}. What are their key differences and similarities?"
        return await self.ask_question(question)


# Singleton instances
cb_insights_api = CBInsightsAPI()
cb_chat = CBChat()
