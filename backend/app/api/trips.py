from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.trip import TripCreate, TripUpdate, TripResponse
from app.services.trip_service import TripService
from app.services.auth_service import AuthService
from app.core.database import get_database
from app.api.auth import oauth2_scheme

router = APIRouter()

@router.post("/", response_model=TripResponse)
async def create_trip(
    trip_data: TripCreate,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Create trip
    trip_service = TripService(db)
    trip = await trip_service.create_trip(user["user_id"], trip_data)
    return trip

@router.get("/", response_model=List[TripResponse])
async def get_user_trips(
    skip: int = 0,
    limit: int = 10,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get trips
    trip_service = TripService(db)
    trips = await trip_service.get_user_trips(user["user_id"], skip, limit)
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get trip
    trip_service = TripService(db)
    trip = await trip_service.get_trip(trip_id, user["user_id"])
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_update: TripUpdate,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Update trip
    trip_service = TripService(db)
    trip = await trip_service.update_trip(trip_id, user["user_id"], trip_update)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.post("/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Validate user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Process receipt
    trip_service = TripService(db)
    result = await trip_service.process_receipt(file, user["user_id"])
    return result

@router.get("/analytics/personal")
async def get_personal_analytics(
    days: int = 30,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    # Get current user
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get analytics
    trip_service = TripService(db)
    analytics = await trip_service.get_personal_analytics(user["user_id"], days)
    return analytics