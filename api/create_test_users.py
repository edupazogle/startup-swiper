#!/usr/bin/env python3
"""
Create test users for authentication testing
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from crud import create_user, get_user_by_email
from schemas import UserCreate
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./startup_swiper.db")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test users data
TEST_USERS = [
    {
        "email": "alice@slushdemo.com",
        "password": "AliceDemo2025!",
        "full_name": "Alice Johnson"
    },
    {
        "email": "bob@slushdemo.com",
        "password": "BobDemo2025!",
        "full_name": "Bob Martinez"
    }
]

def create_test_users():
    """Create test users if they don't exist"""
    db = SessionLocal()

    print("=" * 60)
    print("CREATING TEST USERS")
    print("=" * 60)
    print()

    created_users = []
    existing_users = []

    try:
        for user_data in TEST_USERS:
            email = user_data["email"]

            # Check if user exists
            existing_user = get_user_by_email(db, email=email)

            if existing_user:
                print(f"✓ User already exists: {email}")
                existing_users.append(user_data)
            else:
                # Create new user
                user_create = UserCreate(**user_data)
                new_user = create_user(db, user=user_create)
                print(f"✓ Created new user: {email}")
                print(f"  - Full Name: {new_user.full_name}")
                print(f"  - User ID: {new_user.id}")
                created_users.append(user_data)

            print()

        print("=" * 60)
        print("TEST USERS READY")
        print("=" * 60)
        print()
        print("You can now login with these credentials:")
        print()

        for user_data in TEST_USERS:
            print(f"User: {user_data['full_name']}")
            print(f"  Email:    {user_data['email']}")
            print(f"  Password: {user_data['password']}")
            print()

        print("=" * 60)
        print()

        return True

    except Exception as e:
        print(f"✗ Error creating test users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    success = create_test_users()
    sys.exit(0 if success else 1)
