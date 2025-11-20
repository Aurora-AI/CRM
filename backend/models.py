from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
try:
    from .database import Base
except ImportError:
    from database import Base

class StatusEnum(str, enum.Enum):
    QUALIFICACAO = "Qualificação"
    PROSPECCAO = "Prospecção"
    PROPOSTA = "Proposta"
    NEGOCIACAO = "Negociação"
    FECHADO = "Fechado" # Added based on CSV analysis, though not explicitly in prompt requirements, it's good practice to handle 'Fechado' or similar if they exist, but prompt said "Enums Rígidos". 
    # Prompt said: Status: ['Qualificação', 'Prospecção', 'Proposta', 'Negociação']
    # However, CSV has "Finalizado", "Fechado". I will stick to the prompt's rigid enums for NEW data, but for seed data I might need to map or allow others if I strictly follow "Enums Rígidos".
    # Let's stick to the prompt's list for the Enum definition to be safe, but I might need to handle data cleaning in seed_data.
    # Wait, if I use Enum in SQLAlchemy, it will enforce it.
    # Let's add the prompt ones.
    
class StatusEnumStrict(str, enum.Enum):
    QUALIFICACAO = "Qualificação"
    PROSPECCAO = "Prospecção"
    PROPOSTA = "Proposta"
    NEGOCIACAO = "Negociação"

class TemperaturaEnum(str, enum.Enum):
    FRIO = "Frio"
    MORNO = "Morno"
    QUENTE = "Quente"
    FERVENDO = "Fervendo"

class ProdutoEnum(str, enum.Enum):
    COOPER = "Cooper"
    QUARTA_LINHA = "4L" # Mapped from "4ª Linha"
    PERSONALIZADOS = "Personalizados" # Mapped from "Personalizado"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)

    opportunities = relationship("Opportunity", back_populates="owner")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String, index=True)
    razao_social = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Using String for flexibility if data doesn't match perfectly, or Enum if we want strictness.
    # Prompt says "Enums Rígidos". I will use String in DB but validate in App/Pydantic to avoid import crashes if CSV has bad data, 
    # OR I will map everything in the seed script.
    # Let's use String in DB to be safe with SQLite, but validate in logic.
    status = Column(String) 
    temperatura = Column(String)
    produto = Column(String)
    
    valor_estimado = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction_date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="opportunities")
    interactions = relationship("Interaction", back_populates="opportunity")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    type = Column(String) # call, email, meeting
    notes = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    opportunity = relationship("Opportunity", back_populates="interactions")
