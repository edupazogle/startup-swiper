"""
CB Insights API Integration

This module provides integration with CB Insights API for startup data retrieval.
"""

import os
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

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
    """CB Insights Chat API for advanced research"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CB_INSIGHTS_API_KEY")
        self.base_url = "https://api.cbinsights.com/v1/chat"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
    
    async def ask_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Ask CB Insights Chat a research question
        
        Args:
            question: Research question
            context: Optional context (company IDs, industries, etc.)
            
        Returns:
            Research answer from CB Chat
        """
        if not self.api_key:
            return "CB Insights API key not configured. Unable to perform advanced research."
        
        url = self.base_url
        payload = {
            "question": question,
            "context": context or {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("answer", "No answer available")
                    else:
                        return f"CB Chat API error: {response.status}"
        except Exception as e:
            return f"Error communicating with CB Chat: {str(e)}"
    
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
