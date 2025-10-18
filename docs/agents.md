# Agent Specifications

## Agent Types

### 1. Orchestrator Agent

**Purpose**: Coordinates multiple agents to fulfill complex user requests.

**Responsibilities**:
- Parse user intent
- Delegate to specialized agents
- Aggregate results
- Manage conversation context

**Implementation**: `apps/ai/agents/orchestrator.py`

### 2. Router Agent

**Purpose**: Determines which agent should handle a user query.

**Intents**:
- `RESEARCH`: Market research and analysis
- `RECOMMEND`: Generate trading recommendation
- `EXPLAIN`: Educational explanation
- `MONITOR`: Check alerts and positions
- `ANALYZE`: Long-form document analysis

**Implementation**: `apps/ai/agents/router.py`

### 3. Recommendation Agent

**Purpose**: Generates actionable trading recommendations.

**Process**:
1. Fetch user profile and portfolio
2. Retrieve market data and news (Exa.ai)
3. Run RAG pipeline for relevant research
4. Calculate risk metrics using MCP tools
5. Generate recommendation with LLM
6. Store in database

**Output**:
- Action (BUY/SELL/HOLD)
- Entry, stop, target prices
- Position size
- Thesis and risks
- Confidence score
- Source citations

**Implementation**: `apps/ai/agents/recommend.py`

### 4. Summarizer Agent

**Purpose**: Creates morning briefs and end-of-day reports.

**Morning Brief**:
- Market overview
- Key events today
- Portfolio status
- Top trading ideas
- Audio narration

**EOD Report**:
- Daily performance
- Position updates
- Market recap
- Tomorrow's outlook
- Audio narration

**Implementation**: `apps/ai/agents/summarize.py`

### 5. Long Context Analyst

**Purpose**: Analyzes lengthy financial documents.

**Supported Documents**:
- 10-K annual reports
- 10-Q quarterly reports
- Earnings transcripts
- Research reports

**Process**:
1. Fetch document
2. Process with Claude (200K context)
3. Extract key insights
4. Generate summary
5. Answer specific questions

**Implementation**: `apps/ai/agents/longctx.py`

### 6. Explainer Agent

**Purpose**: Provides educational explanations.

**Levels**:
- Beginner: Simple analogies, no jargon
- Intermediate: Some technical terms
- Expert: Full technical details

**Topics**:
- Trading concepts
- Risk management
- Technical indicators
- Market mechanics

**Implementation**: `apps/ai/agents/explainer.py`

### 7. Market Monitor Agent

**Purpose**: Monitors markets and triggers alerts.

**Alert Types**:
- Price alerts
- Volatility spikes
- News alerts
- Position alerts (stop hit, target reached)

**Implementation**: `apps/ai/agents/monitor.py`

## Agent Communication

Agents communicate through:
- Direct function calls
- Message passing via Redis
- Shared state in Supabase
- MCP tool invocations

## LLM Selection

- **Orchestration**: Claude Opus (reasoning)
- **Recommendations**: Claude Sonnet (fast + accurate)
- **Long Context**: Claude Opus (200K context)
- **Explanations**: GPT-4 Turbo (creative)
- **Fast Operations**: Groq Mixtral (speed)

