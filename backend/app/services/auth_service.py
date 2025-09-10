from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.models.user import UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, verify_token

class AuthService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.users_collection = database.users
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_dict = {
            "user_id": str(uuid.uuid4()),
            "email": user_data.email,
            "full_name": user_data.full_name,
            "phone_number": user_data.phone_number,
            "user_type": user_data.user_type,
            "preferred_language": user_data.preferred_language,
            "age_group": user_data.age_group,
            "location": user_data.location,
            "consent_data_collection": user_data.consent_data_collection,
            "consent_research_use": user_data.consent_research_use,
            "hashed_password": hashed_password,
            "is_active": True,
            "gamification_score": 0,
            "badges_earned": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        await self.users_collection.insert_one(user_dict)
        
        # Return user response (without password)
        user_dict.pop("hashed_password")
        return UserResponse(**user_dict)
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        return await self.users_collection.find_one({"email": email})
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
    
    async def get_current_user(self, token: str) -> Optional[UserResponse]:
        # Verify token and get user_id
        user_id = verify_token(token)
        if not user_id:
            return None
        
        # Get user from database
        user = await self.users_collection.find_one({"user_id": user_id})
        if not user:
            return None
        
        # Remove password from response
        user.pop("hashed_password", None)
        return UserResponse(**user)