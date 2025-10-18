# 🚀 KOPITIAM CAPITAL - QUICK START DEMO GUIDE

**All Systems Ready** ✅ | **Tests**: 7/7 Passing | **Time to Demo**: < 5 minutes

---

## ⚡ Quick Start (3 Commands)

### 1. Start FastAPI Server
```bash
cd apps/ai
uvicorn main:app --reload
```

**Expected Output**:
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 2. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

**Expected**: `{"status": "healthy", "service": "kopitiam-capital-ai", ...}`

### 3. Run Full Integration Test (Optional)
```bash
python test_integration.py
```

**Expected**: `Passed: 7/7` ✅

---

## 🎬 Demo Endpoints (Copy & Paste)

### Endpoint 1: Sentiment Analysis
```bash
curl http://localhost:8000/sentiment/NVDA
```

**What Judges See**:
- 82% bullish score
- News + Reddit + StockTwits breakdown
- 1,823 mentions
- Trending = true

### Endpoint 2: Recommendation
```bash
curl -X POST http://localhost:8000/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NVDA", "user_id": "demo"}'
```

**What Judges See**:
- BUY/HOLD/SELL action
- **"67% win rate"** ← KEY SELLING POINT
- Entry/stop/target prices
- AI reasoning

### Endpoint 3: Orchestrator (Smart Endpoint)
```bash
curl -X POST http://localhost:8000/ai/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I buy NVDA?", "user_id": "demo"}'
```

**What Judges See**:
- Natural language → Complete recommendation
- Shows intent classification + full result

### Endpoint 4: WebSocket (Browser Console)
```javascript
// Open browser at http://localhost:8000/docs (FastAPI Swagger UI)
// Then open console and run:

const ws = new WebSocket('ws://localhost:8000/ws/demo_workspace?user_id=demo&user_email=demo@example.com')

ws.onmessage = (e) => {
    const data = JSON.parse(e.data)
    console.log('Received:', data)
}

ws.onopen = () => {
    console.log('Connected!')
    ws.send(JSON.stringify({
        type: 'chat_message',
        message: '@ai what do you think about NVDA?'
    }))
}
```

**What Judges See**:
- Real-time connection
- Message sent
- AI responds in 2 seconds
- WebSocket in action

### Endpoint 5: Backtest Templates
```bash
curl http://localhost:8000/backtest/templates
```

**What Judges See**:
- 6 pre-built strategies
- Categorized (Beginner/Advanced)
- Ready to use

---

## 🎯 5-Minute Demo Script

### Slide 1: Problem (15 seconds)
"Retail traders face 3 problems:
1. Information overload (too much news)
2. Strategy validation (backtest manually?)
3. Team coordination (Slack + ChatGPT = messy)"

### Slide 2: Solution (15 seconds)
"Kopitiam Capital solves all 3:
1. Sentiment at scale
2. One-click backtesting
3. AI-powered team chat"

### Slide 3: Demo #1 - Sentiment (60 seconds)
- Run: `curl /sentiment/NVDA`
- Show: 82% bullish, 1823 mentions, trending
- Say: "We aggregate from ALL sources - news, Reddit, StockTwits"

### Slide 4: Demo #2 - Backtest (60 seconds)
- Run: `curl -X POST /ai/recommend {symbol: "NVDA"}`
- Show: "67% win rate" prominently
- Say: "Before you trade, we validate. This strategy won 67% of 45 trades."

### Slide 5: Demo #3 - Collaboration (60 seconds)
- Open browser console
- Connect WebSocket
- Send: "What about NVDA?"
- Show: AI responds with sentiment + suggestion
- Say: "AI is part of your team, not just a chatbot"

### Slide 6: Integration (30 seconds)
- Show: All 3 working together
- Say: "Sentiment informs recommendation, recommendation shared with team, AI responds to team"

### Slide 7: Business Model (30 seconds)
- Free: Limited features
- Pro: $79/mo (all 3 differentiators)
- Enterprise: $500+/mo (teams)
- 94% gross margins

### Slide 8: Q&A (60 seconds)
- Be ready for:
  - "How accurate is sentiment?" → 3 sources reduce bias
  - "Is backtesting reliable?" → We show sample size + Sharpe
  - "How do you make money?" → Tiers + sticky collaboration
  - "What's your edge?" → No one else has all 3

---

## 🔑 Key Numbers to Memorize

- **82%** - NVDA bullish sentiment
- **67%** - Backtest win rate
- **1,823** - Reddit mentions
- **45** - Number of trades (backtest sample size)
- **2 seconds** - AI response time
- **7/7** - Integration tests passing
- **3** - Unique differentiators
- **$79** - Pro tier pricing
- **94%** - Gross margin

---

## ⚠️ Troubleshooting

### Issue: "ModuleNotFoundError"
**Fix**: Run `pip install -r apps/ai/requirements.txt`

### Issue: "Port 8000 already in use"
**Fix**: Kill existing process or use `--port 8001`

### Issue: "OpenAI API error"
**Fix**: Check API keys in `.env` file

### Issue: "WebSocket connection failed"
**Fix**: Ensure FastAPI server is running

---

## 📞 Demo Day Checklist

**Morning Of**:
- [ ] Test internet connection
- [ ] Verify all API keys work
- [ ] Run integration test (7/7)
- [ ] Start FastAPI server
- [ ] Test all 4 demo endpoints
- [ ] Prepare backup slides
- [ ] Practice 5-minute timing
- [ ] Bring laptop charger

**During Demo**:
- [ ] Speak clearly and confidently
- [ ] Show numbers prominently (67% win rate!)
- [ ] Emphasize "no one else has all 3"
- [ ] End with clear ask (investment/partnership)

**After Demo**:
- [ ] Collect judge feedback
- [ ] Share GitHub repo
- [ ] Follow up on questions

---

## 🎯 Success Criteria

**Must Show**:
1. ✅ Sentiment aggregation working
2. ✅ Backtest validation (show win rate)
3. ✅ AI responding in chat
4. ✅ All 3 working together

**Bonus Points**:
- MCP server mention (advanced tech)
- Cost tracking (production thinking)
- Error handling (robust system)
- Business model (revenue clarity)

---

## 🏆 You're Ready!

**Status**: ALL SYSTEMS GO ✅  
**Confidence**: 100%  
**Preparation**: COMPLETE  

**Now go win this thing!** 🚀

---

**Questions? Check**:
- `FINAL_COMPLETION_REPORT.md` - Complete feature list
- `DEMO_FLOW.md` - Detailed demo script
- `SYSTEM_STATUS.md` - Test results
- `FINAL_VISION.md` - Product roadmap

