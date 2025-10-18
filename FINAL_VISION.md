# Kopitiam Capital - Final Product Vision

**Complete Product with All Features**  
**Timeline**: MVP (2 weeks) → Beta (6 weeks) → Production (12 weeks)

---

## 🎯 The Complete Platform

**Kopitiam Capital** is the world's first AI-native trading intelligence platform that combines:
1. **Sentiment Analysis at Scale** - Multi-source sentiment aggregation
2. **Backtesting as a Service** - One-click strategy validation
3. **Collaborative Intelligence** - Real-time team trading workspace

**Built for**: Retail traders (Singapore) expanding globally

---

## 🏗️ Complete Feature Set

### TIER 1: FREE (Beginner Traders)

**Core Features**:
- ✅ 5 AI queries per day
- ✅ Basic recommendations (news-based, no sentiment)
- ✅ Paper trading mode
- ✅ Beginner-level explanations
- ✅ 1 backtest per week (pre-built strategies only)
- ✅ Mobile app access
- ✅ Community chat (read-only)

**Limitations**:
- ❌ No sentiment analysis
- ❌ No custom backtesting
- ❌ No real portfolio tracking
- ❌ No team collaboration
- ❌ No API access

### TIER 2: PRO ($49-99/month - Active Traders)

**Everything in Free, plus**:

**Advanced Intelligence**:
- ✅ Unlimited AI queries
- ✅ Full sentiment analysis (news + social + insider)
- ✅ Sentiment-powered recommendations
- ✅ Advanced recommendations with backtest validation
- ✅ Risk-adjusted position sizing
- ✅ Multi-timeframe analysis

**Backtesting Unlimited**:
- ✅ Custom strategy builder (no code required)
- ✅ Parameter optimization (find best settings)
- ✅ Unlimited backtests
- ✅ Advanced metrics (Sharpe, Sortino, Calmar)
- ✅ Compare multiple strategies
- ✅ Export results to CSV

**Portfolio Management**:
- ✅ Real portfolio tracking (broker integration)
- ✅ Auto-sync positions from IBKR/Tiger/Saxo
- ✅ Real-time P&L tracking
- ✅ Performance analytics
- ✅ Tax loss harvesting suggestions

**Alerts & Notifications**:
- ✅ Custom price alerts
- ✅ Sentiment shift alerts
- ✅ Earnings date reminders
- ✅ Mobile push notifications
- ✅ Email digests

**Explanations**:
- ✅ Intermediate/Expert level explanations
- ✅ Voice briefings (ElevenLabs)
- ✅ Multilingual (English, Mandarin, Malay)

**Limitations**:
- ❌ No team features (solo only)
- ❌ No API access
- ❌ No white-label

### TIER 3: ENTERPRISE ($500-2000/month - Professional Traders & Teams)

**Everything in Pro, plus**:

**Team Collaboration**:
- ✅ Team workspaces (up to 50 members)
- ✅ Real-time collaborative chat
- ✅ AI participates in team discussions
- ✅ Shared watchlists
- ✅ Shared research notes
- ✅ Collaborative chart annotations
- ✅ Team P&L leaderboard
- ✅ Role-based permissions (owner, admin, member, viewer)

**Real-Time Intelligence**:
- ✅ WebSocket streaming
- ✅ Live price updates
- ✅ Live P&L dashboard
- ✅ Instant alert broadcasting
- ✅ Real-time sentiment updates

**API Access**:
- ✅ REST API for all features
- ✅ WebSocket API
- ✅ Programmatic trading
- ✅ Custom integrations
- ✅ Webhook support
- ✅ Rate limits: 10,000 req/hour

**Advanced Analytics**:
- ✅ Portfolio-level risk (VaR, Greeks)
- ✅ Correlation analysis
- ✅ Stress testing
- ✅ Multi-account aggregation
- ✅ Custom reporting

**Compliance & Security**:
- ✅ Audit trails
- ✅ Trade history exports
- ✅ Compliance reports
- ✅ SSO/SAML
- ✅ IP whitelisting
- ✅ Encrypted data at rest

**Support & Services**:
- ✅ Dedicated account manager
- ✅ Priority support (24/7)
- ✅ Custom feature development
- ✅ On-premise deployment option
- ✅ White-label capability
- ✅ SLA guarantees (99.9% uptime)

---

## 📱 Complete Feature Matrix

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **AI Queries/Day** | 5 | Unlimited | Unlimited |
| **Sentiment Analysis** | ❌ | ✅ Full | ✅ Full + Custom |
| **Backtesting** | 1/week | Unlimited | Unlimited + API |
| **Custom Strategies** | ❌ | ✅ | ✅ |
| **Parameter Optimization** | ❌ | ✅ | ✅ Advanced |
| **Real Portfolio Sync** | Paper only | ✅ | ✅ Multi-account |
| **Mobile App** | ✅ Basic | ✅ Full | ✅ Full |
| **Voice Briefings** | ❌ | ✅ | ✅ Multilingual |
| **Team Collaboration** | ❌ | ❌ | ✅ Up to 50 |
| **Real-Time Streaming** | ❌ | ❌ | ✅ WebSocket |
| **API Access** | ❌ | ❌ | ✅ Full |
| **Support** | Community | Email | 24/7 Dedicated |
| **Custom Integrations** | ❌ | ❌ | ✅ |

---

## 🎨 Complete User Journeys

### Free Tier User (Beginner - "Sarah")

**6:00 AM**: Sarah opens app
- Sees basic market summary (pre-generated)
- Gets beginner-friendly explanation of yesterday's movements

**12:00 PM**: Asks "Should I buy Apple stock?"
- Router classifies as RECOMMEND intent
- Gets basic recommendation (no sentiment)
- Sees explanation: "What is a stop loss?" (beginner level)
- Can paper trade the idea

**5:00 PM**: Reviews paper portfolio
- Sees mock P&L
- Gets learning tips
- Prompted to upgrade to Pro for real features

**Conversion Hook**: "Upgrade to Pro to see live sentiment and validate strategies"

### Pro Tier User (Active Trader - "Marcus")

**6:00 AM**: Morning brief arrives (push notification)
- Voice briefing in Mandarin (his preference)
- Market overview with sentiment scores
- 3 trade ideas with backtest validation
- "NVDA: 82% bullish sentiment, 67% historical win rate"

**9:00 AM**: Marcus asks "What's the sentiment on Tesla?"
- Router → RESEARCH intent
- Sentiment Aggregator returns:
  - Overall: 78% bullish
  - News: 75% (Reuters, Bloomberg articles)
  - Reddit: 88% (1,823 mentions in past 24h)
  - StockTwits: 84% (542 messages)
- Shows breakdown + top sources

**11:00 AM**: Marcus wants to validate a strategy
- Opens backtest builder
- Selects "RSI Oversold" template
- Customizes: RSI < 25 (instead of 30)
- Clicks "Run Backtest"
- Results in 3 seconds:
  - Win rate: 71%
  - Sharpe: 1.92
  - Max drawdown: -8%
  - Equity curve chart
- Marcus saves strategy to portfolio

**2:00 PM**: Alert triggers
- "AAPL dropped 3% on earnings miss"
- Sentiment shifted: 0.85 → 0.55 (bullish to neutral)
- AI suggests: "Consider taking profits or tightening stop"

**5:00 PM**: End-of-day report
- Today's P&L: +$427
- Best trade: NVDA (+$580)
- Portfolio sentiment: 0.72 (bullish)
- Tomorrow's watchlist with sentiment

**Upgrade Hook**: "Join a team workspace to collaborate with other traders"

### Enterprise Tier User (Professional Team - "Quantum Capital")

**Team Size**: 12 traders + 3 analysts

**6:00 AM**: Team workspace activates
- AI posts morning brief to team chat
- Everyone sees same analysis
- Live discussion begins

**9:30 AM**: Market opens
- Live P&L dashboard updates every 5 seconds
- All team members see real-time portfolio value
- Leaderboard shows top performers

**10:00 AM**: Trader spots opportunity
- Posts in chat: "NVDA breaking out, thoughts?"
- AI responds within 2 seconds:
  - Current sentiment: 0.82 (very bullish)
  - Backtest validation: 67% win rate
  - Suggested entry: $485, stop: $475, target: $510
  - Risk: 2.5% of team NAV
- Team discusses, votes, executes

**11:00 AM**: Risk analyst runs custom backtest
- Uses API to test proprietary strategy
- Optimizes parameters programmatically
- Deploys to paper trading
- Team can monitor performance

**2:00 PM**: Important alert
- AI detects sentiment shift on team's largest position
- Broadcasts to all team members instantly
- Includes AI analysis: "Why this matters"
- Team collaboratively decides to reduce position

**3:00 PM**: New analyst joins team
- Onboarded to workspace
- Sees full chat history
- Granted "viewer" role initially
- Can see all analysis but can't trade

**5:00 PM**: Team review
- AI generates team performance summary
- Individual contribution breakdown
- Best/worst trades discussed
- AI suggests improvements for tomorrow

**6:00 PM**: Compliance export
- Export full audit trail (required for fund)
- All trades, decisions, chat logs
- Compliance-ready format

---

## 🔧 Complete Technical Architecture (Full Depth)

### Full Agent System

```
User Query → Router Agent
    ↓
    ├─ RECOMMEND → Orchestrator
    │   ├─ Sentiment Aggregator
    │   ├─ RAG Pipeline (Exa + pgvector + Mem0)
    │   ├─ Market Data Service
    │   ├─ Recommendation Agent
    │   │   ├─ Risk Calculator (MCP Tools)
    │   │   ├─ GPT-4o for generation
    │   │   ├─ Backtest Validator
    │   │   ├─ Add Disclaimer
    │   │   └─ Store to DB
    │   └─ Return recommendation
    │
    ├─ RESEARCH → Orchestrator
    │   ├─ Sentiment Aggregator
    │   ├─ RAG Pipeline (deep mode)
    │   ├─ Long Context Analyst (10-K analysis)
    │   └─ Return research report
    │
    ├─ PORTFOLIO → Direct DB Query
    │   ├─ Fetch positions
    │   ├─ Calculate live P&L
    │   ├─ Performance analytics
    │   └─ Return portfolio view
    │
    ├─ ALERTS → Monitor Agent
    │   ├─ Check alert rules
    │   ├─ Evaluate triggers
    │   ├─ Send notifications
    │   └─ Broadcast to workspace
    │
    ├─ EXPLAIN → Explainer Agent
    │   ├─ Detect user level (beginner/intermediate/expert)
    │   ├─ Generate explanation
    │   ├─ Optional voice synthesis
    │   └─ Return explanation
    │
    └─ BACKTEST → Backtest Service
        ├─ Strategy Builder
        ├─ Run Backtest
        ├─ Generate Metrics
        └─ Return results (frontend charts)
```

### Full Data Pipeline

**Sentiment Pipeline**:
```
Symbol: NVDA
    ↓
Parallel Fetch (3 sources):
├─ News Sentiment
│  ├─ Exa search: "NVDA latest news"
│  ├─ LLM score each article (0-1)
│  └─ Aggregate: 0.75
│
├─ Reddit Sentiment
│  ├─ PRAW: r/wallstreetbets, r/stocks
│  ├─ Count mentions: 1,823 in 24h
│  ├─ Keyword analysis (bullish/bearish)
│  └─ Score: 0.88
│
└─ StockTwits Sentiment
   ├─ API: Get stream
   ├─ Volume: 542 messages
   └─ Score: 0.84 (provided by StockTwits)
    ↓
Aggregator:
├─ Weighted average (40% news, 30% reddit, 30% stocktwits)
├─ Detect trending (volume > 2x average)
├─ Detect extremes (>90% = contrarian signal)
└─ Return: 0.82 overall
    ↓
Cache (1 hour TTL)
Store in database
Return to user
```

**Full RAG Pipeline** (Post Phase 2):
```
Query: "NVDA analysis"
    ↓
Check Cache (4h TTL)
    ↓ Miss
Parallel Retrieval:
├─ Exa.ai (5 news articles)
├─ Supabase pgvector (10 cached research notes)
├─ Mem0 (user's past NVDA trades + preferences)
└─ Sentiment (current score: 0.82)
    ↓
Rank & Combine (top 10 sources)
    ↓
Assemble Context:
## Market Intelligence
- Current Sentiment: 82% bullish (trending)
- Recent News: [5 articles with scores]
- Historical Performance: [user's past trades]
- Technical Setup: [from cached analysis]
    ↓
Return to LLM for generation
```

**Backtest Pipeline**:
```
Strategy Definition (JSON)
    ↓
Strategy Builder
├─ Parse entry rules
├─ Parse exit rules
├─ Parse position sizing
└─ Build executable function
    ↓
Fetch Historical Data (yfinance/AlphaVantage)
    ↓
Simulate Trades
├─ Loop through each day
├─ Evaluate entry conditions
├─ Track open positions
├─ Check exit conditions
├─ Calculate P&L
└─ Record each trade
    ↓
Calculate Metrics
├─ Total return, win rate
├─ Sharpe ratio, Sortino ratio
├─ Max drawdown, avg win/loss
├─ Monthly returns breakdown
└─ Trade distribution analysis
    ↓
Generate Data for Charts
├─ Equity curve points
├─ Drawdown series
├─ Monthly returns grid
└─ Trade markers
    ↓
Store Results (database)
Return to Frontend (raw data)
```

**Collaboration Pipeline**:
```
User types in workspace chat: "Thinking about NVDA calls"
    ↓
WebSocket receives message
    ↓
Broadcast to all team members (instant)
    ↓
AI Chat Agent analyzes:
├─ Detect symbols mentioned (NVDA)
├─ Check if should respond (keywords: "thinking about", "calls")
├─ Get chat history (last 20 messages)
├─ Get team context (positions, watchlist)
└─ Decision: YES, respond
    ↓
Generate AI Response:
├─ Get sentiment (0.82 bullish)
├─ Run quick backtest of calls strategy
├─ Generate contextual response with GPT-4o
└─ Include trade suggestion
    ↓
Broadcast AI response to team
    ↓
If trade executed:
├─ Update shared P&L
├─ Broadcast to all members
└─ Add to team performance tracking
```

---

## 📊 Complete Data Models

### Sentiment Data
```python
class SentimentScore(BaseModel):
    symbol: str
    overall_score: float  # 0-1
    sentiment_breakdown: Dict[str, float]
    volume: Dict[str, int]
    trending: bool
    contrarian_signal: bool
    confidence: float
    sources: List[SentimentSource]
    timestamp: datetime
    cached: bool
    
class SentimentSource(BaseModel):
    type: Literal["news", "reddit", "stocktwits", "insider"]
    score: float
    title: str
    url: str
    published_date: Optional[str]
    author: Optional[str]
    engagement: Optional[int]  # Upvotes, likes, etc.
```

### Backtest Data
```python
class BacktestRequest(BaseModel):
    strategy_definition: Dict
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    
class BacktestResult(BaseModel):
    strategy_name: str
    symbol: str
    metrics: BacktestMetrics
    trades: List[Trade]
    equity_curve: List[float]
    drawdown_series: List[float]
    monthly_returns: Dict[str, float]
    
class BacktestMetrics(BaseModel):
    total_return: float
    total_return_pct: float
    annualized_return: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    avg_win: float
    avg_loss: float
    num_trades: int
    avg_hold_time_days: float
```

### Collaboration Data
```python
class Workspace(BaseModel):
    id: str
    name: str
    tier: Literal["Pro", "Enterprise"]
    members: List[WorkspaceMember]
    created_at: datetime
    
class WorkspaceMember(BaseModel):
    user_id: str
    email: str
    role: Literal["owner", "admin", "member", "viewer"]
    joined_at: datetime
    
class ChatMessage(BaseModel):
    id: str
    workspace_id: str
    user_id: Optional[str]  # None for AI messages
    message: str
    message_type: Literal["user", "ai", "system"]
    trade_suggestions: Optional[List[Recommendation]]
    timestamp: datetime
    
class SharedWatchlist(BaseModel):
    workspace_id: str
    symbols: List[WatchlistItem]
    
class WatchlistItem(BaseModel):
    symbol: str
    added_by: str
    added_at: datetime
    current_price: float
    sentiment_score: float
    ai_analysis: Optional[str]
```

---

## 🔧 Complete API Reference

### Sentiment Endpoints
```
GET  /sentiment/{symbol}
GET  /sentiment/trending
POST /sentiment/bulk (batch of symbols)
GET  /sentiment/history/{symbol} (historical sentiment)
```

### Backtesting Endpoints
```
POST /backtest/run
POST /backtest/optimize (parameter optimization)
GET  /backtest/templates
GET  /backtest/results/{backtest_id}
GET  /backtest/compare (compare multiple strategies)
POST /backtest/deploy (deploy to paper trading)
```

### Collaboration Endpoints
```
POST   /workspace/create
GET    /workspace/{id}
POST   /workspace/{id}/invite
DELETE /workspace/{id}/member/{user_id}
POST   /workspace/{id}/message
GET    /workspace/{id}/messages
POST   /workspace/{id}/watchlist/add
DELETE /workspace/{id}/watchlist/remove
WS     /ws/{workspace_id} (WebSocket)
```

### Recommendation Endpoints
```
POST /ai/recommend
POST /ai/recommend/bulk (multiple symbols)
GET  /ai/recommend/history
POST /ai/recommend/accept (user executed)
```

### Portfolio Endpoints
```
GET  /portfolio/{user_id}
POST /portfolio/sync (sync from broker)
GET  /portfolio/pnl
GET  /portfolio/analytics
POST /portfolio/position/open
POST /portfolio/position/close
```

---

## 🎯 Complete Demo Script (5 Minutes)

### Opening (30 seconds)
"Kopitiam Capital is an AI-native trading intelligence platform with three unique differentiators that work together."

### Differentiator 1: Sentiment Analysis (90 seconds)
1. Open app, type "What's the sentiment on NVDA?"
2. Show sentiment breakdown:
   - Overall: 82% bullish
   - News: 75% (45 articles analyzed)
   - Reddit: 88% (1,823 mentions, trending)
   - StockTwits: 84% (542 messages)
3. Click through to source articles
4. "We aggregate sentiment from multiple sources in real-time"

### Differentiator 2: Backtesting (90 seconds)
5. Click "Get Recommendation"
6. AI suggests: "BUY NVDA at $485, stop $475, target $510"
7. Shows inline: "This strategy won 67% of trades in past 6 months"
8. Click "See Backtest Details"
9. Shows:
   - Equity curve (rising)
   - Win rate: 67%
   - Sharpe: 1.85
   - 45 historical trades
10. "One-click validation of any strategy before you trade"

### Differentiator 3: Collaboration (90 seconds)
11. Switch to team workspace view
12. Type in chat: "@ai what do you think about this NVDA setup?"
13. AI responds in 2 seconds:
   - "Based on 82% bullish sentiment and backtest validation..."
   - Includes trade suggestion
   - Cites sources
14. Show that message broadcasts to all 3 team members instantly
15. Add NVDA to shared watchlist
16. Everyone sees the update
17. "Real-time collaborative intelligence - AI is part of the team"

### Closing (30 seconds)
18. "Three differentiators: Sentiment, Validation, Collaboration"
19. "Available in three tiers: Free, Pro ($49/mo), Enterprise ($500+/mo)"
20. "Built for the future of trading intelligence"

**Total**: 5 minutes

---

## 💰 Complete Revenue Model

### Target Metrics (Year 1)
- Free users: 10,000
- Pro conversions: 500 (5%)
- Enterprise clients: 25 teams (0.25%)

### Revenue Projections
```
Pro Tier: 500 × $79/mo × 12 = $474,000/year
Enterprise: 25 × $1000/mo × 12 = $300,000/year
Total ARR: $774,000

Costs:
- API costs: ~$150/month × 12 = $1,800/year
- Infrastructure: ~$500/month × 12 = $6,000/year
- Support: 2 people × $50k = $100,000/year
Total Costs: ~$108,000/year

Gross Margin: 86%
```

### Path to Profitability
- Month 1-3: Build MVP, beta test
- Month 4-6: Launch, acquire first 100 Pro users
- Month 7-9: Enterprise sales, first 10 teams
- Month 10-12: Scale to 500 Pro, 25 Enterprise
- **Profitable by Month 8**

---

## 🚀 Post-Hackathon Roadmap

### Week 3-4: Beta Testing
- 50 beta users (mix of free/pro)
- Gather feedback
- Fix bugs
- Tune sentiment algorithms

### Week 5-6: Broker Integration
- Interactive Brokers API
- Tiger Brokers (Singapore)
- Saxo Bank
- Auto-sync positions

### Week 7-8: Mobile App Polish
- Push notifications
- Voice briefings
- Offline mode
- Performance optimization

### Week 9-10: Enterprise Features
- SSO/SAML
- Audit trails
- Advanced analytics
- White-label prep

### Week 11-12: Launch Prep
- Marketing site
- Payment processing (Stripe)
- Customer support
- Legal/compliance review
- Public launch

### Month 4-6: Growth
- Content marketing
- Partnerships (brokers, fintechs)
- Referral program
- Social proof (testimonials)

### Month 7-12: Scale
- API marketplace
- Third-party integrations
- International expansion
- Institutional features

---

## 🎓 Complete Feature Depth (Phase 2+)

### Advanced Sentiment Features
- Insider trading tracker (SEC Form 4)
- Options flow analysis (unusual activity)
- Institutional sentiment (13F filings)
- Analyst upgrades/downgrades
- News sentiment trends (improving/declining)
- Sector rotation signals
- Fear/greed index

### Advanced Backtesting Features
- Walk-forward optimization
- Monte Carlo simulation
- Multi-asset backtesting
- Options strategies
- Portfolio-level backtesting
- Genetic algorithm optimization
- Reality checks (slippage, commission)
- Market regime analysis

### Advanced Collaboration Features
- Live P&L streaming (5-second updates)
- Collaborative chart annotations
- Screen sharing
- Voice channels
- Trade copy functionality
- Performance leaderboards
- Team challenges/competitions
- Shared research library

### Additional Agents
- Long Context Analyst (10-K, 10-Q deep analysis)
- Earnings Analyst (transcript analysis)
- Options Analyst (Greeks, strategies)
- Portfolio Optimizer (rebalancing suggestions)
- Tax Optimizer (loss harvesting)
- Risk Monitor (portfolio VaR, stress testing)

---

## 🏆 Why This Wins

### Technical Excellence
- Production-grade from day one
- Cost-aware architecture
- 99.9% uptime (resilience)
- Real-time capabilities
- Mobile-first design

### Business Model
- Clear tier differentiation
- Path from free to enterprise
- High gross margins (86%)
- Sticky features (collaboration)
- API revenue stream

### Market Fit
- Solves real problems (information overload, strategy validation, team coordination)
- Unique combination (no competitor has all 3)
- Scalable (free → pro → enterprise)
- Global market (English + Mandarin + Malay)

---

**This is the complete vision. Now let's build the MVP!** 🚀

