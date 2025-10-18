# ⚡ Enhanced Backtesting Performance Optimizations

## Current Performance: 8-12 seconds

## Quick Wins (Implement These Now)

### 1. Skip Voice by Default ✅ (Save 2-3 seconds)
**Already Implemented!** Just change the default:

```python
# In /backtest/run endpoint
include_voice: bool = False  # Changed from True
```

**Impact**: 8-12s → 5-7s
**Effort**: Change 1 line

### 2. Add Market Data Caching (Save 1-3 seconds)
**Why**: You download the same AAPL data repeatedly

**Implementation**:
```python
# Create apps/ai/data/data_cache.py

import pandas as pd
from datetime import datetime
from typing import Optional

class MarketDataCache:
    """Cache market data to avoid repeated downloads"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self._ttl = ttl_seconds  # 1 hour default
    
    async def get_or_fetch(self, symbol: str, period: str, fetch_fn):
        """Get from cache or fetch"""
        cache_key = f"{symbol}_{period}"
        
        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            age = datetime.now().timestamp() - timestamp
            
            if age < self._ttl:
                return data
        
        # Fetch and cache
        data = await fetch_fn()
        self._cache[cache_key] = (data, datetime.now().timestamp())
        return data

# Global instance
market_data_cache = MarketDataCache()
```

**Use it in market_data.py**:
```python
# In market_data_service.get_ohlcv()
from data.data_cache import market_data_cache

async def get_ohlcv(self, symbol: str, period: str):
    return await market_data_cache.get_or_fetch(
        symbol, 
        period,
        lambda: self._download_data(symbol, period)
    )
```

**Impact**: 5-7s → 3-5s (first run), <1s (cached)
**Effort**: 30 minutes

### 3. Reduce Default Period to 1 Year (Save 1-2 seconds)
**Why**: Less data to download and process

```python
# In /backtest/run endpoint
if not start_date:
    # Changed from 730 days (2 years) to 365 days (1 year)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
```

Add optional parameter:
```python
backtest_period: str = "1y"  # "1y", "2y", "5y"
```

**Impact**: 5-7s → 4-5s
**Effort**: 5 minutes

## Combined Impact

```
Original:                     8-12s
+ Skip voice by default:      5-7s   (-3s)
+ Market data caching:        3-5s   (-2s first run, <1s cached)
+ 1 year default period:      2-4s   (-1s)
──────────────────────────────────
RESULT:                       2-4s   (66-75% faster!)
```

## Advanced Optimizations (Later)

### 4. Parallel Execution
Run translation and data download simultaneously:

```python
# Before: Sequential
strategy = await translate()
data = await download()

# After: Parallel
strategy, data = await asyncio.gather(
    translate(),
    download()
)
```

**Impact**: -1s
**Effort**: 1 hour

### 5. Database Result Caching
Cache full backtest results for 24h:

```python
# Check if same backtest was run recently
cache_key = f"{symbol}_{strategy_name}_{period}"
cached_result = await get_from_redis(cache_key)

if cached_result:
    return cached_result  # Instant!
```

**Impact**: Instant response on cache hit
**Effort**: 2 hours (needs Redis)

### 6. Response Streaming (WebSocket)
Stream results as they become available:

```python
# Send updates
yield {"status": "translating", "progress": 25}
yield {"status": "backtesting", "progress": 50}
yield {"status": "explaining", "progress": 75}
yield {"status": "complete", "progress": 100, "result": ...}
```

**Impact**: Feels 2x faster (perceived speed)
**Effort**: 3 hours

### 7. Pre-compute Popular Strategies
Run backtests nightly for:
- Top 10 stocks (AAPL, NVDA, TSLA, etc.)
- Top 5 strategies (RSI, MACD, SMA crossover, etc.)
- Store in database

**Impact**: Instant for popular queries
**Effort**: 4 hours

## Performance Comparison

| Optimization | Time | Effort | ROI |
|-------------|------|--------|-----|
| **Skip voice default** | 5-7s | 1 min | ⭐⭐⭐⭐⭐ |
| **Market data cache** | 3-5s | 30 min | ⭐⭐⭐⭐⭐ |
| **1 year default** | 2-4s | 5 min | ⭐⭐⭐⭐ |
| Parallel execution | 2-3s | 1 hr | ⭐⭐⭐ |
| Result caching | <1s | 2 hr | ⭐⭐⭐⭐⭐ |
| Response streaming | Feels faster | 3 hr | ⭐⭐⭐ |
| Pre-compute | <1s | 4 hr | ⭐⭐⭐⭐ |

## Recommendation: Implement These 3 Now

1. **Change voice default to False** (1 minute)
2. **Add market data caching** (30 minutes)  
3. **Change default period to 1 year** (5 minutes)

**Total effort**: 36 minutes
**Total speedup**: 6-8 seconds (66-75% faster!)

## Implementation Order

### Phase 1: Quick Wins (Today - 1 hour)
- ✅ Skip voice by default
- ✅ 1 year default period
- ✅ Market data caching

### Phase 2: Advanced (This Week - 3 hours)
- Parallel execution
- Response streaming (if using WebSocket)

### Phase 3: Production (Next Week - 6 hours)
- Redis result caching
- Pre-compute popular strategies
- Query optimization

## Testing Performance

```bash
# Before optimizations
time curl -X POST http://localhost:8000/backtest/run \
  -d '{"symbol": "AAPL", "natural_language_strategy": "buy when RSI is below 30"}'
# → 8-12 seconds

# After optimizations
time curl -X POST http://localhost:8000/backtest/run \
  -d '{"symbol": "AAPL", "natural_language_strategy": "buy when RSI is below 30"}'
# → 2-4 seconds (first run)
# → <1 second (cached)
```

## Cost Impact

All optimizations are **FREE**:
- Voice was already optional ($0.15 per request)
- Caching reduces API calls (saves money!)
- Faster = happier users = better retention

## User Experience Impact

```
Before: "This is taking forever..."  😩
After:  "Wow, that was fast!"        😍
```

Users perceive <3s as "instant"
Users tolerate 3-5s 
Users complain about >5s

**Target: Get under 3 seconds!**

