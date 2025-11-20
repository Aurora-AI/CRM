"""
Simple script to create a test user and a few sample opportunities.
Run this instead of seed_data.py if you have bcrypt issues.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from database import SessionLocal, engine
import models

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create a test user with pre-hashed password
# Password: "123456" hashed with bcrypt
email = "admin@coopercard.com.br"
test_user = db.query(models.User).filter(models.User.email == email).first()

if not test_user:
    test_user = models.User(
        email=email,
        name="Admin User",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS9kw6WSu"  # 123456
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"✓ Created test user: {test_user.email} (password: 123456)")
else:
    print(f"✓ User {email} already exists")

# Create sample opportunities
opps = [
    {
        "cnpj": "46.373.208/0001-57",
        "razao_social": "Conexão Total",
        "status": "Qualificação",
        "temperatura": "Frio",
        "produto": "4L",
        "valor_estimado": 69000.00,
        "last_interaction_date": datetime.utcnow() - timedelta(days=30)
    },
    {
        "cnpj": "31.611.250/0001-91",
        "razao_social": "Luar Móveis",
        "status": "Negociação",
        "temperatura": "Quente",
        "produto": "4L",
        "valor_estimado": 292000.00,
        "last_interaction_date": datetime.utcnow() - timedelta(days=100)  # Free to claim
    },
    {
        "cnpj": "09.080.039/0001-48",
        "razao_social": "Eletro Casa + Barato",
        "status": "Proposta",
        "temperatura": "Morno",
        "produto": "Cooper",
        "valor_estimado": 300000.00,
        "last_interaction_date": datetime.utcnow() - timedelta(days=5)
    }
]

for opp_data in opps:
    opp = models.Opportunity(**opp_data, owner_id=test_user.id)
    db.add(opp)

db.commit()
print(f"✓ Created test user: {test_user.email} (password: 123456)")
print(f"✓ Created {len(opps)} sample opportunities")
print("Database seeded successfully!")
