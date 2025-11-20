from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from . import models, schemas, auth

def create_user(db: Session, user: schemas.UserCreate):
    # Validate domain
    auth.validate_email_domain(user.email)
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, name=user.name, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_opportunities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Opportunity).offset(skip).limit(limit).all()

def get_my_opportunities(db: Session, user_id: int):
    return db.query(models.Opportunity).filter(models.Opportunity.owner_id == user_id).all()

def create_opportunity(db: Session, opportunity: schemas.OpportunityCreate, user_id: int):
    db_opportunity = models.Opportunity(**opportunity.dict(), owner_id=user_id)
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

def update_opportunity(db: Session, opportunity_id: int, opportunity_update: schemas.OpportunityUpdate, user_id: int):
    db_opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # 90 Days Rule Logic
    days_since_interaction = (datetime.utcnow() - db_opportunity.last_interaction_date).days
    is_free_to_claim = days_since_interaction > 90
    
    if db_opportunity.owner_id != user_id and not is_free_to_claim:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You cannot edit this opportunity. It belongs to another user and is not yet free to claim (>90 days)."
        )
    
    # If free to claim and edited by another user, transfer ownership
    if is_free_to_claim and db_opportunity.owner_id != user_id:
        db_opportunity.owner_id = user_id
    
    # Update fields
    update_data = opportunity_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_opportunity, key, value)
    
    # Update last interaction date automatically on edit
    db_opportunity.last_interaction_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

def create_interaction(db: Session, interaction: schemas.InteractionCreate, opportunity_id: int, user_id: int):
    # Verify permission first (reuse update logic or check ownership)
    # For simplicity, adding an interaction counts as an update, so we check the rule
    db_opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    days_since_interaction = (datetime.utcnow() - db_opportunity.last_interaction_date).days
    is_free_to_claim = days_since_interaction > 90

    if db_opportunity.owner_id != user_id and not is_free_to_claim:
        raise HTTPException(status_code=403, detail="Forbidden")

    if is_free_to_claim and db_opportunity.owner_id != user_id:
        db_opportunity.owner_id = user_id

    db_interaction = models.Interaction(**interaction.dict(), opportunity_id=opportunity_id)
    db.add(db_interaction)
    
    # Update opportunity last interaction
    db_opportunity.last_interaction_date = interaction.date
    
    db.commit()
    db.refresh(db_interaction)
    return db_interaction
