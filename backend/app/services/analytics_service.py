from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import csv
import io

class AnalyticsService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.trips_collection = database.trips
        self.food_collection = database.food_consumption
        self.users_collection = database.users
    
    async def get_dashboard_overview(self, days: int = 30) -> Dict:
        """Get overview statistics for research dashboard"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic statistics
        total_users = await self.users_collection.count_documents({})
        active_users = await self.users_collection.count_documents({
            "last_activity": {"$gte": start_date}
        })
        total_trips = await self.trips_collection.count_documents({
            "created_at": {"$gte": start_date}
        })
        total_food_entries = await self.food_collection.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Get data quality metrics
        quality_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": None,
                "avg_quality": {"$avg": "$data_quality_score"},
                "high_quality_trips": {
                    "$sum": {"$cond": [{"$gte": ["$data_quality_score", 0.8]}, 1, 0]}
                }
            }}
        ]
        
        quality_result = await self.trips_collection.aggregate(quality_pipeline).to_list(1)
        quality_metrics = quality_result[0] if quality_result else {"avg_quality": 0, "high_quality_trips": 0}
        
        return {
            "period_days": days,
            "total_users": total_users,
            "active_users": active_users,
            "total_trips": total_trips,
            "total_food_entries": total_food_entries,
            "data_quality": {
                "avg_quality_score": round(quality_metrics["avg_quality"], 2),
                "high_quality_percentage": round((quality_metrics["high_quality_trips"] / max(total_trips, 1)) * 100, 1)
            },
            "user_engagement": {
                "active_user_percentage": round((active_users / max(total_users, 1)) * 100, 1)
            }
        }
    
    async def get_mode_split_analysis(self, days: int = 30, region: Optional[str] = None, user_type: Optional[str] = None) -> Dict:
        """Get transport mode split analysis"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build match criteria
        match_criteria = {"created_at": {"$gte": start_date}}
        
        # Add user type filter if specified
        user_filter = {}
        if user_type:
            user_filter["user_type"] = user_type
        
        # Pipeline for mode split
        pipeline = [
            {"$match": match_criteria},
            {"$unwind": "$trip_chain"},
            {"$group": {
                "_id": "$trip_chain.mode",
                "count": {"$sum": 1},
                "total_distance": {"$sum": "$trip_chain.distance_km"},
                "total_cost": {"$sum": "$trip_chain.cost"},
                "avg_duration": {"$avg": {"$subtract": ["$trip_chain.end_time", "$trip_chain.start_time"]}}
            }},
            {"$sort": {"count": -1}}
        ]
        
        # Add user join if user type filter is specified
        if user_type:
            pipeline.insert(0, {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_info"
                }
            })
            pipeline.insert(1, {"$match": {"user_info.user_type": user_type}})
        
        result = await self.trips_collection.aggregate(pipeline).to_list(None)
        
        # Calculate percentages
        total_trips = sum(item["count"] for item in result)
        
        mode_split = []
        for item in result:
            mode_split.append({
                "mode": item["_id"],
                "count": item["count"],
                "percentage": round((item["count"] / max(total_trips, 1)) * 100, 1),
                "avg_distance_km": round(item["total_distance"] / max(item["count"], 1), 2),
                "avg_cost": round(item["total_cost"] / max(item["count"], 1), 2),
                "avg_duration_minutes": round(item["avg_duration"] / 60000, 1) if item["avg_duration"] else 0  # Convert milliseconds to minutes
            })
        
        return {
            "period_days": days,
            "total_trip_segments": total_trips,
            "mode_split": mode_split,
            "filters": {
                "region": region,
                "user_type": user_type
            }
        }
    
    async def get_temporal_patterns(self, days: int = 30, granularity: str = "hour") -> Dict:
        """Get temporal travel patterns"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Define grouping based on granularity
        if granularity == "hour":
            group_by = {"hour": {"$hour": "$trip_chain.start_time"}}
        elif granularity == "day":
            group_by = {"day": {"$dayOfWeek": "$trip_chain.start_time"}}
        else:  # week
            group_by = {"week": {"$week": "$trip_chain.start_time"}}
        
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$unwind": "$trip_chain"},
            {"$group": {
                "_id": group_by,
                "trip_count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"},
                "avg_cost": {"$avg": "$trip_chain.cost"},
                "common_modes": {"$push": "$trip_chain.mode"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        result = await self.trips_collection.aggregate(pipeline).to_list(None)
        
        # Process results
        patterns = []
        for item in result:
            # Count mode frequencies
            mode_counts = {}
            for mode in item["common_modes"]:
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
            most_common_mode = max(mode_counts.keys(), key=lambda x: mode_counts[x]) if mode_counts else "unknown"
            
            patterns.append({
                "time_period": item["_id"],
                "trip_count": item["trip_count"],
                "unique_users": len(item["unique_users"]),
                "avg_cost": round(item["avg_cost"] or 0, 2),
                "most_common_mode": most_common_mode
            })
        
        return {
            "period_days": days,
            "granularity": granularity,
            "temporal_patterns": patterns
        }
    
    async def get_origin_destination_matrix(self, days: int = 30, min_trips: int = 5) -> Dict:
        """Get origin-destination trip matrix"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$project": {
                "origin": {"$arrayElemAt": ["$trip_chain", 0]},
                "destination": {"$arrayElemAt": ["$trip_chain", -1]},
                "user_id": 1,
                "total_cost": 1,
                "trip_purpose": 1
            }},
            {"$group": {
                "_id": {
                    "origin": "$origin.origin.name",
                    "destination": "$destination.destination.name"
                },
                "trip_count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"},
                "avg_cost": {"$avg": "$total_cost"},
                "purposes": {"$push": "$trip_purpose"}
            }},
            {"$match": {"trip_count": {"$gte": min_trips}}},
            {"$sort": {"trip_count": -1}}
        ]
        
        result = await self.trips_collection.aggregate(pipeline).to_list(None)
        
        od_matrix = []
        for item in result:
            # Count purpose frequencies
            purpose_counts = {}
            for purpose in item["purposes"]:
                if purpose:
                    purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
            
            most_common_purpose = max(purpose_counts.keys(), key=lambda x: purpose_counts[x]) if purpose_counts else "unknown"
            
            od_matrix.append({
                "origin": item["_id"]["origin"] or "Unknown",
                "destination": item["_id"]["destination"] or "Unknown",
                "trip_count": item["trip_count"],
                "unique_users": len(item["unique_users"]),
                "avg_cost": round(item["avg_cost"] or 0, 2),
                "most_common_purpose": most_common_purpose
            })
        
        return {
            "period_days": days,
            "min_trips_threshold": min_trips,
            "od_pairs": od_matrix
        }
    
    async def get_food_consumption_patterns(self, days: int = 30, cuisine_type: Optional[str] = None) -> Dict:
        """Get food consumption patterns analysis"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        match_criteria = {"created_at": {"$gte": start_date}}
        if cuisine_type:
            match_criteria["dishes_ordered.cuisine_type"] = cuisine_type
        
        # Cuisine popularity pipeline
        cuisine_pipeline = [
            {"$match": match_criteria},
            {"$unwind": "$dishes_ordered"},
            {"$group": {
                "_id": "$dishes_ordered.cuisine_type",
                "dish_count": {"$sum": 1},
                "total_spent": {"$sum": "$dishes_ordered.price"},
                "avg_price": {"$avg": "$dishes_ordered.price"},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$sort": {"dish_count": -1}}
        ]
        
        cuisine_result = await self.food_collection.aggregate(cuisine_pipeline).to_list(None)
        
        # Meal type distribution pipeline
        meal_pipeline = [
            {"$match": match_criteria},
            {"$group": {
                "_id": "$meal_type",
                "count": {"$sum": 1},
                "avg_cost": {"$avg": "$total_cost"},
                "avg_rating": {"$avg": "$food_quality_rating"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        meal_result = await self.food_collection.aggregate(meal_pipeline).to_list(None)
        
        # Format results
        cuisine_patterns = []
        for item in cuisine_result:
            cuisine_patterns.append({
                "cuisine_type": item["_id"],
                "dish_count": item["dish_count"],
                "total_spent": round(item["total_spent"], 2),
                "avg_price": round(item["avg_price"], 2),
                "unique_users": len(item["unique_users"])
            })
        
        meal_patterns = []
        for item in meal_result:
            meal_patterns.append({
                "meal_type": item["_id"],
                "count": item["count"],
                "avg_cost": round(item["avg_cost"] or 0, 2),
                "avg_rating": round(item["avg_rating"] or 0, 1)
            })
        
        return {
            "period_days": days,
            "cuisine_filter": cuisine_type,
            "cuisine_patterns": cuisine_patterns,
            "meal_type_patterns": meal_patterns
        }
    
    async def get_food_transport_correlation(self, days: int = 30) -> Dict:
        """Get correlation between food choices and transport modes"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Pipeline to correlate food and transport data
        pipeline = [
            {"$match": {
                "created_at": {"$gte": start_date},
                "trip_segment_id": {"$exists": True, "$ne": None}
            }},
            {"$lookup": {
                "from": "trips",
                "let": {"segment_id": "$trip_segment_id", "user_id": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}}},
                    {"$unwind": "$trip_chain"},
                    {"$match": {"$expr": {"$eq": [{"$toString": "$trip_chain.segment_id"}, "$$segment_id"]}}}
                ],
                "as": "trip_info"
            }},
            {"$match": {"trip_info": {"$ne": []}}},
            {"$unwind": "$trip_info"},
            {"$group": {
                "_id": {
                    "transport_mode": "$trip_info.trip_chain.mode",
                    "cuisine_type": {"$arrayElemAt": ["$dishes_ordered.cuisine_type", 0]}
                },
                "combination_count": {"$sum": 1},
                "avg_food_cost": {"$avg": "$total_cost"},
                "avg_transport_cost": {"$avg": "$trip_info.trip_chain.cost"}
            }},
            {"$sort": {"combination_count": -1}}
        ]
        
        result = await self.food_collection.aggregate(pipeline).to_list(None)
        
        correlations = []
        for item in result:
            correlations.append({
                "transport_mode": item["_id"]["transport_mode"],
                "cuisine_type": item["_id"]["cuisine_type"],
                "combination_count": item["combination_count"],
                "avg_food_cost": round(item["avg_food_cost"], 2),
                "avg_transport_cost": round(item["avg_transport_cost"] or 0, 2)
            })
        
        return {
            "period_days": days,
            "correlations": correlations
        }
    
    async def get_user_engagement_metrics(self, days: int = 30) -> Dict:
        """Get user engagement and data quality metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # User activity metrics
        activity_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": "$user_id",
                "trip_count": {"$sum": 1},
                "avg_quality": {"$avg": "$data_quality_score"},
                "last_activity": {"$max": "$created_at"},
                "total_segments": {"$sum": {"$size": "$trip_chain"}}
            }},
            {"$group": {
                "_id": None,
                "active_users": {"$sum": 1},
                "avg_trips_per_user": {"$avg": "$trip_count"},
                "avg_data_quality": {"$avg": "$avg_quality"},
                "high_engagement_users": {
                    "$sum": {"$cond": [{"$gte": ["$trip_count", 10]}, 1, 0]}
                }
            }}
        ]
        
        activity_result = await self.trips_collection.aggregate(activity_pipeline).to_list(1)
        activity_metrics = activity_result[0] if activity_result else {}
        
        # Data completeness metrics
        completeness_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$unwind": "$trip_chain"},
            {"$group": {
                "_id": None,
                "total_segments": {"$sum": 1},
                "segments_with_cost": {"$sum": {"$cond": [{"$ne": ["$trip_chain.cost", None]}, 1, 0]}},
                "segments_with_photos": {"$sum": {"$cond": [{"$ne": ["$trip_chain.receipt_photo_url", None]}, 1, 0]}},
                "segments_with_ratings": {"$sum": {"$cond": [{"$ne": ["$trip_chain.comfort_rating", None]}, 1, 0]}}
            }}
        ]
        
        completeness_result = await self.trips_collection.aggregate(completeness_pipeline).to_list(1)
        completeness_metrics = completeness_result[0] if completeness_result else {}
        
        total_segments = completeness_metrics.get("total_segments", 1)
       
        return {
           "period_days": days,
           "user_engagement": {
               "active_users": activity_metrics.get("active_users", 0),
               "avg_trips_per_user": round(activity_metrics.get("avg_trips_per_user", 0), 1),
               "high_engagement_users": activity_metrics.get("high_engagement_users", 0),
               "engagement_rate": round((activity_metrics.get("high_engagement_users", 0) / max(activity_metrics.get("active_users", 1), 1)) * 100, 1)
           },
           "data_quality": {
               "avg_quality_score": round(activity_metrics.get("avg_data_quality", 0), 2),
               "cost_completeness": round((completeness_metrics.get("segments_with_cost", 0) / total_segments) * 100, 1),
               "photo_completeness": round((completeness_metrics.get("segments_with_photos", 0) / total_segments) * 100, 1),
               "rating_completeness": round((completeness_metrics.get("segments_with_ratings", 0) / total_segments) * 100, 1)
           }
       }
   
    async def export_trip_data(self, format: str = "csv", days: int = 30, include_personal_data: bool = False) -> Dict:
       """Export trip data for research"""
       start_date = datetime.utcnow() - timedelta(days=days)
       
       # Define projection based on privacy settings
       projection = {
           "trip_id": 1,
           "trip_chain": 1,
           "group_details": 1,
           "trip_purpose": 1,
           "total_cost": 1,
           "total_duration_minutes": 1,
           "total_distance_km": 1,
           "data_quality_score": 1,
           "created_at": 1
       }
       
       if not include_personal_data:
           # Anonymize user data
           projection["user_id"] = {"$substr": ["$user_id", 0, 8]}  # Only first 8 chars
       else:
           projection["user_id"] = 1
       
       cursor = self.trips_collection.find(
           {"created_at": {"$gte": start_date}},
           projection
       ).sort("created_at", -1)
       
       trips = await cursor.to_list(None)
       
       if format.lower() == "csv":
           # Convert to CSV format
           output = io.StringIO()
           if trips:
               # Flatten trip data for CSV
               flattened_data = []
               for trip in trips:
                   base_data = {
                       "trip_id": trip["trip_id"],
                       "user_id": trip["user_id"],
                       "trip_purpose": trip["trip_purpose"],
                       "total_cost": trip["total_cost"],
                       "total_duration_minutes": trip["total_duration_minutes"],
                       "total_distance_km": trip["total_distance_km"],
                       "data_quality_score": trip["data_quality_score"],
                       "created_at": trip["created_at"].isoformat(),
                       "group_size": trip["group_details"]["total_members"],
                       "group_type": trip["group_details"]["group_type"]
                   }
                   
                   # Add segment data
                   for i, segment in enumerate(trip["trip_chain"]):
                       segment_data = base_data.copy()
                       segment_data.update({
                           "segment_number": i + 1,
                           "segment_mode": segment["mode"],
                           "segment_start_time": segment["start_time"].isoformat(),
                           "segment_end_time": segment["end_time"].isoformat(),
                           "segment_distance_km": segment.get("distance_km"),
                           "segment_cost": segment.get("cost"),
                           "segment_comfort_rating": segment.get("comfort_rating")
                       })
                       flattened_data.append(segment_data)
               
               if flattened_data:
                   writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
                   writer.writeheader()
                   writer.writerows(flattened_data)
           
           return {
               "format": "csv",
               "data": output.getvalue(),
               "record_count": len(trips),
               "generated_at": datetime.utcnow().isoformat()
           }
       
       else:  # JSON format
           # Convert ObjectId and datetime to strings for JSON serialization
           for trip in trips:
               trip["_id"] = str(trip.get("_id", ""))
               trip["created_at"] = trip["created_at"].isoformat()
               for segment in trip["trip_chain"]:
                   segment["start_time"] = segment["start_time"].isoformat()
                   segment["end_time"] = segment["end_time"].isoformat()
           
           return {
               "format": "json",
               "data": trips,
               "record_count": len(trips),
               "generated_at": datetime.utcnow().isoformat()
           }
   
    async def export_food_data(self, format: str = "csv", days: int = 30, include_personal_data: bool = False) -> Dict:
       """Export food consumption data for research"""
       start_date = datetime.utcnow() - timedelta(days=days)
       
       # Define projection
       projection = {
           "food_id": 1,
           "location": 1,
           "meal_type": 1,
           "dishes_ordered": 1,
           "total_cost": 1,
           "cost_per_person": 1,
           "service_rating": 1,
           "food_quality_rating": 1,
           "cultural_authenticity_rating": 1,
           "dining_companions": 1,
           "local_recommendation": 1,
           "dietary_restrictions": 1,
           "language_barrier": 1,
           "created_at": 1
       }
       
       if not include_personal_data:
           projection["user_id"] = {"$substr": ["$user_id", 0, 8]}
       else:
           projection["user_id"] = 1
       
       cursor = self.food_collection.find(
           {"created_at": {"$gte": start_date}},
           projection
       ).sort("created_at", -1)
       
       food_entries = await cursor.to_list(None)
       
       if format.lower() == "csv":
           output = io.StringIO()
           if food_entries:
               flattened_data = []
               for entry in food_entries:
                   base_data = {
                       "food_id": entry["food_id"],
                       "user_id": entry["user_id"],
                       "restaurant_name": entry["location"]["restaurant_name"],
                       "cuisine_type": entry["location"]["cuisine_type"],
                       "establishment_type": entry["location"]["establishment_type"],
                       "meal_type": entry["meal_type"],
                       "total_cost": entry["total_cost"],
                       "cost_per_person": entry["cost_per_person"],
                       "service_rating": entry.get("service_rating"),
                       "food_quality_rating": entry.get("food_quality_rating"),
                       "cultural_authenticity_rating": entry.get("cultural_authenticity_rating"),
                       "dining_companions": entry["dining_companions"],
                       "local_recommendation": entry["local_recommendation"],
                       "language_barrier": entry["language_barrier"],
                       "created_at": entry["created_at"].isoformat()
                   }
                   
                   # Add dish data
                   for i, dish in enumerate(entry["dishes_ordered"]):
                       dish_data = base_data.copy()
                       dish_data.update({
                           "dish_number": i + 1,
                           "dish_name": dish["name"],
                           "dish_cuisine_type": dish["cuisine_type"],
                           "dish_price": dish["price"],
                           "dish_vegetarian": dish["vegetarian"],
                           "dish_local_specialty": dish["local_specialty"]
                       })
                       flattened_data.append(dish_data)
               
               if flattened_data:
                   writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
                   writer.writeheader()
                   writer.writerows(flattened_data)
           
           return {
               "format": "csv",
               "data": output.getvalue(),
               "record_count": len(food_entries),
               "generated_at": datetime.utcnow().isoformat()
           }
       
       else:  # JSON format
           for entry in food_entries:
               entry["_id"] = str(entry.get("_id", ""))
               entry["created_at"] = entry["created_at"].isoformat()
           
           return {
               "format": "json",
               "data": food_entries,
               "record_count": len(food_entries),
               "generated_at": datetime.utcnow().isoformat()
           }
   
    async def get_live_active_trips(self) -> List[Dict]:
       """Get currently active trips for live dashboard"""
       # Consider trips started in last 4 hours as potentially active
       recent_time = datetime.utcnow() - timedelta(hours=4)
       
       pipeline = [
           {"$match": {"created_at": {"$gte": recent_time}}},
           {"$lookup": {
               "from": "users",
               "localField": "user_id",
               "foreignField": "user_id",
               "as": "user_info"
           }},
           {"$project": {
               "trip_id": 1,
               "user_type": {"$arrayElemAt": ["$user_info.user_type", 0]},
               "current_location": {"$arrayElemAt": [{"$arrayElemAt": ["$trip_chain", -1]}, 0]},  # Last segment's destination
               "current_mode": {"$arrayElemAt": [{"$arrayElemAt": ["$trip_chain.mode", -1]}, 0]},
               "trip_purpose": 1,
               "started_at": "$created_at",
               "group_size": "$group_details.total_members"
           }},
           {"$sort": {"created_at": -1}},
           {"$limit": 50}
       ]
       
       active_trips = await self.trips_collection.aggregate(pipeline).to_list(None)
       
       # Format for frontend
       formatted_trips = []
       for trip in active_trips:
           if trip.get("current_location"):
               formatted_trips.append({
                   "trip_id": trip["trip_id"],
                   "user_type": trip.get("user_type", "unknown"),
                   "location": {
                       "lat": trip["current_location"].get("destination", {}).get("lat"),
                       "lng": trip["current_location"].get("destination", {}).get("lng"),
                       "name": trip["current_location"].get("destination", {}).get("name", "Unknown")
                   },
                   "transport_mode": trip.get("current_mode", "unknown"),
                   "trip_purpose": trip.get("trip_purpose", "unknown"),
                   "group_size": trip.get("group_size", 1),
                   "started_at": trip["started_at"].isoformat() if trip.get("started_at") else None
               })
       
       return formatted_trips
   
    async def get_trip_density_heatmap(self, days: int = 7, time_of_day: Optional[str] = None, transport_mode: Optional[str] = None) -> Dict:
       """Get trip density data for heatmap visualization"""
       start_date = datetime.utcnow() - timedelta(days=days)
       
       # Build match criteria
       match_criteria = {"created_at": {"$gte": start_date}}
       
       # Time of day filter
       time_filter = {}
       if time_of_day:
           if time_of_day == "morning":
               time_filter = {"$gte": 6, "$lt": 12}
           elif time_of_day == "afternoon":
               time_filter = {"$gte": 12, "$lt": 18}
           elif time_of_day == "evening":
               time_filter = {"$gte": 18, "$lt": 22}
           elif time_of_day == "night":
               time_filter = {"$or": [{"$gte": 22}, {"$lt": 6}]}
       
       pipeline = [
           {"$match": match_criteria},
           {"$unwind": "$trip_chain"}
       ]
       
       # Add time filter if specified
       if time_filter:
           pipeline.append({
               "$match": {"$expr": {"$and": [
                   time_filter if "$or" not in time_filter else time_filter,
                   {"$eq": [{"$hour": "$trip_chain.start_time"}, {"$hour": "$trip_chain.start_time"}]}
               ]}}
           })
       
       # Add transport mode filter
       if transport_mode:
           pipeline.append({"$match": {"trip_chain.mode": transport_mode}})
       
       # Group by location
       pipeline.extend([
           {"$group": {
               "_id": {
                   "lat": {"$round": [{"$multiply": ["$trip_chain.origin.lat", 100]}, 0]},  # Round to ~1km precision
                   "lng": {"$round": [{"$multiply": ["$trip_chain.origin.lng", 100]}, 0]}
               },
               "trip_count": {"$sum": 1},
               "unique_users": {"$addToSet": "$user_id"},
               "avg_lat": {"$avg": "$trip_chain.origin.lat"},
               "avg_lng": {"$avg": "$trip_chain.origin.lng"}
           }},
           {"$match": {"trip_count": {"$gte": 2}}},  # Only include locations with multiple trips
           {"$sort": {"trip_count": -1}},
           {"$limit": 200}  # Limit for performance
       ])
       
       result = await self.trips_collection.aggregate(pipeline).to_list(None)
       
       # Format for heatmap
       heatmap_points = []
       max_intensity = max([item["trip_count"] for item in result]) if result else 1
       
       for item in result:
           heatmap_points.append({
               "lat": item["avg_lat"],
               "lng": item["avg_lng"],
               "intensity": item["trip_count"] / max_intensity,  # Normalized intensity
               "trip_count": item["trip_count"],
               "unique_users": len(item["unique_users"])
           })
       
       return {
           "period_days": days,
           "time_of_day": time_of_day,
           "transport_mode": transport_mode,
           "heatmap_points": heatmap_points,
           "max_intensity": max_intensity
       }