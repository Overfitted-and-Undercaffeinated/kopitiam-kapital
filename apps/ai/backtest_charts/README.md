# Backtest Chart Data

## Overview

The backtesting API returns chart-ready data in JSON format for frontend visualization.

## API Response Structure

When you call the backtest endpoint:
```javascript
POST /assistant/chat?message=backtest mean reversion on AAPL
```

You receive:
```json
{
  "short_response": "...",
  "detailed_response": "...",
  "metadata": {
    "chart_data": [
      {
        "symbol": "AAPL",
        "equity_curve": [
          {"date": "2023-01-01", "equity": 100000, "trade_pnl": 0},
          {"date": "2023-01-15", "equity": 101500, "trade_pnl": 1500},
          ...
        ]
      }
    ],
    "strategy_name": "Mean Reversion",
    "time_period": "2023-01-01 to 2024-01-01",
    "symbols": ["AAPL"]
  }
}
```

## Available Chart Data

Each backtest result includes:

### 1. Equity Curve
- `date`: ISO date string
- `equity`: Portfolio value at that date
- `trade_pnl`: P&L from that trade

### 2. Drawdown Series (in visuals)
- `date`: ISO date string
- `drawdown`: Drawdown percentage (negative value)

### 3. Performance Metrics
- `total_return`: Dollar amount gained/lost
- `total_return_pct`: Return percentage
- `win_rate`: Percentage of winning trades
- `sharpe_ratio`: Risk-adjusted return metric
- `max_drawdown`: Maximum peak-to-trough decline
- `num_trades`: Total number of trades
- `winning_trades`: Count of winning trades
- `losing_trades`: Count of losing trades
- `profit_factor`: Gross profits / gross losses
- `avg_win`: Average winning trade size
- `avg_loss`: Average losing trade size

## Frontend Integration

Use the `BacktestChart` component (React + Recharts):

```tsx
import BacktestChart from '@/components/BacktestChart';

<BacktestChart
  symbol="AAPL"
  strategyName="Mean Reversion"
  equityCurve={data.metadata.chart_data[0].equity_curve}
  drawdownSeries={data.visuals?.drawdown_series}
  metrics={data.metadata.metrics}
/>
```

## Features

The chart component displays:
- **Equity Curve**: Portfolio value over time (area chart)
- **Starting Capital Reference Line**: Shows initial investment
- **Drawdown Chart**: Shows portfolio declines from peak
- **Performance Metrics Grid**: Key statistics in an organized layout
- **Responsive Design**: Works on all screen sizes
- **Dark Mode Support**: Automatically adapts to theme

## Example

See `apps/web/app/backtest/example.tsx` for a complete working example.

