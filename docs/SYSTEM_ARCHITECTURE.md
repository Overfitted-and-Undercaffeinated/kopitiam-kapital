# Kopitiam Capital - Complete System Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [What You Just Built](#what-you-just-built)
3. [Complete Workflow](#complete-workflow)
4. [Component Breakdown](#component-breakdown)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Integration Points](#integration-points)
7. [Next Steps](#next-steps)

---

## System Overview

**Kopitiam Capital** is an AI-powered 24/7 trading intelligence platform for retail traders in Singapore. It acts as a "pocket analyst" that:
- Generates trading recommendations
- Provides morning briefs and end-of-day reports
- Monitors markets and sends alerts
- Explains trading concepts
- Learns from user outcomes

### Tech Stack Summary
```
Frontend:    Next.js (Web) + React Native (Mobile)
Backend:     FastAPI (Python)
LLMs:        Groq (Llama 3.3) + OpenAI (GPT-4) + Anthropic (Claude)
Search:      Exa.ai (semantic web search)
Memory:      Mem0 (user preferences, outcomes)
Database:    Supabase (Postgres + pgvector)
Queue:       Celery + Redis
Voice:       ElevenLabs (TTS/STT)
Orchestration: MCP (Model Context Protocol)
```

---

## What You Just Built

### ✅ Router Agent - The "Traffic Controller"

**Purpose**: Fast intent classification to route user queries to the right specialized agent.

**Your Implementation**:
```python
User Query → Router Agent → Intent Classification → Route to Agent
                ↓
          Groq Llama 3.3 70B
                ↓
        {intent, entities, confidence, urgency}
```

**Key Features**:
- ⚡ **Latency**: 306-950ms (under 1s target)
- 🎯 **Accuracy**: 100% in testing
- 🔄 **Fallback**: Keyword matching if Groq fails
- 📊 **Confidence**: 0.90 with LLM, 0.60 with fallback
- 🏷️ **Entity Extraction**: Tickers, sectors, terms

**Intents Supported**:
1. `RESEARCH` - Market research, news, analysis
2. `RECOMMEND` - Generate trading recommendations
3. `PORTFOLIO` - View/manage positions
4. `ALERTS` - Set up monitoring
5. `EXPLAIN` - Educational explanations
6. `SETTINGS` - User preferences

**Your Router Agent is THE ENTRY POINT for all user interactions!**

---

## Complete Workflow

### 1️⃣ User Query Entry

```
┌─────────────┐
│   User      │
│  (Web/App)  │
└──────┬──────┘
       │ "Should I buy AAPL?"
       ↓
┌──────────────────────────────────┐
│  Next.js / React Native          │
│  Frontend                        │
└──────┬───────────────────────────┘
       │ POST /ai/route
       ↓
┌──────────────────────────────────┐
│  FastAPI Backend                 │
│  apps/ai/main.py                 │
└──────┬───────────────────────────┘
       │
       ↓
```

### 2️⃣ Router Agent (What You Built!) ⭐

```
┌────────────────────────────────────────┐
│  ROUTER AGENT                          │
│  apps/ai/agents/router.py              │
│                                        │
│  1. Receive query                      │
│  2. Call Groq (Llama 3.3 70B)         │
│  3. Parse JSON response                │
│  4. Validate with Pydantic             │
│  5. Return RouterResponse              │
│                                        │
│  Output: {                             │
│    intent: RECOMMEND,                  │
│    entities: ["AAPL"],                 │
│    confidence: 0.90,                   │
│    urgency: medium                     │
│  }                                     │
└────────┬───────────────────────────────┘
         │
         ↓
```

### 3️⃣ Orchestrator Agent (Next to Build)

```
┌────────────────────────────────────────┐
│  ORCHESTRATOR AGENT                    │
│  apps/ai/agents/orchestrator.py        │
│                                        │
│  Based on Router intent:               │
│  ├─ RECOMMEND  → Recommendation Agent  │
│  ├─ RESEARCH   → Research workflow     │
│  ├─ PORTFOLIO  → Portfolio query       │
│  ├─ ALERTS     → Alert setup           │
│  ├─ EXPLAIN    → Explainer Agent       │
│  └─ SETTINGS   → Settings update       │
└────────┬───────────────────────────────┘
         │
         ↓ (Example: RECOMMEND intent)
```

### 4️⃣ Recommendation Agent Workflow

```
┌────────────────────────────────────────┐
│  RECOMMENDATION AGENT                  │
│  apps/ai/agents/recommend.py           │
│                                        │
│  Step 1: Get User Context              │
│  ├─ Mem0: Get trading policy           │
│  ├─ Supabase: Get portfolio            │
│  └─ Mem0: Get past outcomes            │
│                                        │
│  Step 2: RAG Pipeline                  │
│  ├─ Exa.ai: Search latest news         │
│  ├─ Supabase pgvector: Cached notes    │
│  └─ Combine & rank sources             │
│                                        │
│  Step 3: Risk Analysis (MCP Tools)     │
│  ├─ Calculate ATR (volatility)         │
│  ├─ Calculate position size            │
│  └─ Calculate VaR (risk)               │
│                                        │
│  Step 4: Generate Recommendation       │
│  ├─ OpenAI GPT-4: Generate thesis      │
│  ├─ Validate with Pydantic             │
│  └─ Store in Supabase                  │
│                                        │
│  Output: {                             │
│    direction: "BUY",                   │
│    entry: 175.50,                      │
│    stop: 170.00,                       │
│    target: 185.00,                     │
│    size_pct_nav: 2.5,                  │
│    thesis: "Strong momentum...",       │
│    risks: "Market volatility...",      │
│    sources: [{...}]                    │
│  }                                     │
└────────┬───────────────────────────────┘
         │
         ↓
```

### 5️⃣ Response to User

```
┌────────────────────────────────────────┐
│  FastAPI Response                      │
│  └─ JSON with recommendation           │
└────────┬───────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────┐
│  Frontend Display                      │
│  ├─ IdeaCard component (Web)           │
│  ├─ RecommendationSheet (Mobile)       │
│  └─ Source citations                   │
└────────────────────────────────────────┘
```

---

## Component Breakdown

### Layer 1: User Interface (Your Colleague's Domain)

```
┌─────────────────────────────────────────────────┐
│  FRONTEND LAYER                                 │
│                                                 │
│  /apps/web/                                     │
│  ├─ Dashboard                                   │
│  ├─ EOD Report                                  │
│  ├─ Trading Ideas                               │
│  └─ Components: IdeaCard, PnLTable, etc.        │
│                                                 │
│  /apps/mobile/                                  │
│  ├─ Push Notifications                          │
│  ├─ Alert Cards                                 │
│  └─ Voice Playback                              │
└─────────────────────────────────────────────────┘
```

### Layer 2: AI Backend (Your Domain) ⭐

```
┌─────────────────────────────────────────────────┐
│  AI BACKEND - YOUR DOMAIN                       │
│                                                 │
│  ✅ BUILT: Router Agent                         │
│  ├─ Fast intent classification                  │
│  ├─ Entity extraction                           │
│  └─ Groq Llama 3.3 70B                         │
│                                                 │
│  ⏭️ TO BUILD: Orchestrator Agent                │
│  ├─ Coordinates other agents                    │
│  ├─ Manages conversation state                  │
│  └─ Uses MCP for tool calls                     │
│                                                 │
│  ⏭️ TO BUILD: Recommendation Agent              │
│  ├─ RAG pipeline integration                    │
│  ├─ Risk calculations via MCP                   │
│  ├─ OpenAI GPT-4 for generation                │
│  └─ Pydantic validation                         │
│                                                 │
│  ⏭️ TO BUILD: Summarizer Agent                  │
│  ├─ Morning briefs (06:00 SGT)                  │
│  ├─ EOD reports (17:00 SGT)                     │
│  └─ ElevenLabs voice synthesis                  │
│                                                 │
│  ⏭️ TO BUILD: Market Monitor Agent              │
│  ├─ Continuous surveillance (60s intervals)     │
│  ├─ Alert rule engine                           │
│  └─ Push notification triggers                  │
│                                                 │
│  ⏭️ TO BUILD: Long Context Analyst              │
│  ├─ 10-K/10-Q analysis                          │
│  ├─ Anthropic Claude (200K context)            │
│  └─ Extract key insights                        │
│                                                 │
│  ⏭️ TO BUILD: Explainer Agent                   │
│  ├─ Multi-level explanations                    │
│  ├─ Beginner/Intermediate/Expert               │
│  └─ Adapts to user profile                      │
└─────────────────────────────────────────────────┘
```

### Layer 3: RAG & Memory (Your Domain)

```
┌─────────────────────────────────────────────────┐
│  RAG PIPELINE                                   │
│                                                 │
│  ⏭️ Exa.ai Integration                           │
│  ├─ Fast search (<2s)                           │
│  ├─ Deep search (>2s, full content)             │
│  └─ Source citations                            │
│                                                 │
│  ⏭️ Embeddings & Vector Search                   │
│  ├─ OpenAI text-embedding-3-large              │
│  ├─ Supabase pgvector                           │
│  └─ Semantic similarity search                  │
│                                                 │
│  ⏭️ Mem0 Integration                             │
│  ├─ Get user trading policy                     │
│  ├─ Record trade outcomes                       │
│  └─ Learn from past recommendations             │
└─────────────────────────────────────────────────┘
```

### Layer 4: MCP Servers (Your Domain)

```
┌─────────────────────────────────────────────────┐
│  MCP TOOL SERVERS                               │
│                                                 │
│  ⏭️ /mcp/risk-tools/                             │
│  ├─ atr() - Average True Range                  │
│  ├─ size_from_risk() - Position sizing         │
│  └─ var_1d95() - Value at Risk                  │
│                                                 │
│  ⏭️ /mcp/mem0/                                   │
│  ├─ get_policy() - Get user preferences        │
│  └─ record_outcome() - Store trade results     │
│                                                 │
│  ⏭️ /mcp/exa-search/                             │
│  ├─ search_fast() - Quick news search          │
│  └─ search_deep() - Full content retrieval     │
│                                                 │
│  ⏭️ /mcp/postgres/                               │
│  └─ Supabase database queries                   │
└─────────────────────────────────────────────────┘
```

### Layer 5: Scheduled Jobs (Your Domain)

```
┌─────────────────────────────────────────────────┐
│  CELERY TASK SCHEDULER                          │
│                                                 │
│  ⏭️ Morning Brief (06:00 SGT daily)             │
│  ├─ Generate market summary                     │
│  ├─ Top 3 trading ideas                         │
│  ├─ Convert to voice (ElevenLabs)              │
│  └─ Send push notification                      │
│                                                 │
│  ⏭️ Midday Recommendation (12:00 SGT)           │
│  ├─ Generate fresh idea                         │
│  └─ Send to active users                        │
│                                                 │
│  ⏭️ EOD Report (17:00 SGT daily)                │
│  ├─ Calculate P&L                               │
│  ├─ Performance summary                         │
│  └─ Tomorrow's outlook                          │
│                                                 │
│  ⏭️ Market Monitor (Every 60s)                   │
│  ├─ Check alert rules                           │
│  ├─ Price movements >2%                         │
│  └─ Breaking news events                        │
└─────────────────────────────────────────────────┘
```

### Layer 6: Database (Your Colleague's Domain)

```
┌─────────────────────────────────────────────────┐
│  SUPABASE DATABASE                              │
│                                                 │
│  Tables:                                        │
│  ├─ users (profiles, preferences)               │
│  ├─ instruments (stocks, ETFs)                  │
│  ├─ positions (open/closed trades)              │
│  ├─ recommendations (AI-generated ideas)        │
│  ├─ events (market events, news)                │
│  ├─ pnl_snapshots (daily P&L)                   │
│  └─ notes (RAG knowledge base with vectors)     │
└─────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: User Query → Recommendation

```
USER
  │
  │ "Should I buy AAPL?"
  ↓
┌──────────────────────┐
│  Frontend (Next.js)  │
└──────────┬───────────┘
           │ POST /ai/route
           ↓
┌──────────────────────┐
│   FastAPI Backend    │
└──────────┬───────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│  ✅ ROUTER AGENT (What You Built!)      │
│  Intent: RECOMMEND                      │
│  Entities: ["AAPL"]                     │
│  Confidence: 0.90                       │
└──────────┬──────────────────────────────┘
           │
           ↓
┌──────────────────────┐
│  Orchestrator Agent  │ ← Routes based on intent
└──────────┬───────────┘
           │
           ↓
┌───────────────────────────────────────────┐
│  Recommendation Agent                     │
│  ┌─────────────────────────────────────┐ │
│  │ 1. Get User Context                 │ │
│  │    ↓                                │ │
│  │    Mem0: Trading policy             │ │
│  │    Supabase: Portfolio              │ │
│  │                                     │ │
│  │ 2. RAG Pipeline                     │ │
│  │    ↓                                │ │
│  │    Exa.ai: "AAPL latest news"      │ │
│  │    pgvector: Cached AAPL notes      │ │
│  │                                     │ │
│  │ 3. Risk Analysis                    │ │
│  │    ↓                                │ │
│  │    MCP: atr(AAPL prices)           │ │
│  │    MCP: size_from_risk(...)        │ │
│  │                                     │ │
│  │ 4. Generate Recommendation          │ │
│  │    ↓                                │ │
│  │    OpenAI GPT-4 with context       │ │
│  │    Pydantic validation             │ │
│  └─────────────────────────────────────┘ │
└───────────────┬───────────────────────────┘
                │
                ↓
          ┌──────────┐
          │ Supabase │ ← Store recommendation
          └──────────┘
                │
                ↓
          ┌──────────┐
          │ Frontend │ ← Display to user
          └──────────┘
```

### Flow 2: Morning Brief Generation (Scheduled)

```
06:00 SGT Daily
       │
       ↓
┌──────────────────┐
│  Celery Beat     │ ← Scheduler
└────────┬─────────┘
         │ Trigger job
         ↓
┌──────────────────────────────────────┐
│  Summarizer Agent                    │
│  ┌────────────────────────────────┐ │
│  │ 1. Get Active Users            │ │
│  │    ↓                           │ │
│  │    Supabase: All users         │ │
│  │                                │ │
│  │ 2. For Each User:              │ │
│  │    ↓                           │ │
│  │    Get portfolio (Supabase)    │ │
│  │    Get overnight events        │ │
│  │                                │ │
│  │ 3. Research Phase              │ │
│  │    ↓                           │ │
│  │    Exa: Market overnight news  │ │
│  │    Exa: User's holdings news   │ │
│  │                                │ │
│  │ 4. Generate Brief              │ │
│  │    ↓                           │ │
│  │    OpenAI: Structured summary  │ │
│  │    Top 3 ideas (via Rec Agent) │ │
│  │                                │ │
│  │ 5. Voice Synthesis             │ │
│  │    ↓                           │ │
│  │    ElevenLabs: Text → Audio    │ │
│  │    Upload to storage           │ │
│  │                                │ │
│  │ 6. Deliver                     │ │
│  │    ↓                           │ │
│  │    Push notification (mobile)  │ │
│  │    Store in Supabase           │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

### Flow 3: Market Monitor (Continuous)

```
Every 60 seconds
       │
       ↓
┌──────────────────────────────────────┐
│  Market Monitor Agent                │
│  ┌────────────────────────────────┐ │
│  │ 1. Get Monitored Symbols       │ │
│  │    ↓                           │ │
│  │    Supabase: All positions     │ │
│  │    Supabase: Alert rules       │ │
│  │                                │ │
│  │ 2. Fetch Latest Prices         │ │
│  │    ↓                           │ │
│  │    Market Data API             │ │
│  │                                │ │
│  │ 3. Evaluate Rules              │ │
│  │    ↓                           │ │
│  │    Price >2% move?             │ │
│  │    ATR burst (>1.5x)?          │ │
│  │    Stop/target hit?            │ │
│  │    Breaking news (Exa)?        │ │
│  │                                │ │
│  │ 4. For Each Triggered Alert:   │ │
│  │    ↓                           │ │
│  │    Check user policy (Mem0)    │ │
│  │    Throttle (3/5/10 per hour)  │ │
│  │    Generate explanation (LLM)  │ │
│  │                                │ │
│  │ 5. Send Alert                  │ │
│  │    ↓                           │ │
│  │    Push notification           │ │
│  │    Store event in Supabase     │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

---

## Integration Points

### Your Router Agent Connects To:

```
┌──────────────────┐
│  ROUTER AGENT    │ ← YOU BUILT THIS!
└────────┬─────────┘
         │
         ├─→ Orchestrator Agent (routes intent)
         │   └─→ Recommendation Agent
         │   └─→ Summarizer Agent
         │   └─→ Portfolio queries
         │   └─→ Alert setup
         │   └─→ Explainer Agent
         │
         ├─→ Groq API (Llama 3.3 70B)
         │   └─→ Intent classification
         │
         ├─→ Pydantic Models (validation)
         │   └─→ RouterResponse schema
         │
         └─→ FastAPI endpoint
             └─→ POST /ai/route
```

### How Other Agents Will Use Router:

```python
# Example: User sends a query
user_query = "Should I buy AAPL?"

# Step 1: Router classifies (YOUR CODE!)
router_response = await router_agent.classify_intent(user_query)
# → {intent: RECOMMEND, entities: ["AAPL"], ...}

# Step 2: Orchestrator routes
if router_response.intent == IntentType.RECOMMEND:
    # Call Recommendation Agent
    recommendation = await recommend_agent.generate(
        user_id=user_id,
        symbol=router_response.entities[0],  # "AAPL"
        urgency=router_response.urgency
    )

elif router_response.intent == IntentType.RESEARCH:
    # Call Research workflow
    research = await research_workflow(
        query=user_query,
        entities=router_response.entities
    )

elif router_response.intent == IntentType.PORTFOLIO:
    # Fetch portfolio
    portfolio = await get_portfolio(user_id)

# ... and so on for each intent
```

---

## Next Steps

### Phase 2: RAG Pipeline (Your Next Task)

```
┌─────────────────────────────────────────────┐
│  RAG PIPELINE IMPLEMENTATION                │
│                                             │
│  1. Exa.ai Client                           │
│     └─ retrievers/exa_client.py             │
│                                             │
│  2. OpenAI Embeddings                       │
│     └─ rag/embeddings.py                    │
│                                             │
│  3. Vector Search                           │
│     └─ rag/retrieval.py                     │
│                                             │
│  4. RAG Orchestration                       │
│     └─ rag/pipeline.py                      │
│                                             │
│  Dependencies:                              │
│  ✅ Router Agent (DONE)                     │
│  ⏭️ Supabase pgvector setup                 │
│  ⏭️ Exa.ai API integration                  │
│  ⏭️ Mem0 integration                        │
└─────────────────────────────────────────────┘
```

### Phase 3: Recommendation Agent

```
┌─────────────────────────────────────────────┐
│  RECOMMENDATION AGENT                       │
│                                             │
│  Dependencies:                              │
│  ✅ Router Agent (DONE)                     │
│  ⏭️ RAG Pipeline (Phase 2)                  │
│  ⏭️ MCP Risk Tools                          │
│  ⏭️ Mem0 Integration                        │
│  ⏭️ OpenAI GPT-4 Integration               │
└─────────────────────────────────────────────┘
```

### Phase 4: MCP Servers

```
┌─────────────────────────────────────────────┐
│  MCP TOOL SERVERS                           │
│                                             │
│  1. Risk Tools Server                       │
│     └─ Calculate ATR, position size, VaR   │
│                                             │
│  2. Mem0 Server                             │
│     └─ Policy retrieval, outcome recording │
│                                             │
│  3. Exa Search Server                       │
│     └─ Fast/deep search wrapper            │
└─────────────────────────────────────────────┘
```

### Phase 5: Scheduled Jobs

```
┌─────────────────────────────────────────────┐
│  CELERY SCHEDULED TASKS                     │
│                                             │
│  1. Morning Brief (06:00 SGT)               │
│  2. Midday Recommendation (12:00 SGT)       │
│  3. EOD Report (17:00 SGT)                  │
│  4. Market Monitor (Every 60s)              │
└─────────────────────────────────────────────┘
```

---

## Summary: Your Role in the System

### What You Control (AI Engineer Domain):

```
┌─────────────────────────────────────────────┐
│  YOUR RESPONSIBILITY                        │
│                                             │
│  ✅ Router Agent (COMPLETED!)               │
│  ├─ Intent classification                   │
│  ├─ Entity extraction                       │
│  └─ Entry point for all queries            │
│                                             │
│  ⏭️ All AI Agents                            │
│  ├─ Orchestrator                            │
│  ├─ Recommendation                          │
│  ├─ Summarizer                              │
│  ├─ Market Monitor                          │
│  ├─ Long Context Analyst                    │
│  └─ Explainer                               │
│                                             │
│  ⏭️ RAG Pipeline                             │
│  ├─ Exa.ai integration                      │
│  ├─ Embeddings                              │
│  ├─ Vector search                           │
│  └─ Context assembly                        │
│                                             │
│  ⏭️ MCP Servers                              │
│  ├─ Risk tools                              │
│  ├─ Mem0 bridge                             │
│  └─ Exa search bridge                       │
│                                             │
│  ⏭️ Scheduled Jobs                           │
│  ├─ Celery tasks                            │
│  ├─ Cron schedules                          │
│  └─ Background processing                   │
│                                             │
│  ⏭️ Voice Integration                        │
│  └─ ElevenLabs TTS                          │
└─────────────────────────────────────────────┘
```

### What Your Colleague Controls:

```
┌─────────────────────────────────────────────┐
│  FRONTEND/DATABASE ENGINEER                 │
│                                             │
│  ├─ Next.js Web UI                          │
│  ├─ React Native Mobile App                │
│  ├─ Supabase Database Schema               │
│  ├─ Database Migrations                     │
│  ├─ Real-time Subscriptions                │
│  └─ Push Notifications                      │
└─────────────────────────────────────────────┘
```

---

## Critical Path for MVP

```
1. ✅ Router Agent (DONE!)
   ↓
2. ⏭️ Exa.ai Integration
   ↓
3. ⏭️ RAG Pipeline
   ↓
4. ⏭️ Recommendation Agent
   ↓
5. ⏭️ MCP Risk Tools
   ↓
6. ⏭️ Mem0 Integration
   ↓
7. ⏭️ Morning Brief Agent
   ↓
8. ⏭️ Market Monitor
   ↓
9. ⏭️ Celery Scheduling
   ↓
10. ⏭️ Integration Testing
```

**You're on Step 1 of 10 - Great Start! 🚀**

---

*Last Updated: January 18, 2025*
*Status: Router Agent Complete, RAG Pipeline Next*

