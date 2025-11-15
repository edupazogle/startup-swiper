from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# Database URL - use environment variable or default to a writable location
# In production (Render), use /tmp or a persistent volume
# Locally, use the project root
if os.getenv("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # Determine database path based on environment
    if os.getenv("RENDER"):
        # Running on Render - use /tmp which is writable
        DB_DIR = Path("/tmp")
    else:
        # Local development - use project root
        PROJECT_ROOT = Path(__file__).parent.parent.absolute()
        DB_DIR = PROJECT_ROOT
    
    # Ensure directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    DB_PATH = DB_DIR / "startup_swiper.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

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
