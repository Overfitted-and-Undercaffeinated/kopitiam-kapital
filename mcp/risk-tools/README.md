# Kopitiam Capital - Risk Tools MCP Server

**Model Context Protocol (MCP) server for advanced risk calculations**

## Overview

This MCP server provides sophisticated risk management tools for trading agents:

- **Position Sizing**: Kelly Criterion, Fixed %, Risk Parity
- **Value at Risk (VaR)**: Portfolio risk assessment
- **Stop Loss Optimization**: ATR-based stop placement
- **Risk/Reward Analysis**: Expected value calculations

## Installation

```bash
cd mcp/risk-tools
npm install
npm run build
```

## Usage

### From Python (via MCP Client)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to MCP server
server_params = StdioServerParameters(
    command="node",
    args=["mcp/risk-tools/dist/index.js"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # Call position sizing tool
        result = await session.call_tool(
            "calculate_position_size",
            arguments={
                "method": "kelly",
                "capital": 100000,
                "current_price": 485.50,
                "win_rate": 0.67,
                "avg_win": 0.08,
                "avg_loss": 0.04,
                "stop_loss": 461.23
            }
        )
        
        print(result)
```

## Available Tools

### 1. calculate_position_size

Calculate optimal position size based on risk parameters.

**Methods**:
- `kelly`: Kelly Criterion (optimal growth)
- `fixed_percent`: Fixed risk percentage
- `risk_parity`: Equal risk allocation

**Example**:
```json
{
  "method": "kelly",
  "capital": 100000,
  "current_price": 485.50,
  "win_rate": 0.67,
  "avg_win": 0.08,
  "avg_loss": 0.04
}
```

**Returns**:
```json
{
  "shares": 42,
  "position_value": 20391.00,
  "risk_amount": 4078.20,
  "method": "kelly"
}
```

### 2. calculate_var

Calculate Value at Risk for a position.

**Example**:
```json
{
  "returns": [-0.02, 0.01, -0.01, 0.03, ...],
  "position_value": 25000,
  "confidence_level": 0.95
}
```

**Returns**:
```json
{
  "var_amount": 1250.50,
  "var_percent": 0.05,
  "confidence_level": 0.95,
  "worst_case_loss": 2500.00
}
```

### 3. optimize_stop_loss

Optimize stop loss placement based on ATR.

**Example**:
```json
{
  "entry_price": 485.50,
  "atr": 12.30,
  "risk_tolerance": "moderate"
}
```

**Returns**:
```json
{
  "stop_loss": 460.90,
  "atr_multiplier": 2.0,
  "distance_percent": 0.0506
}
```

### 4. calculate_risk_reward

Calculate risk/reward ratio and expected value.

**Example**:
```json
{
  "entry_price": 485.50,
  "stop_loss": 461.23,
  "take_profit": 534.05,
  "win_rate": 0.67,
  "position_size": 50
}
```

**Returns**:
```json
{
  "risk_reward_ratio": 2.0,
  "risk_amount": 1213.50,
  "reward_amount": 2427.50,
  "expected_value": 1226.28,
  "recommendation": "Excellent setup - good risk/reward and positive expected value"
}
```

## Integration with Kopitiam Capital

This MCP server can be called from any Python agent:

```python
# In recommendation agent
from mcp_integration import call_mcp_tool

# Calculate optimal position size
position = await call_mcp_tool(
    server="risk-tools",
    tool="calculate_position_size",
    args={
        "method": "kelly",
        "capital": user_portfolio_value,
        "current_price": current_price,
        "win_rate": backtest_win_rate,
        "avg_win": backtest_avg_win,
        "avg_loss": backtest_avg_loss
    }
)

# Use result in recommendation
recommendation['position_size_shares'] = position['shares']
recommendation['risk_amount'] = position['risk_amount']
```

## Development

```bash
# Run in dev mode
npm run dev

# Build for production
npm run build

# Start built server
npm start
```

## Deployment (Smithery)

```bash
# Build and publish to Smithery
smithery publish

# Install in other projects
smithery install @kopitiam-capital/risk-tools-mcp
```

## License

MIT

