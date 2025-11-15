from sqlalchemy.orm import Session
from datetime import datetime
import models
import schemas
from auth import get_password_hash

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Calendar Events CRUD
def get_calendar_event(db: Session, event_id: int):
    return db.query(models.CalendarEvent).filter(models.CalendarEvent.id == event_id).first()

def get_calendar_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CalendarEvent).offset(skip).limit(limit).all()

def create_calendar_event(db: Session, event: schemas.CalendarEventCreate):
    db_event = models.CalendarEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_calendar_event(db: Session, event_id: int, event: schemas.CalendarEventCreate):
    db_event = get_calendar_event(db, event_id)
    if db_event:
        for key, value in event.model_dump().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_calendar_event(db: Session, event_id: int):
    db_event = get_calendar_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event

# LinkedIn Messages CRUD
def get_linkedin_message(db: Session, message_id: int):
    return db.query(models.LinkedInChatMessage).filter(models.LinkedInChatMessage.id == message_id).first()

def get_linkedin_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LinkedInChatMessage).offset(skip).limit(limit).all()

def create_linkedin_message(db: Session, message: schemas.LinkedInChatMessageCreate):
    db_message = models.LinkedInChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Admin User CRUD
def get_admin_user(db: Session):
    return db.query(models.AdminUser).first()

def create_admin_user(db: Session, user: schemas.AdminUserCreate):
    db_user = models.AdminUser(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Votes CRUD
def get_votes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vote).offset(skip).limit(limit).all()

def get_votes_by_startup(db: Session, startup_id: str):
    return db.query(models.Vote).filter(models.Vote.startupId == startup_id).all()

def create_vote(db: Session, vote: schemas.VoteCreate):
    db_vote = models.Vote(**vote.model_dump())
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

def delete_vote(db: Session, startup_id: str, user_id: str):
    vote = db.query(models.Vote).filter(
        models.Vote.startupId == startup_id,
        models.Vote.userId == user_id
    ).first()
    if vote:
        db.delete(vote)
        db.commit()
        return True
    return False

# Auroral Info CRUD
def get_auroral_info(db: Session):
    return db.query(models.AuroralInfo).first()

def create_auroral_info(db: Session, info: schemas.AuroralInfoCreate):
    db_info = models.AuroralInfo(**info.model_dump())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

def update_auroral_info(db: Session, info: schemas.AuroralInfoCreate):
    db_info = get_auroral_info(db)
    if db_info:
        for key, value in info.model_dump().items():
            setattr(db_info, key, value)
        db.commit()
        db.refresh(db_info)
    else:
        db_info = create_auroral_info(db, info)
    return db_info

# Ideas CRUD
def get_idea(db: Session, idea_id: int):
    return db.query(models.Idea).filter(models.Idea.id == idea_id).first()

def get_ideas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Idea).offset(skip).limit(limit).all()

def create_idea(db: Session, idea: schemas.IdeaCreate):
    db_idea = models.Idea(**idea.model_dump())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

# Startup Ratings CRUD
def get_startup_rating(db: Session, startup_id: str):
    return db.query(models.StartupRating).filter(models.StartupRating.startupId == startup_id).first()

def get_startup_ratings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StartupRating).offset(skip).limit(limit).all()

def create_startup_rating(db: Session, rating: schemas.StartupRatingCreate):
    db_rating = models.StartupRating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def update_startup_rating(db: Session, startup_id: str, rating: schemas.StartupRatingCreate):
    db_rating = get_startup_rating(db, startup_id)
    if db_rating:
        for key, value in rating.model_dump().items():
            setattr(db_rating, key, value)
        db_rating.lastUpdated = datetime.utcnow()
        db.commit()
        db.refresh(db_rating)
    else:
        db_rating = create_startup_rating(db, rating)
    return db_rating

# Finished Users CRUD
def get_finished_users(db: Session):
    return db.query(models.FinishedUser).all()

def add_finished_user(db: Session, user_id: int):
    db_user = models.FinishedUser(userId=user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# AI Chat Messages CRUD
def get_ai_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AIChatMessage).offset(skip).limit(limit).all()

def create_ai_message(db: Session, message: schemas.AIChatMessageCreate):
    db_message = models.AIChatMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# User Events CRUD
def get_user_events(db: Session):
    return db.query(models.UserEvent).all()

def create_user_event(db: Session, event: schemas.UserEventCreate):
    db_event = models.UserEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# AI Assistant Messages CRUD
def get_ai_assistant_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AIAssistantMessage).offset(skip).limit(limit).all()

def create_ai_assistant_message(db: Session, message: schemas.AIAssistantMessageCreate):
    db_message = models.AIAssistantMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Current User ID CRUD
def get_current_user_id(db: Session):
    return db.query(models.CurrentUserId).first()

def set_current_user_id(db: Session, user_id: int):
    db_user_id = get_current_user_id(db)
    if db_user_id:
        db_user_id.userId = user_id
        db.commit()
        db.refresh(db_user_id)
    else:
        db_user_id = models.CurrentUserId(userId=user_id)
        db.add(db_user_id)
        db.commit()
        db.refresh(db_user_id)
    return db_user_id

# Data Version CRUD
def get_data_version(db: Session):
    return db.query(models.DataVersion).first()

def set_data_version(db: Session, version: str):
    db_version = get_data_version(db)
    if db_version:
        db_version.version = version
        db_version.updatedAt = datetime.utcnow()
        db.commit()
        db.refresh(db_version)
    else:
        db_version = models.DataVersion(version=version)
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
    return db_version
