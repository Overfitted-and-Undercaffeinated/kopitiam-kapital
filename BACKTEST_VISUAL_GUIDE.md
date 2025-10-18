# Backtest Character Visualization - Visual Guide

## What You'll See

### When Running a Backtest

1. **Before Results**: Standard backtest configuration panel
2. **During Execution**: Loading spinner with "Running backtest simulation..."
3. **After Completion**: Character scene appears at the top of results

---

## Good Results Example 🎉

```
┌─────────────────────────────────────────────────────────┐
│  🎉 Yee-Haw! Riding the Bull!                          │
│  This strategy shows strong performance!                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              🤠                                         │
│             /|\ ← Kopikolt with arm raised             │
│            / | \                                        │
│          sitting on                                     │
│            🐂                                           │
│           /||\\ ← Brown Bull                           │
│          / || \\                                        │
│         🦵🦵🦵🦵                                         │
│                                                         │
│  (Animated: bouncing up and down)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Triggers When:**
- Total Return > 0
- Win Rate > 50%
- Sharpe Ratio > 0

(At least 2 of 3 criteria must be met)

**Animation:**
- Bull bounces up and down
- Gentle rotation
- Kopikolt's arm raised in celebration
- Big excited smile

---

## Bad Results Example ⚔️

```
┌─────────────────────────────────────────────────────────┐
│  ⚔️ Battle Mode: Fighting the Bear                      │
│  This strategy needs improvement. Ready to fight back!  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│     🤠                    🐻                            │
│    /|\ ← Kopikolt       /●● ← Bear with red eyes      │
│   / | \ (fighting)     / |\ (fierce)                   │
│  ⚔️ | ⚔️               🐾|🐾                            │
│    / \                  / \                            │
│                                                         │
│  (Animated: slight sway, battle stance)                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Triggers When:**
- Less than 2 of the good criteria are met
- Poor total return
- Win rate below 50%
- Negative Sharpe ratio

**Animation:**
- Slight swaying motion
- Fighting stances
- Bear with fierce red eyes
- Determined expression on Kopikolt

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Strategy Backtesting                  [Back to Dashboard]  │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│ Configuration│  ┌────────────────────────────────────────┐ │
│              │  │  Character Scene (450px tall)          │ │
│ [Symbol]     │  │  Kopikolt + Bull OR Bear               │ │
│ [Strategy]   │  │  Animated 3D visualization             │ │
│ [Start Date] │  └────────────────────────────────────────┘ │
│ [End Date]   │                                              │
│ [Capital]    │  ┌────────────────────────────────────────┐ │
│              │  │  Performance Summary                   │ │
│ [Run Button] │  │  • Total Return  • Win Rate            │ │
│              │  │  • Trades        • Sharpe Ratio        │ │
│              │  └────────────────────────────────────────┘ │
│              │                                              │
│              │  ┌────────────────────────────────────────┐ │
│              │  │  Detailed Metrics                      │ │
│              │  │  Final Value, Profit Factor, etc.      │ │
│              │  └────────────────────────────────────────┘ │
│              │                                              │
│              │  ┌────────────────────────────────────────┐ │
│              │  │  Trade History (Last 10)               │ │
│              │  │  Table of all trades                   │ │
│              │  └────────────────────────────────────────┘ │
└──────────────┴──────────────────────────────────────────────┘
```

---

## Character Details

### Kopikolt Features
- 👒 Tan cowboy hat
- 👔 Blue shirt with brown vest
- 🧣 Red bandana
- 👀 Expressive cartoon eyes
- 🤠 Facial expressions change based on scenario

### Bull (Good Results)
- 🐂 Brown body
- 🦴 Beige horns
- Strong, friendly appearance
- 4 legs in standing position

### Bear (Bad Results)
- 🐻 Dark brown fur
- 👁️ Red fierce eyes
- 🐾 Large paws with implied claws
- Intimidating, challenging stance

---

## Technical Details

- **Rendering**: Three.js (WebGL)
- **Style**: Toon shading (cartoon-like, similar to Brawl Stars)
- **Height**: 450px
- **Responsive**: Full width of container
- **Performance**: Client-side rendered (no SSR)
- **Animation**: 60fps smooth animations

---

## Testing

To test both scenarios:

**Test Good Results:**
```
Symbol: NVDA
Strategy: Any trend following
Period: 2023-2024
Expected: Positive returns, should show bull
```

**Test Bad Results:**
```
Symbol: Any struggling stock
Strategy: Contrarian strategy on wrong market
Period: Volatile period
Expected: Negative returns, should show bear
```

---

## Customization

Want to change when it's "good" vs "bad"? 

Edit `apps/web/app/backtest/page.tsx`, function `isGoodResult()`:

```typescript
const isGoodResult = () => {
  // Modify these thresholds:
  const totalReturn = results.metrics.total_return_pct > 0      // Change threshold
  const goodWinRate = results.metrics.win_rate > 0.5            // Change to 0.6 for stricter
  const goodSharpe = results.metrics.sharpe_ratio > 0           // Change threshold
  
  const goodCriteria = [totalReturn, goodWinRate, goodSharpe].filter(Boolean).length
  return goodCriteria >= 2  // Change to >= 3 for all criteria required
}
```

