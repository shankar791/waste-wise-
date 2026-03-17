from fastapi.testclient import TestClient
from main import app
import os
import pytest
from database import init_db, get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database is initialized before running tests."""
    init_db()
    yield
    # Optionally, we could clean up the DB here if it was an in-memory test DB

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_signup_missing_params():
    response = client.post("/signup", data={"email": "test@example.com"})
    assert response.status_code == 422 # Unprocessable Entity due to missing Form fields

def test_login_missing_params():
    response = client.post("/login", data={"email": "test@example.com"})
    assert response.status_code == 422

def test_rewards_endpoint():
    response = client.get("/rewards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_campaigns_endpoint():
    response = client.get("/campaigns")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_leaderboard_endpoint():
    response = client.get("/leaderboard")
    assert response.status_code == 200
    # Even if empty, it returns a list
    assert isinstance(response.json(), list)

def test_report_missing_fields():
    response = client.post("/report", data={"email": "test@test.com"})
    assert response.status_code == 422
