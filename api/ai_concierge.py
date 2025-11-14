"""
AI Concierge System

Comprehensive AI assistant capable of answering questions about:
- Startups (from database and CB Insights)
- Events and schedules
- Meetings and participants
- Slush main events
- Side events with directions
- Attendees
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import re

from llm_config import llm_completion, simple_llm_call_async
from cb_insights_integration import cb_insights_api, cb_chat
from google_maps_integration import google_maps_api
import models


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
            context_parts.append(f"  Funding: ${startup.get('totalFunding', '0')}M")
            context_parts.append(f"  Stage: {startup.get('currentInvestmentStage', 'N/A')}")
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
        # Determine question type and gather relevant context
        question_lower = question.lower()
        context_parts = []
        
        # Add user context if provided
        if user_context:
            context_parts.append(f"User Context: {json.dumps(user_context, indent=2)}")
        
        # Startup-related questions
        if any(word in question_lower for word in ["startup", "company", "founder", "funding", "investor"]):
            startup_context = self.context_retriever.get_startup_context(question)
            context_parts.append(startup_context)
            
            # Also try CB Insights for additional data
            try:
                cb_response = await cb_chat.ask_question(question)
                if cb_response and "error" not in cb_response.lower():
                    context_parts.append(f"\nCB Insights Research:\n{cb_response}")
            except:
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
        
        # Attendee questions
        if any(word in question_lower for word in ["attendee", "participant", "people", "who"]):
            attendees_context = self._get_attendees_context()
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

Provide helpful, accurate, and friendly responses. If you're asked for directions, provide clear step-by-step instructions.
If information is not available in the provided context, say so clearly but offer to help in other ways.
Always be professional and enthusiastic about helping attendees make the most of Slush 2025."""
        
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
                model="gpt-4o",
                temperature=0.7,
                metadata={
                    "feature": "ai_concierge",
                    "question_type": self._classify_question(question)
                }
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I encountered an error processing your question: {str(e)}"
    
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
        elif any(word in question_lower for word in ["attendee", "participant", "people"]):
            return "attendee_info"
        elif any(word in question_lower for word in ["vote", "interest", "popular"]):
            return "voting_info"
        else:
            return "general"
    
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
        
        details.append(f"**Funding Information:**")
        details.append(f"- Total Funding: ${startup.get('totalFunding', '0')}M")
        details.append(f"- Investment Stage: {startup.get('currentInvestmentStage', 'N/A')}")
        details.append(f"- Last Funding: {startup.get('lastFundingDate', 'N/A')}\n")
        
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
            model="gpt-4o-mini"
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


# Helper function to create concierge instance
def create_concierge(db: Session) -> AIConcierge:
    """Create an AI Concierge instance"""
    return AIConcierge(db)
