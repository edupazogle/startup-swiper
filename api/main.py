from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import timedelta, datetime
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent))

import models
import schemas
import crud
from database import engine, get_db
from llm_config import simple_llm_call_async, llm_completion
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ai_concierge import create_concierge
# from notification_service import NotificationService, notification_worker
import asyncio
import json
from pathlib import Path
from startup_prioritization import prioritizer
from meeting_feedback_llm import feedback_assistant

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Startup Swiper API", version="1.0.0")

# Load startup data - try multiple paths
STARTUPS_FILE = Path(__file__).parent / "startups_data.json"
BACKUP_FILE = Path(__file__).parent.parent / "docs/architecture/ddbb/slush2_extracted.json"
ALL_STARTUPS = []

try:
    # Try primary file first
    if STARTUPS_FILE.exists():
        with open(STARTUPS_FILE, "r") as f:
            ALL_STARTUPS = json.load(f)
        print(f"✓ Loaded {len(ALL_STARTUPS)} startups from {STARTUPS_FILE.name}")
    # Fallback to backup location
    elif BACKUP_FILE.exists():
        with open(BACKUP_FILE, "r") as f:
            ALL_STARTUPS = json.load(f)
        print(f"✓ Loaded {len(ALL_STARTUPS)} startups from {BACKUP_FILE.name}")
    else:
        print(f"⚠️  Warning: Could not find startups file in {STARTUPS_FILE} or {BACKUP_FILE}")
        ALL_STARTUPS = []
except Exception as e:
    print(f"⚠️  Warning: Could not load startups data: {e}")
    ALL_STARTUPS = []

# Initialize notification service
# notification_service = NotificationService()  # Temporarily disabled - install pywebpush first

# Start notification worker on startup
# @app.on_event("startup")
# async def startup_event():
#     """Start background tasks on app startup"""
#     asyncio.create_task(notification_worker())

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Request/Response Models
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-4o"
    system_message: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    return_json: Optional[bool] = False

class LLMResponse(BaseModel):
    content: str
    model: str
    request_id: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "service": "startup-swiper-api",
        "version": "1.0.0",
        "startups_loaded": len(ALL_STARTUPS)
    }

# LLM Endpoints
@app.post("/llm/simple", response_model=LLMResponse)
async def llm_simple_call(request: LLMRequest):
    """
    Simple LLM call endpoint
    - Logs all requests/responses to /logs/llm folder
    - Supports all LiteLLM models (OpenAI, Anthropic, etc.)
    """
    try:
        content = await simple_llm_call_async(
            prompt=request.prompt,
            model=request.model,
            system_message=request.system_message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return LLMResponse(
            content=content,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/chat", response_model=LLMResponse)
async def llm_chat_call(request: ChatRequest):
    """
    Chat-based LLM call with full message history
    - Logs all requests/responses to /logs/llm folder
    - Supports conversation context
    """
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        response = await llm_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        content = response.choices[0].message.content if hasattr(response, 'choices') else str(response)

        return LLMResponse(
            content=content,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Authentication endpoints
@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get access token
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.User)
async def get_me(current_user: models.User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user

@app.get("/auth/users", response_model=List[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (requires authentication)
    """
    return crud.get_users(db, skip=skip, limit=limit)

@app.put("/auth/users/{user_id}", response_model=schemas.User)
async def update_user_endpoint(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user information (users can only update themselves)
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

# Calendar Events endpoints
@app.post("/calendar-events/", response_model=schemas.CalendarEvent)
def create_calendar_event(event: schemas.CalendarEventCreate, db: Session = Depends(get_db)):
    return crud.create_calendar_event(db=db, event=event)

@app.get("/calendar-events/", response_model=List[schemas.CalendarEvent])
def read_calendar_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_calendar_events(db, skip=skip, limit=limit)
    return events

@app.get("/calendar-events/{event_id}", response_model=schemas.CalendarEvent)
def read_calendar_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_calendar_event(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return event

@app.put("/calendar-events/{event_id}", response_model=schemas.CalendarEvent)
def update_calendar_event(event_id: int, event: schemas.CalendarEventCreate, db: Session = Depends(get_db)):
    return crud.update_calendar_event(db=db, event_id=event_id, event=event)

@app.delete("/calendar-events/{event_id}")
def delete_calendar_event(event_id: int, db: Session = Depends(get_db)):
    crud.delete_calendar_event(db=db, event_id=event_id)
    return {"message": "Calendar event deleted"}

# LinkedIn Chat Messages endpoints
@app.post("/linkedin-chat-messages/", response_model=schemas.LinkedInChatMessage)
def create_linkedin_message(message: schemas.LinkedInChatMessageCreate, db: Session = Depends(get_db)):
    return crud.create_linkedin_message(db=db, message=message)

@app.get("/linkedin-chat-messages/", response_model=List[schemas.LinkedInChatMessage])
def read_linkedin_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_linkedin_messages(db, skip=skip, limit=limit)

@app.get("/linkedin-chat-messages/{message_id}", response_model=schemas.LinkedInChatMessage)
def read_linkedin_message(message_id: int, db: Session = Depends(get_db)):
    message = crud.get_linkedin_message(db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

# Admin User endpoints
@app.post("/admin-user/", response_model=schemas.AdminUser)
def create_admin_user(user: schemas.AdminUserCreate, db: Session = Depends(get_db)):
    return crud.create_admin_user(db=db, user=user)

@app.get("/admin-user/", response_model=schemas.AdminUser)
def read_admin_user(db: Session = Depends(get_db)):
    user = crud.get_admin_user(db)
    if user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")
    return user

# Votes endpoints
@app.post("/votes/", response_model=schemas.Vote)
def create_vote(vote: schemas.VoteCreate, db: Session = Depends(get_db)):
    return crud.create_vote(db=db, vote=vote)

@app.get("/votes/", response_model=List[schemas.Vote])
def read_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_votes(db, skip=skip, limit=limit)

@app.get("/votes/startup/{startup_id}", response_model=List[schemas.Vote])
def read_votes_by_startup(startup_id: str, db: Session = Depends(get_db)):
    return crud.get_votes_by_startup(db, startup_id=startup_id)

# Auroral Info endpoints
@app.post("/auroral-info/", response_model=schemas.AuroralInfo)
def create_auroral_info(info: schemas.AuroralInfoCreate, db: Session = Depends(get_db)):
    return crud.create_auroral_info(db=db, info=info)

@app.get("/auroral-info/", response_model=schemas.AuroralInfo)
def read_auroral_info(db: Session = Depends(get_db)):
    info = crud.get_auroral_info(db)
    if info is None:
        raise HTTPException(status_code=404, detail="Auroral info not found")
    return info

# Ideas endpoints
@app.post("/ideas/", response_model=schemas.Idea)
def create_idea(idea: schemas.IdeaCreate, db: Session = Depends(get_db)):
    return crud.create_idea(db=db, idea=idea)

@app.get("/ideas/", response_model=List[schemas.Idea])
def read_ideas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ideas(db, skip=skip, limit=limit)

@app.get("/ideas/{idea_id}", response_model=schemas.Idea)
def read_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = crud.get_idea(db, idea_id=idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

# Startup Ratings endpoints
@app.post("/startup-ratings/", response_model=schemas.StartupRating)
def create_startup_rating(rating: schemas.StartupRatingCreate, db: Session = Depends(get_db)):
    return crud.create_startup_rating(db=db, rating=rating)

@app.get("/startup-ratings/", response_model=List[schemas.StartupRating])
def read_startup_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_startup_ratings(db, skip=skip, limit=limit)

@app.get("/startup-ratings/{startup_id}", response_model=schemas.StartupRating)
def read_startup_rating(startup_id: str, db: Session = Depends(get_db)):
    rating = crud.get_startup_rating(db, startup_id=startup_id)
    if rating is None:
        raise HTTPException(status_code=404, detail="Startup rating not found")
    return rating

# Finished Users endpoints
@app.post("/finished-users/", response_model=schemas.FinishedUser)
def add_finished_user(user_id: int, db: Session = Depends(get_db)):
    return crud.add_finished_user(db=db, user_id=user_id)

@app.get("/finished-users/", response_model=List[schemas.FinishedUser])
def read_finished_users(db: Session = Depends(get_db)):
    return crud.get_finished_users(db)

# AI Chat Messages endpoints
@app.post("/ai-chat-messages/", response_model=schemas.AIChatMessage)
def create_ai_message(message: schemas.AIChatMessageCreate, db: Session = Depends(get_db)):
    return crud.create_ai_message(db=db, message=message)

@app.get("/ai-chat-messages/", response_model=List[schemas.AIChatMessage])
def read_ai_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ai_messages(db, skip=skip, limit=limit)

# User Events endpoints
@app.post("/user-events/", response_model=schemas.UserEvent)
def create_user_event(event: schemas.UserEventCreate, db: Session = Depends(get_db)):
    return crud.create_user_event(db=db, event=event)

@app.get("/user-events/", response_model=List[schemas.UserEvent])
def read_user_events(db: Session = Depends(get_db)):
    return crud.get_user_events(db)

# AI Assistant Messages endpoints
@app.post("/ai-assistant-messages/", response_model=schemas.AIAssistantMessage)
def create_ai_assistant_message(message: schemas.AIAssistantMessageCreate, db: Session = Depends(get_db)):
    return crud.create_ai_assistant_message(db=db, message=message)

@app.get("/ai-assistant-messages/", response_model=List[schemas.AIAssistantMessage])
def read_ai_assistant_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_ai_assistant_messages(db, skip=skip, limit=limit)

# Current User ID endpoints
@app.post("/current-user-id/", response_model=schemas.CurrentUserId)
def set_current_user_id(user_id: int, db: Session = Depends(get_db)):
    return crud.set_current_user_id(db=db, user_id=user_id)

@app.get("/current-user-id/", response_model=schemas.CurrentUserId)
def get_current_user_id(db: Session = Depends(get_db)):
    user_id = crud.get_current_user_id(db)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Current user ID not found")
    return user_id

# Data Version endpoint
@app.get("/data-version/", response_model=schemas.DataVersion)
def get_data_version(db: Session = Depends(get_db)):
    version = crud.get_data_version(db)
    if version is None:
        raise HTTPException(status_code=404, detail="Data version not found")
    return version

@app.post("/data-version/", response_model=schemas.DataVersion)
def set_data_version(version: str, db: Session = Depends(get_db)):
    return crud.set_data_version(db=db, version=version)

# AI Concierge Endpoints
class ConciergeRequest(BaseModel):
    question: str
    user_context: Optional[Dict[str, Any]] = None

class ConciergeResponse(BaseModel):
    answer: str
    question_type: Optional[str] = None

class StartupQuery(BaseModel):
    startup_name: str

class DirectionsRequest(BaseModel):
    origin: str
    destination: str
    mode: Optional[str] = "walking"

@app.post("/concierge/ask", response_model=ConciergeResponse)
async def ask_concierge(request: ConciergeRequest, db: Session = Depends(get_db)):
    """
    Ask the AI Concierge any question about:
    - Startups (database + CB Insights)
    - Events and schedules
    - Meetings and participants
    - Directions and locations
    - Attendees
    """
    concierge = create_concierge(db)
    answer = await concierge.answer_question(request.question, request.user_context)
    question_type = concierge._classify_question(request.question)
    
    return ConciergeResponse(answer=answer, question_type=question_type)

@app.post("/concierge/startup-details", response_model=ConciergeResponse)
async def get_startup_details(query: StartupQuery, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific startup
    - Uses local database
    - Enriched with CB Insights data
    """
    concierge = create_concierge(db)
    details = await concierge.get_startup_details(query.startup_name)
    
    return ConciergeResponse(answer=details, question_type="startup_details")

@app.post("/concierge/event-details", response_model=ConciergeResponse)
async def get_event_details(request: ConciergeRequest, db: Session = Depends(get_db)):
    """
    Get detailed information about events matching the query
    """
    concierge = create_concierge(db)
    details = await concierge.get_event_details(request.question)
    
    return ConciergeResponse(answer=details, question_type="event_details")

@app.post("/concierge/directions", response_model=ConciergeResponse)
async def get_directions(request: DirectionsRequest, db: Session = Depends(get_db)):
    """
    Get directions between two locations
    - Uses Google Maps API
    - Supports walking, driving, transit, bicycling modes
    """
    concierge = create_concierge(db)
    directions = await concierge.get_directions(
        request.origin,
        request.destination,
        request.mode
    )
    
    return ConciergeResponse(answer=directions, question_type="directions")

@app.get("/concierge/search-startups")
async def search_startups(query: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Search for startups by name, description, or category
    """
    concierge = create_concierge(db)
    results = concierge.startup_loader.search_startups(query, limit)
    
    return {"results": results, "count": len(results)}

@app.get("/concierge/startup-categories")
async def get_startup_by_category(category: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get startups in a specific category
    """
    concierge = create_concierge(db)
    results = concierge.startup_loader.get_startups_by_category(category, limit)
    
    return {"results": results, "count": len(results), "category": category}

# Startup Prioritization Endpoints
class PrioritizedStartupsRequest(BaseModel):
    user_id: Optional[int] = None
    limit: Optional[int] = 50

@app.get("/startups/all")
def get_all_startups(skip: int = 0, limit: int = 100):
    """
    Get all startups without prioritization
    """
    return {
        "total": len(ALL_STARTUPS),
        "count": min(limit, len(ALL_STARTUPS) - skip),
        "startups": ALL_STARTUPS[skip:skip+limit]
    }

@app.get("/startups/prioritized")
def get_prioritized_startups(
    user_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get startups prioritized for AXA team based on:
    1. Agentic platform enablers (highest priority)
    2. Agentic solutions (marketing, claims, HR, etc.)
    3. Development & integration tools
    4. Insurance-specific tech
    5. User preferences (based on voting history)
    6. Diversity (stage, category variety)
    """
    # Get user's voting history if user_id provided
    user_votes = []
    if user_id:
        user_votes = crud.get_votes(db, skip=0, limit=1000)
        user_votes = [v for v in user_votes if v.userId == user_id]

    # Get prioritized list
    prioritized = prioritizer.prioritize_startups(
        ALL_STARTUPS,
        user_votes=[{"startupId": v.startupId, "interested": v.interested} for v in user_votes],
        limit=limit
    )

    return {
        "total": len(ALL_STARTUPS),
        "prioritized_count": len(prioritized),
        "user_id": user_id,
        "personalized": user_id is not None,
        "startups": prioritized
    }

@app.get("/startups/{startup_id}/insights")
def get_startup_insights(startup_id: str):
    """
    Get categorization and priority insights for a specific startup
    """
    # Find startup
    startup = next((s for s in ALL_STARTUPS if str(s.get("id")) == startup_id or s.get("name") == startup_id), None)

    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    insights = prioritizer.get_startup_insights(startup)

    return {
        "startup_id": startup_id,
        "startup_name": startup.get("name"),
        "insights": insights
    }

@app.post("/startups/batch-insights")
def get_batch_startup_insights(startup_ids: List[str]):
    """
    Get insights for multiple startups at once
    """
    results = []

    for startup_id in startup_ids:
        startup = next((s for s in ALL_STARTUPS if str(s.get("id")) == startup_id or s.get("name") == startup_id), None)

        if startup:
            insights = prioritizer.get_startup_insights(startup)
            results.append({
                "startup_id": startup_id,
                "startup_name": startup.get("name"),
                "insights": insights
            })

    return {"results": results, "count": len(results)}

# ============================================
# Enriched Data Endpoints
# ============================================

@app.get("/startups/enriched/search")
def search_enriched_startups(
    query: str = "",
    enrichment_type: Optional[str] = None,
    limit: int = 20
):
    """
    Search enriched startups
    - enrichment_type: 'emails', 'social', 'tech_stack', 'team'
    """
    results = []
    
    for startup in ALL_STARTUPS:
        if not startup.get('is_enriched'):
            continue
        
        # Filter by name/description match
        if query and query.lower() not in startup.get('name', '').lower():
            continue
        
        enrichment = startup.get('enrichment', {})
        
        # Filter by enrichment type
        if enrichment_type == 'emails' and not enrichment.get('emails'):
            continue
        elif enrichment_type == 'social' and not enrichment.get('social_media'):
            continue
        elif enrichment_type == 'tech_stack' and not enrichment.get('tech_stack'):
            continue
        elif enrichment_type == 'team' and not enrichment.get('team_members'):
            continue
        
        results.append({
            "id": startup.get('id'),
            "name": startup.get('name'),
            "website": startup.get('website'),
            "enrichment": enrichment,
            "enriched_date": startup.get('last_enriched_date')
        })
        
        if len(results) >= limit:
            break
    
    return {
        "results": results,
        "count": len(results),
        "enrichment_type": enrichment_type,
        "query": query
    }

@app.get("/startups/{startup_id}/enrichment")
def get_startup_enrichment(startup_id: str):
    """
    Get enrichment data for a specific startup
    """
    startup = next((s for s in ALL_STARTUPS 
                   if str(s.get('id')) == startup_id or s.get('name') == startup_id), None)
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    if not startup.get('is_enriched'):
        raise HTTPException(
            status_code=404,
            detail="Startup enrichment not available"
        )
    
    enrichment = startup.get('enrichment', {})
    
    return {
        "startup_id": startup.get('id'),
        "startup_name": startup.get('name'),
        "website": startup.get('website'),
        "enrichment": {
            "emails": enrichment.get('emails', []),
            "phone_numbers": enrichment.get('phone_numbers', []),
            "social_media": enrichment.get('social_media', {}),
            "tech_stack": enrichment.get('tech_stack', []),
            "key_pages": enrichment.get('key_pages', {}),
            "team_members": enrichment.get('team_members', []),
            "enrichment_date": enrichment.get('enrichment_date'),
            "sources_checked": enrichment.get('sources_checked', [])
        },
        "last_enriched": startup.get('last_enriched_date')
    }

@app.get("/startups/enrichment/stats")
def get_enrichment_stats():
    """
    Get enrichment statistics
    """
    total = len(ALL_STARTUPS)
    enriched = [s for s in ALL_STARTUPS if s.get('is_enriched')]
    
    stats = {
        "total_startups": total,
        "enriched_count": len(enriched),
        "enrichment_percentage": (len(enriched) / total * 100) if total > 0 else 0,
        "fields_available": {
            "with_emails": sum(1 for s in enriched if s.get('enrichment', {}).get('emails')),
            "with_phone": sum(1 for s in enriched if s.get('enrichment', {}).get('phone_numbers')),
            "with_social": sum(1 for s in enriched if s.get('enrichment', {}).get('social_media')),
            "with_tech_stack": sum(1 for s in enriched if s.get('enrichment', {}).get('tech_stack')),
            "with_team": sum(1 for s in enriched if s.get('enrichment', {}).get('team_members'))
        }
    }
    
    return stats

@app.post("/startups/enrichment/by-name")
async def get_startups_by_enriched_field(
    field_name: str = None,
    field_value: str = None,
    limit: int = 20,
    # Also accept from JSON body
    body: Optional[Dict[str, Any]] = None
):
    """
    Find startups that have a specific enriched field value
    - field_name: 'email', 'tech', 'phone', 'social', 'person'
    - Can pass as query params or JSON body
    """
    # Support both query params and JSON body
    if body:
        field_name = body.get('field_name', field_name)
        field_value = body.get('field_value', field_value)
        limit = body.get('limit', limit)
    
    if not field_name or not field_value:
        raise HTTPException(status_code=400, detail="field_name and field_value are required")
    
    results = []
    field_value_lower = field_value.lower()
    
    for startup in ALL_STARTUPS:
        if not startup.get('is_enriched'):
            continue
        
        enrichment = startup.get('enrichment', {})
        found = False
        
        if field_name == 'email':
            found = any(field_value_lower in e.lower() 
                       for e in enrichment.get('emails', []))
        elif field_name == 'phone':
            found = any(field_value_lower in p.lower() 
                       for p in enrichment.get('phone_numbers', []))
        elif field_name == 'tech':
            found = any(field_value_lower in t.lower() 
                       for t in enrichment.get('tech_stack', []))
        elif field_name == 'person':
            found = any(field_value_lower in p.lower() 
                       for p in enrichment.get('team_members', []))
        elif field_name == 'social':
            social = enrichment.get('social_media', {})
            found = any(field_value_lower in str(v).lower() 
                       for v in social.values())
        
        if found:
            results.append({
                "id": startup.get('id'),
                "name": startup.get('name'),
                "website": startup.get('website'),
                "matched_field": field_name,
                "enrichment_date": startup.get('last_enriched_date')
            })
            
            if len(results) >= limit:
                break
    
    return {
        "results": results,
        "count": len(results),
        "search_field": field_name,
        "search_value": field_value
    }

@app.get("/")
def root():
    return {
        "message": "Startup Swiper API with AI Concierge & Smart Prioritization",
        "version": "1.0.0",
        "features": [
            "AI Concierge for Q&A",
            "Smart Startup Prioritization (Agentic-First)",
            "Personalized Recommendations",
            "Startup Information (DB + CB Insights)",
            "Event Scheduling",
            "Directions (Google Maps)",
            "Attendee Information",
            "Post-Meeting Insight Notifications"
        ],
        "startups_loaded": len(ALL_STARTUPS)
    }

# ============================================
# Meeting Insights & Notifications Endpoints
# ============================================

@app.post("/insights/submit", response_model=schemas.MeetingInsight)
async def submit_meeting_insight(
    insight: schemas.MeetingInsightCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit an insight after a meeting
    - Automatically marks notification as completed
    - Removes notification from queue
    """
    # Create the insight
    db_insight = models.MeetingInsight(**insight.dict())
    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)
    
    # Mark notification as insight submitted (notification_service not yet enabled)
    # TODO: Enable notification service when pywebpush is installed
    # await notification_service.mark_insight_submitted(
    #     db=db,
    #     meeting_id=insight.meetingId,
    #     user_id=insight.userId
    # )
    
    return db_insight

@app.get("/insights/user/{user_id}", response_model=List[schemas.MeetingInsight])
async def get_user_insights(user_id: str, db: Session = Depends(get_db)):
    """Get all insights submitted by a user"""
    insights = db.query(models.MeetingInsight).filter(
        models.MeetingInsight.userId == user_id
    ).order_by(models.MeetingInsight.timestamp.desc()).all()
    return insights

@app.get("/insights/meeting/{meeting_id}", response_model=List[schemas.MeetingInsight])
async def get_meeting_insights(meeting_id: str, db: Session = Depends(get_db)):
    """Get all insights for a specific meeting"""
    insights = db.query(models.MeetingInsight).filter(
        models.MeetingInsight.meetingId == meeting_id
    ).all()
    return insights

# ============================================
# LLM-Powered Feedback Collection
# ============================================

@app.post("/feedback/start")
async def start_feedback_session(
    meeting_id: str,
    user_id: str,
    startup_id: Optional[str] = None,
    startup_name: str = "",
    startup_description: str = "",
    db: Session = Depends(get_db)
):
    """
    Start a new LLM-powered feedback session
    - Generates 3 contextual questions about the startup meeting
    - Creates a feedback session
    - Returns first question to start the conversation
    """
    # Check if session already exists
    existing = db.query(models.FeedbackSession).filter(
        models.FeedbackSession.meetingId == meeting_id,
        models.FeedbackSession.userId == user_id,
        models.FeedbackSession.status == "in_progress"
    ).first()

    if existing:
        # Resume existing session
        questions = existing.questions
        current_idx = existing.current_question_index

        return {
            "session_id": existing.id,
            "resumed": True,
            "current_question": questions[current_idx] if current_idx < len(questions) else None,
            "progress": {
                "current": current_idx + 1,
                "total": len(questions),
                "answered": current_idx
            },
            "conversation_history": existing.conversation_history
        }

    # Generate 3 contextual questions using LLM
    questions = await feedback_assistant.generate_questions(
        startup_name=startup_name,
        startup_description=startup_description,
        meeting_context=f"Meeting ID: {meeting_id}"
    )

    # Create new feedback session
    session = models.FeedbackSession(
        meetingId=meeting_id,
        userId=user_id,
        startupId=startup_id,
        startupName=startup_name,
        questions=questions,
        answers={},
        conversation_history=[],
        current_question_index=0,
        status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate first message
    first_response = await feedback_assistant.process_conversation_turn(
        message="",
        conversation_history=[],
        current_question=questions[0],
        is_first_message=True
    )

    # Add to conversation history
    session.conversation_history.append({
        "role": "assistant",
        "content": first_response["response"],
        "timestamp": datetime.utcnow().isoformat()
    })
    db.commit()

    return {
        "session_id": session.id,
        "resumed": False,
        "message": first_response["response"],
        "current_question": questions[0],
        "progress": {
            "current": 1,
            "total": len(questions),
            "answered": 0
        }
    }

@app.post("/feedback/chat", response_model=schemas.FeedbackChatResponse)
async def chat_feedback(
    message_data: schemas.FeedbackChatMessage,
    db: Session = Depends(get_db)
):
    """
    Process a user message in the feedback chat
    - Accepts user's answer to current question
    - Moves to next question or completes session
    - Returns conversational response
    """
    session = db.query(models.FeedbackSession).filter(
        models.FeedbackSession.id == message_data.session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Feedback session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session already completed")

    # Add user message to history
    session.conversation_history.append({
        "role": "user",
        "content": message_data.message,
        "timestamp": datetime.utcnow().isoformat()
    })

    current_idx = session.current_question_index
    questions = session.questions

    # Save answer for current question
    current_question = questions[current_idx]
    session.answers[str(current_question["id"])] = {
        "question": current_question["question"],
        "answer": message_data.message,
        "category": current_question["category"]
    }

    # Process with LLM
    response_data = await feedback_assistant.process_conversation_turn(
        message=message_data.message,
        conversation_history=session.conversation_history,
        current_question=current_question,
        is_first_message=False
    )

    # Add assistant response to history
    session.conversation_history.append({
        "role": "assistant",
        "content": response_data["response"],
        "timestamp": datetime.utcnow().isoformat()
    })

    # Move to next question
    next_idx = current_idx + 1

    if next_idx >= len(questions):
        # All questions answered - complete session
        session.status = "completed"
        session.completed_at = datetime.utcnow()

        # Generate completion summary
        qa_pairs = [
            {
                **session.answers[str(q["id"])],
                "question": q["question"],
                "category": q["category"]
            }
            for q in questions
        ]

        completion_message = await feedback_assistant.generate_completion_summary(
            startup_name=session.startupName,
            qa_pairs=qa_pairs
        )

        # Create meeting insight from Q&A
        insight_data = feedback_assistant.format_insights_for_storage(
            qa_pairs=qa_pairs,
            meeting_id=session.meetingId,
            startup_id=session.startupId or "",
            startup_name=session.startupName,
            user_id=session.userId
        )

        # Save insight
        insight = models.MeetingInsight(**insight_data)
        db.add(insight)

        db.commit()

        return schemas.FeedbackChatResponse(
            response=f"{response_data['response']}\n\n{completion_message}",
            question_id=None,
            current_question=None,
            progress={
                "current": len(questions),
                "total": len(questions),
                "answered": len(questions)
            },
            session_id=session.id,
            completed=True
        )

    # Move to next question
    session.current_question_index = next_idx
    next_question = questions[next_idx]

    # Ask next question
    next_message = f"\n\n**Question {next_idx + 1} of {len(questions)}:**\n{next_question['question']}"
    combined_response = response_data["response"] + next_message

    session.conversation_history.append({
        "role": "assistant",
        "content": next_message,
        "timestamp": datetime.utcnow().isoformat()
    })

    session.last_interaction = datetime.utcnow()
    db.commit()

    return schemas.FeedbackChatResponse(
        response=combined_response,
        question_id=next_question["id"],
        current_question=next_question,
        progress={
            "current": next_idx + 1,
            "total": len(questions),
            "answered": next_idx
        },
        session_id=session.id,
        completed=False
    )

@app.get("/feedback/session/{session_id}", response_model=schemas.FeedbackSession)
async def get_feedback_session(session_id: int, db: Session = Depends(get_db)):
    """
    Get feedback session details
    - Returns full conversation history
    - Shows progress and answers
    """
    session = db.query(models.FeedbackSession).filter(
        models.FeedbackSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session

@app.put("/insights/{insight_id}/edit")
async def edit_insight(
    insight_id: int,
    updated_qa: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Edit a previously submitted insight
    - Allows updating the Q&A pairs
    - Re-generates insight text from updated answers
    """
    insight = db.query(models.MeetingInsight).filter(
        models.MeetingInsight.id == insight_id
    ).first()

    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    # Update structured Q&A
    insight.structured_qa = updated_qa

    # Regenerate insight text
    insight_text = "\n\n".join([
        f"**{qa['category'].upper()}**: {qa['question']}\n{qa['answer']}"
        for qa in updated_qa
    ])

    insight.insight = insight_text
    insight.timestamp = datetime.utcnow()  # Update timestamp

    db.commit()
    db.refresh(insight)

    return {
        "success": True,
        "insight_id": insight_id,
        "updated_at": insight.timestamp.isoformat()
    }

@app.get("/feedback/preview/{meeting_id}")
async def preview_feedback_questions(
    meeting_id: str,
    startup_name: str,
    startup_description: str
):
    """
    Preview the 3 questions that would be generated for a meeting
    - Does not create a session
    - Useful for showing users what to expect
    """
    questions = await feedback_assistant.generate_questions(
        startup_name=startup_name,
        startup_description=startup_description,
        meeting_context=None
    )

    return {
        "meeting_id": meeting_id,
        "startup_name": startup_name,
        "questions": questions,
        "total": len(questions)
    }

# ============================================
# Notification System (DISABLED - Install pywebpush first)
# ============================================

# @app.get("/notifications/pending/{user_id}")
# async def get_pending_insights(user_id: str, db: Session = Depends(get_db)):
#     """Get list of meetings that need insights"""
#     pending = await notification_service.get_pending_insights(db, user_id)
#     return {"pending": pending, "count": len(pending)}

# @app.post("/notifications/schedule")
# async def schedule_meeting_notification(...)

# Notifications will be enabled in a future update

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
