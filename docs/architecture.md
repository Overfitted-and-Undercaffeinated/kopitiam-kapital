# Architecture Overview

## System Architecture

Kopitiam Capital is built as a monorepo with the following components:

### Frontend Layer
- **Web App** (Next.js 14): Dashboard, EOD reports, trading ideas
- **Mobile App** (React Native + Expo): Push notifications, mobile-first experience

### Backend Layer
- **AI Service** (FastAPI): Agent orchestration, LLM calls, RAG pipeline
- **Celery Workers**: Background jobs for scheduled briefs and reports
- **MCP Servers**: Tool execution for risk calculations, memory, and search

### Data Layer
- **Supabase/PostgreSQL**: Primary database with pgvector for embeddings
- **Redis**: Message broker for Celery
- **Mem0**: User memory and policy management
- **Exa.ai**: Web search and content retrieval

## Agent Architecture

### Orchestrator Agent
Coordinates all other agents and manages the overall workflow.

### Router Agent
Determines which specialized agent should handle a user query.

### Recommendation Agent
Generates actionable trading recommendations with risk analysis.

### Summarizer Agent
Creates morning briefs and end-of-day reports.

### Long Context Analyst
Analyzes lengthy documents like 10-Ks and annual reports.

### Explainer Agent
Provides educational explanations tailored to user's knowledge level.

### Market Monitor Agent
Monitors markets and triggers alerts based on rules.

## Data Flow

1. User interacts with web/mobile app
2. Request sent to FastAPI backend
3. Router agent determines intent
4. Orchestrator coordinates specialized agents
5. Agents use MCP tools for calculations and data retrieval
6. Results stored in Supabase
7. Response returned to user
8. Background jobs update briefs and reports

## Technology Stack

- **Languages**: Python, TypeScript
- **Frameworks**: FastAPI, Next.js, React Native
- **LLMs**: Anthropic Claude, OpenAI GPT, Groq
- **Database**: PostgreSQL (Supabase) with pgvector
- **Queue**: Redis + Celery
- **Voice**: ElevenLabs
- **Search**: Exa.ai
- **Memory**: Mem0
- **Orchestration**: Model Context Protocol (MCP)

