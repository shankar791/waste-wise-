import logging
import pathlib
import shutil
from datetime import date as datetime_date
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.config import settings, UPLOAD_PATH, ALLOWED_FILE_EXTENSIONS, CARBON_EMISSIONS, DISPOSAL_MAP, WASTE_KEYWORDS
from app.core import security
from app.db.database import engine, Base
from app.models import models
from app.api.deps import get_db
from app.schemas import schemas
from typing import List

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 5. Tables Creation / Migration ──────────────
# Use: Base.metadata.create_all(bind=engine)
# (Optional: mention Alembic but default to create_all)
# 
# Note: In production you'd use Alembic migrations, but this acts as default.
Base.metadata.create_all(bind=engine)

UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

# ─── Utility Functions ──────────────

def classify_waste(filename: str) -> tuple[str, str]:
    filename_lower = filename.lower()
    for waste_type, subcategories in WASTE_KEYWORDS.items():
        for subcategory, keywords in subcategories.items():
            if any(keyword in filename_lower for keyword in keywords):
                return waste_type, subcategory
    return "dry", "general waste"

def validate_email(email: str) -> bool:
    if not email or "@" not in email or "." not in email.split("@")[1]: return False
    return True

def validate_password(password: str) -> bool:
    return bool(password and len(password) >= 6)

def validate_weight(weight: float) -> bool:
    try:
        w = float(weight)
        return 0 < w <= 1000
    except (ValueError, TypeError):
        return False

def validate_file_upload(file: UploadFile) -> bool:
    if not file.filename: raise HTTPException(status_code=400, detail="File name is required")
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
        )
    return True

def save_uploaded_file(file: UploadFile, upload_path: Path) -> Path:
    try:
        file_path = upload_path / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

def calculate_sustainability_score(weight: float, carbon: float) -> float:
    base_score = 0.9 * 0.4
    weight_score = (min(weight, 5) / 5) * 0.3
    carbon_score = (carbon / 5) * 0.3
    score = (base_score + weight_score + carbon_score) * 100
    return round(min(score, 100), 2)

def calculate_reward_points(score: float) -> int:
    return max(int(score * 5), 20)

# ─── Endpoints ──────────────

@app.post("/signup", response_model=schemas.SignupResponse)
def signup(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="user"),
    db: Session = Depends(get_db)
):
    if not validate_email(email): raise HTTPException(status_code=400, detail="Invalid email format")
    if not validate_password(password): raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    email = email.strip()
    result = db.execute(select(models.Account).filter(models.Account.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="Account already exists with this email")
    
    hashed = security.get_password_hash(password)
    new_acc = models.Account(email=email, password=hashed, role=role.strip())
    db.add(new_acc)
    db.commit()
    return {"message": "Account created successfully", "email": email}

@app.post("/login", response_model=schemas.LoginResponse)
def login(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="user"),
    db: Session = Depends(get_db)
):
    email = email.strip()
    result = db.execute(select(models.Account).filter(models.Account.email == email, models.Account.role == role.strip()))
    user = result.scalars().first()
    
    if not user or not security.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful", "email": email}

@app.post("/user/upload", response_model=schemas.UploadResponse)
def upload(
    email: str = Form(...),
    weight: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not validate_email(email): raise HTTPException(status_code=400, detail="Invalid email format")
    if not validate_weight(weight): raise HTTPException(status_code=400, detail="Weight must be between 0 and 1000 kg")
    validate_file_upload(image)
    
    # Check if user exists
    result = db.execute(select(models.Account).filter(models.Account.email == email))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Unknown user. Please sign up first.")
        
    save_uploaded_file(image, UPLOAD_PATH)
    waste_type, subcategory = classify_waste(image.filename)
    carbon = round(weight * CARBON_EMISSIONS.get(waste_type, 1.0), 2)
    trees = round(carbon / 21, 2)
    score = calculate_sustainability_score(weight, carbon)
    points = calculate_reward_points(score)
    disposal_info = DISPOSAL_MAP.get(waste_type, {
        "recyclable_status": "non-recyclable",
        "energy_potential": "none",
        "treatment": "safe disposal",
        "instructions": "Dispose responsibly",
    })
    
    new_log = models.WasteLog(
        email=email, waste_type=waste_type, subcategory=subcategory, 
        carbon=carbon, points=points, date=str(datetime_date.today())
    )
    db.add(new_log)
    db.commit()
    
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

@app.get("/user/stats", response_model=schemas.UserStats)
def user_stats(email: str, db: Session = Depends(get_db)):
    if not email: raise HTTPException(status_code=400, detail="Email is required")
    result = db.execute(
        select(
            func.count().label("uploads"),
            func.coalesce(func.sum(models.WasteLog.points), 0).label("total_points"),
            func.coalesce(func.sum(models.WasteLog.carbon), 0).label("total_carbon")
        ).filter(models.WasteLog.email == email)
    )
    row = result.first()
    if not row:
        return {"uploads": 0, "total_points": 0, "total_carbon": 0.0}
    return {
        "uploads": row.uploads or 0,
        "total_points": int(row.total_points or 0),
        "total_carbon": round(row.total_carbon or 0, 2)
    }

@app.get("/user/co2-graph", response_model=List[schemas.WeeklyCarbon])
def co2_graph(email: str, db: Session = Depends(get_db)):
    if not email: return []
    result = db.execute(select(models.WasteLog.date, models.WasteLog.carbon).filter(models.WasteLog.email == email))
    rows = result.all()
    
    weekly = defaultdict(float)
    for row in rows:
        try:
            d = datetime.strptime(row.date, "%Y-%m-%d")
            # YYYY-WW format
            week_str = d.strftime("%Y-%V") 
            weekly[week_str] += row.carbon
        except Exception:
            pass
            
    # Sort and return
    sorted_weeks = sorted(weekly.keys())
    return [{"week": w, "carbon": round(weekly[w], 2)} for w in sorted_weeks]

@app.get("/user/streak", response_model=schemas.StreakResponse)
def user_streak(email: str, db: Session = Depends(get_db)):
    if not email: raise HTTPException(status_code=400, detail="Email is required")
    result = db.execute(
        select(models.WasteLog.date)
        .filter(models.WasteLog.email == email)
        .order_by(models.WasteLog.date.desc())
        .distinct()
    )
    rows = result.scalars().all()
    if not rows: return {"streak": 0}
    
    dates = []
    for r in rows:
        try: dates.append(datetime.strptime(r, "%Y-%m-%d").date())
        except Exception: pass
        
    if not dates: return {"streak": 0}
    
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    if dates[0] not in [today, yesterday]: return {"streak": 0}
    
    streak = 1
    for i in range(len(dates) - 1):
        if dates[i] - timedelta(days=1) == dates[i+1]:
            streak += 1
        else:
            break
    return {"streak": streak}

@app.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def board(db: Session = Depends(get_db)):
    result = db.execute(
        select(models.WasteLog.email, func.sum(models.WasteLog.points).label("total_points"))
        .group_by(models.WasteLog.email)
        .order_by(func.sum(models.WasteLog.points).desc())
        .limit(10)
    )
    rows = result.all()
    return [{"rank": i + 1, "email": r.email, "points": int(r.total_points or 0)} for i, r in enumerate(rows)]

@app.get("/rewards", response_model=List[schemas.RewardItem])
def rewards(db: Session = Depends(get_db)):
    result = db.execute(select(models.Reward).order_by(models.Reward.points_required))
    rows = result.scalars().all()
    return [{"name": r.name, "points_required": r.points_required} for r in rows]

@app.get("/campaigns", response_model=List[schemas.CampaignItem])
def campaigns(db: Session = Depends(get_db)):
    result = db.execute(select(models.Campaign))
    rows = result.scalars().all()
    return [{"title": r.title, "locality": r.locality} for r in rows]

@app.post("/report", response_model=schemas.GenericResponse)
def report(
    email: str = Form(...),
    message: str = Form(...),
    target: str = Form(...),
    db: Session = Depends(get_db)
):
    if not email or not message or not target:
        raise HTTPException(status_code=400, detail="All fields required")

    new_report = models.Report(email=email, message=message, target=target)
    db.add(new_report)
    db.commit()
    return {"message": "Report submitted successfully"}

@app.get("/health", response_model=schemas.HealthCheckResponse)
def health_check():
    return {"status": "healthy"}

# ─── 6. Test Endpoint ──────────────
@app.get("/test-db")
def test_db():
    return {"status": "connected"}

_PUBLIC = Path(__file__).resolve().parent.parent.parent / "cinematic-scroll" / "public"
if _PUBLIC.exists():
    app.mount("/", StaticFiles(directory=str(_PUBLIC), html=True), name="static")

