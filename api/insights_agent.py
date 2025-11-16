"""
AI Insights Generation Agent

This agent generates AI-powered insights for startups using the Qwen model.
It follows the FEEDBACK_IMPLEMENTATION_GUIDE.md pattern but focuses on
generating comprehensive insights about startups for AXA evaluation.

Features:
- Generates contextual insights about startup-AXA fit
- Uses qwen/qwen3-next-80b-a3b-instruct model
- LangSmith tracing for observability
- Integrates with CB Insights for enriched data
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
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
        print(f"✓ Insights Agent: Loaded environment from: {env_path}")
        break

# LangSmith tracing
from langsmith import traceable

# Local imports
from database import SessionLocal
import db_queries
from llm_config import llm_completion

logger = logging.getLogger(__name__)


class InsightsAgent:
    """Agent for generating AI-powered startup insights"""
    
    def __init__(self, db: Session):
        self.db = db
        self.model = "qwen/qwen3-next-80b-a3b-instruct"
    
    @traceable(name="generate_startup_insights")
    async def generate_insights(self, company_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights for a startup.
        
        Returns structured insights including:
        - Strategic fit with AXA
        - Technology assessment
        - Market opportunity
        - Risk factors
        - Recommended actions
        """
        try:
            # Get startup data from database
            startup = db_queries.get_startup_by_name(self.db, company_name)
            
            if not startup:
                return {
                    "success": False,
                    "error": f"Startup '{company_name}' not found in database"
                }
            
            # Build context for LLM
            context = self._build_startup_context(startup)
            
            # Generate insights using LLM
            insights = await self._generate_llm_insights(company_name, context)
            
            return {
                "success": True,
                "company_name": company_name,
                "insights": insights,
                "timestamp": "auto-generated"
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_startup_context(self, startup: Dict[str, Any]) -> str:
        """Build comprehensive context from startup data"""
        context_parts = [
            f"Company: {startup.get('company_name', 'N/A')}",
            f"Industry: {startup.get('primary_industry', 'N/A')}",
        ]
        
        if startup.get('company_description'):
            context_parts.append(f"Description: {startup['company_description']}")
        
        if startup.get('funding_stage'):
            context_parts.append(f"Funding Stage: {startup['funding_stage']}")
        
        if startup.get('total_funding'):
            context_parts.append(f"Total Funding: ${startup['total_funding']:,.0f}M")
        
        # Topics/tech keywords
        topics = []
        for i in range(1, 11):  # topics_1 through topics_10
            topic = startup.get(f'topics_{i}')
            if topic:
                topics.append(topic)
        
        if topics:
            context_parts.append(f"Technology Focus: {', '.join(topics)}")
        
        if startup.get('company_city') or startup.get('company_country'):
            location = f"{startup.get('company_city', '')}, {startup.get('company_country', '')}".strip(', ')
            context_parts.append(f"Location: {location}")
        
        if startup.get('website'):
            context_parts.append(f"Website: {startup['website']}")
        
        if startup.get('founded_year'):
            context_parts.append(f"Founded: {startup['founded_year']}")
        
        return "\n".join(context_parts)
    
    @traceable(name="llm_insights_generation")
    async def _generate_llm_insights(self, company_name: str, context: str) -> Dict[str, Any]:
        """Generate insights using LLM"""
        
        prompt = f"""You are an AI investment analyst evaluating startups for AXA, a global insurance and asset management company.

Analyze the following startup and provide comprehensive insights:

{context}

Generate a structured analysis covering:

1. **Strategic Fit with AXA** (0-10 score)
   - How well does this startup align with AXA's insurance and financial services business?
   - Potential partnership or acquisition value
   - Synergies with AXA's existing offerings

2. **Technology Assessment** (0-10 score)
   - Innovation level and uniqueness
   - Technology maturity and scalability
   - Technical risks and challenges

3. **Market Opportunity** (0-10 score)
   - Market size and growth potential
   - Competitive positioning
   - Go-to-market strategy

4. **Business Viability** (0-10 score)
   - Financial health and funding runway
   - Revenue model sustainability
   - Team quality and experience

5. **Risk Factors**
   - Key risks to consider
   - Regulatory or compliance concerns
   - Market or technology risks

6. **Recommended Next Steps**
   - Immediate actions (demo, meeting, due diligence)
   - Timeline and priorities
   - Required resources

Provide your analysis in a structured JSON format with clear scores and explanations."""

        try:
            response = await llm_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert startup analyst for AXA. Provide data-driven, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                use_nvidia_nim=True,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Parse response - llm_completion returns ModelResponse object
            insights_text = response.choices[0].message.content
            
            # Try to extract structured insights
            insights = self._parse_insights(insights_text)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error in LLM insights generation: {e}")
            return {
                "error": str(e),
                "raw_text": "Could not generate insights"
            }
    
    def _parse_insights(self, insights_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured insights"""
        # Simple parsing - in production, use more sophisticated extraction
        insights = {
            "strategic_fit": {
                "score": 0,
                "analysis": ""
            },
            "technology": {
                "score": 0,
                "analysis": ""
            },
            "market": {
                "score": 0,
                "analysis": ""
            },
            "viability": {
                "score": 0,
                "analysis": ""
            },
            "risks": [],
            "next_steps": [],
            "full_analysis": insights_text
        }
        
        # Try to extract scores and sections
        import re
        
        # Extract Strategic Fit score
        strategic_match = re.search(r'Strategic Fit.*?(\d+)/10', insights_text, re.IGNORECASE | re.DOTALL)
        if strategic_match:
            insights["strategic_fit"]["score"] = int(strategic_match.group(1))
        
        # Extract Technology score
        tech_match = re.search(r'Technology.*?(\d+)/10', insights_text, re.IGNORECASE | re.DOTALL)
        if tech_match:
            insights["technology"]["score"] = int(tech_match.group(1))
        
        # Extract Market score
        market_match = re.search(r'Market.*?(\d+)/10', insights_text, re.IGNORECASE | re.DOTALL)
        if market_match:
            insights["market"]["score"] = int(market_match.group(1))
        
        # Extract Viability score
        viability_match = re.search(r'Viability.*?(\d+)/10', insights_text, re.IGNORECASE | re.DOTALL)
        if viability_match:
            insights["viability"]["score"] = int(viability_match.group(1))
        
        return insights
    
    @traceable(name="generate_comparative_insights")
    async def generate_comparative_insights(self, company_names: list) -> Dict[str, Any]:
        """
        Generate comparative insights for multiple startups.
        Useful for tier-based comparison.
        """
        try:
            results = []
            
            for company_name in company_names:
                insight = await self.generate_insights(company_name)
                if insight.get("success"):
                    results.append(insight)
            
            # Generate comparison summary
            if len(results) > 1:
                comparison = await self._generate_comparison_summary(results)
                return {
                    "success": True,
                    "individual_insights": results,
                    "comparison": comparison
                }
            
            return {
                "success": True,
                "individual_insights": results
            }
            
        except Exception as e:
            logger.error(f"Error in comparative insights: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @traceable(name="comparison_summary")
    async def _generate_comparison_summary(self, insights_list: list) -> str:
        """Generate a summary comparing multiple startups"""
        
        companies_summary = "\n\n".join([
            f"**{insight['company_name']}**\n{insight['insights'].get('full_analysis', '')[:500]}..."
            for insight in insights_list
        ])
        
        prompt = f"""Compare the following startups and provide a ranking for AXA:

{companies_summary}

Provide:
1. Overall ranking (best to worst)
2. Key differentiators
3. Top recommendation for AXA"""
        
        try:
            response = await llm_completion(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst. Provide concise, actionable comparisons."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                use_nvidia_nim=True,
                temperature=0.7,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating comparison: {e}")
            return f"Error: {str(e)}"


def create_insights_agent(db: Session) -> InsightsAgent:
    """Factory function to create insights agent"""
    return InsightsAgent(db)
