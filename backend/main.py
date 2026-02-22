from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database import *
from datetime import date
import os, pathlib, shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

init_db()

CARBON = {"wet": 0.5, "dry": 1.5, "e-waste": 2.0, "hazardous": 1.2}

# ── Keyword-based classifier (works on filename) ──────────────────────────────
def classify(name: str):
    n = name.lower()

    # Wet / organic
    if any(k in n for k in ["banana", "food", "peel", "vegetable", "fruit", "organic", "kitchen"]):
        return "wet", "food waste"
    if any(k in n for k in ["leaf", "garden", "grass", "plant"]):
        return "wet", "garden waste"

    # Dry / recyclable
    if any(k in n for k in ["bottle", "plastic", "bag", "poly", "sachet"]):
        return "dry", "plastic"
    if any(k in n for k in ["paper", "cardboard", "newspaper", "box"]):
        return "dry", "paper"
    if any(k in n for k in ["can", "tin", "metal", "aluminium", "steel"]):
        return "dry", "metal"
    if any(k in n for k in ["glass", "jar", "vessel"]):
        return "dry", "glass"
    if any(k in n for k in ["cloth", "shirt", "fabric", "textile", "jeans", "dress"]):
        return "dry", "cloth"

    # E-waste
    if any(k in n for k in ["mobile", "phone", "charger", "cable"]):
        return "e-waste", "mobile"
    if any(k in n for k in ["laptop", "computer", "monitor", "keyboard"]):
        return "e-waste", "laptop"
    if any(k in n for k in ["tv", "television", "remote"]):
        return "e-waste", "electronics"

    # Hazardous
    if any(k in n for k in ["battery", "cell", "acid"]):
        return "hazardous", "battery"
    if any(k in n for k in ["paint", "chemical", "oil", "solvent"]):
        return "hazardous", "chemical"

    return "dry", "general waste"


# ── Auth endpoints ────────────────────────────────────────────────────────────

@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...), role: str = Form(...)):
    success = create_account(email, password, role)
    if not success:
        raise HTTPException(status_code=409, detail="Account already exists with this email.")
    return {"msg": "account has been created"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), role: str = Form(...)):
    ok = verify_login(email, password, role)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"login success": True}


# ── Upload & analyse ──────────────────────────────────────────────────────────

@app.post("/user/upload")
def upload(email: str = Form(...), weight: float = Form(...), image: UploadFile = File(...)):
    """
    Frontend now passes the logged-in email along with the upload so the
    server doesn't rely on a fragile global variable.
    """
    if not email:
        return {"error": "User not logged in"}

    # Verify the user actually exists
    if not user_exists(email):
        raise HTTPException(status_code=404, detail="Unknown user. Please sign up first.")

    path = f"{UPLOAD}/{image.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    waste_type, subcategory = classify(image.filename)

    carbon = round(weight * CARBON.get(waste_type, 1.0), 2)
    trees  = round(carbon / 21, 2)

    score  = round(min(((0.9 * 0.4) + (min(weight, 5) * 0.3) + (carbon * 0.3)) * 100, 100), 2)
    points = max(int(score * 5), 20)

    disposal_map = {
        "wet":       ("non-recyclable", "biofuel",  "compost",            "Put into green bin or compost pit"),
        "dry":       ("recyclable",     "rdf",      "recycle",            "Clean and put into blue bin"),
        "e-waste":   ("recyclable",     "none",     "e-waste recycling",  "Drop at authorized e-waste center"),
        "hazardous": ("non-recyclable", "none",     "hazardous disposal", "Hand over to hazardous collection unit"),
    }
    recyclable, energy, treatment, instructions = disposal_map.get(
        waste_type, ("non-recyclable", "none", "safe disposal", "Dispose responsibly")
    )

    log_waste(email, waste_type, subcategory, carbon, points, str(date.today()))

    return {
        "waste_type":             waste_type,
        "subcategory":            subcategory,
        "recyclable_status":      recyclable,
        "energy_potential":       energy,
        "recommended_treatment":  treatment,
        "disposal_instructions":  instructions,
        "carbon_saved":           carbon,
        "trees_equivalent":       trees,
        "sustainability_score":   score,
        "reward_points":          points,
        "impact_message":         f"You reduced {carbon} kg CO₂ — equivalent to planting {trees} trees 🌳"
    }


# ── Data endpoints ────────────────────────────────────────────────────────────

@app.get("/user/co2-graph")
def co2_graph(email: str):
    if not email:
        return []
    rows = weekly_carbon(email)
    return [{"week": r[0], "carbon": round(r[1], 2)} for r in rows]


@app.get("/user/stats")
def user_stats(email: str):
    """Total uploads, total points, total carbon for the logged-in user."""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    return get_user_stats(email)


@app.get("/user/streak")
def user_streak(email: str):
    """Calculates active daily streak for the user."""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    streak = get_user_streak(email)
    return {"streak": streak}


@app.get("/leaderboard")
def board():
    data = leaderboard()
    return [{"rank": i + 1, "email": row[0], "points": row[1]} for i, row in enumerate(data)]


@app.get("/rewards")
def rewards():
    rows = get_rewards()
    return [{"name": r[0], "points_required": r[1]} for r in rows]


@app.get("/campaigns")
def campaigns():
    rows = get_campaigns()
    return [{"title": r[0], "locality": r[1]} for r in rows]


@app.post("/report")
def report(email: str = Form(...), msg: str = Form(...), target: str = Form(...)):
    if not email:
        raise HTTPException(status_code=401, detail="Not logged in")
    add_report(email, msg, target)
    return {"msg": "report submitted"}


# ── Serve frontend static files ───────────────────────────────────────────────
# Must be mounted LAST so API routes take priority.
# Points to cinematic-scroll/public/ which contains index.html (cinematic scroll),
# home.html (WasteWise app), dashboard.html, ai-chat.html, and the /frames folder.
_PUBLIC = pathlib.Path(__file__).resolve().parent.parent / "cinematic-scroll" / "public"
app.mount("/", StaticFiles(directory=str(_PUBLIC), html=True), name="static")