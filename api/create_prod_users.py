#!/usr/bin/env python3
"""
Create production users for deployment
"""
import sys
sys.path.insert(0, '/home/akyo/startup_swiper/api')

from database import SessionLocal, engine
from models import User, Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create tables
Base.metadata.create_all(bind=engine)

# Users to create
users = [
    {
        "email": "nicolas.desaintromain@axa.com",
        "full_name": "DE SAINT ROMAIN Nicolas",
        "password": "123"
    },
    {
        "email": "alice.jin@axa-uk.co.uk",
        "full_name": "JIN Alice",
        "password": "123"
    },
    {
        "email": "josep-oriol.ayats@axa.com",
        "full_name": "AYATS Josep Oriol",
        "password": "123"
    },
    {
        "email": "wolfgang.sachsenhofer@axa.ch",
        "full_name": "SACHSENHOFER Wolfgang",
        "password": "123"
    },
    {
        "email": "clarisse.montmaneix@axaxl.com",
        "full_name": "MONTMANEIX Clarisse",
        "password": "123"
    },
    {
        "email": "adwaith.nair@axa.com",
        "full_name": "NAIR Adwaith",
        "password": "123"
    }
]

db = SessionLocal()

try:
    for user_data in users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing_user:
            print(f"✓ User {user_data['email']} already exists")
            continue
        
        # Create new user
        hashed_password = pwd_context.hash(user_data["password"])
        new_user = User(
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✓ Created user: {user_data['full_name']} ({user_data['email']})")
    
    print(f"\n✅ All {len(users)} users are ready!")
    print("\nLogin credentials:")
    print("Email: [any of the emails above]")
    print("Password: 123")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
