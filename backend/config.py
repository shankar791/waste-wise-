"""Configuration management for the WasteWise application."""
import os
from pathlib import Path
from typing import Set

# Product Information
PRODUCT_NAME: str = "WasteWise"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = "Premium eco-app for waste classification, carbon tracking, and green rewards"
APP_AUTHOR: str = "WasteWise Team"
APP_HOMEPAGE: str = "https://wastewise.eco"

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Database
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "waste_data.db")
DB_PATH: str = os.path.join(PROJECT_ROOT, "backend", DATABASE_NAME)

# Upload settings
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_PATH: Path = Path(__file__).resolve().parent / UPLOAD_DIR
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS: Set[str] = set(
    os.getenv("ALLOWED_FILE_EXTENSIONS", "jpg,jpeg,png,gif,webp").lower().split(",")
)

# CORS
CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "app.log")

# Carbon emission constants (kg CO2 per weight unit)
CARBON_EMISSIONS: dict = {
    "wet": 0.5,
    "dry": 1.5,
    "e-waste": 2.0,
    "hazardous": 1.2,
}

# Waste disposal information
DISPOSAL_MAP: dict = {
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

# Waste classification keywords
WASTE_KEYWORDS: dict = {
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
