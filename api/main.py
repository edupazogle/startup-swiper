from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import timedelta, datetime
import sys
from pathlib import Path
import logging
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / ".env",
    Path(__file__).parent.parent / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✓ Main: Loaded environment from: {env_path}")
        break

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent))

import models
import models_startup
import schemas
import crud
from database import engine, get_db, SessionLocal
from llm_config import simple_llm_call_async, llm_completion
from auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from qwen_agentic_concierge import create_qwen_concierge  # Legacy Qwen Agentic
from qwen_enhanced_concierge import create_enhanced_qwen_concierge  # Enhanced with proper function calling
from qwen_agent_enhanced_concierge import create_qwen_agent_concierge  # NEW: Production Qwen-Agent with LangSmith
from insights_agent import create_insights_agent  # AI-powered insights generation
# from notification_service import NotificationService, notification_worker
from pathlib import Path
from startup_prioritization import prioritizer
from meeting_feedback_llm import feedback_assistant
from whitepaper_insights_agent import whitepaper_agent
from conversational_insights_agent import conversational_insights_agent
import db_queries
from routes_phase_endpoints import router as phase_router
from routes_topics_usecases import router as topics_router

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
    models_startup.Base.metadata.create_all(bind=engine)
    print(f"✓ Database tables created/verified at: {engine.url}")
except Exception as e:
    print(f"⚠️  Warning: Could not create database tables: {e}")
    print(f"    This may happen on first deployment. Retrying on next request...")

app = FastAPI(title="Startup Swiper API", version="1.0.0")

# CORS middleware - add FIRST before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add CORS headers to error responses
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Include Phase 1 & 2 endpoints
app.include_router(phase_router)

# Include Topics & Use Cases endpoints
app.include_router(topics_router)

# Load from DB function
def get_all_startups_from_db(db: Session, skip: int = 0, limit: int = 10000):
    """Get startups from database instead of JSON."""
    return db_queries.get_all_startups(db, skip=skip, limit=limit)

# Initialize notification service
# notification_service = NotificationService()  # Temporarily disabled - install pywebpush first

# Startup event - ensure database is initialized
@app.on_event("startup")
async def startup_event():
    """Initialize database on app startup"""
    try:
        # Ensure tables exist
        models.Base.metadata.create_all(bind=engine)
        models_startup.Base.metadata.create_all(bind=engine)
        print(f"✓ Database tables initialized/verified")
        
        # Check database status
        db = SessionLocal()
        try:
            startup_count = db.query(models_startup.Startup).count()
            print(f"✓ Database ready with {startup_count} startups")
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠️  Error during startup initialization: {e}")
        import traceback
        traceback.print_exc()

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

# Health Check Endpoint - supports both GET and HEAD for monitoring
@app.get("/health")
@app.head("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for deployment platforms and monitoring services"""
    try:
        startup_count = db_queries.count_startups(db)
    except Exception as e:
        logger.error(f"Error counting startups: {e}")
        startup_count = 0
    
    return {
        "status": "healthy",
        "service": "startup-swiper-api",
        "version": "1.0.0",
        "startups_loaded": startup_count
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
    Login with email and password to get access and refresh tokens
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

    # Create access token (30 minutes)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Create refresh token (7 days)
    refresh_token = create_refresh_token(db, user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }

@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_token(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    user = verify_refresh_token(db, token_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Revoke old refresh token
    revoke_refresh_token(db, token_data.refresh_token)
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/logout")
def logout(token_data: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """
    Logout by revoking refresh token
    """
    revoke_refresh_token(db, token_data.refresh_token)
    return {"message": "Successfully logged out"}

@app.post("/auth/logout-all")
async def logout_all(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices by revoking all refresh tokens
    """
    revoke_all_user_tokens(db, current_user.id)
    return {"message": "Successfully logged out from all devices"}

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

@app.get("/calendar-events/")
def read_calendar_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get calendar events from normalized database"""
    events = db_queries.get_calendar_events(db, skip=skip, limit=limit)
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

@app.delete("/votes/{startup_id}/{user_id}")
def delete_vote(startup_id: str, user_id: str, db: Session = Depends(get_db)):
    success = crud.delete_vote(db, startup_id=startup_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vote not found")
    return {"status": "success", "message": "Vote deleted"}

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

@app.put("/ideas/{idea_id}", response_model=schemas.Idea)
def update_idea(idea_id: int, idea: schemas.IdeaCreate, db: Session = Depends(get_db)):
    db_idea = crud.update_idea(db, idea_id=idea_id, idea=idea)
    if db_idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea

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

class LinkedInPostRequest(BaseModel):
    topic: str
    key_points: Optional[List[str]] = None
    people_companies_to_tag: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    link: Optional[str] = None


class AdvancedResearchRequest(BaseModel):
    company_name: str
    focus: Optional[str] = ''


@app.post("/concierge/ask", response_model=ConciergeResponse)
async def ask_concierge(request: ConciergeRequest, db: Session = Depends(get_db)):
    """
    Ask the AI Concierge any question about:
    - Startups (database + CB Insights)
    - Events and schedules
    - People/Attendees
    - Research and insights
    
    Uses Qwen-Agent with proper function calling, LangSmith tracing, and ChatCBI integration
    Model: qwen/qwen3-next-80b-a3b-instruct
    """
    concierge = create_qwen_agent_concierge(db)  # Production Qwen-Agent implementation
    # Use tool-enhanced answer with proper function calling
    answer = await concierge.chat(request.question)
    
    return ConciergeResponse(answer=answer, question_type="general")

@app.post("/concierge/ask-with-tools", response_model=ConciergeResponse)
async def ask_concierge_with_explicit_tools(request: ConciergeRequest, db: Session = Depends(get_db)):
    """
    Ask the AI Concierge with explicit tool support
    
    This endpoint explicitly enables:
    - Qwen model with native function calling
    - Database queries for startups and attendees
    - Tool calling for precise information retrieval
    
    Best for startup-specific questions like:
    - "Find startups in Finland with Series A funding"
    - "Which startups are in the AI space?"
    - "Show me companies founded after 2020"
    """
    concierge = create_enhanced_qwen_concierge(db)  # Enhanced version with function calling
    # Use advanced answer with tool execution
    answer = await concierge.answer_question(request.question)
    
    return ConciergeResponse(answer=answer, question_type="startup_search")

@app.post("/concierge/startup-details", response_model=ConciergeResponse)
async def get_startup_details(query: StartupQuery, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific startup
    - Uses local database
    - Enriched with CB Insights data
    """
    concierge = create_enhanced_qwen_concierge(db)  # Enhanced version with function calling
    # For startup details, build a focused question
    question = f"Get detailed information about {query.startup_name}"
    details = await concierge.answer_question(question)
    
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

@app.post("/concierge/generate-linkedin-post", response_model=ConciergeResponse)
async def generate_linkedin_post(request: LinkedInPostRequest, db: Session = Depends(get_db)):
    """
    Generate a professional LinkedIn post with VC partner persona
    
    Write compelling LinkedIn posts as a seasoned Venture Capital Founding Partner
    with expertise in AI, Blockchain, Web3, and Finance.
    
    Request body:
    {
        "topic": "The announcement of our new AI-focused investment fund",
        "key_points": [
            "Focus on AI infrastructure",
            "Series A to Series C stage startups",
            "European market emphasis"
        ],
        "people_companies_to_tag": ["@VCFirm", "@CoFounder"],
        "call_to_action": "What are your thoughts on AI investing trends?",
        "link": "https://example.com/report"
    }
    """
    concierge = create_concierge(db)
    post = await concierge.generate_linkedin_post(
        topic=request.topic,
        key_points=request.key_points,
        people_companies_to_tag=request.people_companies_to_tag,
        call_to_action=request.call_to_action,
        link=request.link
    )
    
    return ConciergeResponse(answer=post, question_type="linkedin_post")


@app.post("/concierge/advanced-research", response_model=ConciergeResponse)
async def advanced_research_chatcbi(request: AdvancedResearchRequest, db: Session = Depends(get_db)):
    """
    Perform advanced market research using CB Insights ChatCBI API
    
    **REQUIRES:** CB Insights API credentials configured in `.env`
    
    This endpoint:
    - Uses CB Insights ChatCBI for deep market intelligence
    - Consumes CB Insights API credits
    - Provides business model analysis, competitive landscape, funding trends
    - Optimizes queries using Qwen LLM for best results
    
    **Request Body:**
    ```json
    {
        "company_name": "SimplifAI",
        "focus": "funding"  // Optional: funding|competitors|technology|market
    }
    ```
    
    **Note:** Make sure CB Insights credentials are configured:
    - CBINSIGHTS_CLIENT_ID
    - CBINSIGHTS_CLIENT_SECRET
    
    in `app/startup-swipe-schedu/.env`
    """
    concierge = create_enhanced_qwen_concierge(db)
    result = await concierge.perform_advanced_research(request.company_name, request.focus)
    
    return ConciergeResponse(answer=result, question_type="advanced_research")


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
def get_all_startups(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    """
    Get all startups from database with frontend-compatible field names
    """
    startups = db_queries.get_all_startups(db, skip=skip, limit=limit)
    total = db_queries.count_startups(db)
    
    # Add aliases for frontend compatibility
    enhanced_startups = []
    for startup in startups:
        startup_dict = startup if isinstance(startup, dict) else startup.__dict__
        
        # Add frontend-expected field aliases
        if 'company_name' in startup_dict:
            startup_dict['name'] = startup_dict['company_name']
            startup_dict['Company Name'] = startup_dict['company_name']
        
        if 'company_description' in startup_dict:
            startup_dict['Company Description'] = startup_dict['company_description']
        
        if 'website' in startup_dict:
            startup_dict['URL'] = startup_dict['website']
        
        if 'shortDescription' in startup_dict:
            startup_dict['USP'] = startup_dict['shortDescription']
        
        enhanced_startups.append(startup_dict)
    
    return {
        "total": total,
        "count": len(enhanced_startups),
        "startups": enhanced_startups
    }

@app.get("/startups/prioritized")
def get_prioritized_startups(
    user_id: Optional[str] = None,
    limit: int = 100,
    min_score: float = 30.0,
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
    
    Args:
        user_id: User ID for personalization (string or int)
        limit: Maximum number of startups to return
        min_score: Minimum score threshold (filters out very low-relevance startups)
    """
    # Get all startups from DB
    all_startups = db_queries.get_all_startups(db, skip=0, limit=10000)
    
    # Get user's voting history if user_id provided
    user_votes = []
    if user_id:
        all_votes = crud.get_votes(db, skip=0, limit=1000)
        user_votes = [v for v in all_votes if str(v.userId) == str(user_id)]

    # Get prioritized list
    prioritized = prioritizer.prioritize_startups(
        all_startups,
        user_votes=[{"startupId": v.startupId, "interested": v.interested} for v in user_votes],
        limit=limit,
        min_score=min_score
    )

    return {
        "total": len(all_startups),
        "prioritized_count": len(prioritized),
        "user_id": user_id,
        "personalized": user_id is not None and len(user_votes) > 0,
        "votes_count": len(user_votes),
        "startups": prioritized
    }

@app.get("/startups/axa/filtered")
def get_axa_filtered_startups(
    limit: int = 300,
    min_score: int = 25,
    db: Session = Depends(get_db)
):
    """
    Get AXA-filtered startups directly from database.
    Returns Tier 2 startups sorted by funding.
    """
    try:
        # Query Tier 2 startups from database, ordered by funding
        startups = db.query(models_startup.Startup).filter(
            models_startup.Startup.axa_priority_tier.contains("Tier 2")
        ).order_by(
            models_startup.Startup.total_funding.desc()
        ).limit(limit).all()
        
        return {
            "total": len(startups),
            "returned": len(startups),
            "min_score": min_score,
            "source": "database",
            "processing": {
                "method": "Direct database query",
                "tier": "Tier 2: High Priority"
            },
            "startups": startups
        }
    except Exception as e:
        logger.error(f"Error in AXA filter endpoint: {e}", exc_info=True)
        return {
            "total": 0,
            "returned": 0,
            "min_score": min_score,
            "source": "error",
            "processing": {"method": "Error"},
            "startups": []
        }

@app.get("/startups/{startup_id}/insights")
def get_startup_insights(startup_id: str, db: Session = Depends(get_db)):
    """
    Get categorization and priority insights for a specific startup
    """
    # Find startup from DB
    startup = db_queries.get_startup_by_id(db, startup_id)

    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    insights = prioritizer.get_startup_insights(startup)

    return {
        "startup_id": startup_id,
        "startup_name": startup.get("company_name"),
        "insights": insights
    }

@app.post("/startups/batch-insights")
def get_batch_startup_insights(startup_ids: List[str], db: Session = Depends(get_db)):
    """
    Get insights for multiple startups at once
    """
    results = []

    for startup_id in startup_ids:
        startup = db_queries.get_startup_by_id(db, startup_id)

        if startup:
            insights = prioritizer.get_startup_insights(startup)
            results.append({
                "startup_id": startup_id,
                "startup_name": startup.get("company_name"),
                "insights": insights
            })

    return {"results": results, "count": len(results)}


@app.post("/startups/generate-ai-insights")
async def generate_ai_insights(company_name: str, db: Session = Depends(get_db)):
    """
    Generate AI-powered insights for a startup using Qwen model.
    
    This endpoint is triggered when the user clicks the "Generate AI Insights" button.
    It performs comprehensive analysis including:
    - Strategic fit with AXA
    - Technology assessment  
    - Market opportunity analysis
    - Business viability
    - Risk factors
    - Recommended next steps
    
    Uses qwen/qwen3-next-80b-a3b-instruct model with LangSmith tracing
    """
    try:
        insights_agent = create_insights_agent(db)
        result = await insights_agent.generate_insights(company_name)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Failed to generate insights")
            )
        
        return {
            "success": True,
            "company_name": company_name,
            "insights": result["insights"],
            "generated_at": result.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/startups/compare-insights")
async def compare_startup_insights(company_names: List[str], db: Session = Depends(get_db)):
    """
    Generate comparative insights for multiple startups.
    Useful for tier-based evaluation and ranking.
    """
    try:
        insights_agent = create_insights_agent(db)
        result = await insights_agent.generate_comparative_insights(company_names)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate comparative insights"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comparative insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Enriched Data Endpoints
# ============================================

@app.get("/startups/enriched/search")
def search_enriched_startups(
    query: str = "",
    enrichment_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search enriched startups
    - enrichment_type: 'emails', 'social', 'tech_stack', 'team'
    """
    # Get enriched startups from DB
    enriched_startups = db_queries.get_enriched_startups(db, limit=1000)
    
    results = []
    
    for startup in enriched_startups:
        # Filter by name/description match
        if query and query.lower() not in startup.get('company_name', '').lower():
            continue
        
        # Parse enrichment JSON if string
        enrichment = startup.get('enrichment')
        if isinstance(enrichment, str):
            enrichment = json.loads(enrichment) if enrichment else {}
        elif enrichment is None:
            enrichment = {}
        
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
            "name": startup.get('company_name'),
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
def get_startup_enrichment(startup_id: str, db: Session = Depends(get_db)):
    """
    Get enrichment data for a specific startup
    """
    startup = db_queries.get_startup_by_id(db, startup_id)
    
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    if not startup.get('is_enriched'):
        raise HTTPException(
            status_code=404,
            detail="Startup enrichment not available"
        )
    
    # Parse enrichment JSON if string
    enrichment = startup.get('enrichment')
    if isinstance(enrichment, str):
        enrichment = json.loads(enrichment) if enrichment else {}
    elif enrichment is None:
        enrichment = {}
    
    return {
        "startup_id": startup.get('id'),
        "startup_name": startup.get('company_name'),
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
def get_enrichment_stats(db: Session = Depends(get_db)):
    """
    Get enrichment statistics
    """
    stats = db_queries.get_enrichment_stats(db)
    
    return stats

@app.post("/startups/enrichment/by-name")
async def get_startups_by_enriched_field(
    field_name: str = None,
    field_value: str = None,
    limit: int = 20,
    db: Session = Depends(get_db),
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
    
    # Query enriched startups from database
    enriched = db_queries.get_enriched_startups(db, limit=1000)
    
    results = []
    field_value_lower = field_value.lower()
    
    for startup in enriched:
        enrichment_json = startup.get('enrichment', '{}')
        if isinstance(enrichment_json, str):
            try:
                enrichment = json.loads(enrichment_json)
            except (json.JSONDecodeError, TypeError):
                enrichment = {}
        else:
            enrichment = enrichment_json
        
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
                "name": startup.get('company_name'),
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

@app.get("/insights/as-ideas")
async def get_insights_as_ideas(db: Session = Depends(get_db)):
    """
    Get all meeting insights formatted as Idea objects for the Insights page
    - Converts meeting_insights to category '10' (Startups) ideas
    - Compatible with InsightsView component
    """
    insights = db.query(models.MeetingInsight).all()
    
    ideas = []
    for insight in insights:
        # Convert meeting insight to Idea format
        idea = {
            "id": f"insight_{insight.id}",
            "name": insight.startupName,
            "title": f"Meeting with {insight.startupName}",
            "category": "10",  # Category 10: Startups
            "description": insight.insight or "",
            "tags": insight.tags or [],
            "timestamp": int(insight.timestamp.timestamp() * 1000) if insight.timestamp else 0,
            "rating": insight.rating,
            "meetingId": insight.meetingId,
            "userId": insight.userId
        }
        ideas.append(idea)
    
    return ideas

@app.get("/insights/categorized/all")
async def get_all_categorized_insights(db: Session = Depends(get_db)):
    """
    Get all categorized insights grouped by category
    Perfect for populating all 10 whitepaper sections at once
    """
    insights = db.query(models.CategorizedInsight).order_by(
        models.CategorizedInsight.created_at.desc()
    ).all()
    
    # Group by category
    by_category = {}
    for i in range(1, 11):
        by_category[str(i)] = []
    
    for insight in insights:
        if insight.category in by_category:
            by_category[insight.category].append({
                "id": f"insight_{insight.id}",
                "name": insight.startup_name,
                "title": insight.title,
                "category": insight.category,
                "description": insight.insight,  # Use 'insight' field as description
                "tags": insight.tags or [],
                "timestamp": int(insight.created_at.timestamp() * 1000),
                "confidence": insight.confidence_score,
                "meetingId": insight.meeting_id,
                "userName": insight.user_name,
                "userEmail": insight.user_email,
                "insuranceRelevance": insight.insurance_relevance,
                "metrics": insight.metrics or [],
                "isEdited": insight.is_edited,
                "evidenceSource": insight.evidence_source
            })
    
    return by_category

@app.get("/insights/categorized/category/{category_id}")
async def get_insights_by_category(
    category_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get insights for a specific category
    Returns in Idea format compatible with InsightsView
    """
    if category_id not in [str(i) for i in range(1, 11)]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be 1-10")
    
    insights = db.query(models.CategorizedInsight).filter(
        models.CategorizedInsight.category == category_id
    ).order_by(
        models.CategorizedInsight.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    ideas = []
    for insight in insights:
        idea = {
            "id": f"insight_{insight.id}",
            "name": insight.startup_name,
            "title": insight.title,
            "category": insight.category,
            "description": insight.insight,
            "tags": insight.tags or [],
            "timestamp": int(insight.created_at.timestamp() * 1000),
            "confidence": insight.confidence_score,
            "meetingId": insight.meeting_id,
            "userName": insight.user_name,
            "userEmail": insight.user_email,
            "insuranceRelevance": insight.insurance_relevance,
            "metrics": insight.metrics or [],
            "isEdited": insight.is_edited
        }
        ideas.append(idea)
    
    return ideas

@app.put("/insights/categorized/{insight_id}/edit")
async def edit_categorized_insight(
    insight_id: int,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Edit a categorized insight
    - Update title, insight text, tags, category
    - Track edit history
    """
    insight = db.query(models.CategorizedInsight).filter_by(id=insight_id).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    # Save original on first edit
    if not insight.is_edited:
        insight.original_insight = insight.insight
        insight.is_edited = True
    
    # Update fields
    if 'title' in update_data:
        insight.title = update_data['title']
    if 'insight' in update_data:
        insight.insight = update_data['insight']
    if 'category' in update_data:
        if update_data['category'] in [str(i) for i in range(1, 11)]:
            insight.category = update_data['category']
    if 'tags' in update_data:
        insight.tags = update_data['tags']
    if 'insurance_relevance' in update_data:
        insight.insurance_relevance = update_data['insurance_relevance']
    
    insight.edited_at = datetime.utcnow()
    insight.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(insight)
    
    return {
        "id": insight.id,
        "title": insight.title,
        "insight": insight.insight,
        "category": insight.category,
        "is_edited": insight.is_edited,
        "edited_at": insight.edited_at,
        "message": "Insight updated successfully"
    }

@app.delete("/insights/categorized/{insight_id}")
async def delete_categorized_insight(
    insight_id: int,
    db: Session = Depends(get_db)
):
    """Delete a categorized insight"""
    insight = db.query(models.CategorizedInsight).filter_by(id=insight_id).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    db.delete(insight)
    db.commit()
    
    return {"message": "Insight deleted successfully", "id": insight_id}

@app.post("/insights/categorized/{insight_id}/move")
async def move_insight_category(
    insight_id: int,
    new_category: str,
    db: Session = Depends(get_db)
):
    """Move insight to a different category"""
    if new_category not in [str(i) for i in range(1, 11)]:
        raise HTTPException(status_code=400, detail="Invalid category. Must be 1-10")
    
    insight = db.query(models.CategorizedInsight).filter_by(id=insight_id).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    old_category = insight.category
    insight.category = new_category
    insight.is_edited = True
    insight.edited_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": f"Insight moved from Category {old_category} to {new_category}",
        "old_category": old_category,
        "new_category": new_category,
        "id": insight_id
    }

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
    
    # Update answers dict - need to replace the whole dict for SQLAlchemy to track changes
    answers_copy = dict(session.answers) if session.answers else {}
    answers_copy[str(current_question["id"])] = {
        "question": current_question["question"],
        "answer": message_data.message,
        "category": current_question["category"]
    }
    session.answers = answers_copy
    
    # Mark as modified for SQLAlchemy
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(session, "answers")

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
        qa_pairs = []
        for q in questions:
            q_id = str(q["id"])
            if q_id in session.answers:
                qa_pairs.append({
                    **session.answers[q_id],
                    "question": q["question"],
                    "category": q["category"]
                })
        
        completion_message = await feedback_assistant.generate_completion_summary(
            startup_name=session.startupName,
            qa_pairs=qa_pairs
        )

        # Create meeting insight from Q&A (legacy format)
        insight_data = feedback_assistant.format_insights_for_storage(
            qa_pairs=qa_pairs,
            meeting_id=session.meetingId,
            startup_id=session.startupId or "",
            startup_name=session.startupName,
            user_id=session.userId
        )

        # Save legacy insight
        insight = models.MeetingInsight(**insight_data)
        db.add(insight)
        
        # NEW: Categorize insights using LLM
        try:
            # Get startup data from database
            startup = db.query(models_startup.Startup).filter(
                models_startup.Startup.id == session.startupId
            ).first()
            
            startup_data = {
                "name": session.startupName,
                "description": session.startupDescription or "",
                "category": getattr(startup, 'category', 'N/A') if startup else 'N/A',
                "funding": getattr(startup, 'total_funding', 'Undisclosed') if startup else 'Undisclosed',
                "tech": getattr(startup, 'tech', []) if startup else [],
                "maturity": getattr(startup, 'maturity', 'Unknown') if startup else 'Unknown'
            }
            
            # TODO: Get AXA evaluation if exists (placeholder for now)
            axa_evaluation = {
                "priority_score": 75,
                "technical_score": 80,
                "business_fit": "High",
                "innovation_level": "Medium"
            }
            
            # User info for attribution
            user_info = {
                "id": session.userId,
                "name": session.userId.split('@')[0].replace('.', ' ').title(),  # Extract name from email
                "email": session.userId
            }
            
            # Analyze and categorize insights
            categorized = await feedback_assistant.analyze_and_categorize_insights(
                qa_pairs=qa_pairs,
                startup_data=startup_data,
                axa_evaluation=axa_evaluation,
                user_info=user_info
            )
            
            # Save categorized insights to database
            insights_created = 0
            categories_populated = []
            
            for category, insights_list in categorized.items():
                if insights_list:
                    categories_populated.append(category)
                    
                for insight_item in insights_list:
                    categorized_insight = models.CategorizedInsight(
                        meeting_id=session.meetingId,
                        startup_id=session.startupId or "",
                        startup_name=session.startupName,
                        user_id=user_info['id'],
                        user_name=user_info['name'],
                        user_email=user_info['email'],
                        category=category,
                        title=insight_item.get('title', ''),
                        insight=insight_item.get('insight', ''),
                        insurance_relevance=insight_item.get('insurance_relevance', 'general'),
                        metrics=insight_item.get('metrics', []),
                        tags=insight_item.get('tags', []),
                        confidence_score=insight_item.get('confidence', 0.8),
                        evidence_source=insight_item.get('evidence_source', ''),
                        feedback_session_id=session.id
                    )
                    db.add(categorized_insight)
                    insights_created += 1
            
            print(f"✓ Created {insights_created} categorized insights across {len(categories_populated)} categories")
            
        except Exception as e:
            print(f"⚠️  Error creating categorized insights: {e}")
            # Continue anyway - legacy insight was created
            insights_created = 0
            categories_populated = []

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
            completed=True,
            insights_created=insights_created,
            categories_populated=categories_populated
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

# ============================================
# Whitepaper Insights Agent Endpoints
# ============================================

@app.get("/whitepaper/meeting-prep/load")
def load_existing_outline(
    startup_id: str,
    startup_name: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Load existing meeting prep outline if it exists.
    Tries multiple matching strategies to find the outline.
    """
    try:
        from models import MeetingPrepOutline
        
        # Try exact startup_id match first
        outline = db.query(MeetingPrepOutline).filter(
            MeetingPrepOutline.startup_id == startup_id,
            MeetingPrepOutline.user_id == user_id
        ).order_by(MeetingPrepOutline.updated_at.desc()).first()
        
        # If not found, try by startup name (more flexible)
        if not outline:
            outline = db.query(MeetingPrepOutline).filter(
                MeetingPrepOutline.startup_name.ilike(startup_name),
                MeetingPrepOutline.user_id == user_id
            ).order_by(MeetingPrepOutline.updated_at.desc()).first()
        
        if outline:
            return {
                "success": True,
                "found": True,
                "outline": outline.outline,
                "talking_points": outline.talking_points,
                "critical_questions": outline.critical_questions,
                "generated_at": outline.generated_at.isoformat() if outline.generated_at else None
            }
        else:
            return {
                "success": True,
                "found": False
            }
    except Exception as e:
        print(f"Error loading outline: {e}")
        return {
            "success": False,
            "found": False,
            "error": str(e)
        }


@app.post("/whitepaper/meeting-prep/start")
async def start_whitepaper_meeting_prep(
    user_id: str,
    startup_id: str,
    startup_name: str,
    startup_description: str,
    db: Session = Depends(get_db)
):
    """
    Start whitepaper preparation session for meeting with startup
    Generates initial outline with talking points and questions
    """
    try:
        # Try to get startup data from database
        startup = None
        try:
            startup = db.query(models_startup.Startup).filter(
                models_startup.Startup.id == startup_id
            ).first()
        except:
            startup = db.query(models_startup.Startup).filter(
                models_startup.Startup.name == startup_name
            ).first()
        
        # Build startup data
        if startup:
            startup_data = {
                "name": startup_name,
                "description": startup_description or getattr(startup, 'Company Description', ''),
                "category": getattr(startup, 'Category', getattr(startup, 'category', '')),
                "technologies": [],
                "total_funding": getattr(startup, 'Funding', getattr(startup, 'total_funding', 0)),
                "stage": getattr(startup, 'Stage', getattr(startup, 'stage', 'Unknown'))
            }
            try:
                topics = getattr(startup, 'topics', [])
                if topics and isinstance(topics, (list, tuple)):
                    startup_data["technologies"] = [str(t) for t in topics[:5]]
                else:
                    startup_data["technologies"] = []
            except Exception as e:
                print(f"Error extracting topics: {e}")
                startup_data["technologies"] = []
        else:
            startup_data = {
                "name": startup_name,
                "description": startup_description,
                "category": "AI/Enterprise",
                "technologies": [],
                "total_funding": 0,
                "stage": "Unknown"
            }
        
        # Generate initial meeting prep outline
        initial_outline = await whitepaper_agent.generate_initial_outline(
            startup_name=startup_name,
            startup_description=startup_description,
            startup_data=startup_data
        )
        
        # Save outline to database
        try:
            from models import MeetingPrepOutline
            
            meeting_prep = MeetingPrepOutline(
                startup_id=startup_id,
                startup_name=startup_name,
                user_id=user_id,
                outline=initial_outline,
                talking_points=[],  # Could parse these from outline if needed
                critical_questions=[],  # Could parse these from outline if needed
                whitepaper_relevance={}
            )
            db.add(meeting_prep)
            db.commit()
        except Exception as e:
            print(f"Warning: Could not save outline to database: {e}")
            # Don't fail if saving fails, just log it
        
        return {
            "success": True,
            "session_id": f"prep_{startup_id}_{user_id}_{datetime.utcnow().timestamp()}",
            "startup_name": startup_name,
            "outline": initial_outline,
            "message": f"✓ Meeting prep outline generated for {startup_name}\n\nReview the talking points and questions below. Provide feedback or observations to refine the outline further."
        }
        
    except Exception as e:
        print(f"Error starting whitepaper prep: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/whitepaper/meeting-prep/chat")
async def whitepaper_meeting_prep_chat(
    session_id: str,
    message: str,
    startup_name: str,
    startup_description: str,
    previous_outline: str,
    db: Session = Depends(get_db)
):
    """
    Process analyst feedback and adapt the outline
    """
    try:
        # Get startup data for context
        startup = None
        try:
            startup = db.query(models_startup.Startup).filter(
                models_startup.Startup.name == startup_name
            ).first()
        except:
            pass
        
        startup_data = {
            "name": startup_name,
            "description": startup_description,
            "category": getattr(startup, 'Category', 'AI/Enterprise') if startup else 'AI/Enterprise',
            "technologies": [],
            "total_funding": getattr(startup, 'Funding', 0) if startup else 0,
            "stage": getattr(startup, 'Stage', 'Unknown') if startup else 'Unknown'
        }

        # Generate adapted outline based on feedback
        adapted_outline = await whitepaper_agent.generate_adapted_outline(
            startup_name=startup_name,
            startup_description=startup_description,
            startup_data=startup_data,
            previous_outline=previous_outline,
            user_feedback=message
        )
        
        return {
            "success": True,
            "outline": adapted_outline,
            "message": f"✓ Outline updated based on your feedback\n\nThe talking points and questions have been refined to focus on your insights."
        }
        
    except Exception as e:
        print(f"Error in whitepaper prep chat: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# Conversational Insights Agent Request Models
# ============================================

class InsightsSessionStartRequest(BaseModel):
    user_id: str
    startup_id: str
    startup_name: str
    startup_description: str = ""

class DebriefStartRequest(BaseModel):
    user_id: str
    startup_id: str
    startup_name: str
    meeting_prep_outline: str = ""

class DebriefChatRequest(BaseModel):
    session_id: str
    user_message: str
    startup_name: str
    meeting_prep_outline: str
    conversation_history: List[Dict[str, str]] = []

class DebriefGenerateQuestionsRequest(BaseModel):
    session_id: str
    startup_name: str
    meeting_prep_outline: str
    conversation_history: List[Dict[str, str]]

class DebriefCompleteRequest(BaseModel):
    session_id: str
    startup_id: str
    startup_name: str
    user_id: str
    meeting_prep_outline: str
    conversation_history: List[Dict[str, str]]
    ratings: Dict[int, int]  # {question_index: rating_1_to_5}
    final_notes: str = ""


# ============================================
# Conversational Insights Agent Endpoints
# ============================================

@app.post("/insights/session/start")
async def start_insights_session(
    request: InsightsSessionStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new insights session for a startup meeting.
    Returns a session ID that can be used for subsequent interactions.
    """
    try:
        # Generate unique session ID
        session_id = f"insights_{request.startup_id}_{request.user_id}_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"✓ Started insights session: {session_id} for {request.startup_name}")
        
        return {
            "success": True,
            "session_id": session_id,
            "startup_id": request.startup_id,
            "startup_name": request.startup_name,
            "user_id": request.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting insights session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start insights session: {str(e)}"
        )

@app.post("/insights/debrief/start")
async def start_meeting_debrief(
    request: DebriefStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a casual debrief conversation about the meeting
    Returns initial greeting
    """
    try:
        greeting = await conversational_insights_agent.start_debrief(
            startup_name=request.startup_name,
            meeting_prep_outline=request.meeting_prep_outline
        )
        
        return {
            "success": True,
            "session_id": f"debrief_{request.startup_id}_{request.user_id}_{datetime.utcnow().timestamp()}",
            "startup_name": request.startup_name,
            "message": greeting,
            "conversation": []
        }
        
    except Exception as e:
        print(f"Error starting debrief: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start debrief: {str(e)}"
        )


@app.post("/insights/debrief/chat")
async def debrief_conversation(
    request: DebriefChatRequest,
    db: Session = Depends(get_db)
):
    """
    Process analyst message and generate conversational follow-up
    """
    try:
        # Generate natural follow-up response
        response = await conversational_insights_agent.generate_follow_up(
            conversation_history=request.conversation_history,
            startup_name=request.startup_name,
            meeting_prep_outline=request.meeting_prep_outline,
            last_user_message=request.user_message
        )
        
        return {
            "success": True,
            "message": response,
            "session_id": request.session_id
        }
        
    except Exception as e:
        print(f"Error in debrief chat: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/insights/debrief/generate-questions")
async def generate_debrief_questions(
    request: DebriefGenerateQuestionsRequest,
    db: Session = Depends(get_db)
):
    """
    Generate exactly 3 questions after initial conversation
    """
    try:
        questions = await conversational_insights_agent.generate_three_questions(
            conversation_history=request.conversation_history,
            startup_name=request.startup_name,
            meeting_prep_outline=request.meeting_prep_outline
        )
        
        return {
            "success": True,
            "session_id": request.session_id,
            "questions": questions
        }
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/insights/debrief/complete")
async def complete_debrief(
    request: DebriefCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete debrief with analyst ratings and feedback.
    SAVES DEBRIEF DATA FIRST, then extracts insights asynchronously.
    If insights extraction fails, the debrief data is already safely stored and can be regenerated.
    """
    try:
        from models import DebriefSession, CategorizedInsight
        
        print(f"[DebreefComplete] Starting debrief for {request.startup_name}")
        print(f"[DebreefComplete] User: {request.user_id}, Startup ID: {request.startup_id}")
        print(f"[DebreefComplete] Messages count: {len(request.conversation_history)}")
        
        # STEP 1: Save debrief session to database FIRST (this is critical)
        # This ensures we don't lose the conversation data even if insights extraction fails
        debrief_session = DebriefSession(
            session_id=request.session_id,
            startup_id=request.startup_id,
            startup_name=request.startup_name,
            user_id=request.user_id,
            conversation_history=request.conversation_history,
            ratings=request.ratings,
            final_notes=request.final_notes,
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(debrief_session)
        db.flush()  # Flush to get debrief_session.id
        db.commit()
        
        print(f"[DebreefComplete] ✓ Debrief session saved successfully")
        
        # STEP 2: Extract insights (this can fail without losing the debrief data)
        saved_count = 0
        insights_extraction_success = False
        insights_data = {"insights": [], "success": False}
        
        try:
            insights_data = await conversational_insights_agent.extract_insights_from_conversation(
                startup_name=request.startup_name,
                conversation_history=request.conversation_history,
                meeting_prep_outline=request.meeting_prep_outline
            )
            
            print(f"[DebreefComplete] Extraction result: {insights_data}")
            
            # Save extracted insights to CategorizedInsight table
            insights_list = insights_data.get("insights", [])
            print(f"[DebreefComplete] Insights list type: {type(insights_list)}, length: {len(insights_list) if isinstance(insights_list, list) else 'N/A'}")
            
            if isinstance(insights_list, list) and len(insights_list) > 0:
                for i, insight in enumerate(insights_list):
                    try:
                        print(f"[DebreefComplete] Processing insight {i+1}: {insight}")
                        categorized_insight = CategorizedInsight(
                            meeting_id=request.session_id,
                            startup_id=request.startup_id,
                            startup_name=request.startup_name,
                            user_id=request.user_id,
                            user_name=request.user_id.split('@')[0] if '@' in request.user_id else request.user_id,
                            user_email=request.user_id,
                            category=str(insight.get("section", "")),
                            title=insight.get("title", ""),
                            insight=insight.get("insight", ""),
                            insurance_relevance=insight.get("insurance_relevance", ""),
                            metrics=insight.get("metrics", []),
                            tags=insight.get("tags", []),
                            confidence_score=float(insight.get("confidence_score", 0.8)),
                            evidence_source=insight.get("evidence_source", "")
                        )
                        db.add(categorized_insight)
                        saved_count += 1
                    except Exception as e:
                        print(f"[DebreefComplete] Error saving insight {i+1}: {e}")
            
            db.commit()
            insights_extraction_success = True
            print(f"[DebreefComplete] ✓ Saved {saved_count} insights to database")
            
        except Exception as e:
            print(f"[DebreefComplete] ⚠️ Insights extraction failed: {e}")
            print(f"[DebreefComplete] BUT debrief data is safely stored! Insights can be regenerated later.")
            import traceback
            traceback.print_exc()
        
        # STEP 3: Return success - debrief is saved regardless of insights extraction
        return {
            "success": True,
            "session_id": request.session_id,
            "startup_name": request.startup_name,
            "insights_saved": saved_count,
            "insights_extraction_success": insights_extraction_success,
            "insights": insights_data.get("insights", []),
            "message": f"✓ Debrief completed and saved! {saved_count} insights extracted." if insights_extraction_success else f"✓ Debrief saved! {saved_count} insights extracted. (Insights can be regenerated if needed)"
        }
        
    except Exception as e:
        print(f"[DebreefComplete] Error completing debrief: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/insights/debrief/regenerate-insights")
async def regenerate_insights(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Regenerate insights for an existing debrief session.
    Used when initial insights extraction failed.
    Retrieves the debrief from database and re-runs insights extraction.
    """
    try:
        from models import DebriefSession, CategorizedInsight
        
        session_id = request.get("session_id")
        if not session_id:
            return {"success": False, "error": "session_id is required"}
        
        print(f"[RegenerateInsights] Regenerating insights for session: {session_id}")
        
        # Get the existing debrief session
        debrief = db.query(DebriefSession).filter_by(session_id=session_id).first()
        if not debrief:
            return {"success": False, "error": f"Debrief session {session_id} not found"}
        
        print(f"[RegenerateInsights] Found debrief: {debrief.startup_name}")
        
        # Delete any previous insights for this session
        db.query(CategorizedInsight).filter_by(meeting_id=session_id).delete()
        db.commit()
        print(f"[RegenerateInsights] Cleared previous insights")
        
        # Extract insights again
        insights_data = await conversational_insights_agent.extract_insights_from_conversation(
            startup_name=debrief.startup_name,
            conversation_history=debrief.conversation_history,
            meeting_prep_outline=request.get("meeting_prep_outline", "")
        )
        
        print(f"[RegenerateInsights] Extraction result: {insights_data}")
        
        saved_count = 0
        insights_list = insights_data.get("insights", [])
        
        if isinstance(insights_list, list) and len(insights_list) > 0:
            for i, insight in enumerate(insights_list):
                try:
                    print(f"[RegenerateInsights] Processing insight {i+1}: {insight}")
                    categorized_insight = CategorizedInsight(
                        meeting_id=debrief.session_id,
                        startup_id=debrief.startup_id,
                        startup_name=debrief.startup_name,
                        user_id=debrief.user_id,
                        user_name=debrief.user_id.split('@')[0] if '@' in debrief.user_id else debrief.user_id,
                        user_email=debrief.user_id,
                        category=str(insight.get("section", "")),
                        title=insight.get("title", ""),
                        insight=insight.get("insight", ""),
                        insurance_relevance=insight.get("insurance_relevance", ""),
                        metrics=insight.get("metrics", []),
                        tags=insight.get("tags", []),
                        confidence_score=float(insight.get("confidence_score", 0.8)),
                        evidence_source=insight.get("evidence_source", "")
                    )
                    db.add(categorized_insight)
                    saved_count += 1
                except Exception as e:
                    print(f"[RegenerateInsights] Error saving insight {i+1}: {e}")
        
        db.commit()
        print(f"[RegenerateInsights] ✓ Saved {saved_count} insights to database")
        
        return {
            "success": True,
            "session_id": session_id,
            "startup_name": debrief.startup_name,
            "insights_saved": saved_count,
            "insights": insights_data.get("insights", []),
            "message": f"✓ Successfully regenerated {saved_count} insights"
        }
        
    except Exception as e:
        print(f"[RegenerateInsights] Error regenerating insights: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# Utility Endpoints for Normalized DB
# ============================================

@app.get("/api/current-user")
def get_current_user_api(db: Session = Depends(get_db)):
    """Get current active user ID"""
    user_id = db_queries.get_current_user(db)
    return {"user_id": user_id}

@app.post("/api/current-user")
def set_current_user_api(user_id: str, db: Session = Depends(get_db)):
    """Set current active user ID"""
    db_queries.set_current_user(db, user_id)
    return {"user_id": user_id, "status": "updated"}

@app.get("/api/data-version")
def get_data_version_api(db: Session = Depends(get_db)):
    """Get current data version"""
    version = db_queries.get_data_version(db)
    return {"version": version}

@app.get("/api/finished-users")
def get_finished_users_api(db: Session = Depends(get_db)):
    """Get list of users who completed swiper"""
    users = db_queries.get_finished_users(db)
    return {"finished_users": users, "count": len(users)}

@app.post("/api/finished-users")
def add_finished_user_api(user_id: str, db: Session = Depends(get_db)):
    """Mark user as finished"""
    db_queries.add_finished_user(db, user_id)
    return {"user_id": user_id, "status": "marked_finished"}

@app.get("/api/auroral-themes")
def get_auroral_themes_api(db: Session = Depends(get_db)):
    """Get auroral theme configuration with colors"""
    themes = db_queries.get_auroral_themes(db)
    return themes

@app.get("/api/calendar-events/date-range")
def get_events_by_date_api(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get calendar events in date range (ISO format)"""
    events = db_queries.get_events_by_date_range(db, start_date, end_date)
    return {"events": events, "count": len(events)}

@app.get("/api/ratings/average")
def get_average_ratings_api(limit: int = 100, db: Session = Depends(get_db)):
    """Get average ratings per startup"""
    ratings = db_queries.get_average_ratings(db, limit=limit)
    return {"ratings": ratings, "count": len(ratings)}

@app.post("/api/ratings")
def add_rating_api(
    startup_id: str,
    user_id: str,
    rating: int,
    db: Session = Depends(get_db)
):
    """Add or update startup rating (1-5)"""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    db_queries.add_startup_rating(db, startup_id, user_id, rating)
    return {"startup_id": startup_id, "user_id": user_id, "rating": rating, "status": "saved"}

@app.get("/api/messages/ai-assistant")
def get_ai_assistant_messages_api(limit: int = 100, db: Session = Depends(get_db)):
    """Get AI assistant chat messages"""
    messages = db_queries.get_ai_assistant_messages(db, limit=limit)
    return {"messages": messages, "count": len(messages)}

# Slush Events API endpoints
@app.get("/api/slush-events", response_model=List[schemas.SlushEvent])
def get_slush_events_api(
    skip: int = 0,
    limit: int = 100,
    organizer: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get Slush events with optional filtering
    
    - **skip**: Number of events to skip (for pagination)
    - **limit**: Maximum number of events to return
    - **organizer**: Filter by organizer name (partial match)
    """
    if organizer:
        events = crud.get_slush_events_by_organizer(db, organizer)
        # Apply pagination to filtered results
        return events[skip:skip + limit]
    else:
        return crud.get_slush_events(db, skip=skip, limit=limit)

@app.get("/api/slush-events/{event_id}", response_model=schemas.SlushEvent)
def get_slush_event_api(event_id: int, db: Session = Depends(get_db)):
    """Get a specific Slush event by ID"""
    event = crud.get_slush_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.get("/api/slush-events/stats/summary")
def get_slush_events_stats(db: Session = Depends(get_db)):
    """Get statistics about Slush events"""
    from sqlalchemy import func
    
    total_events = db.query(func.count(models.SlushEvent.id)).scalar()
    
    # Top organizers
    top_organizers = db.query(
        models.SlushEvent.organizer,
        func.count(models.SlushEvent.id).label('count')
    ).group_by(models.SlushEvent.organizer).order_by(func.count(models.SlushEvent.id).desc()).limit(10).all()
    
    # Events by status (flatten JSON arrays)
    events_with_status = db.query(models.SlushEvent.status).filter(models.SlushEvent.status.isnot(None)).all()
    status_counts = {}
    for (status_json,) in events_with_status:
        if status_json:
            for status in status_json:
                status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_events": total_events,
        "top_organizers": [{"organizer": org, "count": count} for org, count in top_organizers],
        "status_counts": status_counts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
