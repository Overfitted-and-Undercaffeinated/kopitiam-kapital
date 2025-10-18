# API Reference

## FastAPI Backend

Base URL: `http://localhost:8000`

### Health Check

```
GET /health
```

Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "service": "kopitiam-capital-ai",
  "version": "1.0.0"
}
```

### Route Query

```
POST /ai/route
```

Routes a user query to the appropriate agent.

**Request:**
```json
{
  "query": "What are the best stocks to buy right now?"
}
```

**Response:**
```json
{
  "intent": "RESEARCH",
  "entities": ["stocks"]
}
```

### Generate Recommendation

```
POST /ai/recommend
```

Generates a trading recommendation for a user.

**Request:**
```json
{
  "user_id": "uuid",
  "symbol": "AAPL"
}
```

**Response:**
```json
{
  "action": "BUY",
  "symbol": "AAPL",
  "entry": 175.50,
  "stop": 170.00,
  "target": 185.00,
  "size_pct_nav": 5.0,
  "thesis": "Strong earnings momentum...",
  "risks": "Market volatility, sector rotation...",
  "confidence": 0.75,
  "sources": [...]
}
```

### Morning Brief

```
POST /ai/morning
```

Generates morning brief for a user.

**Request:**
```json
{
  "user_id": "uuid"
}
```

### End-of-Day Report

```
POST /ai/eod
```

Generates end-of-day report for a user.

**Request:**
```json
{
  "user_id": "uuid"
}
```

### Analyze Filing

```
POST /ai/longctx
```

Analyzes a long-form financial document.

**Request:**
```json
{
  "ticker": "AAPL",
  "filing_type": "10-K"
}
```

## Database Schema

See `supabase/migrations/` for the complete database schema.

### Key Tables

- `users`: User profiles and preferences
- `instruments`: Trading instruments (stocks, commodities, etc.)
- `positions`: User positions
- `recommendations`: AI-generated recommendations
- `events`: Market events
- `pnl_snapshots`: P&L history
- `notes`: RAG knowledge base with embeddings

