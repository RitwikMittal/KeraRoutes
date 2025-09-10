from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
from fastapi import UploadFile
import os

from app.models.food import FoodConsumptionCreate, FoodConsumptionResponse, FoodTransportNexus
from app.services.ocr_service import OCRService

class FoodService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.food_collection = database.food_consumption
        self.restaurants_collection = database.restaurants
        self.ocr_service = OCRService()
    
    async def create_food_entry(self, user_id: str, food_data: FoodConsumptionCreate) -> FoodConsumptionResponse:
        """Create new food consumption entry"""
        # Create food document
        food_dict = {
            "food_id": str(uuid.uuid4()),
            "user_id": user_id,
            "trip_segment_id": food_data.trip_segment_id,
            "location": food_data.location.dict(),
            "meal_type": food_data.meal_type,
            "dishes_ordered": [dish.dict() for dish in food_data.dishes_ordered],
            "total_cost": food_data.total_cost,
            "cost_per_person": food_data.cost_per_person,
            "payment_method": food_data.payment_method,
            "service_rating": food_data.service_rating,
            "food_quality_rating": food_data.food_quality_rating,
            "cultural_authenticity_rating": food_data.cultural_authenticity_rating,
            "dining_companions": food_data.dining_companions,
            "local_recommendation": food_data.local_recommendation,
            "dietary_restrictions": food_data.dietary_restrictions,
            "language_barrier": food_data.language_barrier,
            "bill_photo_url": food_data.bill_photo_url,
            "food_photo_urls": food_data.food_photo_urls,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add transport nexus if available
        if food_data.trip_segment_id:
            transport_nexus = await self._calculate_transport_nexus(food_data.trip_segment_id, user_id)
            food_dict["transport_nexus"] = transport_nexus.dict() if transport_nexus else None
        
        # Insert food entry
        await self.food_collection.insert_one(food_dict)
        
        # Update restaurant database
        await self._update_restaurant_data(food_data.location)
        
        return FoodConsumptionResponse(**food_dict)
    
    async def get_user_food_entries(self, user_id: str, skip: int = 0, limit: int = 20, days: Optional[int] = None) -> List[FoodConsumptionResponse]:
        """Get user's food consumption entries"""
        query = {"user_id": user_id}
        
        # Add date filter if specified
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query["created_at"] = {"$gte": start_date}
        
        cursor = self.food_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        entries = []
        async for entry in cursor:
            entries.append(FoodConsumptionResponse(**entry))
        
        return entries
    
    async def get_food_entry(self, food_id: str, user_id: str) -> Optional[FoodConsumptionResponse]:
        """Get specific food entry"""
        entry = await self.food_collection.find_one({
            "food_id": food_id,
            "user_id": user_id
        })
        
        if entry:
            return FoodConsumptionResponse(**entry)
        return None
    
    async def process_food_bill(self, file: UploadFile, user_id: str) -> Dict:
        """Process food bill/receipt using OCR"""
        # Save uploaded file
        timestamp = datetime.now().timestamp()
        filename = f"{user_id}_{timestamp}_{file.filename}"
        file_path = f"uploads/bills/{filename}"
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with OCR
        ocr_result = await self.ocr_service.extract_receipt_data(file_path)
        
        # Structure the response for frontend
        structured_data = {
            "file_url": file_path,
            "extracted_data": ocr_result.get("extracted_data", {}),
            "suggested_entries": await self._create_food_suggestions(ocr_result),
            "processing_status": "completed" if ocr_result.get("success") else "failed"
        }
        
        return structured_data
    
    async def process_food_photo(self, file: UploadFile, user_id: str) -> Dict:
        """Process food photo for dish identification"""
        # Save uploaded file
        timestamp = datetime.now().timestamp()
        filename = f"{user_id}_{timestamp}_{file.filename}"
        file_path = f"uploads/food_photos/{filename}"
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with food recognition
        recognition_result = await self.ocr_service.extract_food_photo_data(file_path)
        
        return {
            "file_url": file_path,
            "recognition_result": recognition_result,
            "suggested_dishes": await self._get_dish_suggestions(recognition_result),
            "processing_status": "completed"
        }
    
    async def get_personal_food_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get personal food consumption analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Aggregation pipeline for personal analytics
        pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": start_date}}},
            {"$facet": {
                "total_stats": [
                    {"$group": {
                        "_id": None,
                        "total_meals": {"$sum": 1},
                        "total_spent": {"$sum": "$total_cost"},
                        "avg_cost_per_meal": {"$avg": "$total_cost"},
                        "unique_restaurants": {"$addToSet": "$location.restaurant_name"}
                    }}
                ],
                "cuisine_breakdown": [
                    {"$unwind": "$dishes_ordered"},
                    {"$group": {
                        "_id": "$dishes_ordered.cuisine_type",
                        "count": {"$sum": 1},
                        "total_cost": {"$sum": "$dishes_ordered.price"}
                    }},
                    {"$sort": {"count": -1}}
                ],
                "meal_type_distribution": [
                    {"$group": {
                        "_id": "$meal_type",
                        "count": {"$sum": 1},
                        "avg_cost": {"$avg": "$total_cost"}
                    }}
                ],
                "monthly_trend": [
                    {"$group": {
                        "_id": {
                            "year": {"$year": "$created_at"},
                            "month": {"$month": "$created_at"},
                            "day": {"$dayOfMonth": "$created_at"}
                        },
                        "meals": {"$sum": 1},
                        "cost": {"$sum": "$total_cost"}
                    }},
                    {"$sort": {"_id": 1}}
                ]
            }}
        ]
        
        result = await self.food_collection.aggregate(pipeline).to_list(1)
        
        if result:
            analytics = result[0]
            return {
                "period_days": days,
                "total_stats": analytics["total_stats"][0] if analytics["total_stats"] else {},
                "cuisine_breakdown": analytics["cuisine_breakdown"],
                "meal_type_distribution": analytics["meal_type_distribution"],
                "monthly_trend": analytics["monthly_trend"]
            }
        
        return {"period_days": days, "total_stats": {}, "cuisine_breakdown": [], "meal_type_distribution": [], "monthly_trend": []}
    
    async def get_nearby_recommendations(self, lat: float, lng: float, cuisine_type: Optional[str] = None, budget_max: Optional[float] = None) -> List[Dict]:
        """Get nearby food recommendations based on location"""
        # Build query for nearby restaurants
        query = {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": 5000  # 5km radius
                }
            }
        }
        
        # Add filters
        if cuisine_type:
            query["cuisine_type"] = cuisine_type
        if budget_max:
            query["avg_cost_per_person"] = {"$lte": budget_max}
        
        # Get restaurants
        cursor = self.restaurants_collection.find(query).limit(20)
        recommendations = []
        
        async for restaurant in cursor:
            # Calculate distance (simplified)
            recommendations.append({
                "name": restaurant["name"],
                "cuisine_type": restaurant["cuisine_type"],
                "avg_cost_per_person": restaurant.get("avg_cost_per_person", 0),
                "rating": restaurant.get("rating", 0),
                "address": restaurant.get("address", ""),
                "distance_km": restaurant.get("distance", 0),  # Would calculate actual distance
                "popular_dishes": restaurant.get("popular_dishes", []),
                "transport_accessibility": restaurant.get("transport_accessibility", "unknown")
            })
        
        return recommendations
    
    async def _calculate_transport_nexus(self, trip_segment_id: str, user_id: str) -> Optional[FoodTransportNexus]:
        """Calculate transport-food nexus data"""
        # Get trip segment data
        trip_segment = await self.database.trips.find_one({
            "user_id": user_id,
            "trip_chain.segment_id": trip_segment_id
        })
        
        if not trip_segment:
            return None
        
        # Find the specific segment
        segment = None
        for seg in trip_segment.get("trip_chain", []):
            if str(seg.get("segment_id")) == trip_segment_id:
                segment = seg
                break
        
        if not segment:
            return None
        
        # Calculate nexus data
        transport_nexus = FoodTransportNexus(
            transport_mode_used=segment.get("mode"),
            travel_time_to_food=segment.get("duration_minutes"),
            transport_cost_to_reach=segment.get("cost"),
            accessibility_rating=4,  # Would calculate based on distance from transport stop
            detour_from_main_route=False,  # Would analyze route deviation
            recommendation_source="app_suggestion"
        )
        
        return transport_nexus
    
    async def _update_restaurant_data(self, location_data) -> None:
        """Update restaurant database with new data"""
        # Check if restaurant exists
        restaurant = await self.restaurants_collection.find_one({
            "name": location_data["restaurant_name"],
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [location_data["lng"], location_data["lat"]]},
                    "$maxDistance": 100  # 100m radius
                }
            }
        })
        
        if not restaurant:
            # Create new restaurant entry
            restaurant_data = {
                "restaurant_id": str(uuid.uuid4()),
                "name": location_data["restaurant_name"],
                "location": {
                    "type": "Point",
                    "coordinates": [location_data["lng"], location_data["lat"]]
                },
                "address": location_data.get("address", ""),
                "cuisine_type": location_data["cuisine_type"],
                "establishment_type": location_data["establishment_type"],
                "visit_count": 1,
                "total_ratings": 0,
                "avg_rating": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.restaurants_collection.insert_one(restaurant_data)
        else:
            # Update existing restaurant
            await self.restaurants_collection.update_one(
                {"restaurant_id": restaurant["restaurant_id"]},
                {
                    "$inc": {"visit_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
    
    async def _create_food_suggestions(self, ocr_result: Dict) -> List[Dict]:
        """Create food entry suggestions from OCR result"""
        extracted_data = ocr_result.get("extracted_data", {})
        
        suggestions = []
        if extracted_data.get("total_amount"):
            suggestion = {
                "suggested_total_cost": extracted_data["total_amount"],
                "suggested_restaurant": extracted_data.get("merchant_name", "Unknown"),
                "suggested_date": extracted_data.get("date"),
                "suggested_items": extracted_data.get("items", [])
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    async def _get_dish_suggestions(self, recognition_result: Dict) -> List[Dict]:
        """Get dish suggestions from food photo recognition"""
        # This would integrate with ML model for food recognition
        # For now, return basic suggestions
        return [
            {
                "dish_name": recognition_result.get("detected_food", "Unknown dish"),
                "cuisine_type": recognition_result.get("cuisine_type", "unknown"),
                "confidence": recognition_result.get("confidence", 0.5),
                "estimated_price": 150  # Would use ML to estimate price
            }
        ]