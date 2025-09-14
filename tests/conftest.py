"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def sample_sales_request():
    """Sample sales report request"""
    return {
        "category": "today_hourly",
        "environment": "production"
    }

@pytest.fixture
def sample_customer_request():
    """Sample customer report request"""
    return {
        "category": "overview",
        "environment": "production"
    }
