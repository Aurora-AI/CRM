import sys
import os
import sqlite3
from passlib.context import CryptContext

# Direct SQLite access to avoid import hell
conn = sqlite3.connect('cooper.db')
cursor = conn.cursor()

cursor.execute("SELECT email, password_hash FROM users WHERE email='admin@coopercard.com.br'")
user = cursor.fetchone()

if user:
    email, pwd_hash = user
    print(f"User found: {email}")
    print(f"Hash: {pwd_hash}")
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    is_valid = pwd_context.verify("123456", pwd_hash)
    print(f"Password '123456' valid? {is_valid}")
    
    if not is_valid:
        print("Updating password to '123456'...")
        new_hash = pwd_context.hash("123456")
        cursor.execute("UPDATE users SET password_hash=? WHERE email=?", (new_hash, email))
        conn.commit()
        print(f"Password updated. New hash: {new_hash}")
        
        # Verify again
        is_valid_now = pwd_context.verify("123456", new_hash)
        print(f"Password '123456' valid now? {is_valid_now}")
else:
    print("User NOT found")

conn.close()
