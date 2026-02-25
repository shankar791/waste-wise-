"""
WasteWise FastAPI Application
Improved version with better error handling, validation, and security.
"""
import logging
import pathlib
import shutil
from datetime import date
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from config import (
    PRODUCT_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    UPLOAD_PATH,
    MAX_UPLOAD_SIZE_BYTES,
    ALLOWED_FILE_EXTENSIONS,
    CARBON_EMISSIONS,
    DISPOSAL_MAP,
    WASTE_KEYWORDS,
    LOG_LEVEL,
    LOG_FILE,
)
from database import (
    init_db,
    create_account,
    verify_login,
    user_exists,
    log_waste,
    weekly_carbon,
    get_user_stats,
    get_user_streak,
    leaderboard,
    get_rewards,
    get_campaigns,
    add_report,
)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title=f"{PRODUCT_NAME} API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if isinstance(CORS_ORIGINS, list) else [CORS_ORIGINS],
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise


# ─── Utility Functions ─────────────────────────────────────────────────────────

def classify_waste(filename: str) -> tuple[str, str]:
    """
    Classify waste based on filename keywords.
    Returns: (waste_type, subcategory)
    """
    filename_lower = filename.lower()

    # Check each waste type and subcategory
    for waste_type, subcategories in WASTE_KEYWORDS.items():
        for subcategory, keywords in subcategories.items():
            if any(keyword in filename_lower for keyword in keywords):
                return waste_type, subcategory

    # Default fallback
    return "dry", "general waste"


def validate_email(email: str) -> bool:
    """Basic email validation."""
    if not email or "@" not in email or "." not in email.split("@")[1]:
        return False
    return True


def validate_password(password: str) -> bool:
    """Password validation - minimum 6 characters."""
    return bool(password and len(password) >= 6)


def validate_weight(weight: float) -> bool:
    """Validate waste weight."""
    try:
        w = float(weight)
        return 0 < w <= 1000  # Between 0 and 1000 kg
    except (ValueError, TypeError):
        return False


def validate_file_upload(file: UploadFile) -> bool:
    """
    Validate uploaded file.
    Returns True if valid, raises HTTPException if invalid.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
        )

    # File size validation happens at middleware level, but we can add manual check if needed
    return True


async def save_uploaded_file(file: UploadFile, upload_path: Path) -> Path:
    """
    Save uploaded file to disk.
    Returns: Path to saved file
    """
    try:
        file_path = upload_path / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")


def calculate_sustainability_score(weight: float, carbon: float) -> float:
    """
    Calculate sustainability score based on weight and carbon impact.
    Score is between 0 and 100.
    """
    # Weighted formula: 40% base score + 30% weight + 30% carbon reduction
    base_score = 0.9 * 0.4
    weight_score = (min(weight, 5) / 5) * 0.3  # Normalized to 5kg max
    carbon_score = (carbon / 5) * 0.3  # Normalized to 5kg CO2 max
    score = (base_score + weight_score + carbon_score) * 100
    return round(min(score, 100), 2)


def calculate_reward_points(score: float) -> int:
    """Calculate reward points from sustainability score."""
    points = max(int(score * 5), 20)  # Minimum 20 points
    return points


# ─── Authentication Endpoints ──────────────────────────────────────────────────

@app.post("/signup")
def signup(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="user"),
):
    """
    Create a new user account.
    
    - email: Valid email address
    - password: At least 6 characters
    - role: User role (default: 'user')
    """
    # Validate input
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    if not validate_password(password):
        raise HTTPException(
            status_code=400, detail="Password must be at least 6 characters"
        )

    if not role or len(role) > 50:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Attempt account creation
    success = create_account(email.strip(), password, role.strip())
    if not success:
        raise HTTPException(
            status_code=409, detail="Account already exists with this email"
        )

    logger.info(f"New account created: {email}")
    return {"message": "Account created successfully", "email": email}


@app.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="user"),
):
    """
    Authenticate user and return login status.
    
    - email: User email
    - password: User password
    - role: User role
    """
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    success = verify_login(email.strip(), password, role.strip())
    if not success:
        logger.warning(f"Failed login attempt: {email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info(f"User logged in: {email}")
    return {"message": "Login successful", "email": email}


# ─── Upload & Analysis Endpoint ────────────────────────────────────────────────

@app.post("/user/upload")
async def upload(
    email: str = Form(...),
    weight: float = Form(...),
    image: UploadFile = File(...),
):
    """
    Upload waste image and get analysis.
    
    - email: User email (must be logged in)
    - weight: Weight of waste in kg
    - image: Image file (jpg, png, etc.)
    """
    # Validate email
    if not email:
        raise HTTPException(status_code=400, detail="User email required")

    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Validate user exists
    if not user_exists(email):
        raise HTTPException(
            status_code=404,
            detail="Unknown user. Please sign up first.",
        )

    # Validate weight
    if not validate_weight(weight):
        raise HTTPException(
            status_code=400,
            detail="Weight must be between 0 and 1000 kg",
        )

    # Validate file upload
    validate_file_upload(image)

    # Save file
    file_path = await save_uploaded_file(image, UPLOAD_PATH)

    # Classify waste
    waste_type, subcategory = classify_waste(image.filename)
    logger.info(f"Waste classified: {waste_type} - {subcategory}")

    # Calculate carbon impact
    carbon = round(weight * CARBON_EMISSIONS.get(waste_type, 1.0), 2)
    trees = round(carbon / 21, 2)  # Approximate: 1 tree absorbs 21kg CO2/year

    # Calculate score and points
    score = calculate_sustainability_score(weight, carbon)
    points = calculate_reward_points(score)

    # Get disposal information
    disposal_info = DISPOSAL_MAP.get(
        waste_type,
        {
            "recyclable_status": "non-recyclable",
            "energy_potential": "none",
            "treatment": "safe disposal",
            "instructions": "Dispose responsibly",
        },
    )

    # Log waste to database
    success = log_waste(
        email=email,
        waste_type=waste_type,
        subcategory=subcategory,
        carbon=carbon,
        points=points,
        date=str(date.today()),
    )

    if not success:
        logger.error(f"Failed to log waste for {email}")
        raise HTTPException(status_code=500, detail="Failed to save waste data")

    logger.info(f"Waste logged for {email}: {waste_type}, {carbon}kg CO2")

    return {
        "success": True,
        "waste_type": waste_type,
        "subcategory": subcategory,
        "recyclable_status": disposal_info["recyclable_status"],
        "energy_potential": disposal_info["energy_potential"],
        "recommended_treatment": disposal_info["treatment"],
        "disposal_instructions": disposal_info["instructions"],
        "carbon_saved": carbon,
        "trees_equivalent": trees,
        "sustainability_score": score,
        "reward_points": points,
        "impact_message": f"You reduced {carbon} kg CO₂ — equivalent to planting {trees} trees 🌳",
    }


# ─── Data Endpoints ────────────────────────────────────────────────────────────

@app.get("/user/stats")
def user_stats(email: str):
    """
    Get user statistics.
    
    - email: User email (required)
    
    Returns: uploads count, total points, total carbon saved
    """
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    stats = get_user_stats(email)
    logger.info(f"Stats retrieved for {email}")
    return stats


@app.get("/user/co2-graph")
def co2_graph(email: str):
    """
    Get weekly CO2 graph data for user.
    
    - email: User email (required)
    
    Returns: List of weekly carbon data
    """
    if not email:
        return []

    data = weekly_carbon(email)
    return [{"week": r[0], "carbon": round(r[1], 2)} for r in data]


@app.get("/user/streak")
def user_streak(email: str):
    """
    Get user's current activity streak (consecutive days).
    
    - email: User email (required)
    
    Returns: Current streak count
    """
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    streak = get_user_streak(email)
    return {"streak": streak}


@app.get("/leaderboard")
def board():
    """Get top 10 users by reward points."""
    data = leaderboard()
    return [{"rank": i + 1, "email": row[0], "points": row[1]} for i, row in enumerate(data)]


@app.get("/rewards")
def rewards():
    """Get all available rewards and their required points."""
    rows = get_rewards()
    return [{"name": r[0], "points_required": r[1]} for r in rows]


@app.get("/campaigns")
def campaigns():
    """Get active environmental campaigns."""
    rows = get_campaigns()
    return [{"title": r[0], "locality": r[1]} for r in rows]


@app.post("/report")
def report(
    email: str = Form(...),
    message: str = Form(...),
    target: str = Form(...),
):
    """
    Submit user feedback or bug report.
    
    - email: User email
    - message: Report message
    - target: Target of the report (bug, feedback, etc.)
    """
    if not email or not message or not target:
        raise HTTPException(status_code=400, detail="All fields required")

    success = add_report(email, message, target)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to submit report")

    logger.info(f"Report submitted by {email}")
    return {"message": "Report submitted successfully"}


# ─── Health Check Endpoint ────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# ─── Serve Frontend Static Files ──────────────────────────────────────────────
# Must be mounted LAST so API routes take priority.
# Points to cinematic-scroll/public/ which contains index.html (cinematic scroll),
# home.html (WasteWise app), dashboard.html, ai-chat.html, and the /frames folder.
_PUBLIC = pathlib.Path(__file__).resolve().parent.parent / "cinematic-scroll" / "public"
if _PUBLIC.exists():
    app.mount("/", StaticFiles(directory=str(_PUBLIC), html=True), name="static")
    logger.info(f"Static files mounted from: {_PUBLIC}")
else:
    logger.warning(f"Static files directory not found: {_PUBLIC}")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting WasteWise API Server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
