import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
import uuid

async def setup_database():
    """Set up MongoDB collections and indexes"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.natpac_transport
    
    # Create indexes for better performance
    
    # Users collection indexes
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_type")
    await db.users.create_index("created_at")
    
    # Trips collection indexes
    await db.trips.create_index("trip_id", unique=True)
    await db.trips.create_index("user_id")
    await db.trips.create_index("created_at")
    await db.trips.create_index("trip_purpose")
    await db.trips.create_index("data_quality_score")
    await db.trips.create_index([("created_at", -1), ("user_id", 1)])
    
    # Food collection indexes
    await db.food_consumption.create_index("food_id", unique=True)
    await db.food_consumption.create_index("user_id")
    await db.food_consumption.create_index("created_at")
    await db.food_consumption.create_index("location.cuisine_type")
    await db.food_consumption.create_index("meal_type")
    
    # Restaurants collection indexes with geospatial index
    await db.restaurants.create_index("restaurant_id", unique=True)
    await db.restaurants.create_index([("location", "2dsphere")])
    await db.restaurants.create_index("cuisine_type")
    await db.restaurants.create_index("establishment_type")
    
    # Live locations collection (temporary data)
    await db.live_locations.create_index("user_id")
    await db.live_locations.create_index("created_at")
    await db.live_locations.create_index("processed")
    # TTL index to auto-delete old location data after 24 hours
    await db.live_locations.create_index("created_at", expireAfterSeconds=86400)
    
    print("Database setup completed with indexes")

async def create_sample_data():
    """Create sample data for development and demo"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.natpac_transport
    
    # Sample users
    sample_users = [
        {
            "user_id": str(uuid.uuid4()),
            "email": "tourist1@example.com",
            "full_name": "John Doe",
            "user_type": "tourist",
            "preferred_language": "english",
            "age_group": "26-35",
            "location": "International",
            "is_active": True,
            "gamification_score": 450,
            "badges_earned": ["first_trip", "photo_master"],
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow()
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "local1@example.com",
            "full_name": "Priya Nair",
            "user_type": "local",
            "preferred_language": "malayalam",
            "age_group": "26-35",
            "location": "Kochi, Kerala",
            "is_active": True,
            "gamification_score": 1250,
            "badges_earned": ["data_champion", "bus_explorer", "food_enthusiast"],
            "created_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow()
        },
        {
            "user_id": str(uuid.uuid4()),
            "email": "researcher@natpac.gov.in",
            "full_name": "Dr. Rajesh Kumar",
            "user_type": "researcher",
            "preferred_language": "english",
            "age_group": "36-50",
            "location": "Thiruvananthapuram, Kerala",
            "is_active": True,
            "gamification_score": 0,
            "badges_earned": [],
            "created_at": datetime.utcnow() - timedelta(days=90),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.users.insert_many(sample_users)
    
    # Sample restaurants
    sample_restaurants = [
        {
            "restaurant_id": str(uuid.uuid4()),
            "name": "Saravana Bhavan",
            "location": {
                "type": "Point",
                "coordinates": [76.9366, 8.5241]  # [lng, lat] for GeoJSON
            },
            "address": "MG Road, Ernakulam, Kochi",
            "cuisine_type": "south_indian",
            "establishment_type": "restaurant",
            "avg_cost_per_person": 200,
            "rating": 4.2,
            "popular_dishes": ["Masala Dosa", "Idli Sambar", "Filter Coffee"],
            "transport_accessibility": "excellent",
            "visit_count": 45,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        },
        {
            "restaurant_id": str(uuid.uuid4()),
            "name": "Kerala Kitchen",
            "location": {
                "type": "Point",
                "coordinates": [76.9544, 8.4875]
            },
            "address": "Fort Kochi",
            "cuisine_type": "kerala_traditional",
            "establishment_type": "local_eatery",
            "avg_cost_per_person": 350,
            "rating": 4.5,
            "popular_dishes": ["Fish Curry", "Appam", "Beef Fry"],
            "transport_accessibility": "good",
            "visit_count": 23,
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.restaurants.insert_many(sample_restaurants)
    
    # Sample trips
    user_ids = [user["user_id"] for user in sample_users[:2]]  # Tourist and local user
    
    sample_trips = []
    for i in range(20):
        user_id = random.choice(user_ids)
        trip_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        # Generate random trip segments
        segments = []
        num_segments = random.randint(1, 4)
        
        for j in range(num_segments):
            segment_start = trip_date + timedelta(minutes=j*30)
            segment_end = segment_start + timedelta(minutes=random.randint(10, 45))
            
            segments.append({
                "segment_id": j + 1,
                "mode": random.choice(["walk", "bus", "auto_rickshaw", "car", "bicycle"]),
                "sub_mode": "KSRTC_ordinary" if segments and segments[-1].get("mode") == "bus" else None,
                "start_time": segment_start,
                "end_time": segment_end,
                "origin": {
                    "lat": 8.5241 + random.uniform(-0.1, 0.1),
                    "lng": 76.9366 + random.uniform(-0.1, 0.1),
                    "name": random.choice(["Ernakulam", "Fort Kochi", "Marine Drive", "MG Road"])
                },
                "destination": {
                    "lat": 8.5241 + random.uniform(-0.1, 0.1),
                    "lng": 76.9366 + random.uniform(-0.1, 0.1),
                    "name": random.choice(["Mattancherry", "Vytilla", "Kakkanad", "Edappally"])
                },
                "distance_km": random.uniform(2, 25),
                "cost": random.uniform(10, 150),
                "waiting_time_minutes": random.randint(0, 15) if j > 0 else 0,
                "comfort_rating": random.randint(2, 5),
                "occupancy_level": random.choice(["comfortable", "moderate", "crowded"]),
                "weather": random.choice(["sunny", "cloudy", "rainy"])
            })
        
        total_cost = sum(s["cost"] for s in segments)
        total_distance = sum(s["distance_km"] for s in segments)
        total_duration = sum((s["end_time"] - s["start_time"]).total_seconds() / 60 for s in segments)
        
        trip = {
            "trip_id": str(uuid.uuid4()),
            "user_id": user_id,
            "trip_chain": segments,
            "group_details": {
                "total_members": random.randint(1, 6),
                "group_type": random.choice(["solo", "couple", "family", "friends"]),
                "companions": []
            },
            "trip_purpose": random.choice(["work", "education", "shopping", "tourism", "social", "medical"]),
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "total_distance_km": total_distance,
            "data_quality_score": random.uniform(0.6, 1.0),
            "user_notes": random.choice([None, "Good trip", "Heavy traffic", "Pleasant journey"]),
            "created_at": trip_date,
            "updated_at": trip_date
        }
        
        sample_trips.append(trip)
    
    await db.trips.insert_many(sample_trips)
    
    # Sample food entries
    sample_food_entries = []
    for i in range(15):
        user_id = random.choice(user_ids)
        meal_date = datetime.utcnow() - timedelta(days=random.randint(1, 20))
        
        dishes = [
            {
                "name": random.choice(["Sadya", "Fish Curry", "Appam", "Dosa", "Biryani"]),
                "cuisine_type": random.choice(["kerala_traditional", "south_indian", "north_indian"]),
                "price": random.uniform(80, 300),
                "quantity": 1,
                "vegetarian": random.choice([True, False]),
                "local_specialty": random.choice([True, False])
            }
        ]
        
        food_entry = {
            "food_id": str(uuid.uuid4()),
            "user_id": user_id,
            "trip_segment_id": None,
            "location": {
                "restaurant_name": random.choice(["Saravana Bhavan", "Kerala Kitchen", "Pai Restaurant", "Hotel Rahmath"]),
                "lat": 8.5241 + random.uniform(-0.05, 0.05),
                "lng": 76.9366 + random.uniform(-0.05, 0.05),
                "cuisine_type": random.choice(["kerala_traditional", "south_indian", "north_indian"]),
                "establishment_type": random.choice(["restaurant", "local_eatery", "hotel"])
            },
            "meal_type": random.choice(["breakfast", "lunch", "dinner", "snack"]),
            "dishes_ordered": dishes,
            "total_cost": sum(d["price"] for d in dishes),
            "cost_per_person": sum(d["price"] for d in dishes) / random.randint(1, 4),
            "payment_method": random.choice(["cash", "upi", "card"]),
            "service_rating": random.randint(3, 5),
            "food_quality_rating": random.randint(3, 5),
            "cultural_authenticity_rating": random.randint(2, 5),
            "dining_companions": random.randint(1, 4),
            "local_recommendation": random.choice([True, False]),
            "dietary_restrictions": [],
            "language_barrier": random.choice([True, False]),
            "created_at": meal_date,
            "updated_at": meal_date
        }
        
        sample_food_entries.append(food_entry)
    
    await db.food_consumption.insert_many(sample_food_entries)
    
    print(f"Sample data created:")
    print(f"- {len(sample_users)} users")
    print(f"- {len(sample_restaurants)} restaurants") 
    print(f"- {len(sample_trips)} trips")
    print(f"- {len(sample_food_entries)} food entries")

if __name__ == "__main__":
    asyncio.run(setup_database())
    asyncio.run(create_sample_data())