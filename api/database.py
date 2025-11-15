from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# Database URL - points to root startup_swiper.db
# Using absolute path to avoid issues with relative path resolution from different working directories
PROJECT_ROOT = Path("/home/akyo/startup_swiper").absolute()
DB_PATH = PROJECT_ROOT / "startup_swiper.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# For PostgreSQL, use something like:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)


# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
