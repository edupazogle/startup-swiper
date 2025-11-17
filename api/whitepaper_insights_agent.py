"""
Whitepaper Insights Agent
Helps AXA analysts prepare for startup meetings by generating adaptive talking points,
key questions, and potential concerns based on startup data and user feedback.
Focused on AXA's Slush 2025 Whitepaper Insights framework.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm_config import simple_llm_call_async
import json


class WhitepaperInsightsAgent:
    """
    LLM-powered assistant for preparing analysts to meet startups.
    Generates adaptive talking points, questions organized by whitepaper sections.
    """

    def __init__(self):
        self.system_prompts = {
            "outline_generator": """You're an AXA analyst preparing for a startup meeting. Generate a practical meeting brief with:
- 3 key talking points about strategic fit and business value
- 3 critical questions to ask during the meeting
- Whitepaper section relevance

Be specific to the startup's actual capabilities and how they align with AXA's insurance business.""",

            "outline_adapter": """You're refining a meeting brief based on analyst feedback. Update the talking points and questions to reflect their insights while keeping the same structure."""
        }

        self.whitepaper_sections = {
            "1": "AI: Present and Future",
            "2": "Agentic AI: The Forefront",
            "3": "General Trends & Venture State",
            "4": "Other AXA Priorities",
            "5": "AI Business Benefits & Adoption 2030",
            "6": "Tech & Ethical Choices",
            "7": "Make or Buy in Agentic AI Era",
            "8": "Talent and Culture",
            "9": "Visionaries and Leaders",
            "10": "Startups"
        }

    async def generate_initial_outline(
        self,
        startup_name: str,
        startup_description: str,
        startup_data: Dict[str, Any]
    ) -> str:
        """
        Generate initial meeting prep outline with talking points and questions
        Returns formatted outline text
        """
        # Safely extract technologies
        technologies = startup_data.get('technologies', [])
        if not technologies or not isinstance(technologies, list):
            technologies = []
        tech_summary = ", ".join([str(t) for t in technologies[:5]]) if technologies else "N/A"
        
        funding = startup_data.get('total_funding', 'Unknown')
        
        prompt = f"""Generate a meeting prep outline for {startup_name}.

{startup_name}
{startup_description}
Technologies: {tech_summary}
Funding: ${funding}M | Category: {startup_data.get('category', 'AI/Enterprise')}

Create exactly 3 talking points and 3 questions:
- Talking points: Specific strategic insights about how this startup fits AXA's insurance business
- Questions: Probing questions about capabilities, team, and partnership potential

Use this format:

═══════════════════════════════════════════════════════
MEETING PREP: {startup_name}
═══════════════════════════════════════════════════════

📌 KEY TALKING POINTS:
  1. [Point about strategic fit]
  2. [Point about business value/ROI]
  3. [Point about execution/partnership]

❓ CRITICAL QUESTIONS:
  1. [Question about capabilities]
  2. [Question about team/execution]
  3. [Question about AXA integration]

🎯 WHITEPAPER RELEVANCE:
  • Section 1 (AI: Present and Future): [relevance]
  • Section 5 (Business Benefits & Adoption 2030): [relevance]
  • Section 7 (Make or Buy): [relevance]
  • Section 10 (Startups): [relevance]

═══════════════════════════════════════════════════════"""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["outline_generator"],
                temperature=0.8
            )

            return response.strip()

        except Exception as e:
            print(f"Error generating initial outline: {e}")
            return self._get_default_outline(startup_name, startup_data)

    def _get_default_outline(self, startup_name: str, startup_data: Dict[str, Any]) -> str:
        """Fallback outline if LLM fails"""
        return f"""═══════════════════════════════════════════════════════
MEETING PREP: {startup_name}
═══════════════════════════════════════════════════════

📌 KEY TALKING POINTS:
  1. Innovative approach to AI/technology with potential to address insurance industry pain points
  2. Clear business value proposition aligned with AXA's operational efficiency and customer experience goals
  3. Strong strategic fit for partnership or integration into AXA's broader AI roadmap

❓ CRITICAL QUESTIONS:
  1. What specific technical capabilities differentiate {startup_name} from existing solutions in the market?
  2. Can you demonstrate measurable business impact or customer success metrics relevant to AXA's insurance operations?
  3. What would a pilot or partnership with AXA look like, and what are the integration requirements and timeline?

🎯 WHITEPAPER RELEVANCE:
  • Section 1 (AI: Present and Future): Represents emerging AI capabilities
  • Section 5 (Business Benefits & Adoption 2030): Demonstrates operational improvement potential
  • Section 7 (Make or Buy): Partnership/integration opportunity assessment
  • Section 10 (Startups): Key innovator in the insurance tech space

═══════════════════════════════════════════════════════"""

    async def generate_adapted_outline(
        self,
        startup_name: str,
        startup_description: str,
        startup_data: Dict[str, Any],
        previous_outline: str,
        user_feedback: str
    ) -> str:
        """
        Generate adapted outline based on analyst feedback
        """
        prompt = f"""Update this meeting prep outline based on analyst feedback.

STARTUP: {startup_name} - {startup_description}

CURRENT OUTLINE:
{previous_outline}

ANALYST FEEDBACK:
{user_feedback}

Generate an updated outline that incorporates their insights while keeping the same format (talking points, questions, whitepaper relevance)."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["outline_adapter"],
                temperature=0.7
            )

            return response.strip()

        except Exception as e:
            print(f"Error adapting outline: {e}")
            return previous_outline

    def format_outline_for_email(
        self,
        startup_name: str,
        outline: str,
        analyst_name: str
    ) -> Dict[str, str]:
        """
        Format outline as email-ready content
        """
        email_subject = f"Meeting Prep Brief: {startup_name}"
        
        email_body = f"""Hi,

Please find attached the meeting preparation brief for {startup_name}.

This outline includes:
• Key talking points aligned with our whitepaper themes
• Critical questions to ask during the meeting
• Whitepaper relevance mapping

Meeting Prep Outline:
{outline}

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Prepared by: {analyst_name}

---
AXA Whitepaper Insights Tool
Slush 2025 Conference"""

        return {
            "subject": email_subject,
            "body": email_body,
            "outline": outline
        }

    def format_for_clipboard(self, outline: str) -> str:
        """Format outline for clipboard copying"""
        return outline


# Global instance
whitepaper_agent = WhitepaperInsightsAgent()
