# Backtest Character Visualization

## Overview
Kopikolt character now appears on the backtest page with different animations based on the backtest results:
- **Good Results**: Kopikolt rides a bull (celebrating success!)
- **Bad Results**: Kopikolt fights a bear (ready to battle back!)

## Implementation

### Files Created/Modified

1. **New Component**: `apps/web/app/backtest/components/BacktestCharacterScene.tsx`
   - 3D Three.js scene with Kopikolt character
   - Creates either a bull or bear based on results
   - Animated for visual appeal

2. **Updated**: `apps/web/app/backtest/page.tsx`
   - Integrated the character scene
   - Added logic to determine if results are "good" or "bad"
   - Displays character prominently above metrics

### Good vs Bad Criteria

A backtest is considered **GOOD** if at least 2 of these 3 criteria are met:
1. Total return is positive (`total_return_pct > 0`)
2. Win rate above 50% (`win_rate > 0.5`)
3. Sharpe ratio positive or not available (`sharpe_ratio > 0`)

If less than 2 criteria are met, it's considered **BAD**.

### Visual Features

#### Good Results (Riding the Bull)
- Kopikolt sits on a brown bull
- One arm raised in celebration
- Big excited smile
- Bull bounces up and down with riding motion
- Message: "🎉 Yee-Haw! Riding the Bull!"

#### Bad Results (Fighting the Bear)
- Kopikolt in fighting stance
- Fierce brown bear with red eyes
- Both in combat positions
- Slight swaying motion
- Message: "⚔️ Battle Mode: Fighting the Bear"

## Character Details

### Kopikolt (The Cowboy)
- Cowboy hat (tan with brown brim)
- Blue shirt with brown vest
- Red bandana
- Cartoon-style proportions (Brawl Stars inspired)
- Expressive eyes that change based on situation

### The Bull (Success)
- Brown body with beige horns
- Four legs in standing position
- Tail
- Simple, friendly design

### The Bear (Challenge)
- Dark brown fur
- Fierce red eyes (showing challenge)
- Raised arms in fighting pose
- Larger and more imposing than the bull

## Usage

The component automatically displays when backtest results are loaded:

```typescript
<BacktestCharacterScene isGoodResult={isGoodResult()} />
```

The scene is:
- 450px tall
- Responsive width
- Animated automatically
- Rendered with Three.js (client-side only)

## Customization

To adjust the "good vs bad" criteria, modify the `isGoodResult()` function in `apps/web/app/backtest/page.tsx`:

```typescript
const isGoodResult = () => {
  if (!results || !results.metrics) return false
  
  // Modify these thresholds as needed
  const totalReturn = results.metrics.total_return_pct > 0
  const goodWinRate = results.metrics.win_rate > 0.5
  const goodSharpe = !results.metrics.sharpe_ratio || results.metrics.sharpe_ratio > 0
  
  const goodCriteria = [totalReturn, goodWinRate, goodSharpe].filter(Boolean).length
  return goodCriteria >= 2  // Change threshold here
}
```

## Future Enhancements

Potential improvements:
- Add sound effects (yeehaw for bull, roar for bear)
- More elaborate animations (bull bucking, bear swiping)
- Multiple bear/bull designs based on severity of results
- Confetti effect for exceptional results
- Interactive elements (click to make them react)

