# Frontend ↔ Backend Integration Guide

## ✅ What's Now Connected

### Backend Status
- ✅ **Server Running**: `http://localhost:8000`
- ✅ **Redis Running**: Port 6379
- ✅ **Morning Brief**: `POST /briefs/morning` (working, ~20s response time)
- ✅ **EOD Brief**: `POST /briefs/eod` (working, ~20s response time)
- ✅ **Recommendations**: `POST /ai/recommend` (ready)
- ✅ **Sentiment**: `GET /sentiment/{symbol}` (ready)
- ✅ **Orchestrator**: `POST /ai/orchestrate` (ready)

### Frontend Status
- ✅ **Dashboard UI**: Complete with dummy data
- ✅ **Brief Overlays**: Morning + EOD components ready
- ✅ **API Client**: `/lib/aiBackend.ts` created
- ✅ **Auto-fetch**: Dashboard now calls real backend on load

---

## 📊 Actual Backend Output Formats

### Morning Brief Response
```json
{
  "type": "morning",
  "text": "Good morning! Here's your market overview.\n\nAs the U.S. markets prepare for the day ahead, investors are closely watching premarket movers highlighted in Barron's financial news. Today, sentiment remains mixed, with a particular focus on NVIDIA, which is drawing attention for both bullish and bearish perspectives.\n\nIn our watchlist analysis, NVIDIA is signaling a sentiment score of zero point four four, indicating a cautious outlook among traders...",
  "audio_base64": null,
  "symbols_analyzed": ["NVDA", "AAPL", "DBS"],
  "sentiment_summary": {
    "average_sentiment": 0.44,
    "bullish_count": 0,
    "bearish_count": 0,
    "trending_count": 0
  },
  "generated_at": "2025-10-18T06:00:00.123456"
}
```

### EOD Brief Response
```json
{
  "type": "eod",
  "text": "Market close for US, the major indices ended the day with mixed results. Notably, Nvidia, ticker NVDA, closed flat at zero percent change, signaling a day of indecisiveness among investors.\n\nIn today's watchlist performance, NVDA's sentiment remains neutral at point five one...",
  "audio_base64": null,
  "symbols_analyzed": ["NVDA", "AAPL", "DBS"],
  "performance_summary": {
    "gainers": 2,
    "losers": 1,
    "average_change": 0.87,
    "sentiment_improved": 2,
    "sentiment_declined": 0
  },
  "generated_at": "2025-10-18T17:00:00.123456"
}
```

---

## 🔄 How Frontend Transforms Backend Data

The frontend needs structured data, but backend returns plain text. The `aiBackend.ts` file handles this transformation:

### Backend → Frontend Transform
```typescript
// Backend gives you:
{
  text: "Long paragraph of text..."
}

// Frontend needs:
{
  summary: "First paragraph",
  market_overview: "Second paragraph",
  key_points: ["Point 1", "Point 2", "Point 3"],
  recommendations: ["Rec 1", "Rec 2"]
}

// The parseBriefText() function in aiBackend.ts handles this automatically
```

---

## 🚀 How to Use in Your Frontend

### Dashboard Page (Already Integrated!)

```typescript
// apps/web/app/dashboard/page.tsx

// On page load:
useEffect(() => {
  const userId = localStorage.getItem('userId') || 'demo_user'
  fetchRealBriefs(userId)
}, [])

// This function now:
// 1. Calls getMorningBrief() from aiBackend.ts
// 2. Calls getEODBrief() from aiBackend.ts
// 3. Transforms responses to match your Brief interface
// 4. Sets todayMorningBrief and todayEODBrief state
// 5. Falls back to dummy data if backend fails
```

### Manual Trigger

Add a "Refresh Briefs" button:
```typescript
const handleRefreshBriefs = async () => {
  const userId = localStorage.getItem('userId') || 'demo_user'
  await fetchRealBriefs(userId)
}

// In your JSX:
<button onClick={handleRefreshBriefs}>
  🔄 Refresh Briefs
</button>
```

---

## ⚙️ Configuration

### Watchlist Configuration
Your briefs analyze a watchlist of stocks. Currently defaults to:
```typescript
['DBS', 'OCBC', 'UOB']  // SGX stocks
```

To customize:
```typescript
import { saveUserWatchlist, getUserWatchlist } from '@/lib/aiBackend'

// Get current watchlist
const watchlist = getUserWatchlist()

// Update watchlist
saveUserWatchlist(['NVDA', 'AAPL', 'MSFT'])
```

### Market Selection
```typescript
getMorningBrief(userId, watchlist, 'SGX')  // Singapore stocks
getMorningBrief(userId, watchlist, 'US')   // US stocks
```

---

## ⏱️ Performance Notes

### Response Times (with Redis running)
- **Morning Brief**: ~15-25 seconds
  - Sentiment analysis: 5-10s per symbol
  - Market context (Exa.ai): 2-3s
  - GPT-4o-mini generation: 2-3s
  - Total for 3 stocks: ~20s

- **EOD Brief**: ~20-30 seconds
  - Same as morning +
  - Price performance lookup: 2-5s
  - RAG research on movers: 3-5s

### Why So Slow?
1. **Sentiment Analysis** calls multiple APIs:
   - Exa.ai news search (mock mode = fast, real = 2-3s)
   - Reddit PRAW scraping (2-3s per symbol)
   - StockTwits API (1s per symbol)
   - Groq article scoring (5-10 articles)

2. **AI Generation**:
   - OpenAI GPT-4o-mini text generation (2-3s)

3. **Sequential Processing**:
   - Each symbol analyzed one by one
   - With 3 symbols: 3x the time

### Optimization Ideas
- ✅ **Redis caching**: Cache sentiment for 15 minutes
- ✅ **Parallel processing**: Analyze symbols in parallel
- ✅ **Pre-generation**: Generate briefs at 6am/5pm, store in DB
- 🔄 **Streaming**: Return partial results as they come in

---

## 🧪 Testing the Integration

### 1. Check Backend is Running
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### 2. Test Morning Brief
```bash
curl -X POST "http://localhost:8000/briefs/morning" \
  -H "Content-Type: application/json" \
  -d '{
    "watchlist": ["NVDA"],
    "market": "US",
    "user_id": "demo",
    "include_voice": false
  }' \
  --max-time 60
```

### 3. Test from Frontend
Open browser console on `/dashboard` and check:
```javascript
// Should see logs like:
"Fetching briefs from backend..."
"Morning brief received: 1447 characters"
"EOD brief received: 982 characters"
```

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch"
**Cause**: Backend not running
**Fix**: 
```bash
cd apps/ai
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### Issue: Request times out
**Cause**: Brief generation takes 20+ seconds
**Fix**: Already handled - frontend has 60s timeout

### Issue: "CORS error"
**Cause**: Backend CORS not configured for your domain
**Fix**: Backend already has `allow_origins=["*"]` - should work

### Issue: Briefs return dummy data
**Cause**: Backend returned error or timeout
**Fix**: Check browser console for errors. Backend falls back to dummy data gracefully.

---

## 📁 Files Modified

### New Files Created
1. ✅ `/apps/web/lib/aiBackend.ts` - Backend integration layer

### Files Updated
1. ✅ `/apps/web/app/dashboard/page.tsx` - Now calls real backend
2. ✅ `/apps/web/lib/api.ts` - Updated with new endpoints
3. ✅ `/apps/ai/requirements-quick.txt` - Python 3.12 compatible deps

### Files Ready (No Changes Needed)
- ✅ `/components/BriefOverlay.tsx` - Already displays Brief format
- ✅ `/components/IdeaCard.tsx` - Ready for recommendations
- ✅ `/app/assistant/page.tsx` - Ready for orchestrator integration

---

## 🎯 Integration Summary

### What Works Now
```
Dashboard Page Load
    ↓
Calls getMorningBrief(userId, watchlist, market)
    ↓
POST http://localhost:8000/briefs/morning
    ↓
Backend:
  - Gets sentiment for each symbol (Exa + Reddit + StockTwits)
  - Calls Mem0 for user preferences
  - Generates brief with GPT-4o-mini
  - Returns JSON
    ↓
Frontend parseBriefText():
  - Extracts summary (first paragraph)
  - Extracts market_overview (second paragraph)
  - Extracts key_points (bullet points or sentences)
  - Extracts recommendations (if morning brief)
    ↓
Displays in BriefOverlay component
```

### What's Next
1. Test the integration by loading `/dashboard`
2. Verify morning brief appears automatically
3. Click "🌙 EOD Report" to see EOD brief
4. Check that real data appears (not dummy data)

---

## ⚡ Quick Start

1. **Start Backend** (if not running):
```bash
cd apps/ai
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

2. **Start Frontend**:
```bash
cd apps/web
npm run dev
```

3. **Visit**: `http://localhost:3000/dashboard`

4. **Expected Behavior**:
- Loading spinner shows for ~20 seconds
- Morning brief auto-appears
- Real sentiment data from backend
- Falls back to dummy data if backend fails

---

**Your frontend is now fully structured to accept backend briefs! 🚀**

