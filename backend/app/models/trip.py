from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TransportMode(str, Enum):
    WALK = "walk"
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    AUTO_RICKSHAW = "auto_rickshaw"
    BUS = "bus"
    TRAIN = "train"
    METRO = "metro"
    FERRY = "ferry"
    TAXI = "taxi"
    RIDE_SHARE = "ride_share"

class TripPurpose(str, Enum):
    WORK = "work"
    EDUCATION = "education"
    SHOPPING = "shopping"
    MEDICAL = "medical"
    SOCIAL = "social"
    RECREATION = "recreation"
    TOURISM = "tourism"
    OTHER = "other"

class GroupType(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"
    BUSINESS = "business"
    STUDENT_GROUP = "student_group"

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None
    address: Optional[str] = None

class TripSegment(BaseModel):
    segment_id: int
    mode: TransportMode
    sub_mode: Optional[str] = None
    start_time: datetime
    end_time: datetime
    origin: Location
    destination: Location
    distance_km: Optional[float] = None
    cost: Optional[float] = None
    waiting_time_minutes: Optional[int] = None
    comfort_rating: Optional[int] = Field(None, ge=1, le=5)
    occupancy_level: Optional[str] = None
    delays: Optional[List[str]] = []
    receipt_photo_url: Optional[str] = None
    weather: Optional[str] = None
    notes: Optional[str] = None

class GroupDetails(BaseModel):
    total_members: int = Field(..., ge=1)
    group_type: GroupType
    age_distribution: Optional[Dict[str, int]] = None  # {"adults": 2, "children": 1, "elderly": 0}
    companions: Optional[List[str]] = []

class TripCreate(BaseModel):
    trip_chain: List[TripSegment]
    group_details: GroupDetails
    trip_purpose: TripPurpose
    user_notes: Optional[str] = None

class TripUpdate(BaseModel):
    trip_chain: Optional[List[TripSegment]] = None
    group_details: Optional[GroupDetails] = None
    trip_purpose: Optional[TripPurpose] = None
    user_notes: Optional[str] = None

class TripResponse(BaseModel):
    trip_id: str
    user_id: str
    trip_chain: List[TripSegment]
    group_details: GroupDetails
    trip_purpose: TripPurpose
    total_cost: float
    total_duration_minutes: int
    total_distance_km: float
    data_quality_score: float
    created_at: datetime
    updated_at: datetime
    user_notes: Optional[str] = None