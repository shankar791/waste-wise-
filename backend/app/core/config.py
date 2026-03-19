from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Project Roots
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "WasteWise API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Premium eco-app for waste classification, carbon tracking, and green rewards"
    APP_AUTHOR: str = "WasteWise Team"
    APP_HOMEPAGE: str = "https://wastewise.eco"

    # Force SQLite for local usage seamlessly
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local_db.sqlite3")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_here")

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    CORS_ORIGINS: str | list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    # AI Classification Settings
    AI_CONFIDENCE_THRESHOLD: float = 0.55

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Upload Path mapping
UPLOAD_PATH: Path = PROJECT_ROOT / settings.UPLOAD_DIR
MAX_UPLOAD_SIZE_BYTES: int = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

CARBON_EMISSIONS = {
    "wet": 0.5,
    "dry": 1.5,
    "e-waste": 2.0,
    "hazardous": 1.2,
}

DISPOSAL_MAP = {
    "wet": {
        "recyclable_status": "non-recyclable",
        "energy_potential": "biofuel",
        "treatment": "compost",
        "instructions": "Put into green bin or compost pit",
    },
    "dry": {
        "recyclable_status": "recyclable",
        "energy_potential": "rdf",
        "treatment": "recycle",
        "instructions": "Clean and put into blue bin",
    },
    "e-waste": {
        "recyclable_status": "recyclable",
        "energy_potential": "none",
        "treatment": "e-waste recycling",
        "instructions": "Drop at authorized e-waste center",
    },
    "hazardous": {
        "recyclable_status": "non-recyclable",
        "energy_potential": "none",
        "treatment": "hazardous disposal",
        "instructions": "Hand over to hazardous collection unit",
    },
}

WASTE_KEYWORDS = {
    "wet": {
        "food": ["banana", "food", "peel", "vegetable", "fruit", "organic", "kitchen"],
        "garden": ["leaf", "garden", "grass", "plant"],
    },
    "dry": {
        "plastic": ["bottle", "plastic", "bag", "poly", "sachet"],
        "paper": ["paper", "cardboard", "newspaper", "box"],
        "metal": ["can", "tin", "metal", "aluminium", "steel"],
        "glass": ["glass", "jar", "vessel"],
        "cloth": ["cloth", "shirt", "fabric", "textile", "jeans", "dress"],
    },
    "e-waste": {
        "mobile": ["mobile", "phone", "charger", "cable"],
        "laptop": ["laptop", "computer", "monitor", "keyboard"],
        "electronics": ["tv", "television", "remote"],
    },
    "hazardous": {
        "battery": ["battery", "cell", "acid"],
        "chemical": ["paint", "chemical", "oil", "solvent"],
    },
}
