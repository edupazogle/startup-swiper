"""
AI Concierge System with MCP Integration

Comprehensive AI assistant capable of answering questions about:
- Startups (from database via MCP and CB Insights)
- Events and schedules
- Meetings and participants
- Slush main events
- Side events with directions
- Attendees

Features:
- LiteLLM integration with NVIDIA NIM support
- MCP (Model Context Protocol) for database queries
- Tool calling support for LLM function calls
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import re
import asyncio
import logging

from llm_config import llm_completion, simple_llm_call_async
from cb_insights_integration import cb_insights_api, cb_chat
from google_maps_integration import google_maps_api
from mcp_client import StartupDatabaseMCPTools
import models

logger = logging.getLogger(__name__)


class StartupDataLoader:
    """Load and manage startup data from JSON files"""
    
    def __init__(self):
        self.startups_data = None
        self.startups_dir = Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / "startups"
        self._load_startups()
    
    def _load_startups(self):
        """Load startup data from JSON files"""
        try:
            # Try to load the extracted data first
            extracted_file = self.startups_dir / "slush2_extracted.json"
            if extracted_file.exists():
                with open(extracted_file, 'r', encoding='utf-8') as f:
                    self.startups_data = json.load(f)
                    print(f"✓ Loaded {len(self.startups_data)} startups from slush2_extracted.json")
                    return
            
            # Fallback to other files
            for filename in ["slush2.json", "slush_full.json"]:
                file_path = self.startups_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.startups_data = data
                        elif isinstance(data, dict) and "startups" in data:
                            self.startups_data = data["startups"]
                        print(f"✓ Loaded {len(self.startups_data)} startups from {filename}")
                        return
            
            print("⚠️  No startup data files found")
            self.startups_data = []
            
        except Exception as e:
            print(f"✗ Error loading startup data: {e}")
            self.startups_data = []
    
    def search_startups(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search startups by name, description, or category
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching startups
        """
        if not self.startups_data:
            return []
        
        query_lower = query.lower()
        results = []
        
        for startup in self.startups_data:
            # Search in name
            if query_lower in startup.get("name", "").lower():
                results.append(startup)
                continue
            
            # Search in description
            if query_lower in startup.get("description", "").lower():
                results.append(startup)
                continue
            
            # Search in short description
            if query_lower in startup.get("shortDescription", "").lower():
                results.append(startup)
                continue
            
            # Search in categories
            categories = startup.get("categories", [])
            if isinstance(categories, list):
                for cat in categories:
                    if isinstance(cat, dict) and query_lower in cat.get("name", "").lower():
                        results.append(startup)
                        break
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    def get_startup_by_id(self, startup_id: int) -> Optional[Dict[str, Any]]:
        """Get startup by ID"""
        if not self.startups_data:
            return None
        
        for startup in self.startups_data:
            if startup.get("id") == startup_id:
                return startup
        
        return None
    
    def get_startups_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get startups by category"""
        if not self.startups_data:
            return []
        
        category_lower = category.lower()
        results = []
        
        for startup in self.startups_data:
            categories = startup.get("categories", [])
            if isinstance(categories, list):
                for cat in categories:
                    if isinstance(cat, dict) and category_lower in cat.get("name", "").lower():
                        results.append(startup)
                        break
            
            if len(results) >= limit:
                break
        
        return results


class ContextRetriever:
    """Retrieve relevant context for AI responses"""
    
    def __init__(self, db: Session, startup_loader: StartupDataLoader):
        self.db = db
        self.startup_loader = startup_loader
    
    def get_startup_context(self, query: str) -> str:
        """Get context about startups based on query"""
        # Search local database
        startups = self.startup_loader.search_startups(query, limit=5)
        
        if not startups:
            return "No startups found matching the query in the local database."
        
        context_parts = ["Found these startups:\n"]
        for startup in startups:
            context_parts.append(f"\n- **{startup.get('name')}**")
            context_parts.append(f"  Description: {startup.get('shortDescription', 'N/A')}")
            if startup.get('total_funding'):
                context_parts.append(f"  Total Funding: ${startup.get('total_funding')}M (CB Insights)")
            context_parts.append(f"  Employees: {startup.get('employees', 'N/A')}")
            context_parts.append(f"  Website: {startup.get('website', 'N/A')}")
            
            # Add categories
            categories = startup.get("categories", [])
            if categories:
                cat_names = [c.get("name") for c in categories if isinstance(c, dict)]
                if cat_names:
                    context_parts.append(f"  Categories: {', '.join(cat_names)}")
        
        return "\n".join(context_parts)
    
    def get_events_context(self, query: str = None) -> str:
        """Get context about calendar events"""
        events = self.db.query(models.CalendarEvent).limit(50).all()
        
        if not events:
            return "No events found in the database."
        
        # Filter events if query provided
        if query:
            query_lower = query.lower()
            events = [e for e in events if 
                     query_lower in e.title.lower() or 
                     (e.category and query_lower in e.category.lower()) or
                     (e.stage and query_lower in e.stage.lower())]
        
        context_parts = ["Calendar Events:\n"]
        for event in events[:20]:  # Limit to 20 events
            context_parts.append(f"\n- **{event.title}**")
            context_parts.append(f"  Time: {event.startTime} to {event.endTime}")
            context_parts.append(f"  Type: {event.type}")
            if event.stage:
                context_parts.append(f"  Stage: {event.stage}")
            if event.category:
                context_parts.append(f"  Category: {event.category}")
            if event.attendees:
                context_parts.append(f"  Attendees: {', '.join(event.attendees[:5])}")
            if event.link:
                context_parts.append(f"  Link: {event.link}")
        
        return "\n".join(context_parts)
    
    def get_votes_context(self, startup_id: str = None) -> str:
        """Get context about votes"""
        if startup_id:
            votes = self.db.query(models.Vote).filter(
                models.Vote.startupId == startup_id
            ).all()
        else:
            votes = self.db.query(models.Vote).limit(50).all()
        
        if not votes:
            return "No votes found."
        
        # Aggregate statistics
        interested_count = sum(1 for v in votes if v.interested)
        not_interested_count = len(votes) - interested_count
        meeting_scheduled = sum(1 for v in votes if v.meetingScheduled)
        
        context = f"Vote Statistics:\n"
        context += f"- Total votes: {len(votes)}\n"
        context += f"- Interested: {interested_count}\n"
        context += f"- Not interested: {not_interested_count}\n"
        context += f"- Meetings scheduled: {meeting_scheduled}\n"
        
        return context
    
    def get_ideas_context(self) -> str:
        """Get context about submitted ideas"""
        ideas = self.db.query(models.Idea).limit(20).all()
        
        if not ideas:
            return "No ideas found."
        
        context_parts = ["Submitted Ideas:\n"]
        for idea in ideas:
            context_parts.append(f"\n- **{idea.title}** by {idea.name}")
            context_parts.append(f"  Category: {idea.category}")
            context_parts.append(f"  Description: {idea.description}")
            if idea.tags:
                context_parts.append(f"  Tags: {', '.join(idea.tags)}")
        
        return "\n".join(context_parts)
    
    def get_attendees_context(self, query: str = None) -> str:
        """Get context about attendees based on query"""
        import db_queries
        
        if not query:
            attendees = db_queries.get_all_attendees(self.db, limit=20)
            if not attendees:
                return "No attendee information available."
            
            context_parts = ["Top Attendees:\n"]
            for attendee in attendees:
                name = attendee.get("name", "Unknown")
                title = attendee.get("title", "")
                company = attendee.get("company_name", "")
                title_str = f" - {title}" if title else ""
                company_str = f" @ {company}" if company else ""
                context_parts.append(f"- {name}{title_str}{company_str}")
            
            return "\n".join(context_parts)
        
        # Search attendees based on query
        query_lower = query.lower()
        results = []
        
        # Try different search methods
        if any(word in query_lower for word in ["name", "called", "named"]):
            name_query = query_lower.replace("name", "").replace("called", "").replace("named", "").strip()
            results = db_queries.search_attendees_by_name(self.db, name_query, limit=5)
        elif any(word in query_lower for word in ["company", "from", "at", "working"]):
            company_query = query_lower.replace("company", "").replace("from", "").replace("at", "").replace("working", "").strip()
            results = db_queries.search_attendees_by_company(self.db, company_query, limit=5)
        elif any(word in query_lower for word in ["country", "from", "based"]):
            country_query = query_lower.replace("country", "").replace("from", "").replace("based", "").strip()
            results = db_queries.search_attendees_by_country(self.db, country_query, limit=10)
        elif any(word in query_lower for word in ["ceo", "founder", "investor", "developer", "engineer"]):
            results = db_queries.search_attendees_by_occupation(self.db, query, limit=5)
        else:
            # Default to name search
            results = db_queries.search_attendees_by_name(self.db, query, limit=5)
        
        if not results:
            return f"No attendees found matching '{query}'."
        
        context_parts = [f"Attendees matching '{query}':\n"]
        for attendee in results:
            name = attendee.get("name", "Unknown")
            title = attendee.get("title", "")
            company = attendee.get("company_name", "")
            country = attendee.get("country", "")
            bio = attendee.get("bio", "")
            
            title_str = f" - {title}" if title else ""
            company_str = f" @ {company}" if company else ""
            country_str = f" ({country})" if country else ""
            
            context_parts.append(f"\n- **{name}{title_str}**{company_str}{country_str}")
            if bio:
                context_parts.append(f"  Bio: {bio[:100]}...")
        
        return "\n".join(context_parts)


class AIConcierge:
    """Main AI Concierge system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.startup_loader = StartupDataLoader()
        self.context_retriever = ContextRetriever(db, self.startup_loader)
    
    async def answer_question(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Answer a question using all available resources
        
        Args:
            question: User's question
            user_context: Optional user context (location, preferences, etc.)
            
        Returns:
            AI-generated answer
        """
        # Check if this is a quick action request (LinkedIn, Startups, People, Calendar)
        question_lower = question.lower()
        
        # LinkedIn action
        if any(phrase in question_lower for phrase in [
            "linkedin", "write a linkedin post", "write linkedin post", "create linkedin post",
            "generate linkedin post", "linkedin post", "write a post", "write post",
            "create a post", "generate post", "compelling linkedin", "amazing post"
        ]):
            # For LinkedIn posts, ask clarifying questions in a conversational way
            # We'll have a natural back-and-forth conversation, asking follow-up questions
            # based on what they share
            return await self._ask_linkedin_clarification_questions(question)
        
        # Startups action
        if any(phrase in question_lower for phrase in [
            "discover", "promising startups", "learn about startups", "find startups",
            "startup matches", "match my interests", "startups that match",
            "promising companies", "find companies"
        ]):
            return await self._ask_startup_discovery_questions(question)
        
        # People action
        if any(phrase in question_lower for phrase in [
            "find", "connect with", "the right people", "investors", "founders",
            "industry experts", "ceos", "entrepreneurs", "venture capitalists",
            "people at slush", "meet people", "who to talk to"
        ]):
            return await self._ask_people_discovery_questions(question)
        
        # Calendar action
        if any(phrase in question_lower for phrase in [
            "show me", "key events", "sessions", "shouldn't miss", "must attend",
            "calendar", "schedule", "happening at slush", "what's going on",
            "what events", "important sessions"
        ]):
            return await self._ask_calendar_questions(question)
        
        # Check if this is an advanced research request
        # Include common typos and variations
        if any(phrase in question_lower for phrase in [
            "advanced research", "advance research",  # Include typo
            "deep research", "detailed analysis", 
            "research this startup", "research on",
            "in-depth analysis", "comprehensive analysis",
            "do an advanced", "do advanced", "perform advanced", "perform an advanced"
        ]):
            # Check credentials first
            creds_check = cb_chat.check_credentials()
            if not creds_check["configured"]:
                return f"""⚠️ **CB Insights API Credentials Required**

To perform advanced research using ChatCBI, please ensure your CB Insights API credentials are configured in:

📁 `app/startup-swipe-schedu/.env`

Required credentials:
- `CB_INSIGHTS_CLIENT_ID`
- `CB_INSIGHTS_CLIENT_SECRET`

Once configured, I'll be able to provide comprehensive research using CB Insights' advanced AI chatbot.

Would you like me to help with a regular search using our local database instead?"""
            
            # Proceed with ChatCBI research
            return await self._perform_advanced_research(question)
        
        # Determine question type and gather relevant context
        context_parts = []
        
        # Add user context if provided
        if user_context:
            context_parts.append(f"User Context: {json.dumps(user_context, indent=2)}")
        
        # Check if this looks like a NAME SEARCH first (person's name)
        # This should take priority over startup/founder keywords
        is_likely_person_name = self._is_likely_person_name(question)
        
        if is_likely_person_name:
            # Try to search for attendee first
            attendees_context = self.context_retriever.get_attendees_context(question)
            if "No attendees found" not in attendees_context:
                context_parts.append(attendees_context)
            else:
                # If no attendee found, fall back to startup search
                startup_context = self.context_retriever.get_startup_context(question)
                context_parts.append(startup_context)
        else:
            # Regular classification logic
            
            # Startup-related questions (but not simple name queries)
            if any(word in question_lower for word in ["startup", "company", "funding", "investment", "series", "raise"]):
                startup_context = self.context_retriever.get_startup_context(question)
                context_parts.append(startup_context)
                
                # Suggest using ChatCBI for more detailed research
                context_parts.append("\n💡 **Tip:** For comprehensive research with market analysis, competitive landscape, and funding trends, ask me to 'do an advanced research on [startup name]' using CB Insights ChatCBI.")
                
                # Also try CB Insights for additional data (but don't fail if it doesn't work)
                try:
                    cb_response = await cb_chat.ask_question(question)
                    if cb_response and "error" not in cb_response.lower() and "not configured" not in cb_response.lower():
                        context_parts.append(f"\n**CB Insights Research:**\n{cb_response}")
                except Exception as e:
                    logger.debug(f"CB Insights lookup skipped: {e}")
                    pass
            
            # Event-related questions
            if any(word in question_lower for word in ["event", "schedule", "meeting", "session", "talk", "slush"]):
                events_context = self.context_retriever.get_events_context(question)
                context_parts.append(events_context)
            
            # Direction/location questions
            if any(word in question_lower for word in ["how to get", "directions", "navigate", "arrive", "location", "where is"]):
                # Extract locations from question
                await self._add_directions_context(question, context_parts)
            
            # Voting/interest questions
            if any(word in question_lower for word in ["vote", "interest", "popular", "trending"]):
                votes_context = self.context_retriever.get_votes_context()
                context_parts.append(votes_context)
            
            # Ideas questions
            if any(word in question_lower for word in ["idea", "suggestion", "proposal"]):
                ideas_context = self.context_retriever.get_ideas_context()
                context_parts.append(ideas_context)
            
            # Attendee questions (including founder, CEO, investor context)
            if any(word in question_lower for word in ["attendee", "participant", "people", "who", "person", "founder", "ceo", "investor"]):
                attendees_context = self.context_retriever.get_attendees_context(question)
                context_parts.append(attendees_context)
        
        # Build the prompt for LLM
        full_context = "\n\n---\n\n".join(context_parts)
        
        system_message = """You are a helpful AI concierge for Slush 2025, a major startup conference. 
You have access to information about:
- Startups attending the event (from the database and CB Insights)
- Event schedules and sessions
- Meeting information and attendees
- Venue locations and directions
- Attendee information

**Advanced Research Capability:**
When users ask for "advanced research" or "detailed analysis" on a startup, you can use CB Insights' ChatCBI API 
to provide comprehensive market intelligence including:
- Business model analysis
- Competitive landscape
- Funding history and trends
- Market position and trajectory
- Technology stack insights

Provide helpful, accurate, and friendly responses. If you're asked for directions, provide clear step-by-step instructions.
If information is not available in the provided context, say so clearly but offer to help in other ways.
Always be professional and enthusiastic about helping attendees make the most of Slush 2025.

When you see startup-related questions, suggest the advanced research option if appropriate."""
        
        user_prompt = f"""Question: {question}

Available Context:
{full_context}

Please provide a helpful and comprehensive answer based on the available information."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,  # Use NVIDIA NIM default (DeepSeek-R1)
                temperature=0.7,
                max_tokens=2000,
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": self._classify_question(question)
                }
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I encountered an error processing your question: {str(e)}"
    
    async def _ask_linkedin_clarification_questions(self, question: str) -> str:
        """
        Ask clarifying questions for LinkedIn post requests
        This helps gather context about what the user wants to write about
        Intelligently searches the startup database for relevant companies
        
        Args:
            question: The original LinkedIn post request
            
        Returns:
            Response with clarifying questions incorporating database context
        """
        import db_queries
        
        # Extract potential startup/company names from the question
        startup_context = ""
        mentioned_startups = []
        
        # Try to find startups mentioned in the question
        words = question.split()
        keywords_to_skip = {"write", "post", "linkedin", "help", "me", "a", "about", "on", "for", "the", "to", "create", "generate", "can", "you", "i", "want", "would", "like", "please", "post"}
        
        potential_company_names = [word.strip('.,!?') for word in words if word.lower() not in keywords_to_skip and len(word) > 2]
        
        # Search database for mentioned startups - use actual database queries
        for company_name in potential_company_names:
            # Search the actual database
            results = db_queries.search_startups(self.db, query_text=company_name, limit=3)
            if results:
                for result in results:
                    if result:  # Make sure result is not None
                        startup_name = result.get('company_name', 'Unknown')
                        industry = result.get('primary_industry', 'N/A').upper()
                        country = result.get('company_country', '')
                        city = result.get('company_city', '')
                        location = f"{city}, {country}" if city and country else (country or city or "Global")
                        description = result.get('company_description', '')[:90]
                        
                        mentioned_startups.append({
                            'name': startup_name,
                            'industry': industry,
                            'location': location,
                            'description': description,
                            'original_query': company_name
                        })
        
        # Build context about found startups
        if mentioned_startups:
            startup_context = "\n\nI found some relevant startups in our Slush database:\n"
            for startup in mentioned_startups[:3]:  # Limit to top 3
                startup_context += f"- {startup['name']} ({startup['industry']}, {startup['location']})\n"
                if startup['description']:
                    startup_context += f"  {startup['description']}...\n"
        
        system_message = """You are a warm, human concierge working with the AXA Venture Clienteling team at Slush 2025.

Your role is to help AXA team members craft authentic LinkedIn posts that:
- Showcase innovative startups solving real insurance problems
- Highlight AXA's venture clienteling activities and approach
- Tell compelling stories about how startups are transforming insurance with a human-first perspective
- Position AXA as innovation-forward and open to ecosystem partnerships

You're NOT a marketing robot. You're a friendly colleague who understands:
- The insurance industry and its challenges
- How startups are bringing fresh thinking to insurance
- The importance of authentic storytelling
- That great posts come from genuine insights, not marketing templates

Your approach: Ask ONE question at a time, in a natural, conversational way. Like you're having coffee with someone.
Wait for their answer before moving to the next question. Let the conversation flow naturally.

Context: AXA is here to discover solutions that help customers in human ways. The startups at Slush are pioneers in this space."""
        
        user_prompt = f"""The user wants to write a LinkedIn post: "{question}"

You're helping an AXA Venture Clienteling team member at Slush write an authentic post about startups they've discovered, our venture clienteling activity, or innovative insurance solutions.

Here's how to help them:
1. Start conversational - acknowledge their interest
2. Ask questions ONE at a time (not all at once)
3. Listen to understand what genuinely excited them at Slush
4. Help them tell that story authentically
5. Make it about real insights, not marketing

Start by asking: What was the most interesting conversation or startup you met at Slush so far? What made it stand out?

Wait for their response before asking more."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,
                temperature=0.85,  # Higher for natural, conversational tone
                max_tokens=400,  # Shorter responses - one question at a time
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": "linkedin_axa_post",
                    "startups_found": len(mentioned_startups)
                }
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in LinkedIn clarification: {e}")
            # Fallback response - conversational, one question at a time
            fallback = "Hey! Happy to help you share what you're discovering at Slush. So tell me—what was the most interesting conversation or startup you've come across so far? What made it really stand out to you?"
            return fallback
    
    async def _generate_linkedin_post(self, user_responses: str) -> str:
        """
        Generate an authentic LinkedIn post based on the user's framework responses
        
        Args:
            user_responses: The user's answers to the framework questions
            
        Returns:
            A polished LinkedIn post that sounds like a real person
        """
        system_message = """You are a skilled ghostwriter helping AXA Venture Clienteling team members craft authentic LinkedIn posts about Slush 2025.

Your posts should naturally highlight:
- Innovative startups solving real insurance problems in human-centered ways
- How AXA is actively engaging in venture clienteling and innovation
- The market's solutions for modern insurance challenges
- Genuine insights about the future of insurance

But never feel promotional or fake. The best posts are the ones that sound like a real person sharing something they genuinely learned or discovered.

Key principles:
✅ **Opens with a real moment or conversation** from Slush
✅ **Tells a genuine story** (not a press release)
✅ **Includes specific startup or speaker names** where relevant
✅ **Shows authentic perspective** on what matters
✅ **Ends with a real question or reflection** that invites conversation
✅ **Uses simple, conversational language** (no corporate jargon)
✅ **Has 3-5 relevant hashtags**
✅ **Is mobile-readable** with good spacing

Most importantly: Sound like a human. Someone thoughtful. Someone who gets excited about good ideas and isn't afraid to share what they really think."""
        
        user_prompt = f"""Here's what the AXA team member shared about their Slush experience:

{user_responses}

Create an authentic LinkedIn post that sounds like them sharing a genuine insight. The post should:
- Start with their actual moment/story from Slush
- Talk about what they discovered or learned
- Feel like a real conversation, not a corporate announcement
- Mention the startup or speaker if relevant
- End naturally (question, reflection, or call to action)

Keep it conversational and real. This should feel like they're genuinely sharing something cool they found."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,
                temperature=0.75,
                max_tokens=1200,
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": "linkedin_post_generation",
                    "organization": "AXA_Venture_Clienteling"
                }
            )
            
            post = response.choices[0].message.content
            
            return f"""{post}

Before you post: Does this sound like you? If not, let me know what to adjust. Any specific startups or people you want to tag? Want to add anything else?"""
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            return "Hmm, I hit a snag generating that. No worries—let me try again with what you shared. Can you quickly remind me: What was the most interesting thing you discovered? Was it about a specific startup, or more about the broader market? That'll help me craft something better."
    
    async def _ask_startup_discovery_questions(self, question: str) -> str:
        """
        Ask detailed questions to help user discover and learn about startups
        """
        system_message = """You are a friendly startup discovery advisor at Slush 2025. 
Your goal is to help attendees find startups that match what they're looking for.

You ask ONE question at a time, in a natural conversational way. You listen to their answer before asking the next question.
You help them find startups by understanding their interests—what industries they care about, what stage they're looking for, what problems they want to solve.

Sound like a friendly colleague having a conversation, not someone reading from a script."""
        
        user_prompt = f"""The user said: "{question}"

Ask ONE natural, friendly question to understand what startups they're looking for. Just one question - something to get the conversation started.
Keep it conversational and warm. Wait for their answer before you ask anything else."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,
                temperature=0.85,
                max_tokens=400,
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": "startup_discovery"
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return "I'd love to help you find startups that match what you're looking for. Let me start with the basics—what industries or sectors are you most interested in exploring? For example, are you looking at fintech, healthtech, AI, or something else?"
    
    async def _ask_people_discovery_questions(self, question: str) -> str:
        """
        Ask detailed questions to help user find and connect with the right people
        """
        system_message = """You are a friendly networking advisor at Slush 2025.
Your goal is to help attendees find the right people to connect with.

You ask ONE question at a time, in a natural conversational way. You listen to their answer before asking the next question.
You help them by understanding what they're looking for—what roles, expertise, or goals drive their networking.

Sound like a friendly colleague helping them navigate the event, not someone reading from a script."""
        
        user_prompt = f"""The user said: "{question}"

Ask ONE natural, friendly question to understand who they want to meet at Slush. Just one question - something to get the conversation started.
Keep it conversational and warm. Wait for their answer before you ask anything else."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,
                temperature=0.85,
                max_tokens=400,
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": "people_discovery"
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return "I can definitely help you connect with the right people at Slush. First question—who are you hoping to meet? Are you looking for founders, investors, engineers, or someone specific to your industry?"
    
    async def _ask_calendar_questions(self, question: str) -> str:
        """
        Ask detailed questions to help user navigate the calendar and find key events
        """
        system_message = """You are a friendly event guide at Slush 2025.
Your goal is to help attendees discover the sessions and events that matter most to them.

You ask ONE question at a time, in a natural conversational way. You listen to their answer before asking the next question.
You help them by understanding what they care about—what topics, what format, what they want to learn.

Sound like a friendly colleague helping them plan their day, not someone reading from a script."""
        
        user_prompt = f"""The user said: "{question}"

Ask ONE natural, friendly question to understand what events they're interested in at Slush. Just one question - something to get the conversation started.
Keep it conversational and warm. Wait for their answer before you ask anything else."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                model=None,
                temperature=0.85,
                max_tokens=400,
                use_nvidia_nim=True,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": "calendar_discovery"
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Let's find the events that'll matter most for you at Slush. What topics are you most interested in learning about? For example, are you focused on fundraising, scaling, new technologies, or something else?"
    
    async def _perform_advanced_research(self, question: str) -> str:
        """
        Perform advanced research using CB Insights ChatCBI API with LLM-optimized queries
        
        Args:
            question: Research question about a startup
            
        Returns:
            Comprehensive research answer from ChatCBI
        """
        try:
            # Extract startup name from the question if possible
            words = question.split()
            company_name = None
            
            # Build the ChatCBI query - let Qwen LLM optimize it
            chatcbi_query = question
            
            # Try to extract company name for focused optimization
            for i, word in enumerate(words):
                if word.lower() in ["research", "analyze", "about", "on"]:
                    if i + 1 < len(words):
                        # Take next 1-3 words as potential company name
                        potential_name = " ".join(words[i+1:min(i+4, len(words))])
                        company_name = potential_name.strip('.,!?')
                        break
            
            # Call ChatCBI with LLM optimization
            logger.info(f"🔍 Performing advanced research: {chatcbi_query}")
            research_result = await cb_chat.ask_question(
                chatcbi_query, 
                company_name=company_name,
                optimize_query=True  # Enable Qwen LLM query optimization
            )
            
            # Format the response
            formatted_response = f"""## 🔬 Advanced Research Results (CB Insights ChatCBI)

{research_result}

---
*This research was powered by CB Insights ChatCBI with query optimization via Qwen LLM.*
"""
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in advanced research: {e}")
            return f"I encountered an error while performing advanced research: {str(e)}\n\nWould you like me to try a regular database search instead?"
    
    async def _add_directions_context(self, question: str, context_parts: List[str]):
        """Add directions context for location-based questions"""
        # Try to extract origin and destination from question
        # This is a simple extraction - could be improved with NER
        words = question.split()
        
        # Look for common location indicators
        from_idx = -1
        to_idx = -1
        
        for i, word in enumerate(words):
            if word.lower() in ["from", "leaving"]:
                from_idx = i
            elif word.lower() in ["to", "arrive", "reach", "get"]:
                to_idx = i
        
        # If we found location indicators, try to get directions
        if from_idx > 0 or to_idx > 0:
            # For now, add a note that directions can be provided
            context_parts.append(
                "Google Maps integration is available for providing directions. "
                "The system can provide walking, driving, transit, or cycling directions."
            )
    
    def _get_attendees_context(self) -> str:
        """Get context about attendees"""
        # Get unique attendees from events
        events = self.db.query(models.CalendarEvent).all()
        
        all_attendees = set()
        for event in events:
            if event.attendees:
                all_attendees.update(event.attendees)
        
        if not all_attendees:
            return "No attendee information available."
        
        return f"Total unique attendees across all events: {len(all_attendees)}\n" + \
               f"Sample attendees: {', '.join(list(all_attendees)[:20])}"
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["startup", "company", "founder"]):
            return "startup_info"
        elif any(word in question_lower for word in ["event", "schedule", "session"]):
            return "event_info"
        elif any(word in question_lower for word in ["direction", "location", "navigate"]):
            return "directions"
        elif any(word in question_lower for word in ["attendee", "participant"]):
            return "attendee_info"
        elif any(word in question_lower for word in ["vote", "interest"]):
            return "voting_info"
        elif any(word in question_lower for word in ["linkedin", "post", "write"]):
            return "linkedin_post"
        else:
            return "general"
    
    async def generate_linkedin_post(
        self,
        topic: str,
        key_points: Optional[List[str]] = None,
        people_companies_to_tag: Optional[List[str]] = None,
        call_to_action: Optional[str] = None,
        link: Optional[str] = None
    ) -> str:
        """
        Generate a professional LinkedIn post with VC partner persona
        
        Args:
            topic: Main topic for the post
            key_points: List of key points to include (optional)
            people_companies_to_tag: List of people/companies to tag (optional)
            call_to_action: Custom CTA for the post (optional)
            link: Link to include in the post (optional)
        
        Returns:
            Generated LinkedIn post
        """
        generator = LinkedInPostGenerator()
        return await generator.generate_post(
            topic=topic,
            key_points=key_points,
            people_companies_to_tag=people_companies_to_tag,
            call_to_action=call_to_action,
            link=link
        )
    
    def _is_likely_person_name(self, question: str) -> bool:
        """
        Detect if the question looks like it's asking about a person by name.
        Examples: "Eduardo Paz Ogle", "Who is John Smith?", "Tell me about Jane Doe"
        """
        question_lower = question.lower()
        
        # If it's very short (2-4 words) and doesn't contain action verbs, likely a name
        words = question.split()
        
        # Single name query (just a name, no keywords)
        if len(words) <= 4 and not any(
            keyword in question_lower for keyword in [
                "startup", "company", "event", "schedule", "vote", "idea",
                "trending", "popular", "directions", "located", "headquartered"
            ]
        ):
            return True
        
        # Explicit person-asking phrases
        if any(phrase in question_lower for phrase in [
            "who is ", "tell me about ", "search for ", "find ",
            "do you know ", "is there someone called", "is anyone named"
        ]):
            # But exclude startup-specific contexts
            if not any(word in question_lower for word in ["founder's startup", "their company", "their startup"]):
                return True
        
        return False
    
    async def get_startup_details(self, startup_name: str) -> str:
        """Get detailed information about a specific startup"""
        # Search local database
        startups = self.startup_loader.search_startups(startup_name, limit=1)
        
        if not startups:
            return f"I couldn't find information about '{startup_name}' in the local database."
        
        startup = startups[0]
        
        # Build detailed response
        details = []
        details.append(f"# {startup.get('name')}\n")
        details.append(f"**Description:** {startup.get('description', 'N/A')}\n")
        details.append(f"**Founded:** {startup.get('dateFounded', 'N/A')}")
        details.append(f"**Employees:** {startup.get('employees', 'N/A')}")
        details.append(f"**Location:** {startup.get('billingCity', 'N/A')}, {startup.get('billingCountry', 'N/A')}")
        details.append(f"**Website:** {startup.get('website', 'N/A')}\n")
        
        # Funding information from CB Insights
        if startup.get('total_funding'):
            details.append(f"**Funding Information (CB Insights):**")
            details.append(f"- Total Funding: ${startup.get('total_funding')}M")
            if startup.get('valuation'):
                details.append(f"- Latest Valuation: ${startup.get('valuation')}M")
            if startup.get('last_funding_date'):
                details.append(f"- Last Funding Date: {startup.get('last_funding_date')}\n")
        
        # Categories
        categories = startup.get("categories", [])
        if categories:
            cat_names = [c.get("name") for c in categories if isinstance(c, dict)]
            if cat_names:
                details.append(f"**Categories:** {', '.join(cat_names)}\n")
        
        # Try to get additional info from CB Insights
        try:
            cb_research = await cb_chat.research_company(startup_name, "overview and recent developments")
            if cb_research and "error" not in cb_research.lower():
                details.append(f"\n**Additional Research (CB Insights):**\n{cb_research}")
        except:
            pass
        
        return "\n".join(details)
    
    async def get_event_details(self, event_query: str) -> str:
        """Get detailed information about events"""
        events_context = self.context_retriever.get_events_context(event_query)
        
        system_message = "You are a helpful event coordinator for Slush 2025. Provide clear, organized information about events."
        user_prompt = f"The user is asking about: {event_query}\n\nAvailable events:\n{events_context}\n\nProvide a helpful summary."
        
        response = await simple_llm_call_async(
            prompt=user_prompt,
            system_message=system_message,
            model=None,  # Use NVIDIA NIM default
            use_nvidia_nim=True
        )
        
        return response
    
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "walking"
    ) -> str:
        """Get directions between two locations"""
        directions = await google_maps_api.get_directions(origin, destination, mode)
        
        if "error" in directions:
            return f"I'm sorry, I couldn't get directions: {directions['error']}"
        
        formatted = google_maps_api.format_directions_text(directions)
        return formatted


class MCPEnhancedAIConcierge(AIConcierge):
    """
    AI Concierge with MCP (Model Context Protocol) integration
    
    This extends the base AIConcierge with:
    - Tool calling support for LLM function calls
    - MCP server integration for database queries
    - Enhanced startup information retrieval
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.mcp_tools = StartupDatabaseMCPTools()
        self._init_mcp_tools()
    
    def _init_mcp_tools(self):
        """Initialize MCP tools"""
        logger.info("Initializing MCP tools for AI Concierge")
        # Tools are now available through self.mcp_tools
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for LLM function calling
        
        These tools allow the LLM to query the startup database
        when answering questions.
        
        Returns:
            List of tool definitions compatible with Claude, GPT-4, etc.
        """
        return self.mcp_tools.get_tools_for_llm()
    
    async def answer_question_with_tools(
        self,
        question: str,
        user_context: Optional[Dict[str, Any]] = None,
        use_nvidia_nim: bool = True,
        max_iterations: int = 5
    ) -> str:
        """
        Answer a question with tool calling support
        
        The LLM can call tools to extract startup information from the database
        as needed during the conversation.
        
        Args:
            question: User's question
            user_context: Optional user context
            use_nvidia_nim: Whether to use NVIDIA NIM for LLM calls
            max_iterations: Maximum number of tool call iterations
        
        Returns:
            AI-generated answer with potentially tool-enhanced context
        """
        # Check if this is a LinkedIn post request first
        question_lower = question.lower()
        if any(phrase in question_lower for phrase in [
            "write a linkedin post", "write linkedin post", "create linkedin post",
            "generate linkedin post", "linkedin post", "write a post", "write post",
            "create a post", "generate post"
        ]):
            # For LinkedIn posts, ask clarifying questions first
            return await self._ask_linkedin_clarification_questions(question)
        
        # Check if this looks like a person name (prioritize attendee search)
        is_likely_person_name = self._is_likely_person_name(question)
        
        if is_likely_person_name:
            # For name queries, use the enhanced answer_question method with name detection
            return await self.answer_question(question, user_context)
        
        # Get tool definitions in OpenAI function calling format
        tools = self.get_tool_definitions()
        
        # Build system message WITHOUT listing tools (they're passed as tools parameter)
        system_message = """You are an intelligent AI Concierge assistant for Slush 2025.

You have access to tools to query startup information from the database.
When a user asks about startups, use the available tools to get accurate information.

Guidelines:
1. Use tools to search for startups by name, industry, funding, or location
2. Get detailed startup information when needed
3. Use enrichment data for team, tech stack, and social information
4. Always provide accurate, sourced information from the tools
5. If tools return no results, explain that clearly to the user
6. DO NOT show tool call JSON to the user - execute tools silently and show only results"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
        
        # Iterative tool calling loop
        for iteration in range(max_iterations):
            try:
                # Make LLM call with tools
                response = await llm_completion(
                    messages=messages,
                    use_nvidia_nim=use_nvidia_nim,
                    temperature=0.7,
                    max_tokens=2000,
                    tools=tools,
                    tool_choice="auto"
                )
                
                # Check if the model wants to call tools
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    choice = response.choices[0]
                    message = choice.message
                    
                    # Check for tool calls
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        # Execute all tool calls
                        tool_results = []
                        for tool_call in message.tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)
                            
                            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                            
                            # Call the tool
                            result = await self.handle_tool_call(tool_name, **tool_args)
                            
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": json.dumps(result)
                            })
                        
                        # Add assistant message with tool calls
                        messages.append({
                            "role": "assistant",
                            "content": message.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                }
                                for tc in message.tool_calls
                            ]
                        })
                        
                        # Add tool results
                        messages.extend(tool_results)
                        
                        # Continue loop to let LLM process tool results
                        continue
                    
                    # No tool calls - return the response
                    return message.content or str(response)
                
                # Fallback
                return str(response)
            
            except Exception as e:
                logger.error(f"Error in tool-enhanced answer (iteration {iteration}): {e}")
                # Fall back to regular answer without tools
                if iteration == 0:
                    return await self.answer_question(question, user_context)
                else:
                    return f"I encountered an error while processing your question: {str(e)}"
        
        # Max iterations reached
        return "I apologize, but I'm having trouble processing your question. Please try rephrasing it."
    
    async def handle_tool_call(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Handle a tool call from the LLM
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments for the tool
        
        Returns:
            Tool result
        """
        logger.info(f"Calling tool: {tool_name} with args: {kwargs}")
        return await self.mcp_tools.call_tool(tool_name, **kwargs)
    
    async def conversational_startup_search(
        self,
        query: str,
        search_type: str = "name"
    ) -> str:
        """
        Perform a startup search and format results conversationally
        
        Args:
            query: Search query
            search_type: Type of search (name, industry, location, funding)
        
        Returns:
            Formatted search results
        """
        try:
            if search_type == "name":
                result = await self.mcp_tools.call_tool("search_startups_by_name", query=query, limit=10)
            elif search_type == "industry":
                result = await self.mcp_tools.call_tool("search_startups_by_industry", industry=query, limit=10)
            elif search_type == "location":
                # Parse location - assume "City, Country" format
                parts = query.split(",")
                country = parts[0].strip() if parts else query
                city = parts[1].strip() if len(parts) > 1 else None
                result = await self.mcp_tools.call_tool(
                    "search_startups_by_location",
                    country=country,
                    city=city,
                    limit=10
                )
            elif search_type == "funding":
                result = await self.mcp_tools.call_tool("search_startups_by_funding", stage=query, limit=10)
            else:
                return f"Unknown search type: {search_type}"
            
            if not result.get("success"):
                return f"Search failed: {result.get('error', 'Unknown error')}"
            
            # Format results conversationally
            results = result.get("results", [])
            if not results:
                return f"No startups found matching '{query}'."
            
            formatted_results = [f"Found {len(results)} startups:\n"]
            for startup in results[:5]:  # Show top 5
                formatted_results.append(f"\n**{startup.get('name', 'N/A')}**")
                if startup.get('description'):
                    formatted_results.append(f"  {startup['description'][:100]}...")
                if startup.get('industry'):
                    formatted_results.append(f"  Industry: {startup['industry']}")
                if startup.get('funding'):
                    formatted_results.append(f"  Funding: ${startup['funding']}M")
                if startup.get('stage'):
                    formatted_results.append(f"  Stage: {startup['stage']}")
                if startup.get('website'):
                    formatted_results.append(f"  Website: {startup['website']}")
            
            return "\n".join(formatted_results)
        
        except Exception as e:
            logger.error(f"Error in conversational search: {e}")
            return f"Error performing search: {str(e)}"


class LinkedInPostGenerator:
    """
    Generate professional LinkedIn posts with a VC partner persona
    Similar to Frank DESVIGNES - expert in AI, Blockchain, Web3, and Finance
    """
    
    def __init__(self):
        self.persona_prompt = """You are a seasoned Venture Capital Founding Partner and thought leader, similar to Frank DESVIGNES. 
Your expertise is at the intersection of AI, Blockchain, Web3, and Finance.

You have been invited to write a LinkedIn post based on the following information provided by the user.

Style and Tone Guidelines:
* Persona: You are an enthusiastic, authoritative, and globally-connected VC partner.
* Tone: Confident, optimistic, collaborative, and forward-looking.
* Language: Professional but energetic. Use emojis strategically to add personality and break up text.

Structure to follow:
1. Hook: Start with 1-2 relevant emojis and a strong, engaging opening sentence (a "Breaking News" tag, a quote, or a personal observation).
2. Context/Personal Link: Briefly explain why this topic is relevant to you or your firm.
3. Body: Break down the main points into a digestible list (using bullet points like 🔹, 👉, 🔑, or numbered lists). 
   This section should explain the "what," "why," and "how."
4. Evidence (If applicable): Include 1-2 specific data points, statistics, or quotes to support your points.
5. Tagging: Tag relevant companies and individuals involved.
6. Call to Action (CTA): End with a clear action for your audience. 
   This could be a question to drive engagement or a link to learn more.
7. Hashtags: Conclude with 5-8 relevant hashtags, including broad topics (#AI, #VentureCapital, #Blockchain) 
   and specifics related to your post.

Generate a compelling LinkedIn post now following this structure."""
    
    async def generate_post(
        self,
        topic: str,
        key_points: Optional[List[str]] = None,
        people_companies_to_tag: Optional[List[str]] = None,
        call_to_action: Optional[str] = None,
        link: Optional[str] = None
    ) -> str:
        """
        Generate a LinkedIn post with the VC partner persona
        
        Args:
            topic: Main topic for the post
            key_points: List of key points to include (optional)
            people_companies_to_tag: List of people/companies to tag (optional)
            call_to_action: Custom CTA for the post (optional)
            link: Link to include in the post (optional)
        
        Returns:
            Generated LinkedIn post
        """
        # Build the user prompt with provided inputs
        prompt_parts = [
            f"Topic: {topic}\n"
        ]
        
        if key_points:
            prompt_parts.append(f"Key Points to Include:\n" + 
                              "\n".join([f"- {point}" for point in key_points]) + "\n")
        
        if people_companies_to_tag:
            prompt_parts.append(f"People/Companies to Tag:\n" +
                              "\n".join([f"- {tag}" for tag in people_companies_to_tag]) + "\n")
        
        if call_to_action:
            prompt_parts.append(f"Desired Call to Action: {call_to_action}\n")
        
        if link:
            prompt_parts.append(f"Link to Include: {link}\n")
        
        user_prompt = "".join(prompt_parts)
        
        messages = [
            {"role": "system", "content": self.persona_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await llm_completion(
                messages=messages,
                use_nvidia_nim=True,
                temperature=0.8,  # Slightly higher for more creative writing
                max_tokens=2500
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return str(response)
        
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {e}")
            return f"Error generating LinkedIn post: {str(e)}"


# Helper functions
def create_concierge(db: Session) -> MCPEnhancedAIConcierge:
    """
    Create an AI Concierge instance with MCP and NVIDIA NIM integration
    
    Returns:
        MCPEnhancedAIConcierge: Concierge with tool calling and NVIDIA NIM support
    """
    return MCPEnhancedAIConcierge(db)


def create_mcp_concierge(db: Session) -> MCPEnhancedAIConcierge:
    """
    Create an MCP-enhanced AI Concierge instance
    
    This version has tool calling capabilities for database queries
    """
    return MCPEnhancedAIConcierge(db)

