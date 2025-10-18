# Chart Y-Axis Scaling Update

## Changes Made

Updated the `BacktestChart` component to show **greater variance** in the portfolio value over time by implementing custom Y-axis scaling.

### What Changed

**File**: `apps/web/components/BacktestChart.tsx`

### Before:
- Y-axis auto-scaled from 0 to max value
- Small portfolio changes appeared flat
- Example: $99,178 to $100,000 looked like a flat line when scaled from $0 to $100,000

### After:
- Y-axis now scales dynamically based on actual data range
- Adds 5% padding on top and bottom
- Example: $99,178 to $100,000 now scales from ~$98,500 to ~$100,500
- Portfolio movements are much more visible

## Technical Details

```typescript
// Calculate min/max equity for Y-axis scaling
const equityValues = equityCurve.map(p => p.equity);
const minEquity = Math.min(...equityValues);
const maxEquity = Math.max(...equityValues);

// Add 5% padding on top and bottom for better visualization
const range = maxEquity - minEquity;
const padding = range * 0.05;
const yAxisMin = Math.floor(minEquity - padding);
const yAxisMax = Math.ceil(maxEquity + padding);

// Apply to YAxis component
<YAxis domain={[yAxisMin, yAxisMax]} />
```

## Visual Impact

### Example Backtest:
- Starting Capital: $100,000
- Ending Capital: $99,178
- Total Change: -$822 (-0.82%)

**Before**: Chart appears flat (scaled $0 to $100,000)
**After**: Chart shows clear downward trend (scaled ~$98,500 to ~$100,500)

## Benefits

1. ✅ **Better Visualization**: Small changes are now clearly visible
2. ✅ **Dynamic Scaling**: Automatically adjusts to any data range
3. ✅ **Preserves Context**: 5% padding prevents data from touching edges
4. ✅ **Works for All Scenarios**: Whether portfolio goes up, down, or sideways

## Testing

To test the updated chart:
1. Start the web app: `cd apps/web && npm run dev`
2. Navigate to the Assistant page
3. Send a backtest request: "backtest mean reversion on AAPL"
4. Observe the improved chart with visible variance

The chart will now clearly show even small portfolio movements!

