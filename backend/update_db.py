import os
import sys

# Add backend to path to import app modules correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

def run_migration():
    commands = [
        "ALTER TABLE waste_logs ADD COLUMN weight FLOAT;",
        "ALTER TABLE waste_logs ADD COLUMN image_url VARCHAR;"
    ]
    print(f"Connecting to database using engine: {engine.url}")
    with engine.connect() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                print(f"✅ Successfully Executed: {cmd}")
            except Exception as e:
                print(f"⚠️ Skipped (column might already exist): {str(e)}")
        conn.commit()
    print("Database updated!")

if __name__ == "__main__":
    run_migration()
