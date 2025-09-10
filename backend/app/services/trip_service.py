from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
from fastapi import UploadFile

from app.models.trip import TripCreate, TripUpdate, TripResponse
from app.services.ocr_service import OCRService
from app.services.mode_detection import ModeDetectionService

class TripService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.trips_collection = database.trips
        self.ocr_service = OCRService()
        self.mode_detection = ModeDetectionService()
    
    async def create_trip(self, user_id: str, trip_data: TripCreate) -> TripResponse:
        # Calculate trip metrics
        total_cost = sum(segment.cost or 0 for segment in trip_data.trip_chain)
        total_distance = sum(segment.distance_km or 0 for segment in trip_data.trip_chain)
        
        # Calculate duration
        start_time = min(segment.start_time for segment in trip_data.trip_chain)
        end_time = max(segment.end_time for segment in trip_data.trip_chain)
        total_duration = int((end_time - start_time).total_seconds() / 60)
        
        # Calculate data quality score (simple algorithm)
        data_quality_score = self._calculate_data_quality(trip_data.trip_chain)
        
        # Create trip document
        trip_dict = {
            "trip_id": str(uuid.uuid4()),
            "user_id": user_id,
            "trip_chain": [segment.dict() for segment in trip_data.trip_chain],
            "group_details": trip_data.group_details.dict(),
            "trip_purpose": trip_data.trip_purpose,
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "total_distance_km": total_distance,
            "data_quality_score": data_quality_score,
            "user_notes": trip_data.user_notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert trip
        await self.trips_collection.insert_one(trip_dict)
        
        return TripResponse(**trip_dict)
    
    async def get_user_trips(self, user_id: str, skip: int = 0, limit: int = 10) -> List[TripResponse]:
        cursor = self.trips_collection.find(
            {"user_id": user_id}
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        trips = []
        async for trip in cursor:
            trips.append(TripResponse(**trip))
        
        return trips
    
    async def get_trip(self, trip_id: str, user_id: str) -> Optional[TripResponse]:
        trip = await self.trips_collection.find_one({
            "trip_id": trip_id,
            "user_id": user_id
        })
        
        if trip:
            return TripResponse(**trip)
        return None
    
    async def update_trip(self, trip_id: str, user_id: str, trip_update: TripUpdate) -> Optional[TripResponse]:
        update_data = {k: v for k, v in trip_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.trips_collection.update_one(
            {"trip_id": trip_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_trip(trip_id, user_id)
        return None
    
    async def process_receipt(self, file: UploadFile, user_id: str) -> dict:
        # Save uploaded file
        file_path = f"uploads/{user_id}_{datetime.now().timestamp()}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with OCR
        ocr_result = await self.ocr_service.extract_receipt_data(file_path)
        
        return {
            "file_path": file_path,
            "extracted_data": ocr_result,
            "status": "processed"
        }
    
    async def get_personal_analytics(self, user_id: str, days: int = 30) -> dict:
        # Get trips from last N days
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": None,
                "total_trips": {"$sum": 1},
                "total_cost": {"$sum": "$total_cost"},
                "total_distance": {"$sum": "$total_distance_km"},
                "avg_data_quality": {"$avg": "$data_quality_score"}
            }}
        ]
        
        result = await self.trips_collection.aggregate(pipeline).to_list(1)
        
        if result:
            return result[0]
        return {"total_trips": 0, "total_cost": 0, "total_distance": 0, "avg_data_quality": 0}
    
    def _calculate_data_quality(self, trip_chain) -> float:
        # Simple data quality algorithm
        total_segments = len(trip_chain)
        quality_points = 0
        
        for segment in trip_chain:
            if segment.cost is not None:
                quality_points += 1
            if segment.distance_km is not None:
                quality_points += 1
            if segment.comfort_rating is not None:
                quality_points += 1
            if segment.receipt_photo_url:
                quality_points += 1
        
        max_possible_points = total_segments * 4
        return quality_points / max_possible_points if max_possible_points > 0 else 0