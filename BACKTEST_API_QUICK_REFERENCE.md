# Enhanced Backtesting API - Quick Reference Card

## Endpoint

```
POST /backtest/run
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | string | ✅ Yes | - | Stock ticker (e.g., "AAPL", "NVDA") |
| `natural_language_strategy` | string | No* | - | Strategy in plain English |
| `strategy_template_id` | string | No* | - | Pre-built template ID |
| `strategy_definition` | object | No* | - | Custom strategy JSON |
| `start_date` | string | No | 2 years ago | Start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | End date (YYYY-MM-DD) |
| `initial_capital` | number | No | 100000 | Starting capital |
| `include_visuals` | boolean | No | true | Include chart data |
| `include_voice` | boolean | No | true | Include voice narration |
| `user_id` | string | No | - | User ID for cost tracking |

\* Must provide ONE of: `natural_language_strategy`, `strategy_template_id`, or `strategy_definition`

## Natural Language Examples

```
"buy when RSI is below 30"
"buy when price crosses above 50-day moving average"
"buy when price is below the 2 week low"
"buy on MACD bullish crossover"
"buy when Bollinger Bands touch lower band"
"buy when price crosses above 200-day moving average"
"buy when RSI is below 40 and MACD is positive"
"buy on golden cross"
```

## Pre-built Templates

```
"rsi_oversold"
"momentum_breakout"
"macd_crossover"
"sma_crossover"
"bollinger_mean_reversion"
"rsi_macd_combo"
```

## Response Structure

```json
{
  "symbol": "AAPL",
  "strategy": {
    "name": "2-Week Low Breakout",
    "description": "Buy when price drops below 2-week low",
    "indicators": [...],
    "entry_rules": [...],
    "exit_rules": [...]
  },
  "metrics": {
    "total_return": 23000,
    "total_return_pct": 0.23,
    "win_rate": 0.67,
    "sharpe_ratio": 1.85,
    "max_drawdown": -0.08,
    "var_95": -0.05,
    "cvar_95": -0.07,
    "num_trades": 45,
    "profit_factor": 1.8,
    "winning_trades": 30,
    "losing_trades": 15,
    "avg_win": 1200,
    "avg_loss": 650,
    "trades": [...],
    "visuals": {
      "equity_curve": [
        {"date": "2023-01-15", "equity": 100000, "trade_pnl": 0},
        {"date": "2023-02-03", "equity": 102500, "trade_pnl": 2500}
      ],
      "drawdown_series": [
        {"date": "2023-01-01", "drawdown": 0, "peak": 100000},
        {"date": "2023-03-15", "drawdown": -0.08, "peak": 110000}
      ],
      "monthly_returns": {
        "2023-01": 0.05,
        "2023-02": -0.02,
        "2023-03": 0.08
      },
      "trade_distribution": {
        "wins": 30,
        "losses": 15
      }
    }
  },
  "explanation": "Let me walk you through the results...",
  "voice_audio_base64": "UklGRiQAAABXQVZFZm10...",
  "period": "2023-01-18 to 2025-01-18",
  "initial_capital": 100000
}
```

## cURL Examples

### Example 1: Natural Language
```bash
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "natural_language_strategy": "buy when price is below the 2 week low"
  }'
```

### Example 2: Fast (No Voice)
```bash
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NVDA",
    "natural_language_strategy": "buy on MACD bullish crossover",
    "include_voice": false
  }'
```

### Example 3: Template
```bash
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "strategy_template_id": "rsi_oversold"
  }'
```

### Example 4: Custom Date Range
```bash
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TSLA",
    "natural_language_strategy": "buy when RSI is below 30",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 50000
  }'
```

## Python Examples

### Example 1: Basic
```python
import httpx
import asyncio

async def backtest():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/backtest/run",
            json={
                "symbol": "AAPL",
                "natural_language_strategy": "buy when RSI is below 30"
            }
        )
        return response.json()

result = asyncio.run(backtest())
print(f"Return: {result['metrics']['total_return_pct']*100:.2f}%")
```

### Example 2: Save Voice
```python
import httpx
import asyncio
import base64

async def backtest_with_voice():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/backtest/run",
            json={
                "symbol": "AAPL",
                "natural_language_strategy": "buy when RSI is below 30",
                "include_voice": True
            }
        )
        result = response.json()
        
        # Save voice to file
        if 'voice_audio_base64' in result:
            audio_data = base64.b64decode(result['voice_audio_base64'])
            with open('explanation.mp3', 'wb') as f:
                f.write(audio_data)
            print("✓ Voice saved to explanation.mp3")

asyncio.run(backtest_with_voice())
```

## JavaScript/TypeScript Examples

### Example 1: Fetch API
```typescript
const response = await fetch('http://localhost:8000/backtest/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'AAPL',
    natural_language_strategy: 'buy when RSI is below 30'
  })
});

const result = await response.json();
console.log(`Return: ${(result.metrics.total_return_pct * 100).toFixed(2)}%`);
```

### Example 2: Next.js API Route
```typescript
// app/api/backtest/route.ts
export async function POST(request: Request) {
  const body = await request.json();
  
  const response = await fetch('http://localhost:8000/backtest/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  
  return Response.json(await response.json());
}
```

### Example 3: React Component
```tsx
'use client';

import { useState } from 'react';

export default function BacktestForm() {
  const [strategy, setStrategy] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const runBacktest = async () => {
    setLoading(true);
    
    const response = await fetch('/api/backtest', {
      method: 'POST',
      body: JSON.stringify({
        symbol: 'AAPL',
        natural_language_strategy: strategy
      })
    });
    
    setResult(await response.json());
    setLoading(false);
  };
  
  return (
    <div>
      <input
        value={strategy}
        onChange={(e) => setStrategy(e.target.value)}
        placeholder="Describe your strategy..."
      />
      <button onClick={runBacktest} disabled={loading}>
        {loading ? 'Running...' : 'Run Backtest'}
      </button>
      
      {result && (
        <div>
          <h3>Results</h3>
          <p>Return: {(result.metrics.total_return_pct * 100).toFixed(2)}%</p>
          <p>Win Rate: {(result.metrics.win_rate * 100).toFixed(1)}%</p>
          <p>Sharpe: {result.metrics.sharpe_ratio.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
}
```

## Error Responses

### 400 Bad Request - Translation Failed
```json
{
  "detail": "Could not translate strategy: Invalid strategy description. Please rephrase or try a different description."
}
```
**Fix**: User should rephrase their strategy description

### 400 Bad Request - Missing Parameters
```json
{
  "detail": "Must provide natural_language_strategy, strategy_definition, or strategy_template_id"
}
```
**Fix**: Provide at least one strategy source

### 404 Not Found - No Data
```json
{
  "detail": "No data available for symbol XYZ"
}
```
**Fix**: Check symbol is valid and has historical data

### 404 Not Found - Template Not Found
```json
{
  "detail": "Template 'invalid_template' not found"
}
```
**Fix**: Use valid template ID from list

## Performance

| Feature | Latency | Cost |
|---------|---------|------|
| With Voice | 8-12s | $0.15 |
| Without Voice | 5-7s | FREE |

## Rate Limits (Recommended)

| Tier | Limit |
|------|-------|
| FREE | 3 per day |
| PRO | 50 per day |
| ENTERPRISE | Unlimited |

## Tips

1. **Skip voice for faster results**: Set `include_voice: false` (saves 2-3s)
2. **Test strategies quickly**: Use shorter date ranges
3. **Compare strategies**: Run multiple backtests with different strategies
4. **Save voice files**: Decode base64 and save as MP3
5. **Cache results**: Frontend can cache results for 24 hours

## Support

- **API Docs**: http://localhost:8000/docs
- **Tests**: `python test_enhanced_backtest.py`
- **Examples**: `python example_enhanced_backtest.py`
- **Logs**: `apps/ai/logs/app.log`

---

**Quick Start**: `curl -X POST http://localhost:8000/backtest/run -H "Content-Type: application/json" -d '{"symbol": "AAPL", "natural_language_strategy": "buy when RSI is below 30"}'`

