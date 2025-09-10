import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class MockDatabase:
    """In-memory database for testing and development"""
    
    def __init__(self):
        self.trips: List[Dict[str, Any]] = []
        self.food_entries: List[Dict[str, Any]] = []
        self.users: List[Dict[str, Any]] = []
        
        # Add some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with some sample data for demonstration"""
        # Sample trips
        sample_trips = [
            {
                "_id": str(uuid.uuid4()),
                "transport_mode": "bus",
                "purpose": "work",
                "start_location": {"city": "Kochi", "latitude": 9.9312, "longitude": 76.2673},
                "end_location": {"city": "Ernakulam", "latitude": 9.9816, "longitude": 76.2999},
                "cost": 25.0,
                "number_of_people": 1,
                "created_at": "2024-12-26T09:00:00"
            },
            {
                "_id": str(uuid.uuid4()),
                "transport_mode": "auto",
                "purpose": "shopping",
                "start_location": {"city": "Thiruvananthapuram", "latitude": 8.5241, "longitude": 76.9366},
                "end_location": {"city": "Kovalam", "latitude": 8.4004, "longitude": 76.9784},
                "cost": 150.0,
                "number_of_people": 2,
                "created_at": "2024-12-26T14:30:00"
            }
        ]
        
        # Sample food entries
        sample_food = [
            {
                "_id": str(uuid.uuid4()),
                "restaurant_name": "Kerala House",
                "cuisine_type": "kerala",
                "meal_type": "lunch",
                "total_cost": 200.0,
                "number_of_people": 2,
                "notes": "Excellent fish curry and appam",
                "location": {"city": "Kochi", "latitude": 9.9312, "longitude": 76.2673},
                "created_at": "2024-12-26T13:00:00"
            },
            {
                "_id": str(uuid.uuid4()),
                "restaurant_name": "Spice Garden",
                "cuisine_type": "south_indian",
                "meal_type": "dinner",
                "total_cost": 350.0,
                "number_of_people": 3,
                "notes": "Great variety of dosas",
                "location": {"city": "Thiruvananthapuram", "latitude": 8.5241, "longitude": 76.9366},
                "created_at": "2024-12-26T19:30:00"
            }
        ]
        
        self.trips.extend(sample_trips)
        self.food_entries.extend(sample_food)
    
    # Trip methods
    def add_trip(self, trip_data: Dict[str, Any]) -> str:
        """Add a new trip and return its ID"""
        trip_id = str(uuid.uuid4())
        trip_data["_id"] = trip_id
        if "created_at" not in trip_data:
            trip_data["created_at"] = datetime.now().isoformat()
        self.trips.append(trip_data)
        return trip_id
    
    def get_trips(self) -> List[Dict[str, Any]]:
        """Get all trips"""
        return self.trips.copy()
    
    def get_trip_by_id(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Get a trip by its ID"""
        for trip in self.trips:
            if trip.get("_id") == trip_id:
                return trip.copy()
        return None
    
    def update_trip(self, trip_id: str, trip_data: Dict[str, Any]) -> bool:
        """Update a trip by its ID"""
        for i, trip in enumerate(self.trips):
            if trip.get("_id") == trip_id:
                trip_data["_id"] = trip_id
                trip_data["updated_at"] = datetime.now().isoformat()
                self.trips[i] = trip_data
                return True
        return False
    
    def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip by its ID"""
        for i, trip in enumerate(self.trips):
            if trip.get("_id") == trip_id:
                del self.trips[i]
                return True
        return False
    
    # Food entry methods
    def add_food_entry(self, food_data: Dict[str, Any]) -> str:
        """Add a new food entry and return its ID"""
        food_id = str(uuid.uuid4())
        food_data["_id"] = food_id
        if "created_at" not in food_data:
            food_data["created_at"] = datetime.now().isoformat()
        self.food_entries.append(food_data)
        return food_id
    
    def get_food_entries(self) -> List[Dict[str, Any]]:
        """Get all food entries"""
        return self.food_entries.copy()
    
    def get_food_entry_by_id(self, food_id: str) -> Optional[Dict[str, Any]]:
        """Get a food entry by its ID"""
        for food in self.food_entries:
            if food.get("_id") == food_id:
                return food.copy()
        return None
    
    def update_food_entry(self, food_id: str, food_data: Dict[str, Any]) -> bool:
        """Update a food entry by its ID"""
        for i, food in enumerate(self.food_entries):
            if food.get("_id") == food_id:
                food_data["_id"] = food_id
                food_data["updated_at"] = datetime.now().isoformat()
                self.food_entries[i] = food_data
                return True
        return False
    
    def delete_food_entry(self, food_id: str) -> bool:
        """Delete a food entry by its ID"""
        for i, food in enumerate(self.food_entries):
            if food.get("_id") == food_id:
                del self.food_entries[i]
                return True
        return False
    
    # User methods
    def add_user(self, user_data: Dict[str, Any]) -> str:
        """Add a new user and return its ID"""
        user_id = str(uuid.uuid4())
        user_data["_id"] = user_id
        if "created_at" not in user_data:
            user_data["created_at"] = datetime.now().isoformat()
        self.users.append(user_data)
        return user_id
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        return self.users.copy()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by their ID"""
        for user in self.users:
            if user.get("_id") == user_id:
                return user.copy()
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email"""
        for user in self.users:
            if user.get("email") == email:
                return user.copy()
        return None
    
    # Analytics methods
    def get_trip_statistics(self) -> Dict[str, Any]:
        """Get trip statistics"""
        if not self.trips:
            return {"total_trips": 0, "total_cost": 0, "avg_cost": 0}
        
        total_cost = sum(trip.get("cost", 0) for trip in self.trips)
        return {
            "total_trips": len(self.trips),
            "total_cost": total_cost,
            "avg_cost": total_cost / len(self.trips)
        }
    
    def get_food_statistics(self) -> Dict[str, Any]:
        """Get food statistics"""
        if not self.food_entries:
            return {"total_entries": 0, "total_cost": 0, "avg_cost": 0}
        
        total_cost = sum(food.get("total_cost", 0) for food in self.food_entries)
        return {
            "total_entries": len(self.food_entries),
            "total_cost": total_cost,
            "avg_cost": total_cost / len(self.food_entries)
        }
    
    def clear_all_data(self):
        """Clear all data (for testing)"""
        self.trips.clear()
        self.food_entries.clear()
        self.users.clear()
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            "trips_count": len(self.trips),
            "food_entries_count": len(self.food_entries),
            "users_count": len(self.users)
        }
