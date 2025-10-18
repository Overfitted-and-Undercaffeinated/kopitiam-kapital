"""
Pytest configuration with mock/real modes
"""
import pytest
import sys
import os
from pathlib import Path

# Add apps/ai to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "ai"))

from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: Integration tests (real API calls)"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests with mocks only"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment
    By default, all tests run with mocks enabled
    """
    from utils.config import settings
    
    # Save original settings
    original_api_calls = settings.enable_api_calls
    original_mock_llm = settings.use_mock_llm
    original_mock_market = settings.use_mock_market_data
    
    # Enable mocks by default
    settings.enable_api_calls = False
    settings.use_mock_llm = True
    settings.use_mock_market_data = True
    
    print("\n[TEST ENV] Mocks enabled by default")
    print("           Run with: pytest -m integration --enable-api for real API calls")
    
    yield
    
    # Restore original settings
    settings.enable_api_calls = original_api_calls
    settings.use_mock_llm = original_mock_llm
    settings.use_mock_market_data = original_mock_market

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--enable-api",
        action="store_true",
        default=False,
        help="Enable real API calls for integration tests"
    )

@pytest.fixture
def enable_api(request):
    """Fixture to enable API calls for specific tests"""
    from utils.config import settings
    
    if request.config.getoption("--enable-api"):
        settings.enable_api_calls = True
        settings.use_mock_llm = False
        settings.use_mock_market_data = False
        yield True
        # Reset after test
        settings.enable_api_calls = False
        settings.use_mock_llm = True
        settings.use_mock_market_data = True
    else:
        yield False

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
