from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class GenericResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    message: str
    email: str
    password: str

class SignupResponse(BaseModel):
    message: str
    email: str
    password: str

class UploadResponse(BaseModel):
    success: bool
    waste_type: str
    subcategory: str
    item_name: str
    
    predicted_label: Optional[str] = "Unknown"
    confidence_score: float = 0.0
    classification_source: str = "fallback"
    image_url: Optional[str] = None
    
    recyclable_status: str
    energy_potential: str
    recommended_treatment: str
    disposal_instructions: str
    carbon_saved: float
    trees_equivalent: float
    sustainability_score: float
    reward_points: int
    impact_message: str

class UserStats(BaseModel):
    uploads: int
    total_points: int
    total_carbon: float

class WeeklyCarbon(BaseModel):
    week: str
    carbon: float

class StreakResponse(BaseModel):
    streak: int

class LeaderboardEntry(BaseModel):
    rank: int
    email: str
    points: int

class RewardItem(BaseModel):
    name: str
    points_required: int

class CampaignItem(BaseModel):
    title: str
    locality: str

class HealthCheckResponse(BaseModel):
    status: str

class HistoryEntry(BaseModel):
    id: int
    waste_type: str
    subcategory: Optional[str] = None
    item_name: Optional[str] = None
    predicted_label: Optional[str] = None
    confidence_score: Optional[float] = None
    classification_source: Optional[str] = None
    weight: Optional[float] = None
    image_url: Optional[str] = None
    carbon: Optional[float] = None
    points: Optional[int] = None
    date: str

class UserHistoryResponse(BaseModel):
    logs: List[HistoryEntry]

class UserProfileResponse(BaseModel):
    email: str
    full_name: str
    profile_picture_url: Optional[str] = None
