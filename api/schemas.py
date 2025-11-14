from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Calendar Event schemas
class CalendarEventBase(BaseModel):
    title: str
    startTime: datetime
    endTime: datetime
    type: str
    attendees: Optional[List[str]] = None
    isSaved: Optional[bool] = False
    link: Optional[str] = None
    stage: Optional[str] = None
    category: Optional[str] = None
    highlight: Optional[str] = None

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEvent(CalendarEventBase):
    id: int
    
    class Config:
        from_attributes = True

# LinkedIn Chat Message schemas
class LinkedInChatMessageBase(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class LinkedInChatMessageCreate(LinkedInChatMessageBase):
    pass

class LinkedInChatMessage(LinkedInChatMessageBase):
    id: int
    
    class Config:
        from_attributes = True

# Admin User schemas
class AdminUserBase(BaseModel):
    username: str
    password: str

class AdminUserCreate(AdminUserBase):
    pass

class AdminUser(AdminUserBase):
    id: int
    
    class Config:
        from_attributes = True

# Vote schemas
class VoteBase(BaseModel):
    startupId: str
    userId: int
    userName: str
    interested: bool
    timestamp: Optional[datetime] = None
    meetingScheduled: Optional[bool] = False

class VoteCreate(VoteBase):
    pass

class Vote(VoteBase):
    id: int
    
    class Config:
        from_attributes = True

# Auroral Info schemas
class AuroralInfoBase(BaseModel):
    intensity: Optional[int] = 5
    speed: Optional[int] = 3
    colors: Optional[List[str]] = None

class AuroralInfoCreate(AuroralInfoBase):
    pass

class AuroralInfo(AuroralInfoBase):
    id: int
    
    class Config:
        from_attributes = True

# Idea schemas
class IdeaBase(BaseModel):
    name: str
    title: str
    category: str
    description: str
    tags: Optional[List[str]] = None
    timestamp: Optional[datetime] = None

class IdeaCreate(IdeaBase):
    pass

class Idea(IdeaBase):
    id: int
    
    class Config:
        from_attributes = True

# Startup Rating schemas
class StartupRatingBase(BaseModel):
    startupId: str
    averageRating: Optional[int] = 0
    totalRatings: Optional[int] = 0
    ratings: Optional[Dict[str, int]] = None
    feedback: Optional[List[str]] = None
    lastUpdated: Optional[datetime] = None
    trendingScore: Optional[int] = 0

class StartupRatingCreate(StartupRatingBase):
    pass

class StartupRating(StartupRatingBase):
    
    class Config:
        from_attributes = True

# Finished User schemas
class FinishedUserBase(BaseModel):
    userId: int
    finishedAt: Optional[datetime] = None

class FinishedUserCreate(FinishedUserBase):
    pass

class FinishedUser(FinishedUserBase):
    id: int
    
    class Config:
        from_attributes = True

# AI Chat Message schemas
class AIChatMessageBase(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class AIChatMessageCreate(AIChatMessageBase):
    pass

class AIChatMessage(AIChatMessageBase):
    id: int
    
    class Config:
        from_attributes = True

# User Event schemas
class UserEventBase(BaseModel):
    eventType: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class UserEventCreate(UserEventBase):
    pass

class UserEvent(UserEventBase):
    id: int
    
    class Config:
        from_attributes = True

# AI Assistant Message schemas
class AIAssistantMessageBase(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class AIAssistantMessageCreate(AIAssistantMessageBase):
    pass

class AIAssistantMessage(AIAssistantMessageBase):
    id: int
    
    class Config:
        from_attributes = True

# Current User ID schemas
class CurrentUserIdBase(BaseModel):
    userId: int

class CurrentUserIdCreate(CurrentUserIdBase):
    pass

class CurrentUserId(CurrentUserIdBase):
    id: int
    
    class Config:
        from_attributes = True

# Data Version schemas
class DataVersionBase(BaseModel):
    version: str
    updatedAt: Optional[datetime] = None

class DataVersionCreate(DataVersionBase):
    pass

class DataVersion(DataVersionBase):
    id: int
    
    class Config:
        from_attributes = True

# Meeting Insight schemas
class MeetingInsightBase(BaseModel):
    meetingId: str
    userId: str
    startupId: Optional[str] = None
    startupName: Optional[str] = None
    insight: str
    tags: Optional[List[str]] = None
    rating: Optional[int] = None
    followUp: Optional[bool] = False
    structured_qa: Optional[List[Dict[str, Any]]] = None

class MeetingInsightCreate(MeetingInsightBase):
    pass

class MeetingInsight(MeetingInsightBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Feedback Session schemas
class FeedbackSessionBase(BaseModel):
    meetingId: str
    userId: str
    startupId: Optional[str] = None
    startupName: str

class FeedbackSessionCreate(FeedbackSessionBase):
    questions: List[Dict[str, Any]]

class FeedbackSession(FeedbackSessionBase):
    id: int
    questions: List[Dict[str, Any]]
    answers: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    current_question_index: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_interaction: datetime

    class Config:
        from_attributes = True

# Feedback Chat schemas
class FeedbackChatMessage(BaseModel):
    message: str
    session_id: int

class FeedbackChatResponse(BaseModel):
    response: str
    question_id: Optional[int] = None
    current_question: Optional[Dict[str, Any]] = None
    progress: Dict[str, Any]
    session_id: int
    completed: bool

# Notification Queue schemas
class NotificationQueueBase(BaseModel):
    userId: str
    meetingId: str
    meetingEndTime: datetime
    scheduledFor: datetime

class NotificationQueueCreate(NotificationQueueBase):
    pass

class NotificationQueue(NotificationQueueBase):
    id: int
    sent: bool
    sentAt: Optional[datetime] = None
    dismissed: bool
    insightSubmitted: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True

# Push Subscription schemas
class PushSubscriptionBase(BaseModel):
    userId: str
    endpoint: str
    p256dh: str
    auth: str
    userAgent: Optional[str] = None

class PushSubscriptionCreate(PushSubscriptionBase):
    pass

class PushSubscription(PushSubscriptionBase):
    id: int
    active: bool
    createdAt: datetime
    lastUsed: datetime
    
    class Config:
        from_attributes = True
