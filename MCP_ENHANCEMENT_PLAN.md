# MCP (Model Context Protocol) Enhancement Plan
## Smithery Risk Tools Integration

### 📊 **Current State Analysis**

#### What You Have Built
✅ **MCP Risk Tools Server** (`mcp/risk-tools/`)
- TypeScript server with Model Context Protocol
- 4 sophisticated tools implemented:
  1. `calculate_position_size` - Kelly Criterion, Fixed %, Risk Parity
  2. `calculate_var` - Value at Risk calculations
  3. `optimize_stop_loss` - ATR-based stop optimization
  4. `calculate_risk_reward` - Expected value analysis

✅ **MCP Client Wrapper** (`apps/ai/utils/mcp_client.py`)
- Python client to communicate with MCP server
- Auto-start functionality
- Graceful fallback to simple calculations

#### Where MCP is Currently Used
✅ **Recommendation Agent Only** (`apps/ai/agents/recommend.py`)
- Position sizing (Kelly Criterion)
- Stop loss optimization (ATR-based)
- Risk/reward calculations
- **~3 MCP calls per recommendation**

#### Where MCP is NOT Used (But Should Be!)
❌ **Enhanced Backtesting** - Lines 748-758 in `main.py`
```python
# CURRENTLY: Using local Python calculations
from data.risk import calculate_var, calculate_cvar
returns = [t['pnl_pct'] for t in results['trades']]
results['var_95'] = calculate_var(returns, 0.95)  # ← Local Python
results['cvar_95'] = calculate_cvar(returns, 0.95)  # ← Local Python
```

**Problem**: Your fancy MCP server with professional VaR calculations is being ignored!

---

## 🚀 **Enhancement Opportunities**

### 1. **Integrate MCP VaR into Enhanced Backtesting** 🔥🔥🔥

**Impact**: Higher quality risk metrics + showcase MCP in backtesting

**Current Code** (main.py:748-758):
```python
# Local Python calculations
from data.risk import calculate_var, calculate_cvar
returns = [t['pnl_pct'] for t in results['trades']]
results['var_95'] = calculate_var(returns, 0.95)
results['cvar_95'] = calculate_cvar(returns, 0.95)
```

**Enhanced Code**:
```python
# Try MCP first, fallback to local
from utils.mcp_client import mcp_risk_client
from data.risk import calculate_var, calculate_cvar

returns = [t['pnl_pct'] for t in results['trades']]

# Use MCP for VaR if available
if mcp_risk_client.enabled:
    logger.info("Using MCP for VaR calculation")
    
    var_result = await mcp_risk_client.call_tool(
        'calculate_var',
        {
            'returns': returns,
            'position_value': initial_capital,
            'confidence_level': 0.95,
            'holding_period_days': 1
        }
    )
    
    if var_result:
        results['var_95'] = var_result['var_percent']
        results['var_amount'] = var_result['var_amount']
        results['worst_case_loss'] = var_result['worst_case_loss']
        results['mcp_powered'] = True  # ← Show users MCP was used!
    else:
        # Fallback to local
        results['var_95'] = calculate_var(returns, 0.95)
        results['mcp_powered'] = False
else:
    # Local calculations
    results['var_95'] = calculate_var(returns, 0.95)
    results['mcp_powered'] = False

results['cvar_95'] = calculate_cvar(returns, 0.95)
```

**Benefits**:
- ✅ Showcase MCP in backtesting feature
- ✅ Get `worst_case_loss` metric (not available in local)
- ✅ Consistent risk calculations across recommendation + backtest
- ✅ Professional-grade VaR (time-scaled, position-aware)

---

### 2. **Add MCP Position Sizing to Backtest Results** 🔥🔥

**Impact**: Tell users how much to actually invest

**New Addition** (main.py after line 758):
```python
# STEP 4.5: Calculate recommended position size using MCP
if mcp_risk_client.enabled and results['win_rate'] > 0:
    logger.info("Calculating optimal position size with MCP Kelly Criterion")
    
    # Get current price
    from data.market_data import market_data_service
    current_data = await market_data_service.get_current_quote(symbol)
    current_price = current_data['price']
    
    # Calculate using backtest metrics
    position_sizing = await mcp_risk_client.calculate_position_size(
        method='kelly',
        capital=initial_capital,
        current_price=current_price,
        win_rate=results['win_rate'],
        avg_win=results.get('avg_win', 0),
        avg_loss=abs(results.get('avg_loss', 0))
    )
    
    if position_sizing:
        results['recommended_position'] = {
            'shares': position_sizing['shares'],
            'position_value': position_sizing['position_value'],
            'risk_amount': position_sizing['risk_amount'],
            'method': 'kelly_criterion',
            'message': f"Based on backtest performance, invest ${position_sizing['position_value']:,.2f} ({position_sizing['shares']} shares)"
        }
        logger.info(f"MCP recommended position: {position_sizing['shares']} shares")
```

**New Response Field**:
```json
{
  "symbol": "AAPL",
  "metrics": {...},
  "recommended_position": {
    "shares": 42,
    "position_value": 20391.00,
    "risk_amount": 4078.20,
    "method": "kelly_criterion",
    "message": "Based on backtest performance, invest $20,391.00 (42 shares)"
  },
  "mcp_powered": true
}
```

**User Experience**:
```
User: "Test this strategy on AAPL"
AI: "Strategy returned 23% over 2 years with 67% win rate. 
     Based on Kelly Criterion, you should invest $20,391 (42 shares)
     to optimally balance growth and risk."
```

---

### 3. **Add MCP Stop Loss Optimization to Strategy Builder** 🔥

**Impact**: Smarter default stop losses based on volatility

**Enhancement Location**: `apps/ai/backtesting/builder.py`

**Current** (lines 86-95):
```python
# Fixed 5% and 10% stops/targets
stop_loss_pct = risk_mgmt.get('stop_loss_percent', 0.05)  # ← Arbitrary
take_profit_pct = risk_mgmt.get('take_profit_percent', 0.10)
```

**Enhanced**:
```python
# Dynamic stops based on ATR (if MCP available)
from utils.mcp_client import mcp_risk_client
from data.indicators import calculate_atr

# Calculate ATR from recent data
atr = calculate_atr(data, period=14)[-1]

# Use MCP to optimize stop loss
if mcp_risk_client.enabled and atr > 0:
    stop_result = await mcp_risk_client.optimize_stop_loss(
        entry_price=entry_price,
        atr=atr,
        risk_tolerance='moderate',
        direction='BUY'
    )
    
    if stop_result:
        stop_price = stop_result['stop_loss']
        logger.info(f"MCP optimized stop: ${stop_price} ({stop_result['atr_multiplier']}x ATR)")
    else:
        # Fallback to fixed %
        stop_price = entry_price * (1 - 0.05)
else:
    # Fallback to fixed %
    stop_price = entry_price * (1 - 0.05)
```

**Result**: Stops adapt to volatility (tighter for calm markets, wider for volatile)

---

### 4. **Add MCP Risk/Reward Analysis to Backtest Explainer** 🔥

**Impact**: Better AI explanations with quantitative backing

**Enhancement Location**: `apps/ai/agents/backtest_explainer.py`

**Add Before Explanation Generation**:
```python
# Calculate risk/reward for typical trade using MCP
if mcp_risk_client.enabled and avg_win > 0 and avg_loss > 0:
    risk_reward = await mcp_risk_client.calculate_risk_reward(
        entry_price=100,  # Normalized
        stop_loss=100 - abs(metrics['avg_loss']),
        take_profit=100 + metrics['avg_win'],
        win_rate=metrics['win_rate'],
        position_size=1
    )
    
    if risk_reward:
        # Add to prompt
        prompt += f"\nRisk/Reward Analysis (MCP):\n"
        prompt += f"- R:R Ratio: {risk_reward['risk_reward_ratio']}\n"
        prompt += f"- Expected Value: ${risk_reward['expected_value']}\n"
        prompt += f"- Assessment: {risk_reward['recommendation']}\n"
```

**Result**: AI explanations now include professional risk/reward assessment

---

### 5. **Expose MCP Status in API** 🔥

**Impact**: Transparency - users know when professional tools are used

**Add New Endpoint** (`main.py`):
```python
@app.get("/system/capabilities")
async def get_system_capabilities():
    """
    Show what advanced features are available
    
    Returns system capabilities including MCP server status
    """
    from utils.mcp_client import mcp_risk_client
    
    return {
        "mcp_risk_tools": {
            "enabled": mcp_risk_client.enabled,
            "features": [
                "Kelly Criterion position sizing",
                "Professional VaR calculations",
                "ATR-based stop optimization",
                "Risk/reward analysis"
            ] if mcp_risk_client.enabled else [],
            "status": "operational" if mcp_risk_client.enabled else "using_fallback"
        },
        "ai_models": {
            "groq": "llama-3.3-70b-versatile",
            "openai": "gpt-4o",
            "voice": "elevenlabs"
        },
        "data_sources": ["yfinance", "alpha_vantage", "reddit", "exa"]
    }
```

**Result**: Dashboard can show "⚡ MCP-Powered Risk Analytics" badge

---

## 📈 **Implementation Priority**

| Enhancement | Impact | Effort | Priority | Lines |
|-------------|--------|--------|----------|-------|
| **#1: MCP VaR in Backtesting** | 🔥🔥🔥 | 30 min | **NOW** | ~40 |
| **#2: Position Sizing Recommendation** | 🔥🔥 | 45 min | High | ~60 |
| **#5: Capabilities Endpoint** | 🔥 | 15 min | High | ~30 |
| **#4: Risk/Reward in Explainer** | 🔥 | 30 min | Medium | ~40 |
| **#3: Dynamic Stops (ATR)** | 🔥 | 60 min | Medium | ~80 |

**Total Implementation Time**: 3 hours
**Total New Code**: ~250 lines

---

## 🎯 **What You'll Gain**

### Before (Current State)
```
Backtest Result:
- 67% win rate
- 23% return
- VaR: -5% (basic Python calculation)
```

### After (MCP-Enhanced)
```
Backtest Result:
- 67% win rate
- 23% return
- VaR: -5% (MCP-powered, time-scaled) ⚡
- Worst case loss: $8,234
- Risk/Reward: 2.0 (Excellent setup)
- Recommended investment: $20,391 (42 shares)
- Stop loss: $461.23 (2.0x ATR, volatility-adjusted)
```

### Marketing Value
```
Before: "We calculate VaR"
After:  "MCP-powered institutional-grade risk analytics using Kelly Criterion 
         and ATR-based optimization" ⚡
```

---

## 🔧 **Implementation Steps**

### Phase 1: Core Integration (1 hour)
1. ✅ Start MCP server at app startup
2. ✅ Add MCP VaR to backtesting (Enhancement #1)
3. ✅ Add capabilities endpoint (Enhancement #5)

### Phase 2: Position Sizing (45 min)
4. ✅ Add position size recommendation (Enhancement #2)
5. ✅ Update response schema
6. ✅ Test with real backtests

### Phase 3: Advanced Features (1.25 hours)
7. ✅ Add risk/reward to explainer (Enhancement #4)
8. ✅ Add dynamic stops (Enhancement #3)
9. ✅ Update tests

---

## 🧪 **Testing Checklist**

```bash
# Test MCP integration
cd apps/ai
python test_mcp_backtest_integration.py

# Verify all tools work
python test_mcp_all_tools.py

# Full backtest with MCP
python test_full_demo.py
```

---

## 📊 **Cost Impact**

**Current**: ~$0.15 per backtest (voice only)

**With MCP**: ~$0.15 per backtest (MCP is FREE, runs locally)

**MCP Benefits**: ✅ Professional tools, ✅ Zero API costs, ✅ Fast (<50ms)

---

## 🎓 **Smithery Publishing**

Once enhanced, publish to Smithery marketplace:

```bash
cd mcp/risk-tools
smithery publish

# Description:
"Professional-grade risk analytics for trading platforms
- Kelly Criterion position sizing
- Time-scaled VaR calculations
- ATR-based stop optimization
- Integrated with Kopitiam Capital backtesting"
```

**Potential Users**:
- Other trading platforms
- Quant research tools
- Portfolio managers
- AI trading assistants

---

## 💡 **Future Enhancements**

### MCP Tool #5: Monte Carlo Simulation
```typescript
{
  name: 'monte_carlo_backtest',
  description: 'Run 1000 simulations to test strategy robustness',
  // Returns distribution of possible outcomes
}
```

### MCP Tool #6: Portfolio Optimization
```typescript
{
  name: 'optimize_portfolio',
  description: 'Markowitz portfolio optimization for multi-asset strategies',
  // Returns optimal allocation across strategies
}
```

### MCP Tool #7: Greeks Calculator
```typescript
{
  name: 'calculate_greeks',
  description: 'Options greeks for strategy risk assessment',
  // Returns delta, gamma, theta, vega
}
```

---

## 📝 **Summary**

### Current MCP Usage: **20%** 
- ✅ Recommendation agent only
- ❌ Backtesting ignores MCP
- ❌ No visibility in API

### With Enhancements: **80%**
- ✅ Recommendation agent
- ✅ Backtesting powered by MCP
- ✅ Position sizing recommendations
- ✅ Dynamic stop optimization
- ✅ API exposes capabilities

### ROI
- **3 hours work** → **Professional-grade analytics**
- **Zero ongoing cost** (MCP runs locally)
- **Marketing gold** ("MCP-powered" badge)
- **Smithery revenue** (publish + license to others)

---

## 🚀 **Ready to Implement?**

Say "implement MCP enhancements" and I'll:
1. Add MCP VaR to backtesting
2. Add position sizing recommendations
3. Create capabilities endpoint
4. Update tests
5. Verify everything works

**Estimated time**: 1-2 hours for core features (#1, #2, #5)

