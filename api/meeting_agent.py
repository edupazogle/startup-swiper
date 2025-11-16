"""
LLM-Powered Meeting Planning Agent
Generates contextual questions and guides users through meeting scheduling and logistics planning
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm_config import simple_llm_call_async
import json


class MeetingPlanningAgent:
    """
    LLM-powered assistant for collecting structured meeting planning information
    Similar to MeetingFeedbackAssistant but focused on scheduling and logistics
    """

    def __init__(self):
        self.system_prompts = {
            "question_generator": """You are an expert at capturing meeting logistics and planning details.
Your role is to generate 3 focused questions that will help capture essential meeting scheduling information.

The questions should be:
1. Specific to the startup context
2. Focused on practical logistics (time, attendees, objectives)
3. Action-oriented for scheduling
4. Easy to answer in 2-3 sentences each

Return ONLY a JSON array of 3 questions. No additional text.""",

            "conversation_guide": """You are a friendly meeting planning assistant helping AXA team members schedule startup meetings.

Your role:
1. Ask the pre-defined questions one at a time
2. Acknowledge their answers warmly
3. Provide helpful suggestions if they mention constraints
4. Keep the conversation flowing naturally
5. Be concise and professional

Remember: This is about making scheduling easier. Be helpful and conversational.""",

            "answer_enhancer": """You are helping to refine meeting logistics for scheduling.

Your role:
1. Review the user's answer
2. If it's clear and complete, accept it as-is
3. If it's too brief or unclear, suggest 1-2 specific clarifying questions
4. Keep suggestions short and actionable

Return format:
{
  "status": "complete" or "needs_clarification",
  "message": "your response",
  "suggestions": ["optional", "clarifying", "questions"]
}"""
        }

    async def generate_questions(
        self,
        startup_name: str,
        startup_description: str,
        meeting_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate 3 contextual questions for meeting planning
        """
        prompt = f"""Generate 3 focused questions for planning a meeting with this startup:

**Startup**: {startup_name}
**Description**: {startup_description}
{f"**Context**: {meeting_context}" if meeting_context else ""}

The questions should help capture:
1. Best times/preferences for scheduling
2. Key attendees and meeting objectives
3. Preparation needs and follow-up actions

Return as JSON array:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "category": "scheduling|attendees|objectives",
    "placeholder": "Helpful placeholder text"
  }}
]"""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["question_generator"],
                temperature=0.7
            )

            # Parse JSON response
            questions = json.loads(response.strip())

            # Validate structure
            if not isinstance(questions, list) or len(questions) != 3:
                return self._get_default_questions(startup_name)

            return questions

        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_default_questions(startup_name)

    def _get_default_questions(self, startup_name: str) -> List[Dict[str, Any]]:
        """
        Fallback questions if LLM fails
        """
        return [
            {
                "id": 1,
                "question": f"What are your preferred times and format for meeting with {startup_name}?",
                "category": "scheduling",
                "placeholder": "E.g., Next week Tuesday-Thursday, 2-4 PM, in-person at Paris office..."
            },
            {
                "id": 2,
                "question": "Who should attend from your team and what are the main meeting objectives?",
                "category": "attendees",
                "placeholder": "E.g., VP Innovation, Head of Tech, Goals: evaluate AI capabilities, assess partnership fit..."
            },
            {
                "id": 3,
                "question": "What preparation or materials would make this meeting most valuable?",
                "category": "objectives",
                "placeholder": "E.g., demo video, technical documentation, pricing details, case studies..."
            }
        ]

    async def process_conversation_turn(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        current_question: Dict[str, Any],
        is_first_message: bool = False
    ) -> Dict[str, Any]:
        """
        Process a turn in the meeting planning conversation
        """
        # Build conversation context
        messages = []
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append(f"{msg['role']}: {msg['content']}")

        context = "\n".join(messages)

        if is_first_message:
            # First message - greet and ask first question
            return {
                "response": f"Great! Let's plan this meeting together. I'll ask you a few quick questions to find the best time and format.\n\n**Question 1 of 3:**\n{current_question['question']}",
                "question_id": current_question['id'],
                "waiting_for_answer": True,
                "completed": False
            }

        # User provided an answer - acknowledge and prepare for next question
        prompt = f"""The user just answered this meeting planning question:
**Question**: {current_question['question']}
**Their answer**: {message}

Conversation so far:
{context}

Acknowledge their answer briefly (1 sentence), confirm the information is helpful, and indicate we're moving to the next question.
Keep it warm, professional, and enthusiastic about planning the meeting."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["conversation_guide"],
                temperature=0.7
            )

            return {
                "response": response.strip(),
                "question_id": current_question['id'],
                "user_answer": message,
                "waiting_for_answer": False,
                "completed": False
            }

        except Exception as e:
            print(f"Error processing conversation: {e}")
            return {
                "response": "Perfect! That's helpful information. Let's move to the next question.",
                "question_id": current_question['id'],
                "user_answer": message,
                "waiting_for_answer": False,
                "completed": False
            }

    async def generate_completion_summary(
        self,
        startup_name: str,
        qa_pairs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a summary message when all planning questions are answered
        """
        answers_text = "\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in qa_pairs
        ])

        prompt = f"""The user has completed providing meeting planning information for {startup_name}.

Here's what they provided:
{answers_text}

Generate a brief, enthusiastic completion message (2-3 sentences) that:
1. Thanks them for the planning details
2. Confirms the meeting is ready to be scheduled
3. Mentions next steps (e.g., "calendar invite will be sent", "our team will prepare")

Keep it friendly, professional, and action-oriented."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["conversation_guide"],
                temperature=0.7
            )

            return response.strip()

        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Perfect! Your meeting with {startup_name} is all planned. Our team will send a calendar invite with the confirmed details. You're all set!"

    async def enhance_answer(
        self,
        question: str,
        answer: str,
        startup_context: str
    ) -> Dict[str, Any]:
        """
        Optionally enhance or request clarification on an answer
        """
        prompt = f"""Context: Planning a meeting with {startup_context}
Question: {question}
User's answer: {answer}

Is this answer clear and complete for meeting planning, or would it benefit from clarification?
If complete, acknowledge it. If not, suggest 1-2 specific follow-up questions."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message=self.system_prompts["answer_enhancer"],
                temperature=0.5
            )

            result = json.loads(response.strip())
            return result

        except Exception as e:
            print(f"Error enhancing answer: {e}")
            return {
                "status": "complete",
                "message": "Thanks for that information!",
                "suggestions": []
            }

    def format_meeting_plan_for_storage(
        self,
        qa_pairs: List[Dict[str, Any]],
        startup_id: str,
        startup_name: str,
        user_id: str,
        user_name: str
    ) -> Dict[str, Any]:
        """
        Format the meeting planning Q&A pairs for storage in the database
        Similar to feedback formatting but optimized for meeting data
        """
        # Create structured meeting plan text
        plan_text = "\n\n".join([
            f"**{qa['category'].upper()}**: {qa['question']}\n{qa['answer']}"
            for qa in qa_pairs
        ])

        # Extract tags from categories
        tags = list(set([qa['category'] for qa in qa_pairs]))
        tags.append(startup_name)

        # Extract key information for quick access
        scheduling_info = next((qa['answer'] for qa in qa_pairs if qa['category'] == 'scheduling'), '')
        attendees_info = next((qa['answer'] for qa in qa_pairs if qa['category'] == 'attendees'), '')
        prep_info = next((qa['answer'] for qa in qa_pairs if qa['category'] == 'objectives'), '')

        return {
            "startup_id": startup_id,
            "startup_name": startup_name,
            "user_id": user_id,
            "user_name": user_name,
            "meeting_plan": plan_text,
            "scheduling_info": scheduling_info,
            "attendees_info": attendees_info,
            "preparation_info": prep_info,
            "tags": tags,
            "structured_qa": qa_pairs,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"  # Can be: scheduled, pending_confirmation, completed, cancelled
        }

    async def generate_meeting_summary_for_calendar(
        self,
        startup_name: str,
        qa_pairs: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Generate calendar event details from the meeting plan
        Returns title, description, and suggested attendees
        """
        qa_text = "\n".join([
            f"- {qa['answer']}"
            for qa in qa_pairs
        ])

        prompt = f"""Based on this meeting planning information for {startup_name}, generate:
1. A concise calendar event title (5-10 words)
2. Event description with key points
3. Suggested duration in minutes

Meeting planning details:
{qa_text}

Return as JSON:
{{
  "title": "Meeting title",
  "description": "Event description",
  "duration_minutes": 60,
  "suggested_attendees_count": 3
}}"""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="qwen/qwen3-next-80b-a3b-instruct",
                system_message="You are an expert at creating clear, professional calendar events.",
                temperature=0.7
            )

            return json.loads(response.strip())

        except Exception as e:
            print(f"Error generating calendar summary: {e}")
            return {
                "title": f"Meeting with {startup_name}",
                "description": f"Scheduled meeting to discuss partnership and evaluate opportunities",
                "duration_minutes": 60,
                "suggested_attendees_count": 3
            }


# Global instance
meeting_agent = MeetingPlanningAgent()
