from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)  # Changed from startTime
    end_time = Column(DateTime, nullable=False)    # Changed from endTime
    type = Column(String, nullable=False)
    attendees = Column(JSON)
    is_saved = Column(Boolean, default=False)       # Changed from isSaved
    link = Column(String)
    stage = Column(String)
    category = Column(String)
    highlight = Column(String)

class LinkedInChatMessage(Base):
    __tablename__ = "linkedin_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admin_user"
    
    id = Column(Integer, primary_key=True, default=1)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    startupId = Column(String, name="startup_id", nullable=False, index=True)
    userId = Column(String, name="user_id", nullable=False)
    userName = Column(String, name="user_name", nullable=False)
    interested = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meetingScheduled = Column(Boolean, name="meeting_scheduled", default=False)

class AuroralInfo(Base):
    __tablename__ = "auroral_info"
    
    id = Column(Integer, primary_key=True, default=1)
    intensity = Column(Integer, default=5)
    speed = Column(Integer, default=3)
    colors = Column(JSON)

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class StartupRating(Base):
    __tablename__ = "startup_ratings"
    
    startupId = Column(String, primary_key=True, index=True)
    averageRating = Column(Integer, default=0)
    totalRatings = Column(Integer, default=0)
    ratings = Column(JSON)
    feedback = Column(JSON)
    lastUpdated = Column(DateTime, default=datetime.utcnow)
    trendingScore = Column(Integer, default=0)

class FinishedUser(Base):
    __tablename__ = "finished_users"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, unique=True, nullable=False)
    finishedAt = Column(DateTime, default=datetime.utcnow)

class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserEvent(Base):
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    eventType = Column(String, nullable=False)
    data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AIAssistantMessage(Base):
    __tablename__ = "ai_assistant_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CurrentUserId(Base):
    __tablename__ = "current_user_id"
    
    id = Column(Integer, primary_key=True, default=1)
    userId = Column(Integer, nullable=False)

class DataVersion(Base):
    __tablename__ = "data_version"
    
    id = Column(Integer, primary_key=True, default=1)
    version = Column(String, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow)

class MeetingInsight(Base):
    __tablename__ = "meeting_insights"

    id = Column(Integer, primary_key=True, index=True)
    meetingId = Column(String, nullable=False, index=True)  # References calendar_events.id
    userId = Column(String, nullable=False, index=True)
    startupId = Column(String, nullable=True)
    startupName = Column(String, nullable=True)
    insight = Column(Text, nullable=False)
    tags = Column(JSON)  # Array of insight tags/categories
    rating = Column(Integer, nullable=True)  # Optional rating 1-5
    followUp = Column(Boolean, default=False)  # Whether user wants to follow up
    structured_qa = Column(JSON, nullable=True)  # Structured Q&A pairs for editing
    timestamp = Column(DateTime, default=datetime.utcnow)

class FeedbackSession(Base):
    __tablename__ = "feedback_sessions"

    id = Column(Integer, primary_key=True, index=True)
    meetingId = Column(String, nullable=False, index=True)
    userId = Column(String, nullable=False, index=True)
    startupId = Column(String, nullable=True)
    startupName = Column(String, nullable=False)
    questions = Column(JSON, nullable=False)  # Generated questions
    answers = Column(JSON, default={})  # User answers
    conversation_history = Column(JSON, default=[])  # Chat history
    current_question_index = Column(Integer, default=0)
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    
class NotificationQueue(Base):
    __tablename__ = "notification_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, nullable=False, index=True)
    meetingId = Column(String, nullable=False, index=True)
    meetingEndTime = Column(DateTime, nullable=False)
    scheduledFor = Column(DateTime, nullable=False)  # 5 minutes after meeting end
    sent = Column(Boolean, default=False)
    sentAt = Column(DateTime, nullable=True)
    dismissed = Column(Boolean, default=False)
    insightSubmitted = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String, nullable=False, index=True)
    endpoint = Column(String, nullable=False, unique=True)
    p256dh = Column(String, nullable=False)  # Encryption key
    auth = Column(String, nullable=False)  # Authentication secret
    userAgent = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    lastUsed = Column(DateTime, default=datetime.utcnow)

class Attendee(Base):
    __tablename__ = "attendees"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    country = Column(String, nullable=True, index=True)
    city = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    twitter = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    industry = Column(JSON, nullable=True)  # Array of industries
    occupation = Column(JSON, nullable=True)  # Array of occupations
    company_name = Column(String, nullable=True, index=True)
    company_type = Column(String, nullable=True)
    company_country = Column(String, nullable=True)
    company_city = Column(String, nullable=True)
    website = Column(String, nullable=True)
    company_linkedin = Column(String, nullable=True)
    company_description = Column(Text, nullable=True)
    profile_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CategorizedInsight(Base):
    """
    Whitepaper-ready insights extracted from meeting feedback.
    Each insight is 1-2 phrases, insurance-focused, and categorized into one of 10 whitepaper sections.
    """
    __tablename__ = "categorized_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Meeting context
    meeting_id = Column(String, index=True)
    startup_id = Column(String, index=True)
    startup_name = Column(String)
    
    # Contributor info (for avatar display)
    user_id = Column(String, index=True)
    user_name = Column(String)
    user_email = Column(String)  # To get avatar from email hash
    
    # Category and content
    category = Column(String, index=True)  # "1" through "10"
    title = Column(String)  # Brief title (5-8 words)
    insight = Column(Text)  # The 1-2 phrase insight (30-80 words)
    
    # Insurance context
    insurance_relevance = Column(String)  # claims, underwriting, customer-service, etc
    metrics = Column(JSON)  # List of quantified metrics mentioned
    
    # Metadata
    tags = Column(JSON)  # List of tags
    confidence_score = Column(Float, default=0.8)
    evidence_source = Column(String)  # Which Q&A this came from
    
    # Editability tracking
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    original_insight = Column(Text, nullable=True)  # Keep original for comparison
    
    # Relations
    feedback_session_id = Column(Integer, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MeetingPrepOutline(Base):
    """
    Stored meeting preparation outlines with talking points and critical questions.
    """
    __tablename__ = "meeting_prep_outlines"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(String, index=True)
    startup_name = Column(String)
    user_id = Column(String, index=True)
    
    # The complete outline
    outline = Column(Text)
    
    # Parsed sections
    talking_points = Column(JSON)  # List of {title, description}
    critical_questions = Column(JSON)  # List of {title, question}
    whitepaper_relevance = Column(JSON)  # Dict of section -> relevance
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DebriefSession(Base):
    """
    Tracks debrief conversations between analyst and insights agent.
    """
    __tablename__ = "debrief_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    startup_id = Column(String, index=True)
    startup_name = Column(String)
    user_id = Column(String, index=True)
    
    # Meeting prep reference
    meeting_prep_id = Column(Integer, nullable=True)
    
    # Conversation history
    conversation_history = Column(JSON)  # List of {role, content, timestamp}
    
    # Agent questions asked
    questions_asked = Column(JSON)  # List of 3 questions asked by agent
    
    # Analyst ratings and feedback
    ratings = Column(JSON)  # {question_index: rating_1_to_5}
    final_notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String, default="in_progress")  # in_progress, awaiting_feedback, completed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
