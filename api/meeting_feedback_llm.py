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
                model="qwen/qwen3-next-80b-a3b-instruct",  # Use NVIDIA NIM
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
                model="qwen/qwen3-next-80b-a3b-instruct",
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
        if len(qa_pairs) > 0:
            avg_length = sum(len(qa['answer']) for qa in qa_pairs) / len(qa_pairs)
            rating = min(5, max(3, int(avg_length / 50) + 3))  # 3-5 stars based on detail
        else:
            rating = 3  # Default rating

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
            # Don't set timestamp - let SQLAlchemy handle it with default=datetime.utcnow
        }

    async def analyze_and_categorize_insights(
        self,
        qa_pairs: List[Dict],
        startup_data: Dict,
        axa_evaluation: Dict,
        user_info: Dict
    ) -> Dict[str, List[Dict]]:
        """
        Analyze meeting Q&A and extract whitepaper-ready insights for each relevant category.
        
        Returns insights grouped by category (1-10), with each insight being:
        - Concise (1-2 phrases, 30-80 words)
        - Insurance-focused
        - Including metrics and evidence
        """
        
        system_prompt = self._get_categorization_system_prompt()
        user_prompt = self._build_categorization_prompt(qa_pairs, startup_data, axa_evaluation)
        
        try:
            response = await simple_llm_call_async(
                prompt=user_prompt,
                system_message=system_prompt,
                temperature=0.7,
                use_nvidia_nim=True
            )
            
            # Clean response - remove markdown code blocks if present
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse and validate response
            categorized = json.loads(response_text)
            
            # Add user info to each insight
            for category in categorized.values():
                for insight in category:
                    insight['user_name'] = user_info.get('name', 'Unknown')
                    insight['user_email'] = user_info.get('email', '')
                    insight['user_id'] = user_info.get('id', '')
            
            return categorized
            
        except Exception as e:
            print(f"Error in categorization: {e}")
            # Fallback: create basic Category 10 insight
            return {
                "10": [{
                    "title": f"Meeting with {startup_data.get('name', 'Startup')}",
                    "insight": self._create_fallback_insight(qa_pairs, startup_data),
                    "insurance_relevance": "general",
                    "metrics": [],
                    "tags": [startup_data.get('name', 'Startup')],
                    "confidence": 0.7,
                    "evidence_source": "All Q&A",
                    "user_name": user_info.get('name', 'Unknown'),
                    "user_email": user_info.get('email', ''),
                    "user_id": user_info.get('id', '')
                }]
            }
    
    def _get_categorization_system_prompt(self) -> str:
        """System prompt for categorizing insights"""
        return """You are an expert analyst creating whitepaper-ready insights for AXA's insurance AI report.

CRITICAL REQUIREMENTS:
1. CONCISE: Each insight must be 1-2 phrases (30-80 words maximum)
2. INSURANCE-FOCUSED: Every insight must relate to insurance operations (claims, underwriting, customer service, risk assessment, fraud detection, compliance)
3. ACTIONABLE: Provide concrete, specific information with metrics when available
4. PROFESSIONAL: Authoritative tone suitable for executive whitepaper
5. EVIDENCE-BASED: Ground insights in meeting data, don't speculate

CATEGORY GUIDELINES:
Only create insights for categories where there's meaningful, specific content from the meeting.
Each category must clearly support the whitepaper section's goal.

OUTPUT FORMAT (JSON):
{
  "1": [
    {
      "title": "Brief Title (5-8 words)",
      "insight": "Concise 1-2 phrase insight (30-80 words)",
      "insurance_relevance": "claims|underwriting|customer-service|risk-assessment|fraud-detection|compliance|operational-efficiency",
      "metrics": ["95% accuracy", "80% cost reduction"],
      "tags": ["GPT-4", "Claims", "Automation"],
      "confidence": 0.9,
      "evidence_source": "Q1 technical capabilities"
    }
  ],
  "2": [...],
  ...
}

QUALITY CRITERIA:
- Minimum confidence: 0.7
- Minimum insight length: 30 words
- Must include clear insurance connection
- Prefer insights with quantified metrics
- Only include insights grounded in meeting data"""

    def _build_categorization_prompt(self, qa_pairs: List[Dict], startup_data: Dict, axa_evaluation: Dict) -> str:
        """Build user prompt with meeting data"""
        
        # Format Q&A
        qa_text = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}\nCategory: {qa['category']}"
            for qa in qa_pairs
        ])
        
        return f"""Extract whitepaper-ready insights from this meeting for AXA's insurance AI report.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MEETING TRANSCRIPT:
{qa_text}

STARTUP INFORMATION:
• Name: {startup_data.get('name', 'Unknown')}
• Description: {startup_data.get('description', 'N/A')}
• Category: {startup_data.get('category', 'N/A')}
• Funding: {startup_data.get('funding', 'Undisclosed')}
• Technologies: {', '.join(startup_data.get('tech', []))}
• Maturity: {startup_data.get('maturity', 'Unknown')}

AXA EVALUATION:
• Priority Score: {axa_evaluation.get('priority_score', 'N/A')}/100
• Technical Score: {axa_evaluation.get('technical_score', 'N/A')}/100
• Business Fit: {axa_evaluation.get('business_fit', 'N/A')}
• Innovation Level: {axa_evaluation.get('innovation_level', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHITEPAPER SECTIONS (Extract relevant insights for each):

1. AI: Present and Future
   Goal: Document AI evolution, foundation models, enterprise adoption
   Extract: Foundation model mentions (GPT, Claude, Llama), AI capabilities, adoption metrics

2. Agentic AI: The Forefront
   Goal: Showcase autonomous AI systems revolutionizing insurance
   Extract: Multi-agent systems, autonomous workflows, decision-making capabilities

3. General Trends & Venture State
   Goal: Capture market dynamics and funding patterns
   Extract: Funding info, market trends, competitive landscape, growth metrics

4. Other AXA Priorities
   Goal: Document strategic focus areas
   Extract: Health insurance, DeepTech (Quantum, Energy), HR, Sustainability

5. AI Business Benefits & Adoption 2030
   Goal: Quantify business impact and ROI
   Extract: Cost savings, efficiency gains, ROI metrics, timeline projections (2025-2030)

6. Tech & Ethical Choices
   Goal: Guide technical and ethical decisions
   Extract: Explainability, GDPR compliance, ethics, bias mitigation, security

7. Make or Buy in Agentic AI Era
   Goal: Provide strategic recommendations
   Extract: Build vs buy analysis, integration complexity, partnership potential, time to value

8. Talent and Culture
   Goal: Team building and organizational insights
   Extract: Team composition, skills, culture, expertise, organizational learnings

9. Visionaries and Leaders
   Goal: Capture leadership perspectives
   Extract: Key people met, backgrounds, notable quotes, strategic vision

10. Startups
    Goal: Company profiles and partnership potential
    Extract: Name, UVP, AXA-specific impact, next steps (pilot, POC, partnership)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXTRACTION RULES:

✅ DO:
- Keep insights to 1-2 phrases (30-80 words)
- Include specific metrics when mentioned in the meeting
- Connect every insight to insurance operations
- Use action verbs and concrete examples
- Cite which Q&A provides the evidence
- Only create insights with confidence > 0.7

❌ DON'T:
- Write long paragraphs or verbose explanations
- Include vague or generic statements
- Create insights without clear insurance relevance
- Duplicate information across categories
- Speculate beyond what was discussed in the meeting

EXAMPLE HIGH-QUALITY INSIGHTS:

Category 2 (Agentic AI):
{{
  "title": "Multi-Agent Claims Automation",
  "insight": "Three specialized agents coordinate document extraction, fraud detection, and payment approval autonomously, reducing processing time from 5 days to 2 hours with 98% accuracy.",
  "insurance_relevance": "claims",
  "metrics": ["5 days to 2 hours", "98% accuracy", "3 agents"],
  "tags": ["Multi-Agent", "Claims", "Automation"],
  "confidence": 0.95,
  "evidence_source": "Q1 technical architecture"
}}

Category 5 (Business Benefits):
{{
  "title": "Claims Cost Reduction Projection",
  "insight": "80% processing cost reduction achievable by 2027, with early adopter pilots showing 60% improvement within 6 months of deployment.",
  "insurance_relevance": "operational-efficiency",
  "metrics": ["80% cost reduction", "60% in 6 months", "2027"],
  "tags": ["ROI", "Cost-Savings", "Timeline"],
  "confidence": 0.88,
  "evidence_source": "Q2 business value discussion"
}}

Now extract whitepaper-ready insights from the meeting data above. Focus on insurance-relevant, concise, actionable insights with clear evidence from the meeting.

IMPORTANT: Return ONLY valid JSON in the exact format specified above. No markdown, no code blocks, just the JSON object."""

    def _create_fallback_insight(self, qa_pairs: List[Dict], startup_data: Dict) -> str:
        """Create a basic insight if categorization fails"""
        answers = " ".join([qa['answer'][:100] for qa in qa_pairs])
        return f"{startup_data.get('name', 'Startup')} discussed: {answers[:150]}..."


# Global instance
feedback_assistant = MeetingFeedbackAssistant()
