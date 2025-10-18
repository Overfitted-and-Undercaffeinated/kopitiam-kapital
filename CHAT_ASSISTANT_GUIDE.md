# Unified Chat Assistant - Complete Guide

## Overview

The chat assistant is now a **unified interface** where users can input natural language queries and the system intelligently routes to the appropriate function. No more separate pages for backtest, sentiment, or recommendations - everything happens through conversation!

## Architecture

### Backend Flow

```
User Message → Chat Orchestrator (GPT-4o-mini) → Intent Analysis → Function Router
                                                                    ↓
                                        ┌──────────────────────────────────────┐
                                        │                                      │
                                   ┌────▼────┐    ┌─────────┐    ┌──────────┐
                                   │BACKTEST │    │RECOMMEND│    │SENTIMENT │
                                   └────┬────┘    └────┬────┘    └────┬─────┘
                                        │              │              │
                                   ┌────▼────┐    ┌───▼─────┐    ┌───▼──────┐
                                   │EXPLAIN  │    │PORTFOLIO│    │RESEARCH  │
                                   └─────────┘    └─────────┘    └──────────┘
```

### Components

1. **Chat Orchestrator** (`apps/ai/agents/chat_orchestrator.py`)
   - Uses OpenAI GPT-4o-mini to analyze user messages
   - Extracts intent, symbols, strategy descriptions
   - Routes to appropriate handlers
   - Combines results into conversational responses

2. **Backend Endpoint** (`apps/ai/main.py`)
   - `POST /assistant/chat`
   - Parameters: `message`, `user_id`, `user_context` (optional)
   - Returns: `short_response`, `detailed_response`, `metadata`

3. **Frontend Interface** (`apps/web/app/assistant/page.tsx`)
   - Text and voice input
   - Conversational display with PnL charts
   - Animated Kopi Colt character
   - Voice narration

## Supported Functions

### 1. Backtesting 📊

**What it does:** Tests trading strategies on historical data with fixed 2-year period and $100k capital.

**Example Queries:**
- "backtest mean reversion on AAPL"
- "test RSI oversold strategy on TSLA"
- "apply moving average crossover to NVDA"
- "run momentum strategy on AAPL, MSFT, GOOGL" (multiple symbols)

**Response Format:**
- Conversational narrative explaining results
- TL;DR section with key metrics
- PnL equity curve chart for each symbol

**Key Features:**
- Natural language strategy input (e.g., "mean reversion", "RSI < 30", "buy below 50-day MA")
- Strategy translated automatically to backtest format
- Multiple symbols processed in parallel
- Visual charts showing equity curve over time

**Response Example:**
```
Let me analyze that mean reversion strategy on AAPL for you...

Over the past 2 years, the strategy showed solid performance with a 
22% total return and a win rate of 58%. The Sharpe ratio of 1.4 
indicates good risk-adjusted returns. However, you should note that 
the maximum drawdown was 12%, meaning at one point your portfolio 
would have been down by that amount.

**TL;DR for AAPL:**
• Total Return: +22.0%
• Win Rate: 58%
• Sharpe Ratio: 1.40 (good)
• Max Drawdown: -12.0%
• Trade Count: 15 trades
• Verdict: Solid strategy
```

### 2. Recommendations 💡

**What it does:** Generates trading recommendations with sentiment + backtest validation.

**Example Queries:**
- "should I buy Microsoft?"
- "what do you think about NVDA?"
- "recommend me some tech stocks"

**Response Format:**
- Action (BUY/SELL/HOLD)
- Confidence level
- Reasoning based on sentiment and historical performance

### 3. Sentiment Analysis 📰

**What it does:** Analyzes market sentiment from news and social media.

**Example Queries:**
- "what's the sentiment on TSLA?"
- "news about Apple stock"
- "market sentiment for tech stocks"

**Response Format:**
- Overall sentiment (Bullish/Bearish/Neutral)
- Sentiment score
- Number of sources analyzed

### 4. Research 🔍

**What it does:** Provides market research and analysis.

**Example Queries:**
- "what's happening with the market?"
- "research on semiconductor stocks"
- "tell me about the tech sector"

### 5. Explanations 📚

**What it does:** Explains trading concepts and indicators.

**Example Queries:**
- "what is RSI?"
- "explain moving averages"
- "how does MACD work?"
- "teach me about support and resistance"

### 6. Portfolio (Coming Soon) 💼

**What it does:** Shows your portfolio positions and performance.

**Example Queries:**
- "show my portfolio"
- "how's my portfolio doing?"
- "what are my positions?"

## Usage Guide

### For Users

1. **Navigate to `/assistant`** in the web app
2. **Type or speak your question** - be natural!
3. **Wait for response** (backtests take 30-60 seconds)
4. **View results:**
   - Short spoken response (Kopi reads this aloud)
   - Detailed text analysis
   - Charts (for backtests)

### Example Workflow

**Scenario:** You want to test a mean reversion strategy on multiple tech stocks

1. Type: `"apply mean reversion strategy to AAPL, TSLA, NVDA"`
2. Wait 60 seconds (3 backtests running in parallel)
3. Receive:
   - Spoken summary
   - Detailed narrative for each stock
   - TL;DR metrics for each
   - 3 PnL equity curve charts

### Tips for Best Results

**For Backtests:**
- Be specific about the strategy (e.g., "RSI below 30" not just "RSI")
- You can use layman terms - the AI translates them
- Mention multiple symbols separated by commas or "and"
- Don't worry about time period or capital - they're fixed

**For Recommendations:**
- Just ask naturally: "should I buy X?"
- The system automatically checks sentiment and runs validation

**For Explanations:**
- Ask like you're talking to a teacher
- "What is X?" or "Explain Y to me"

## Technical Details

### Backtest Defaults

| Parameter | Value | Why? |
|-----------|-------|------|
| Time Period | 2 years (730 days) | Balances recency with statistical significance |
| Initial Capital | $100,000 | Standard benchmark amount |
| Position Sizing | 10% per trade | Conservative risk management |
| Stop Loss | 5% | Default risk per trade |
| Take Profit | 10% | 2:1 reward/risk ratio |

### Intent Detection

The orchestrator uses GPT-4o-mini to classify user intent:

| Intent | Triggers | Function |
|--------|----------|----------|
| BACKTEST | "backtest", "test strategy", "apply strategy", strategy mentions | Backtesting engine |
| RECOMMEND | "should I buy", "recommend", "trade idea" | Recommendation agent |
| RESEARCH | "what's happening", "sentiment", "news about" | Sentiment aggregator |
| EXPLAIN | "what is", "how does", "explain", "teach me" | Explainer agent |
| PORTFOLIO | "my portfolio", "my positions", "my holdings" | Portfolio manager |

### Response Times

| Function | Expected Latency | Why? |
|----------|------------------|------|
| Backtest (single) | 20-40 seconds | Historical data fetch + strategy execution |
| Backtest (multiple) | 30-60 seconds | Parallel processing of multiple symbols |
| Recommend | 5-10 seconds | Sentiment + quick backtest validation |
| Research | 3-7 seconds | Sentiment aggregation |
| Explain | 2-4 seconds | GPT-4 explanation generation |
| Portfolio | <1 second | Database query |

## API Reference

### POST `/assistant/chat`

**Request:**
```json
{
  "message": "backtest mean reversion on AAPL",
  "user_id": "user_123",
  "user_context": {
    "risk_profile": "moderate",
    "preferences": {...}
  }
}
```

**Response:**
```json
{
  "short_response": "I've backtested that Mean Reversion strategy on AAPL...",
  "detailed_response": "## AAPL\n\nLet me analyze that mean reversion...\n\n**TL;DR:**...",
  "metadata": {
    "chart_data": [
      {
        "symbol": "AAPL",
        "equity_curve": [
          {"date": "2023-01-01", "equity": 100000, "trade_pnl": 0},
          {"date": "2023-02-15", "equity": 102500, "trade_pnl": 2500},
          ...
        ]
      }
    ],
    "strategy_name": "Mean Reversion",
    "time_period": "2023-01-01 to 2025-01-01",
    "symbols": ["AAPL"],
    "intent": "BACKTEST"
  },
  "intent": "BACKTEST"
}
```

## Testing

### Run Backend Tests

```bash
cd apps/ai
python test_chat_assistant.py
```

This tests:
1. Single symbol backtest
2. Multiple symbol backtest
3. Recommendations
4. Sentiment analysis
5. Explanations
6. Portfolio queries

### Manual Testing Queries

**Backtest:**
- "backtest mean reversion on AAPL"
- "test RSI oversold on TSLA, NVDA"
- "apply moving average crossover to MSFT"

**Recommendations:**
- "should I buy Amazon?"
- "what do you think about Tesla?"

**Research:**
- "sentiment on tech stocks"
- "what's happening with NVDA?"

**Explain:**
- "what is RSI?"
- "explain MACD"

## Troubleshooting

### "API timeout" error
- **Cause:** Backtest taking too long (>60 seconds)
- **Solution:** Frontend timeout increased to 60s, backend should complete within this

### "Strategy translation failed"
- **Cause:** Strategy description too vague or unsupported
- **Solution:** Be more specific (e.g., "RSI below 30" not just "RSI")

### Charts not displaying
- **Cause:** No `chart_data` in metadata
- **Solution:** Check backtest completed successfully and `include_visuals=True`

### "Connection refused"
- **Cause:** Backend not running
- **Solution:** `cd apps/ai && uvicorn main:app --reload`

## Future Enhancements

- [ ] Real-time streaming responses for long backtests
- [ ] Save favorite strategies
- [ ] Compare multiple strategies side-by-side
- [ ] Custom time periods and capital amounts
- [ ] Export backtest results to PDF
- [ ] Integration with portfolio for live trading
- [ ] Multi-language support
- [ ] Strategy optimization suggestions

## Architecture Decisions

### Why GPT-4o-mini for orchestration?
- Fast (200-500ms latency)
- Cost-effective ($0.15/1M input tokens)
- Excellent intent classification accuracy
- Handles natural language variations well

### Why fixed 2-year period?
- Balance between statistical significance and recency
- Captures multiple market conditions
- Fast enough to compute (20-40 seconds)

### Why $100k fixed capital?
- Standard benchmark amount
- Easy mental math (10% = $10k)
- Realistic for target audience

### Why conversational responses?
- Better user experience than raw metrics
- Works well with voice narration
- Easier for beginners to understand
- More engaging than tables

## Contributing

To add new functions to the chat assistant:

1. **Create handler** in `chat_orchestrator.py`:
   ```python
   async def _handle_new_function(self, params, user_id):
       # Implementation
       return {
           'short_response': '...',
           'detailed_response': '...',
           'metadata': {}
       }
   ```

2. **Add intent detection** in orchestrator prompt:
   ```
   - NEW_FUNCTION: Keywords like "xyz", "abc"
   ```

3. **Route in handle_message**:
   ```python
   elif intent == "NEW_FUNCTION":
       return await self._handle_new_function(...)
   ```

4. **Update tests** in `test_chat_assistant.py`

5. **Update this guide** with examples and usage

---

Built with ❤️ by the Kopitiam Capital team

