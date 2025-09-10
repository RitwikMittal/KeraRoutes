from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    TOURIST = "tourist"
    LOCAL = "local"
    RESEARCHER = "researcher"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone_number: Optional[str] = None
    user_type: UserType = UserType.TOURIST
    preferred_language: str = "english"
    age_group: Optional[str] = None  # 18-25, 26-35, 36-50, 51+
    location: Optional[str] = None
    consent_data_collection: bool = True
    consent_research_use: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    user_type: UserType
    preferred_language: str
    is_active: bool
    created_at: datetime
    gamification_score: int = 0
    badges_earned: List[str] = []

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_language: Optional[str] = None
    age_group: Optional[str] = None
    location: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None