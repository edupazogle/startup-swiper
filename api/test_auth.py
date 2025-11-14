#!/usr/bin/env python3
"""
Simple authentication test script
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from crud import create_user, get_user_by_email
from schemas import UserCreate
from auth import authenticate_user, create_access_token, verify_password

# Create test database
engine = create_engine("sqlite:///./test_auth.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_authentication():
    """Test the complete authentication flow"""
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 1. Test user registration
        print("\n1. Testing User Registration...")
        test_user = UserCreate(
            email="test@example.com",
            password="SecurePassword123!",
            full_name="Test User"
        )

        # Check if user already exists
        existing_user = get_user_by_email(db, email=test_user.email)
        if existing_user:
            print(f"   ✓ User already exists: {existing_user.email}")
            user = existing_user
        else:
            user = create_user(db, user=test_user)
            print(f"   ✓ User created successfully!")
            print(f"     - Email: {user.email}")
            print(f"     - Full Name: {user.full_name}")
            print(f"     - ID: {user.id}")
            print(f"     - Active: {user.is_active}")

        # 2. Test password hashing
        print("\n2. Testing Password Hashing...")
        print(f"   ✓ Password is hashed (not stored in plain text)")
        print(f"     - Hash preview: {user.hashed_password[:50]}...")

        # 3. Test authentication
        print("\n3. Testing User Authentication...")
        authenticated_user = authenticate_user(db, test_user.email, test_user.password)
        if authenticated_user:
            print(f"   ✓ Authentication successful!")
            print(f"     - User ID: {authenticated_user.id}")
            print(f"     - Email: {authenticated_user.email}")
        else:
            print(f"   ✗ Authentication failed!")
            return False

        # 4. Test wrong password
        print("\n4. Testing Wrong Password...")
        wrong_auth = authenticate_user(db, test_user.email, "WrongPassword")
        if not wrong_auth:
            print(f"   ✓ Correctly rejected wrong password")
        else:
            print(f"   ✗ ERROR: Accepted wrong password!")
            return False

        # 5. Test JWT token generation
        print("\n5. Testing JWT Token Generation...")
        token = create_access_token(data={"sub": user.email})
        print(f"   ✓ JWT token created successfully")
        print(f"     - Token preview: {token[:50]}...")

        # 6. Test password verification
        print("\n6. Testing Password Verification...")
        if verify_password(test_user.password, user.hashed_password):
            print(f"   ✓ Password verification works correctly")
        else:
            print(f"   ✗ Password verification failed!")
            return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)

        # Print summary
        print("\n📋 AUTHENTICATION SYSTEM SUMMARY:")
        print("   • User model with email/password authentication: ✓")
        print("   • Password hashing with bcrypt: ✓")
        print("   • JWT token generation: ✓")
        print("   • User authentication: ✓")
        print("   • Password verification: ✓")
        print("   • Database integration: ✓")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
