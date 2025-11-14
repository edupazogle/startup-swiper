"""
LLM-Powered Meeting Feedback Collection
Generates contextual questions and guides users through insights collection
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from llm_config import simple_llm_call_async
import json


class MeetingFeedbackAssistant:
    """
    LLM-powered assistant for collecting structured meeting feedback
    """

    def __init__(self):
        self.system_prompts = {
            "question_generator": """You are an expert at extracting valuable insights from startup meetings.
Your role is to generate 3 focused, high-impact questions that will help AXA team members capture the most important takeaways from their meeting.

The questions should be:
1. Specific to the startup and meeting context
2. Action-oriented and strategic
3. Focused on business value, technical capabilities, and next steps
4. Easy to answer in 2-3 sentences each

Return ONLY a JSON array of 3 questions. No additional text.""",

            "conversation_guide": """You are a friendly meeting insights assistant helping AXA team members reflect on their startup meetings.

Your role:
1. Ask the pre-defined questions one at a time
2. Acknowledge their answers warmly
3. Ask follow-up questions if answers are too brief (optional)
4. Keep the conversation flowing naturally
5. Be concise and professional

Remember: This is about capturing valuable insights, not interrogating. Make it conversational.""",

            "answer_enhancer": """You are helping to refine meeting insights for future reference.

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
        Generate 3 contextual questions for post-meeting insights
        """
        prompt = f"""Generate 3 focused questions for a team member who just met with this startup:

**Startup**: {startup_name}
**Description**: {startup_description}
{f"**Meeting Context**: {meeting_context}" if meeting_context else ""}

The questions should help capture:
1. Key technical capabilities or innovations discussed
2. Business value and potential use cases for AXA
3. Next steps or action items

Return as JSON array:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "category": "technical|business|action",
    "placeholder": "Helpful placeholder text"
  }}
]"""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="gpt-4o-mini",
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
                "question": f"What were the most impressive technical capabilities or innovations that {startup_name} demonstrated?",
                "category": "technical",
                "placeholder": "Describe their key technology, unique features, or technical approach..."
            },
            {
                "id": 2,
                "question": f"What specific business value or use cases could {startup_name} provide to AXA?",
                "category": "business",
                "placeholder": "Think about departments, processes, or challenges this could address..."
            },
            {
                "id": 3,
                "question": "What are the recommended next steps or follow-up actions?",
                "category": "action",
                "placeholder": "E.g., schedule demo, request proposal, connect with specific team..."
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
        Process a turn in the feedback conversation
        """
        # Build conversation context
        messages = []
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            messages.append(f"{msg['role']}: {msg['content']}")

        context = "\n".join(messages)

        if is_first_message:
            # First message - greet and ask first question
            return {
                "response": f"Thanks for taking a moment to share your insights! Let's capture the key takeaways from your meeting.\n\n**Question 1 of 3:**\n{current_question['question']}",
                "question_id": current_question['id'],
                "waiting_for_answer": True,
                "completed": False
            }

        # User provided an answer - acknowledge and decide next step
        prompt = f"""The user just answered this question:
**Question**: {current_question['question']}
**Their answer**: {message}

Conversation so far:
{context}

Acknowledge their answer briefly (1 sentence) and indicate we're moving to the next question.
Keep it warm and conversational."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="gpt-4o-mini",
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
                "response": "Thank you for that insight! Let's move to the next question.",
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
        Generate a summary message when all questions are answered
        """
        answers_text = "\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in qa_pairs
        ])

        prompt = f"""The user has completed sharing insights about their meeting with {startup_name}.

Here's what they shared:
{answers_text}

Generate a brief, warm completion message (2-3 sentences) that:
1. Thanks them for their insights
2. Confirms the insights have been saved
3. Mentions they can edit these later if needed

Keep it friendly and professional."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="gpt-4o-mini",
                system_message=self.system_prompts["conversation_guide"],
                temperature=0.7
            )

            return response.strip()

        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Perfect! Your insights about {startup_name} have been saved. You can review or edit them anytime from the insights section. Thanks for sharing!"

    async def enhance_answer(
        self,
        question: str,
        answer: str,
        startup_context: str
    ) -> Dict[str, Any]:
        """
        Optionally enhance or request clarification on an answer
        """
        prompt = f"""Context: Meeting with {startup_context}
Question: {question}
User's answer: {answer}

Is this answer clear and complete, or would it benefit from clarification?
If complete, acknowledge it. If not, suggest 1-2 specific follow-up questions."""

        try:
            response = await simple_llm_call_async(
                prompt=prompt,
                model="gpt-4o-mini",
                system_message=self.system_prompts["answer_enhancer"],
                temperature=0.5
            )

            result = json.loads(response.strip())
            return result

        except Exception as e:
            print(f"Error enhancing answer: {e}")
            return {
                "status": "complete",
                "message": "Thanks for that insight!",
                "suggestions": []
            }

    def format_insights_for_storage(
        self,
        qa_pairs: List[Dict[str, Any]],
        meeting_id: str,
        startup_id: str,
        startup_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Format the Q&A pairs for storage in the database
        """
        # Create structured insight text
        insight_text = "\n\n".join([
            f"**{qa['category'].upper()}**: {qa['question']}\n{qa['answer']}"
            for qa in qa_pairs
        ])

        # Extract tags from categories
        tags = list(set([qa['category'] for qa in qa_pairs]))

        # Calculate rating based on answer quality (simple heuristic)
        avg_length = sum(len(qa['answer']) for qa in qa_pairs) / len(qa_pairs)
        rating = min(5, max(3, int(avg_length / 50) + 3))  # 3-5 stars based on detail

        return {
            "meetingId": meeting_id,
            "userId": user_id,
            "startupId": startup_id,
            "startupName": startup_name,
            "insight": insight_text,
            "tags": tags,
            "rating": rating,
            "followUp": any("follow" in qa['answer'].lower() or "next step" in qa['answer'].lower() for qa in qa_pairs),
            "structured_qa": qa_pairs,  # Store the structured Q&A for editing
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
feedback_assistant = MeetingFeedbackAssistant()
