import sqlite3
import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import DB_PATH, WASTE_KEYWORDS, DISPOSAL_MAP

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with tables and seed data."""
    with get_db() as conn:
        cur = conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS accounts(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT UNIQUE,
            password TEXT,
            role     TEXT
        );

        CREATE TABLE IF NOT EXISTS waste_logs(
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT,
            waste_type TEXT,
            subcategory TEXT,
            carbon     REAL,
            points     INTEGER,
            date       TEXT
        );

        CREATE TABLE IF NOT EXISTS rewards(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT,
            points_required INTEGER
        );

        CREATE TABLE IF NOT EXISTS campaigns(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT,
            locality TEXT
        );

        CREATE TABLE IF NOT EXISTS reports(
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            email   TEXT,
            message TEXT,
            target  TEXT
        );
        """)

        # ── Seed rewards if empty ────────────────────────────────────────────────
        cur.execute("SELECT COUNT(*) FROM rewards")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO rewards(name, points_required) VALUES(?,?)",
                [
                    ("Free Compost Bag",          500),
                    ("Plant a Tree Certificate",  1000),
                    ("Eco Tote Bag",              750),
                    ("5% Off at Green Store",     300),
                    ("Community Hero Badge",      2000),
                ]
            )

        # ── Seed campaigns if empty ──────────────────────────────────────────────
        cur.execute("SELECT COUNT(*) FROM campaigns")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO campaigns(title, locality) VALUES(?,?)",
                [
                    ("Clean Koramangala Drive",     "Koramangala, Bangalore"),
                    ("HSR Plastic Free Weekend",    "HSR Layout, Bangalore"),
                    ("Indiranagar E-Waste Collect", "Indiranagar, Bangalore"),
                    ("Whitefield Compost Campaign", "Whitefield, Bangalore"),
                    ("JP Nagar Green Street",       "JP Nagar, Bangalore"),
                ]
            )

        conn.commit()
        logger.info("Database initialized successfully")


# ── Account helpers ───────────────────────────────────────────────────────────

def create_account(email: str, password: str, role: str) -> bool:
    """Returns True on success, False if email already exists."""
    if not email or not password or not role:
        logger.warning("Create account called with missing parameters")
        return False
    
    hashed_password = pwd_context.hash(password)
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO accounts(email, password, role) VALUES(?,?,?)",
                (email, hashed_password, role)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError as e:
        logger.warning(f"Account creation failed - email already exists: {email}")
        return False
    except Exception as e:
        logger.error(f"Account creation error: {e}")
        return False


def verify_login(email: str, password: str, role: str) -> bool:
    """Verify user login credentials."""
    if not email or not password or not role:
        return False
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT password FROM accounts WHERE email=? AND role=?",
                (email, role)
            )
            row = cur.fetchone()
        
        if row and pwd_context.verify(password, row[0]):
            return True
        return False
    except Exception as e:
        logger.error(f"Login verification error: {e}")
        return False


def user_exists(email: str) -> bool:
    """Check if user exists in database."""
    if not email:
        return False
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM accounts WHERE email=?", (email,))
            result = cur.fetchone()
        return result is not None
    except Exception as e:
        logger.error(f"User existence check error: {e}")
        return False


# ── Waste log helpers ─────────────────────────────────────────────────────────

def log_waste(email: str, waste_type: str, subcategory: str, carbon: float, points: int, date: str) -> bool:
    """Log waste entry for user. Returns True on success."""
    if not all([email, waste_type, subcategory, date]):
        logger.warning("Log waste called with missing parameters")
        return False
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO waste_logs(email,waste_type,subcategory,carbon,points,date) VALUES(?,?,?,?,?,?)",
                (email, waste_type, subcategory, carbon, points, date)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Waste log error: {e}")
        return False


def weekly_carbon(email: str) -> list:
    """Get weekly carbon data for user."""
    if not email:
        return []
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT strftime('%Y-%W', date) AS week, SUM(carbon)
                FROM waste_logs
                WHERE email=?
                GROUP BY week
                ORDER BY week
            """, (email,))
            data = cur.fetchall()
        return data
    except Exception as e:
        logger.error(f"Weekly carbon query error: {e}")
        return []


def get_user_stats(email: str) -> dict:
    """Get aggregated stats for a user."""
    if not email:
        return {"uploads": 0, "total_points": 0, "total_carbon": 0.0}
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COUNT(*)          AS uploads,
                    COALESCE(SUM(points), 0)  AS total_points,
                    COALESCE(SUM(carbon), 0)  AS total_carbon
                FROM waste_logs
                WHERE email=?
            """, (email,))
            row = cur.fetchone()
        if not row:
            return {"uploads": 0, "total_points": 0, "total_carbon": 0.0}
        return {
            "uploads":      row[0],
            "total_points": row[1],
            "total_carbon": round(row[2], 2)
        }
    except Exception as e:
        logger.error(f"User stats query error: {e}")
        return {"uploads": 0, "total_points": 0, "total_carbon": 0.0}


# ── Leaderboard ───────────────────────────────────────────────────────────────

def leaderboard() -> list:
    """Get top 10 users by points."""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT email, SUM(points) AS total_points
                FROM waste_logs
                GROUP BY email
                ORDER BY total_points DESC
                LIMIT 10
            """)
            data = cur.fetchall()
        return data
    except Exception as e:
        logger.error(f"Leaderboard query error: {e}")
        return []


# ── Rewards & Campaigns ───────────────────────────────────────────────────────

def get_rewards() -> list:
    """Get all available rewards."""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, points_required FROM rewards ORDER BY points_required")
            data = cur.fetchall()
        return data
    except Exception as e:
        logger.error(f"Rewards query error: {e}")
        return []


def get_campaigns() -> list:
    """Get all campaigns."""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT title, locality FROM campaigns")
            data = cur.fetchall()
        return data
    except Exception as e:
        logger.error(f"Campaigns query error: {e}")
        return []


# ── Reports ───────────────────────────────────────────────────────────────────

def add_report(email: str, message: str, target: str) -> bool:
    """Add user report. Returns True on success."""
    if not all([email, message, target]):
        logger.warning("Add report called with missing parameters")
        return False
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO reports(email, message, target) VALUES(?,?,?)",
                (email, message, target)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Report add error: {e}")
        return False


def get_user_streak(email: str) -> int:
    """Calculate consecutive days of activity including today or yesterday."""
    if not email:
        return 0
    
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT date FROM waste_logs WHERE email=? ORDER BY date DESC", 
                (email,)
            )
            dates = [
                datetime.strptime(row[0], "%Y-%m-%d").date() 
                for row in cur.fetchall()
            ]

        if not dates:
            return 0

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Streak starts if latest activity is today or yesterday
        if dates[0] not in [today, yesterday]:
            return 0

        streak = 1
        for i in range(len(dates) - 1):
            if dates[i] - timedelta(days=1) == dates[i+1]:
                streak += 1
            else:
                break
                
        return streak
    except Exception as e:
        logger.error(f"Streak calculation error: {e}")
        return 0