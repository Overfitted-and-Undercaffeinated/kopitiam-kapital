"""
Test market data service with and without API calls
"""
import pytest
import sys
from pathlib import Path

# Add apps/ai to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "ai"))

from data.market_data import market_data_service
from utils.config import settings

@pytest.mark.unit
class TestMarketDataService:
    """Test market data functionality"""
    
    @pytest.mark.asyncio
    async def test_get_price_mock(self):
        """Test with mock data (no API calls)"""
        # Enable mock mode
        settings.use_mock_market_data = True
        
        price = await market_data_service.get_latest_price("AAPL")
        
        assert price is not None
        assert price > 0
        assert isinstance(price, float)
        
        print(f"[OK] Mock price for AAPL: ${price:.2f}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_price_real(self, enable_api):
        """Test with real API (only if enabled)"""
        if not enable_api:
            pytest.skip("Integration test - use --enable-api to run")
        
        settings.use_mock_market_data = False
        
        price = await market_data_service.get_latest_price("AAPL")
        
        assert price is not None
        assert price > 0
        print(f"[OK] Real API call successful: AAPL = ${price:.2f}")
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_mock(self):
        """Test OHLCV with mock data"""
        settings.use_mock_market_data = True
        
        data = await market_data_service.get_ohlcv("AAPL", period="1mo")
        
        assert data is not None
        assert not data.empty
        assert 'Close' in data.columns
        assert 'Open' in data.columns
        assert 'High' in data.columns
        assert 'Low' in data.columns
        assert 'Volume' in data.columns
        
        print(f"[OK] Mock OHLCV data: {len(data)} rows")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_integration_real_api(self, enable_api):
        """
        Full integration test with real API
        Only runs when enable_api_calls=true
        """
        if not enable_api:
            pytest.skip("Integration test - use --enable-api to run")
        
        settings.use_mock_market_data = False
        
        # Test complete flow
        price = await market_data_service.get_latest_price("AAPL")
        data = await market_data_service.get_ohlcv("AAPL", period="5d")
        
        assert price > 0
        assert not data.empty
        
        print(f"[OK] Integration test passed with real API")
        print(f"    Price: ${price:.2f}")
        print(f"    Data points: {len(data)}")

