from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import logging

from ..core.mock_database import MockDatabase
from ..core.database import get_database

# Initialize router
router = APIRouter()

# Initialize mock database
mock_db = MockDatabase()

logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.post("/trips")
async def create_trip(trip_data: Dict[str, Any]):
    """Create a new trip entry"""
    try:
        # Add timestamp if not present
        if 'created_at' not in trip_data:
            trip_data['created_at'] = datetime.now().isoformat()
        
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.trips
            result = await collection.insert_one(trip_data)
            trip_data['_id'] = str(result.inserted_id)
            logger.info("Trip saved to MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            trip_id = mock_db.add_trip(trip_data)
            trip_data['_id'] = trip_id
            
        return {
            "success": True,
            "message": "Trip created successfully",
            "data": trip_data
        }
    except Exception as e:
        logger.error(f"Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trips")
async def get_trips():
    """Get all trips"""
    try:
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.trips
            trips = []
            async for trip in collection.find():
                trip['_id'] = str(trip['_id'])
                trips.append(trip)
            logger.info("Trips retrieved from MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            trips = mock_db.get_trips()
            
        return {
            "success": True,
            "data": trips
        }
    except Exception as e:
        logger.error(f"Error retrieving trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trips/{trip_id}")
async def get_trip_by_id(trip_id: str):
    """Get a specific trip by ID"""
    try:
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.trips
            from bson import ObjectId
            trip = await collection.find_one({"_id": ObjectId(trip_id)})
            if trip:
                trip['_id'] = str(trip['_id'])
            logger.info("Trip retrieved from MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            trip = mock_db.get_trip_by_id(trip_id)
            
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
            
        return {
            "success": True,
            "data": trip
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/food")
async def create_food_entry(food_data: Dict[str, Any]):
    """Create a new food entry"""
    try:
        # Add timestamp if not present
        if 'created_at' not in food_data:
            food_data['created_at'] = datetime.now().isoformat()
        
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.food_entries
            result = await collection.insert_one(food_data)
            food_data['_id'] = str(result.inserted_id)
            logger.info("Food entry saved to MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            food_id = mock_db.add_food_entry(food_data)
            food_data['_id'] = food_id
            
        return {
            "success": True,
            "message": "Food entry created successfully",
            "data": food_data
        }
    except Exception as e:
        logger.error(f"Error creating food entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food")
async def get_food_entries():
    """Get all food entries"""
    try:
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.food_entries
            food_entries = []
            async for food in collection.find():
                food['_id'] = str(food['_id'])
                food_entries.append(food)
            logger.info("Food entries retrieved from MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            food_entries = mock_db.get_food_entries()
            
        return {
            "success": True,
            "data": food_entries
        }
    except Exception as e:
        logger.error(f"Error retrieving food entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food/{food_id}")
async def get_food_entry_by_id(food_id: str):
    """Get a specific food entry by ID"""
    try:
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            collection = db.food_entries
            from bson import ObjectId
            food = await collection.find_one({"_id": ObjectId(food_id)})
            if food:
                food['_id'] = str(food['_id'])
            logger.info("Food entry retrieved from MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            food = mock_db.get_food_entry_by_id(food_id)
            
        if not food:
            raise HTTPException(status_code=404, detail="Food entry not found")
            
        return {
            "success": True,
            "data": food
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving food entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard-summary")
async def get_dashboard_summary():
    """Get analytics dashboard summary"""
    try:
        # Try to use real database first, fall back to mock
        try:
            db = await get_database()
            trips_collection = db.trips
            food_collection = db.food_entries
            
            # Get trips data
            trips = []
            async for trip in trips_collection.find():
                trips.append(trip)
            
            # Get food entries data
            food_entries = []
            async for food in food_collection.find():
                food_entries.append(food)
            
            logger.info("Analytics data retrieved from MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB not available, using mock database: {e}")
            trips = mock_db.get_trips()
            food_entries = mock_db.get_food_entries()
        
        # Calculate analytics
        total_trips = len(trips)
        total_food_entries = len(food_entries)
        
        total_transport_spending = sum(trip.get('cost', 0) for trip in trips)
        total_food_spending = sum(food.get('total_cost', 0) for food in food_entries)
        
        # Transport mode distribution
        mode_distribution = {}
        for trip in trips:
            mode = trip.get('transport_mode', 'unknown')
            mode_distribution[mode] = mode_distribution.get(mode, 0) + 1
        
        # Calculate averages
        avg_trip_cost = total_transport_spending / total_trips if total_trips > 0 else 0
        avg_meal_cost = total_food_spending / total_food_entries if total_food_entries > 0 else 0
        
        # Count unique restaurants
        unique_restaurants = len(set(food.get('restaurant_name', '') for food in food_entries))
        
        analytics_data = {
            "overview": {
                "total_trips": total_trips,
                "total_food_entries": total_food_entries,
                "total_transport_spending": round(total_transport_spending, 2),
                "total_food_spending": round(total_food_spending, 2),
                "total_combined_spending": round(total_transport_spending + total_food_spending, 2)
            },
            "transport_analysis": {
                "mode_distribution": mode_distribution,
                "avg_trip_cost": round(avg_trip_cost, 2)
            },
            "food_analysis": {
                "avg_meal_cost": round(avg_meal_cost, 2),
                "total_restaurants_visited": unique_restaurants
            }
        }
        
        return {
            "success": True,
            "data": analytics_data
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_user_profile():
    """Get user profile (simplified for demo)"""
    try:
        profile = {
            "name": "Demo User",
            "location": "Kerala, India",
            "total_trips": len(mock_db.get_trips()),
            "total_food_entries": len(mock_db.get_food_entries()),
            "joined_date": "2024-01-01",
            "preferences": {
                "transport_modes": ["bus", "train", "auto"],
                "cuisine_types": ["kerala", "south_indian"]
            }
        }
        
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_user_profile(profile_data: Dict[str, Any]):
    """Update user profile (simplified for demo)"""
    try:
        # In a real app, this would update the database
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": profile_data
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))
