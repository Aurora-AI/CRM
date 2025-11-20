from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, database, auth
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cooper CRM Lite")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Opportunity Routes
@app.get("/opportunities/", response_model=List[schemas.Opportunity])
def read_opportunities(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_opportunities(db, skip=skip, limit=limit)

@app.post("/opportunities/", response_model=schemas.Opportunity)
def create_opportunity(opportunity: schemas.OpportunityCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_opportunity(db=db, opportunity=opportunity, user_id=current_user.id)

@app.put("/opportunities/{opportunity_id}", response_model=schemas.Opportunity)
def update_opportunity(opportunity_id: int, opportunity: schemas.OpportunityUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.update_opportunity(db=db, opportunity_id=opportunity_id, opportunity_update=opportunity, user_id=current_user.id)

# Interaction Routes
@app.post("/opportunities/{opportunity_id}/interactions/", response_model=schemas.Interaction)
def create_interaction(opportunity_id: int, interaction: schemas.InteractionCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_interaction(db=db, interaction=interaction, opportunity_id=opportunity_id, user_id=current_user.id)
