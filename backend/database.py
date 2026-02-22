import sqlite3
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_NAME = "waste_data.db"


def _conn():
    return sqlite3.connect(DB_NAME)


def init_db():
    con = _conn()
    cur = con.cursor()

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

    con.commit()
    con.close()


# ── Account helpers ───────────────────────────────────────────────────────────

def create_account(email: str, password: str, role: str) -> bool:
    """Returns True on success, False if email already exists."""
    con = _conn()
    cur = con.cursor()
    hashed_password = pwd_context.hash(password)
    try:
        cur.execute(
            "INSERT INTO accounts(email, password, role) VALUES(?,?,?)",
            (email, hashed_password, role)
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()


def verify_login(email: str, password: str, role: str) -> bool:
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "SELECT password FROM accounts WHERE email=? AND role=?",
        (email, role)
    )
    row = cur.fetchone()
    con.close()
    
    if row and pwd_context.verify(password, row[0]):
        return True
    return False


def user_exists(email: str) -> bool:
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT id FROM accounts WHERE email=?", (email,))
    result = cur.fetchone()
    con.close()
    return result is not None


# ── Waste log helpers ─────────────────────────────────────────────────────────

def log_waste(email, waste_type, subcategory, carbon, points, date):
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO waste_logs(email,waste_type,subcategory,carbon,points,date) VALUES(?,?,?,?,?,?)",
        (email, waste_type, subcategory, carbon, points, date)
    )
    con.commit()
    con.close()


def weekly_carbon(email: str):
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT strftime('%Y-%W', date) AS week, SUM(carbon)
        FROM waste_logs
        WHERE email=?
        GROUP BY week
        ORDER BY week
    """, (email,))
    data = cur.fetchall()
    con.close()
    return data


def get_user_stats(email: str) -> dict:
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT
            COUNT(*)          AS uploads,
            COALESCE(SUM(points), 0)  AS total_points,
            COALESCE(SUM(carbon), 0)  AS total_carbon
        FROM waste_logs
        WHERE email=?
    """, (email,))
    row = cur.fetchone()
    con.close()
    return {
        "uploads":      row[0],
        "total_points": row[1],
        "total_carbon": round(row[2], 2)
    }


# ── Leaderboard ───────────────────────────────────────────────────────────────

def leaderboard():
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT email, SUM(points) AS total_points
        FROM waste_logs
        GROUP BY email
        ORDER BY total_points DESC
        LIMIT 10
    """)
    data = cur.fetchall()
    con.close()
    return data


# ── Rewards & Campaigns ───────────────────────────────────────────────────────

def get_rewards():
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT name, points_required FROM rewards ORDER BY points_required")
    data = cur.fetchall()
    con.close()
    return data


def get_campaigns():
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT title, locality FROM campaigns")
    data = cur.fetchall()
    con.close()
    return data


# ── Reports ───────────────────────────────────────────────────────────────────

def add_report(email: str, message: str, target: str):
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO reports(email, message, target) VALUES(?,?,?)",
        (email, message, target)
    )
    con.commit()
    con.close()


def get_user_streak(email: str) -> int:
    """Calculates the number of consecutive days of activity including today or yesterday."""
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT DISTINCT date FROM waste_logs WHERE email=? ORDER BY date DESC", (email,))
    dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cur.fetchall()]
    con.close()

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