# Kopitiam Capital

AI-powered pocket analyst for retail traders in Singapore.

## Architecture

- **AI Backend**: FastAPI + Celery (Python)
- **Web App**: Next.js 14 + TypeScript + Tailwind
- **Mobile App**: React Native + Expo
- **Database**: Supabase (Postgres + pgvector)
- **Models**: Anthropic, OpenAI, Groq
- **Retrieval**: Exa.ai
- **Memory**: Mem0
- **Orchestration**: Smithery MCP

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Supabase CLI

### Quick Start

1. **Install dependencies**
   ```bash
   # Python backend
   cd apps/ai
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Web frontend
   cd apps/web
   npm install

   # Mobile app
   cd apps/mobile
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services**
   ```bash
   # Start all services
   docker-compose up -d

   # Start AI backend
   cd apps/ai
   uvicorn main:app --reload

   # Start web app
   cd apps/web
   npm run dev

   # Start mobile app
   cd apps/mobile
   npm start
   ```

## Team Responsibilities

### AI Engineer
- `/apps/ai` - Agent logic, RAG, LLM integration
- `/mcp` - MCP server development
- Celery tasks & scheduling

### Frontend + Database Engineer
- `/apps/web` - Next.js UI components
- `/apps/mobile` - React Native app
- `/supabase` - Database schema & migrations

## Documentation

See `/docs` for detailed documentation.

