from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums mirroring models.py for validation
class StatusEnum(str, Enum):
    QUALIFICACAO = "Qualificação"
    PROSPECCAO = "Prospecção"
    PROPOSTA = "Proposta"
    NEGOCIACAO = "Negociação"
    FECHADO = "Fechado" # Handling legacy/csv data

class TemperaturaEnum(str, Enum):
    FRIO = "Frio"
    MORNO = "Morno"
    QUENTE = "Quente"
    FERVENDO = "Fervendo"

class ProdutoEnum(str, Enum):
    COOPER = "Cooper"
    QUARTA_LINHA = "4L"
    PERSONALIZADOS = "Personalizados"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Interaction Schemas
class InteractionBase(BaseModel):
    type: str
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    opportunity_id: int

    class Config:
        from_attributes = True

# Opportunity Schemas
class OpportunityBase(BaseModel):
    cnpj: str
    razao_social: str
    status: str # flexible to accept imported data, but UI should use enums
    temperatura: Optional[str] = None
    produto: Optional[str] = None
    valor_estimado: float = 0.0
    last_interaction_date: Optional[datetime] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    status: Optional[str] = None
    temperatura: Optional[str] = None
    produto: Optional[str] = None
    valor_estimado: Optional[float] = None
    notes: Optional[str] = None # For adding interaction note implicitly if needed

class Opportunity(OpportunityBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: Optional[User] = None
    interactions: List[Interaction] = []

    class Config:
        from_attributes = True

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
