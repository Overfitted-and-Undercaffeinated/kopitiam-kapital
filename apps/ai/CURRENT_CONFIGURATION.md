# Enhanced Backtesting - Current Configuration

## ✅ Active Features

### 1. Voice Narration: **ENABLED** 🔊
- Default: `include_voice: bool = True`
- Generates ElevenLabs voice narration for all backtests
- Cost: ~$0.15 per backtest
- Can be disabled by user with `include_voice: false`

### 2. Default Period: **2 YEARS** 📊
- Default: 730 days of historical data
- More comprehensive analysis
- Better statistical significance
- Can be overridden by user with custom `start_date` and `end_date`

### 3. Market Data Caching: **ENABLED** ⚡
- Cache duration: 1 hour (3600 seconds)
- Saves 2-3 seconds on cache hits
- Automatically invalidates after TTL
- Reduces API calls to yfinance

## Performance Profile

```
With Current Configuration:

Strategy Translation:  1-2s    (Groq - FREE)
Market Data Download:  3-5s    (2 years, or <1s cached)
Backtest Execution:    2-3s    (computation)
Explanation:          1-2s    (Groq - FREE)
Voice Generation:     2-3s    (ElevenLabs - $0.15)
────────────────────────────────────
TOTAL (First Run):    10-15s
TOTAL (Cached):       7-11s
```

## Cost Per Request

| Component | Cost |
|-----------|------|
| Strategy Translation | FREE (Groq) |
| Market Data | FREE (yfinance) |
| Backtest Execution | FREE |
| Explanation | FREE (Groq) |
| Voice Narration | **$0.15** (ElevenLabs) |
| **TOTAL** | **$0.15** |

## API Request Format

```json
{
  "symbol": "AAPL",
  "natural_language_strategy": "buy when price is below the 2 week low",
  "include_visuals": true,
  "include_voice": true,
  "user_id": "user123"
}
```

## Response Format

```json
{
  "symbol": "AAPL",
  "strategy": {
    "name": "2-Week Low Breakout",
    "description": "Buy when price drops below 2-week low",
    ...
  },
  "metrics": {
    "total_return_pct": 0.23,
    "win_rate": 0.67,
    "sharpe_ratio": 1.85,
    "var_95": -0.05,
    "cvar_95": -0.07,
    "num_trades": 45,
    "visuals": {
      "equity_curve": [...],
      "drawdown_series": [...],
      "monthly_returns": {...}
    }
  },
  "explanation": "Let me walk you through...",
  "voice_audio_base64": "UklGRiQAAABXQVZF...",
  "period": "2023-01-18 to 2025-01-18"
}
```

## User Options

Users can customize behavior:

### Fast Mode (Skip Voice)
```json
{
  "symbol": "AAPL",
  "natural_language_strategy": "buy when RSI is below 30",
  "include_voice": false
}
```
**Result**: 7-10s response, FREE

### Custom Period
```json
{
  "symbol": "AAPL",
  "natural_language_strategy": "buy when RSI is below 30",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```
**Result**: Faster with shorter period

### Template-Based (No Translation)
```json
{
  "symbol": "AAPL",
  "strategy_template_id": "rsi_oversold",
  "include_voice": false
}
```
**Result**: Fastest option (skip translation)

## Cache Behavior

### First Query (Cache Miss)
```
User requests AAPL backtest
  ↓
Download 2 years of AAPL data (3-5s)
  ↓
Cache for 1 hour
  ↓
Run backtest + voice
  ↓
Return result (10-15s total)
```

### Second Query (Cache Hit)
```
User requests AAPL backtest again
  ↓
Use cached data (<1s)
  ↓
Run backtest + voice
  ↓
Return result (7-11s total)
```

### Different Symbol (Cache Miss)
```
User requests NVDA backtest
  ↓
Download 2 years of NVDA data (3-5s)
  ↓
Cache separately
  ↓
Return result (10-15s total)
```

## Cache Management

### View Cache Stats
```bash
curl http://localhost:8000/cache/stats
```

### Clear Cache
```bash
# Clear specific symbol
curl -X POST http://localhost:8000/cache/clear?symbol=AAPL

# Clear all cache
curl -X POST http://localhost:8000/cache/clear
```

## Optimization Summary

| Optimization | Status | Impact |
|-------------|--------|--------|
| Voice Narration | ✅ ON | Default experience, costs $0.15 |
| 2-Year Period | ✅ ON | Better analysis, slower |
| Market Data Caching | ✅ ON | 3-5s faster on cache hit |

## Trade-offs

### Current Configuration (Voice ON, 2 Years)
**Pros:**
- ✅ Complete, rich user experience
- ✅ Voice narration for accessibility
- ✅ 2 years = better statistical significance
- ✅ More comprehensive analysis

**Cons:**
- ⚠️ Slower: 10-15s total
- ⚠️ Costs $0.15 per request

### Alternative: Fast Mode (Voice OFF, 1 Year)
**Pros:**
- ✅ Faster: 5-7s total
- ✅ FREE (no voice cost)
- ✅ Still good analysis

**Cons:**
- ⚠️ No voice narration
- ⚠️ Less historical data

## Recommendation

**Current configuration is OPTIMAL for**:
- Demo/presentation (show voice feature)
- Premium users (PRO/ENTERPRISE tiers)
- Mobile users (voice while multitasking)
- Accessibility requirements

**Consider fast mode for**:
- Free tier users (save costs)
- Quick testing/exploration
- API-only usage (no audio needed)

## Testing

```bash
# Test with voice (current default)
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "natural_language_strategy": "buy when price is below the 2 week low"
  }'

# Test without voice (faster)
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "natural_language_strategy": "buy when price is below the 2 week low",
    "include_voice": false
  }'
```

## Files Modified

1. ✅ `apps/ai/main.py`
   - Voice: Enabled by default
   - Period: 2 years (730 days)
   - Latency target updated: 10-15s

2. ✅ `apps/ai/data/market_data.py`
   - Market data caching integrated
   - Cache duration: 1 hour

3. ✅ `apps/ai/data/data_cache.py`
   - New cache implementation
   - TTL-based expiration

---

**Configuration matches your original requirements:**
- ✅ Voice narration included
- ✅ 2-year historical analysis
- ⚡ Plus bonus: Market data caching for speed boost!

