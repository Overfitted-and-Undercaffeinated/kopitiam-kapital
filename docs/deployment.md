# Deployment Guide

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Supabase CLI

### Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd kopitiam-capital
   ```

2. **Install dependencies**
   ```bash
   # Root dependencies
   npm install
   
   # AI backend
   cd apps/ai
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Web app
   cd ../web
   npm install
   
   # Mobile app
   cd ../mobile
   npm install
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Start services**
   ```bash
   # Start infrastructure
   cd infra
   docker-compose up -d
   
   # Start AI backend
   cd ../apps/ai
   uvicorn main:app --reload
   
   # Start web app
   cd ../web
   npm run dev
   ```

## Production Deployment

### Docker Deployment

Build and run with Docker Compose:

```bash
cd infra
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables

Required environment variables for production:

```bash
# LLM APIs
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=

# Services
EXA_API_KEY=
MEM0_API_KEY=
ELEVENLABS_API_KEY=

# Database
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# Infrastructure
REDIS_URL=
JWT_SECRET=

# Environment
NODE_ENV=production
PYTHON_ENV=production
```

### Database Migration

```bash
cd supabase
supabase db push
```

### Monitoring

- Application logs: Check Docker logs
- Database: Supabase dashboard
- Queue: Redis Commander
- Celery: Flower monitoring

### Scaling

- Horizontal: Add more Celery workers
- Vertical: Increase container resources
- Database: Use Supabase connection pooling

## CI/CD

### GitHub Actions (Example)

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and deploy
        run: |
          docker-compose build
          docker-compose up -d
```

## Security

- Use environment variables for secrets
- Enable HTTPS in production
- Configure CORS properly
- Use Supabase RLS policies
- Implement rate limiting
- Monitor for anomalies

