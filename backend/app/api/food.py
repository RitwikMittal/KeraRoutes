from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.food import FoodConsumptionCreate, FoodConsumptionResponse
from app.services.food_service import FoodService
from app.services.auth_service import AuthService
from app.core.database import get_database
from app.api.auth import oauth2_scheme

router = APIRouter()

@router.post("/", response_model=FoodConsumptionResponse)
async def create_food_entry(
    food_data: FoodConsumptionCreate,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Create new food consumption entry"""
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create food entry
    food_service = FoodService(db)
    food_entry = await food_service.create_food_entry(user.user_id, food_data)
    return food_entry

@router.get("/", response_model=List[FoodConsumptionResponse])
async def get_user_food_entries(
    skip: int = 0,
    limit: int = 20,
    days: Optional[int] = None,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get user's food consumption entries"""
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get food entries
    food_service = FoodService(db)
    entries = await food_service.get_user_food_entries(user.user_id, skip, limit, days)
    return entries

@router.get("/{food_id}", response_model=FoodConsumptionResponse)
async def get_food_entry(
    food_id: str,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get specific food entry"""
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get food entry
    food_service = FoodService(db)
    entry = await food_service.get_food_entry(food_id, user.user_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    return entry

@router.post("/upload-bill")
async def upload_food_bill(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Upload and process food bill/receipt"""
    # Validate user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Process bill
    food_service = FoodService(db)
    result = await food_service.process_food_bill(file, user.user_id)
    return result

@router.post("/upload-food-photo")
async def upload_food_photo(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Upload food photo for dish identification"""
    # Validate user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Process food photo
    food_service = FoodService(db)
    result = await food_service.process_food_photo(file, user.user_id)
    return result

@router.get("/analytics/personal")
async def get_personal_food_analytics(
    days: int = 30,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get personal food consumption analytics"""
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get analytics
    food_service = FoodService(db)
    analytics = await food_service.get_personal_food_analytics(user.user_id, days)
    return analytics

@router.get("/recommendations/nearby")
async def get_nearby_food_recommendations(
    lat: float,
    lng: float,
    cuisine_type: Optional[str] = None,
    budget_max: Optional[float] = None,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get nearby food recommendations based on location"""
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get recommendations
    food_service = FoodService(db)
    recommendations = await food_service.get_nearby_recommendations(
        lat, lng, cuisine_type, budget_max
    )
    return recommendations