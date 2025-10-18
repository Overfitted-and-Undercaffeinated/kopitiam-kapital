"""Pytest configuration and fixtures"""
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_user_id():
    """Test user ID"""
    return "test-user-123"

@pytest.fixture
def test_symbol():
    """Test stock symbol"""
    return "AAPL"

@pytest.fixture
def sample_recommendation():
    """Sample recommendation data"""
    return {
        "action": "BUY",
        "symbol": "AAPL",
        "entry": 175.50,
        "stop": 170.00,
        "target": 185.00,
        "size_pct_nav": 5.0,
        "thesis": "Strong earnings momentum and technical breakout above resistance.",
        "risks": "Market volatility and potential sector rotation.",
        "confidence": 0.75,
        "sources": [
            {
                "title": "Apple Q4 Earnings Beat",
                "url": "https://example.com/article",
                "published": "2024-01-01"
            }
        ]
    }

@pytest.fixture
def sample_position():
    """Sample position data"""
    return {
        "symbol": "AAPL",
        "qty": 10,
        "avg_price": 170.00,
        "stop": 165.00,
        "target": 185.00,
    }

