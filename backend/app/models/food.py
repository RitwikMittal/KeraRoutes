from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class CuisineType(str, Enum):
    KERALA_TRADITIONAL = "kerala_traditional"
    SOUTH_INDIAN = "south_indian"
    NORTH_INDIAN = "north_indian"
    CHINESE = "chinese"
    CONTINENTAL = "continental"
    FAST_FOOD = "fast_food"
    STREET_FOOD = "street_food"
    SEAFOOD = "seafood"

class EstablishmentType(str, Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    STREET_VENDOR = "street_vendor"
    FOOD_COURT = "food_court"
    LOCAL_EATERY = "local_eatery"
    FINE_DINING = "fine_dining"
    CAFETERIA = "cafeteria"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    BEVERAGE = "beverage"

class DishItem(BaseModel):
    name: str
    cuisine_type: CuisineType
    price: float
    quantity: int = 1
    vegetarian: bool = True
    spice_level: Optional[str] = None  # mild, medium, hot
    local_specialty: bool = False

class FoodLocation(BaseModel):
    restaurant_name: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    cuisine_type: CuisineType
    establishment_type: EstablishmentType
    accessibility_from_transport: Optional[str] = None

class FoodConsumptionCreate(BaseModel):
    trip_segment_id: Optional[str] = None  # Link to transport trip
    location: FoodLocation
    meal_type: MealType
    dishes_ordered: List[DishItem]
    total_cost: float
    cost_per_person: float
    payment_method: str
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    food_quality_rating: Optional[int] = Field(None, ge=1, le=5)
    cultural_authenticity_rating: Optional[int] = Field(None, ge=1, le=5)
    dining_companions: int = 1
    local_recommendation: bool = False
    dietary_restrictions: Optional[List[str]] = []
    language_barrier: bool = False
    bill_photo_url: Optional[str] = None
    food_photo_urls: Optional[List[str]] = []

class FoodTransportNexus(BaseModel):
    transport_mode_used: Optional[str] = None
    travel_time_to_food: Optional[int] = None  # minutes
    transport_cost_to_reach: Optional[float] = None
    accessibility_rating: Optional[int] = Field(None, ge=1, le=5)
    detour_from_main_route: bool = False
    recommendation_source: Optional[str] = None

class FoodConsumptionResponse(BaseModel):
    food_id: str
    user_id: str
    trip_segment_id: Optional[str] = None
    location: FoodLocation
    meal_type: MealType
    dishes_ordered: List[DishItem]
    total_cost: float
    cost_per_person: float
    transport_nexus: Optional[FoodTransportNexus] = None
    created_at: datetime
    updated_at: datetime