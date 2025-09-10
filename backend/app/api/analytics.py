from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.core.database import get_database
from app.api.auth import oauth2_scheme

router = APIRouter()

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    days: int = 30,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get overview statistics for research dashboard"""
    # Verify user is researcher
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    overview = await analytics_service.get_dashboard_overview(days)
    return overview

@router.get("/trips/mode-split")
async def get_mode_split_analysis(
    days: int = 30,
    region: Optional[str] = None,
    user_type: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get transport mode split analysis"""
    # Verify user is researcher
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    analysis = await analytics_service.get_mode_split_analysis(days, region, user_type)
    return analysis

@router.get("/trips/temporal-patterns")
async def get_temporal_patterns(
    days: int = 30,
    granularity: str = "hour",  # hour, day, week
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get temporal travel patterns"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    patterns = await analytics_service.get_temporal_patterns(days, granularity)
    return patterns

@router.get("/trips/origin-destination")
async def get_origin_destination_matrix(
    days: int = 30,
    min_trips: int = 5,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get origin-destination trip matrix"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    od_matrix = await analytics_service.get_origin_destination_matrix(days, min_trips)
    return od_matrix

@router.get("/food/consumption-patterns")
async def get_food_consumption_patterns(
    days: int = 30,
    cuisine_type: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get food consumption patterns analysis"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    patterns = await analytics_service.get_food_consumption_patterns(days, cuisine_type)
    return patterns

@router.get("/food/transport-correlation")
async def get_food_transport_correlation(
    days: int = 30,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get correlation between food choices and transport modes"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    correlation = await analytics_service.get_food_transport_correlation(days)
    return correlation

@router.get("/users/engagement")
async def get_user_engagement_metrics(
    days: int = 30,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get user engagement and data quality metrics"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    metrics = await analytics_service.get_user_engagement_metrics(days)
    return metrics

@router.get("/export/trips")
async def export_trip_data(
    format: str = "csv",  # csv, json
    days: int = 30,
    include_personal_data: bool = False,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Export trip data for research"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    export_data = await analytics_service.export_trip_data(format, days, include_personal_data)
    return export_data

@router.get("/export/food")
async def export_food_data(
    format: str = "csv",  # csv, json
    days: int = 30,
    include_personal_data: bool = False,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Export food consumption data for research"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    export_data = await analytics_service.export_food_data(format, days, include_personal_data)
    return export_data

@router.get("/live/active-trips")
async def get_live_active_trips(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get currently active trips for live dashboard"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    active_trips = await analytics_service.get_live_active_trips()
    return active_trips

@router.get("/heatmap/trip-density")
async def get_trip_density_heatmap(
    days: int = 7,
    time_of_day: Optional[str] = None,  # morning, afternoon, evening, night
    transport_mode: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database)
):
    """Get trip density data for heatmap visualization"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    if not user or user.user_type != "researcher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    heatmap_data = await analytics_service.get_trip_density_heatmap(
        days, time_of_day, transport_mode
    )
    return heatmap_data