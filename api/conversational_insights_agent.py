"""
Conversational Insights Agent
Guides analysts through casual post-meeting debriefs to extract insights for the whitepaper.
Uses meeting prep outlines to focus conversation on key areas.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm_config import simple_llm_call_async
import json


class ConversationalInsightsAgent:
    """
    LLM-powered agent for collecting meeting insights through natural conversation.
    Guides discussion using the meeting prep outline as context.
    """

    def __init__(self):
        self.system_prompts = {
            "initial_greeting": """You are a professional and thoughtful colleague debriefing an analyst after their startup meeting.
Your tone is professional yet warm and engaging. You want to understand what happened in the meeting.
Start by asking how the meeting went, showing genuine interest and professionalism.
Think of this as a colleague-to-colleague debrief, not an interrogation.""",

            "follow_up_questions": """You are a skilled professional having a thoughtful conversation with a colleague about their startup meeting.
Your goal is to extract insights that will inform AXA's whitepaper about innovation and partnerships.
Based on what they've told you, ask natural follow-up questions that:
1. Dig deeper into topics they mentioned
2. Reference the key talking points and questions from the meeting prep
3. Are conversational and professional
4. Don't feel forced or artificial
5. Move the conversation forward naturally

If they mention something important, ask for clarification.
If they don't know something, acknowledge it professionally and move to the next topic naturally.
Always stay curious and engaged, but maintain professional tone.""",

            "insight_extraction": """You are analyzing a conversation between a colleague and an analyst about a startup meeting.
Extract key insights that should be documented in the whitepaper.
Focus on:
1. Technology differentiation and capabilities
2. Business model and value proposition viability
3. Team capabilities and execution risk
4. Partnership or integration fit with AXA
5. Strategic relevance to insurance industry trends

Format insights as clear, actionable statements that can populate the whitepaper sections.""",
            
            "generate_three_questions": """You are preparing structured questions for a debrief discussion.
Based on the meeting prep outline and initial conversation, generate exactly 3 focused, professional questions.
These questions should:
1. Be open-ended to encourage detailed responses
2. Focus on key areas: technology, business model, team, and partnership fit
3. Be specific to the startup being discussed
4. Build naturally on the conversation so far
5. Help extract insights for the whitepaper

Return as JSON array with 3 questions: ["question 1", "question 2", "question 3"]"""
        }

        self.whitepaper_sections = {
            "1": "AI: Present and Future",
            "2": "Agentic AI: The Forefront",
            "5": "AI Business Benefits & Adoption 2030",
            "7": "Make or Buy in Agentic AI Era",
            "10": "Startups"
        }

    async def start_debrief(
        self,
        startup_name: str,
        meeting_prep_outline: str
    ) -> str:
        """
        Start the casual debrief by greeting the analyst and asking how the meeting went
        """
        greeting = f"""Hey! How did your meeting with {startup_name} go? Tell me about it! 👋"""
        return greeting

    async def generate_follow_up(
        self,
        conversation_history: List[Dict[str, str]],
        startup_name: str,
        meeting_prep_outline: str,
        last_user_message: str
    ) -> str:
        """
        Generate natural follow-up questions based on the conversation and meeting prep.
        """
        # Build conversation context
        recent_context = "\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in conversation_history[-4:] if len(conversation_history) > 0
        ])

        # Extract key questions from meeting prep to guide conversation
        key_topics = self._extract_key_topics(meeting_prep_outline)

        prompt = f"""You're having a casual debrief conversation with a colleague about their {startup_name} meeting.

RECENT CONVERSATION:
{recent_context}

KEY TOPICS TO EXPLORE (from meeting prep):
{key_topics}

Their last comment was: "{last_user_message}"

Now, respond as a friendly colleague:
1. Acknowledge what they said
2. Ask 1-2 natural follow-up questions that dig deeper
3. Reference the meeting prep topics naturally if relevant
4. Keep the tone conversational and warm
5. If they seem unsure about something, acknowledge it and move on naturally
6. Show genuine curiosity about their insights

Your response should feel like a coffee chat, not an interview. Be brief and natural."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["follow_up_questions"],
                temperature=0.8
            )
            return response.strip()

        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "That's interesting! Tell me more about that."

    def _extract_key_topics(self, outline: str) -> str:
        """Extract key talking points and questions from the outline for context"""
        import re
        topics = []
        
        # Extract talking points
        if "📌 KEY TALKING POINTS:" in outline:
            tp_section = outline.split("📌 KEY TALKING POINTS:")[1].split("❓")[0]
            points = [line.strip() for line in tp_section.split('\n') if line.strip() and line.strip()[0].isdigit()]
            topics.append("Key areas discussed:")
            for p in points[:3]:
                cleaned = re.sub(r'^\d+\.\s*', '', p).strip()
                topics.append(f"  • {cleaned}")

        # Extract questions
        if "❓ CRITICAL QUESTIONS:" in outline:
            cq_section = outline.split("❓ CRITICAL QUESTIONS:")[1].split("🎯")[0]
            questions = [line.strip() for line in cq_section.split('\n') if line.strip() and line.strip()[0].isdigit()]
            topics.append("\nWe wanted to ask about:")
            for q in questions[:3]:
                cleaned = re.sub(r'^\d+\.\s*', '', q).strip()
                topics.append(f"  • {cleaned}")

        return "\n".join(topics) if topics else "General startup discussion"

    async def extract_insights_from_conversation(
        self,
        startup_name: str,
        conversation_history: List[Dict[str, str]],
        meeting_prep_outline: str
    ) -> Dict[str, Any]:
        """
        Analyze the full conversation and extract insights for the whitepaper.
        Returns insights in structured format ready for CategorizedInsight table.
        """
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Analyze this post-meeting debrief conversation about {startup_name} and extract key insights for our whitepaper.

CONVERSATION:
{conversation_text}

MEETING PREP CONTEXT:
{meeting_prep_outline}

Extract insights and categorize them into these whitepaper sections (1-10):
1. AI: Present and Future
2. Agentic AI: The Forefront
3. General Trends & Venture State
4. Other AXA Priorities
5. AI Business Benefits & Adoption 2030
6. Tech & Ethical Choices
7. Make or Buy in Agentic AI Era
8. Talent and Culture
9. Visionaries and Leaders
10. Startups

For each insight, provide:
- section: (1-10)
- title: (5-8 words, brief title)
- insight: (30-80 words, the actual insight)
- insurance_relevance: (one of: claims, underwriting, customer-service, product-development, risk-management, operations, partnerships)
- tags: (array of relevant tags)
- confidence_score: (0.0-1.0)
- evidence_source: (which Q&A or conversation point it came from)

Return as JSON array of insights. Example format:
[
  {{
    "section": "5",
    "title": "AI-Driven Risk Assessment",
    "insight": "The startup's AI model demonstrates real-time risk assessment capabilities that could enhance AXA's underwriting processes, reducing claims frequency by 15-20% based on behavioral patterns.",
    "insurance_relevance": "underwriting",
    "tags": ["AI", "underwriting", "risk-assessment"],
    "confidence_score": 0.85,
    "evidence_source": "Question about technology differentiation"
  }}
]

Return ONLY the JSON array, no other text."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["insight_extraction"],
                temperature=0.7
            )
            
            try:
                # Parse as JSON array
                insights_list = json.loads(response.strip())
                if not isinstance(insights_list, list):
                    insights_list = [insights_list] if isinstance(insights_list, dict) else []
                
                return {
                    "success": True,
                    "insights": insights_list,
                    "timestamp": datetime.utcnow().isoformat(),
                    "startup": startup_name
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract insights as generic items
                print(f"Failed to parse insights JSON, returning text format")
                return {
                    "success": True,
                    "insights": [],
                    "raw_text": response.strip(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "startup": startup_name,
                    "format": "text"
                }

        except Exception as e:
            print(f"Error extracting insights: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "insights": []
            }

    async def generate_three_questions(
        self,
        conversation_history: List[Dict[str, str]],
        startup_name: str,
        meeting_prep_outline: str
    ) -> List[str]:
        """
        Generate exactly 3 focused questions for the debrief.
        """
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on this conversation about {startup_name}, generate exactly 3 focused, professional questions for the debrief.

CONVERSATION SO FAR:
{conversation_text}

MEETING PREP OUTLINE:
{meeting_prep_outline}

Generate 3 open-ended questions that:
1. Focus on key areas: technology capability, business viability, team execution, partnership fit
2. Are specific to {startup_name}
3. Build naturally on the conversation
4. Will help extract whitepaper insights

Return ONLY a JSON array with exactly 3 questions: ["question 1", "question 2", "question 3"]
Do not include any other text."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["generate_three_questions"],
                temperature=0.7
            )
            
            try:
                questions = json.loads(response.strip())
                if isinstance(questions, list) and len(questions) == 3:
                    return questions
                else:
                    return [
                        "What were the key technical capabilities or innovations that stood out to you?",
                        "How credible is their business model and path to market success?",
                        "What is your assessment of the team's ability to execute and their relevant experience?"
                    ]
            except:
                return [
                    "What were the key technical capabilities or innovations that stood out to you?",
                    "How credible is their business model and path to market success?",
                    "What is your assessment of the team's ability to execute and their relevant experience?"
                ]

        except Exception as e:
            print(f"Error generating questions: {e}")
            return [
                "What were the key technical capabilities or innovations that stood out to you?",
                "How credible is their business model and path to market success?",
                "What is your assessment of the team's ability to execute and their relevant experience?"
            ]


# Global instance
conversational_insights_agent = ConversationalInsightsAgent()
