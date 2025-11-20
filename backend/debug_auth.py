import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
import auth

db = SessionLocal()
user = db.query(models.User).filter(models.User.email == "admin@coopercard.com.br").first()

if user:
    print(f"User found: {user.email}")
    print(f"Hash in DB: {user.password_hash}")
    
    # Test password verification
    is_valid = auth.verify_password("123456", user.password_hash)
    print(f"Password '123456' valid? {is_valid}")
else:
    print("User not found!")
