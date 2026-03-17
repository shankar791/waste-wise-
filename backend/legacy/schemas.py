from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class GenericResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    message: str
    email: str

class SignupResponse(BaseModel):
    message: str
    email: str

class UploadResponse(BaseModel):
    success: bool
    waste_type: str
    subcategory: str
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
