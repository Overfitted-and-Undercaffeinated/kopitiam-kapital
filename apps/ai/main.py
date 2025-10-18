"""
Kopitiam Capital - AI Backend
FastAPI application for AI agents and intelligence
"""
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import time
from pathlib import Path
from typing import Dict
from contextlib import asynccontextmanager

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models and agents
from models.schemas import RouterRequest, RouterResponse, BriefRequest, BriefResponse
from agents.router import RouterAgent

# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler for resource management
    
    Handles:
    - Startup initialization
    - Graceful shutdown and cleanup
    """
    # Startup
    logger.info("🚀 Starting Kopitiam Capital AI Backend...")
    yield
    # Shutdown
    logger.info("🔄 Shutting down gracefully...")
    
    # Close asyncpraw Reddit client
    try:
        from sentiment.social_scraper import social_sentiment_analyzer
        await social_sentiment_analyzer.close()
    except Exception as e:
        logger.warning(f"Error closing social sentiment analyzer: {e}")
    
    # Close shared HTTP client
    try:
        from utils.http_client import http_client_manager
        await http_client_manager.close()
    except Exception as e:
        logger.warning(f"Error closing HTTP client: {e}")
    
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Kopitiam Capital AI",
    description="AI-powered trading intelligence API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
router_agent = RouterAgent()

# Store conversation histories per workspace
workspace_chat_histories: Dict[str, list] = {}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time*1000:.0f}ms "
        f"(status: {response.status_code})"
    )
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for API endpoints
    
    Applies limits based on endpoint and user tier
    Free tier: 5 req/day, Pro: unlimited, Enterprise: unlimited
    """
    # Skip rate limiting for health check and docs
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get user_id from query params or body
    user_id = request.query_params.get('user_id')
    
    if not user_id:
        # Try to get from JSON body for POST requests
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)
                    user_id = data.get('user_id')
                    # Re-populate body for downstream handlers
                    request._body = body
            except:
                pass
    
    # If still no user_id, allow request (guest mode)
    if not user_id:
        return await call_next(request)
    
    # Check rate limit
    from utils.rate_limiter import rate_limiter
    
    # Define limits per endpoint
    endpoint_limits = {
        '/sentiment': (10, 3600),  # 10 per hour for free tier
        '/ai/recommend': (5, 86400),  # 5 per day for free tier
        '/ai/orchestrate': (5, 86400),  # 5 per day
        '/backtest/run': (3, 86400),  # 3 per day
    }
    
    # Get limit for this endpoint
    for endpoint_prefix, (max_calls, window) in endpoint_limits.items():
        if request.url.path.startswith(endpoint_prefix):
            rate_limit_key = f"{endpoint_prefix}:{user_id}"
            
            # Check limit (only if rate limiting enabled)
            from utils.config import settings
            if settings.enable_rate_limiting:
                allowed = await rate_limiter.check_limit(
                    key=rate_limit_key,
                    max_calls=max_calls,
                    window_seconds=window
                )
                
                if not allowed:
                    remaining = await rate_limiter.get_remaining(rate_limit_key, max_calls, window)
                    
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"You've used your {max_calls} free requests. Upgrade to Pro for unlimited access.",
                            "limit": max_calls,
                            "remaining": remaining,
                            "window_seconds": window,
                            "upgrade_url": "https://kopitiamcapital.com/pricing"
                        }
                    )
            break
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kopitiam-capital-ai",
        "version": "1.0.0",
        "agents": {
            "router": "active"
        }
    }

@app.post("/ai/route", response_model=RouterResponse)
async def route_query(request: RouterRequest):
    """
    Route user query to appropriate agent using intent classification.
    
    **Latency target**: <1s (95th percentile)
    
    Args:
        request: RouterRequest with query and optional user_id
        
    Returns:
        RouterResponse with intent, entities, confidence, and urgency
    """
    try:
        logger.info(f"Routing query: '{request.query[:100]}...'")
        
        # Classify intent using Router Agent
        response = await router_agent.classify_intent(
            query=request.query,
            user_id=request.user_id
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Router error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to classify intent: {str(e)}"
        )

@app.post("/ai/orchestrate")
async def orchestrate_request(
    query: str,
    user_id: str,
    context: Dict = None
):
    """
    Orchestrate complete AI workflow
    
    **Latency target**: <5s (varies by intent)
    
    This is the "smart" endpoint that:
    1. Classifies intent
    2. Routes to appropriate agent(s)
    3. Coordinates multi-step workflows
    4. Returns complete result
    
    Example queries:
    - "Should I buy NVDA?" → RECOMMEND → Full recommendation
    - "What's the sentiment on TSLA?" → RESEARCH → Sentiment analysis
    - "Show my portfolio" → PORTFOLIO → Positions + P&L
    
    Args:
        query: Natural language query
        user_id: User ID
        context: Optional context dict
    
    Returns:
        {
            "intent": "RECOMMEND",
            "result": {...complete recommendation...}
        }
    """
    try:
        from agents.orchestrator import orchestrator_agent
        
        result = await orchestrator_agent.handle_request(
            query=query,
            user_id=user_id,
            context=context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Orchestration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to orchestrate request: {str(e)}"
        )

@app.post("/ai/recommend")
async def generate_recommendation(
    symbol: str,
    user_id: str,
    user_context: Dict = None
):
    """
    Generate trading recommendation with sentiment + backtest validation
    
    **Latency target**: <5s
    
    Integrates:
    - Sentiment analysis (all 3 sources)
    - Backtest validation (RSI oversold strategy)
    - Risk parameters (2.5% position, 5% stop, 10% target)
    - AI reasoning (GPT-4o-mini)
    
    Args:
        symbol: Stock ticker
        user_id: User ID
        user_context: Optional context (risk tolerance, portfolio)
    
    Returns:
        {
            "symbol": "NVDA",
            "action": "BUY",
            "entry_price": 485.50,
            "stop_loss": 461.23,
            "take_profit": 534.05,
            "position_size_percent": 0.025,
            "sentiment": {...},
            "backtest_validation": {...},
            "reasoning": "...",
            "disclaimer": "..."
        }
    """
    try:
        from agents.recommend import recommendation_agent
        
        logger.info(f"Generating recommendation for {symbol} (user: {user_id})")
        
        recommendation = await recommendation_agent.generate_recommendation(
            symbol=symbol,
            user_id=user_id,
            user_context=user_context
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendation: {str(e)}"
        )

@app.post("/ai/morning")
async def generate_morning_brief(user_id: str):
    """Generate morning brief"""
    # TODO: Implement morning brief agent
    return {"message": "Not implemented yet"}

@app.post("/ai/eod")
async def generate_eod_report(user_id: str):
    """Generate end-of-day report"""
    # TODO: Implement EOD report agent
    return {"message": "Not implemented yet"}

# ============================================================================
# MONITOR, LONG CONTEXT, AND EXPLAINER ENDPOINTS
# ============================================================================

@app.post("/alerts/check")
async def check_user_alerts(user_id: str):
    """
    Check and trigger user alerts
    
    Monitors positions and alert rules, triggers notifications for:
    - Price thresholds (FREE tier)
    - Volatility + sentiment changes (PRO tier)
    - News events + technical signals (ENTERPRISE tier)
    
    Alert limits:
    - FREE: 3 per day
    - PRO: 50 per day
    - ENTERPRISE: Unlimited
    """
    try:
        from agents.monitor import market_monitor_agent
        
        logger.info(f"Checking alerts for user {user_id}")
        
        # Check alerts
        alerts = await market_monitor_agent.check_alerts(user_id)
        
        # Check positions
        position_alerts = await market_monitor_agent.monitor_positions(user_id)
        
        return {
            "user_id": user_id,
            "alerts": alerts,
            "position_alerts": position_alerts,
            "total_triggered": len(alerts) + len(position_alerts)
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alerts/create")
async def create_alert_rule(
    user_id: str,
    symbol: str,
    alert_type: str,
    condition: Dict
):
    """
    Create a new alert rule
    
    Args:
        user_id: User ID
        symbol: Stock symbol
        alert_type: Type of alert (price_above, price_below, etc.)
        condition: Alert condition (e.g., {"price": 100})
    
    Returns:
        Created alert rule
    """
    try:
        from agents.monitor import market_monitor_agent, AlertType
        
        logger.info(f"Creating alert for {user_id}: {symbol} {alert_type}")
        
        # Create alert rule
        alert_rule = await market_monitor_agent.create_alert_rule(
            user_id=user_id,
            symbol=symbol,
            alert_type=AlertType(alert_type),
            condition=condition
        )
        
        return alert_rule
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/long-context")
async def analyze_long_document(
    text: str,
    document_type: str,
    user_id: str,
    ticker: str = None
):
    """
    Analyze long-form financial documents
    
    Uses Anthropic Claude with 200K context window.
    
    Analysis depth by tier:
    - FREE: Basic summary + metrics (1 per month)
    - PRO: Summary + risks + opportunities (10 per month)
    - ENTERPRISE: Full analysis + competitive positioning (unlimited)
    
    Args:
        text: Document text
        document_type: Type (e.g., "10-K", "annual_report", "earnings_call")
        user_id: User ID
        ticker: Optional stock ticker
    
    Returns:
        Analysis results
    """
    try:
        from agents.longctx import long_context_analyst
        
        logger.info(f"Analyzing {document_type} for user {user_id} (ticker: {ticker})")
        
        # Analyze document
        analysis = await long_context_analyst.analyze_document(
            text=text,
            document_type=document_type,
            user_id=user_id,
            ticker=ticker
        )
        
        return analysis
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/long-context/auto-fetch")
async def auto_fetch_and_analyze(
    ticker: str,
    user_id: str,
    include_earnings_call: bool = True
):
    """
    Auto-fetch and analyze financial documents via Exa.ai
    
    Automatically searches for and analyzes:
    - Latest 10-K (SEC filing)
    - Latest earnings call transcript (optional)
    
    Analysis depth by tier:
    - FREE: Basic summary (1 document/month)
    - PRO: Summary + risks + opportunities (10 documents/month)
    - ENTERPRISE: Full analysis (unlimited)
    
    Args:
        ticker: Stock ticker (e.g., "AAPL", "TSLA", "GOOGL")
        user_id: User ID
        include_earnings_call: Whether to include earnings call (default: True)
    
    Returns:
        Combined analysis of fetched documents
    """
    try:
        from agents.longctx import long_context_analyst
        
        logger.info(f"Auto-fetching documents for {ticker} (user: {user_id})")
        
        # Fetch and analyze documents
        analysis = await long_context_analyst.fetch_and_analyze(
            ticker=ticker,
            user_id=user_id,
            include_earnings_call=include_earnings_call
        )
        
        return analysis
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error in auto-fetch-and-analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain_concept(
    topic: str,
    user_id: str,
    level_override: str = None,
    category: str = None
):
    """
    Explain a trading concept
    
    Adapts explanation to user's knowledge level (from Mem0 profile).
    
    Topics by tier:
    - FREE: Trading concepts (RSI, MACD, support/resistance)
    - PRO: + Platform features (briefs, alerts, backtesting)
    - ENTERPRISE: + Advanced strategies (swing trading, risk management)
    
    Args:
        topic: Topic to explain
        user_id: User ID
        level_override: Override knowledge level (beginner/intermediate/advanced)
        category: Optional category hint
    
    Returns:
        Explanation with examples and next steps
    """
    try:
        from agents.explainer import explainer_agent
        
        logger.info(f"Explaining '{topic}' to user {user_id}")
        
        # Generate explanation
        explanation = await explainer_agent.explain(
            topic=topic,
            user_id=user_id,
            level_override=level_override,
            category=category
        )
        
        # Check for upgrade prompt
        if "error" in explanation:
            raise HTTPException(status_code=403, detail=explanation["error"])
        
        return explanation
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining topic: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BACKTESTING ENDPOINTS
# ============================================================================

@app.get("/backtest/templates")
async def get_strategy_templates():
    """
    Get list of pre-built strategy templates
    
    Returns:
        List of templates with metadata
    """
    try:
        from backtesting.templates import list_templates
        
        templates = list_templates()
        return {"templates": templates, "count": len(templates)}
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backtest/templates/{template_id}")
async def get_strategy_template(template_id: str):
    """Get a specific strategy template by ID"""
    try:
        from backtesting.templates import get_template
        
        template = get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest/run")
async def run_backtest(
    symbol: str,
    strategy_definition: Dict = None,
    strategy_template_id: str = None,
    start_date: str = None,
    end_date: str = None,
    initial_capital: float = 100000
):
    """
    Run a backtest with custom strategy or template
    
    **Latency target**: <5s for 1-year backtest
    
    Args:
        symbol: Stock ticker
        strategy_definition: Custom strategy JSON (optional)
        strategy_template_id: Use a pre-built template (optional)
        start_date: Start date (YYYY-MM-DD, optional)
        end_date: End date (YYYY-MM-DD, optional)
        initial_capital: Starting capital (default: $100,000)
    
    Returns:
        {
            "metrics": {...},
            "trades": [...],
            "equity_curve": [...],
            "summary": {...}
        }
    """
    try:
        from backtesting.engine import BacktestEngine
        from backtesting.builder import strategy_builder
        from backtesting.templates import get_template
        from data.market_data import market_data_service
        from datetime import datetime, timedelta
        
        logger.info(f"Running backtest for {symbol}")
        
        # Get strategy
        if strategy_template_id:
            strategy_def = get_template(strategy_template_id)
            if not strategy_def:
                raise HTTPException(status_code=404, detail=f"Template '{strategy_template_id}' not found")
        elif strategy_definition:
            strategy_def = strategy_definition
        else:
            raise HTTPException(status_code=400, detail="Must provide either strategy_definition or strategy_template_id")
        
        # Build strategy function
        strategy_func = strategy_builder.build_strategy(strategy_def)
        
        # Set date defaults
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Run backtest
        engine = BacktestEngine()
        results = await engine.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy_fn=strategy_func,
            initial_capital=initial_capital
        )
        
        logger.info(f"Backtest complete for {symbol}: {results['total_return_pct']:.2%} return, {results['num_trades']} trades")
        
        return {
            'symbol': symbol,
            'strategy': strategy_def.get('name', 'Custom'),
            'metrics': results,  # Return metrics directly
            'period': f"{start_date} to {end_date}",
            'initial_capital': initial_capital
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

# ============================================================================
# SENTIMENT ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str, user_id: str = None):
    """
    Get aggregated sentiment analysis for a symbol
    
    **Latency target**: <3s (95th percentile)
    
    Combines:
    - News sentiment (Exa.ai + LLM scoring) - 60% weight
    - Reddit sentiment (r/wallstreetbets, r/stocks) - 40% weight
    
    Note: StockTwits removed from analysis
    
    Returns:
        {
            "symbol": "NVDA",
            "overall_score": 0.82,
            "direction": "bullish",
            "sentiment_breakdown": {news, reddit, stocktwits},
            "volume": {article/mention counts},
            "trending": bool,
            "contrarian_signal": bool,
            "confidence": 0-1,
            "top_sources": [...]
        }
    """
    try:
        from sentiment.aggregator import sentiment_aggregator
        
        logger.info(f"Getting sentiment for {symbol}")
        
        result = await sentiment_aggregator.get_sentiment(
            symbol=symbol.upper(),
            lookback_hours=24,
            user_id=user_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Sentiment endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sentiment: {str(e)}"
        )

# ============================================================================
# BRIEF ENDPOINTS
# ============================================================================

@app.post("/briefs/morning", response_model=BriefResponse)
async def generate_morning_brief(request: BriefRequest):
    """
    Generate morning market brief with voice narration
    
    Features:
    - Watchlist sentiment analysis
    - Pre-market movers identification  
    - Personalized insights from Mem0
    - Voice narration with ElevenLabs
    - <2 minute read/listen
    
    Request body:
        {
            "watchlist": ["NVDA", "TSLA", "AAPL"],
            "market": "US",
            "user_id": "user123",
            "include_voice": true
        }
    
    Returns:
        {
            "type": "morning",
            "text": "Good morning! Market overview...",
            "audio_base64": "base64_encoded_mp3...",
            "symbols_analyzed": ["NVDA", "TSLA", "AAPL"],
            "sentiment_summary": {...},
            "generated_at": "2025-10-18T10:00:00Z"
        }
    """
    try:
        from agents.morning_brief import morning_brief_agent
        
        brief = await morning_brief_agent.generate_brief(
            watchlist=request.watchlist,
            market=request.market,
            user_id=request.user_id,
            include_voice=request.include_voice
        )
        
        return brief
    
    except Exception as e:
        logger.error(f"Error generating morning brief: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate morning brief: {str(e)}"
        )

@app.post("/briefs/eod", response_model=BriefResponse)
async def generate_eod_brief(request: BriefRequest):
    """
    Generate end-of-day market brief with voice narration
    
    Features:
    - Watchlist performance tracking (day's % change)
    - Sentiment analysis
    - AI research on why top movers moved
    - Tomorrow's outlook prediction
    - Voice narration with ElevenLabs
    - <2 minute read/listen
    
    Request body:
        {
            "watchlist": ["NVDA", "TSLA", "AAPL"],
            "market": "US",
            "user_id": "user123",
            "include_voice": true
        }
    
    Returns:
        {
            "type": "eod",
            "text": "Market close for US...",
            "audio_base64": "base64_encoded_mp3...",
            "symbols_analyzed": ["NVDA", "TSLA", "AAPL"],
            "performance_summary": {...},
            "generated_at": "2025-10-18T16:00:00Z"
        }
    """
    try:
        from agents.eod_brief import eod_brief_agent
        
        brief = await eod_brief_agent.generate_brief(
            watchlist=request.watchlist,
            market=request.market,
            user_id=request.user_id,
            include_voice=request.include_voice
        )
        
        return brief
    
    except Exception as e:
        logger.error(f"Error generating EOD brief: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate EOD brief: {str(e)}"
        )

# ============================================================================
# WEBSOCKET & COLLABORATION ENDPOINTS
# ============================================================================

@app.websocket("/ws/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    workspace_id: str,
    user_id: str,
    user_email: str
):
    """
    WebSocket endpoint for real-time workspace collaboration
    
    Features:
    - Real-time chat messages
    - AI participation
    - Live P&L updates
    - Shared watchlist updates
    - Alert broadcasting
    
    Args:
        workspace_id: Team workspace ID
        user_id: User ID
        user_email: User email
    """
    from streaming.websocket_server import connection_manager
    from collaboration.chat import chat_ai_agent
    
    # Connect to workspace
    await connection_manager.connect(
        websocket=websocket,
        workspace_id=workspace_id,
        user_id=user_id,
        user_email=user_email
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                # User sent a chat message
                message = data.get('message', '')
                
                # Initialize workspace history if needed
                if workspace_id not in workspace_chat_histories:
                    workspace_chat_histories[workspace_id] = []
                
                # Add user message to history
                workspace_chat_histories[workspace_id].append({
                    'user': user_email,
                    'message': message,
                    'timestamp': time.time()
                })
                
                # Keep last 50 messages
                if len(workspace_chat_histories[workspace_id]) > 50:
                    workspace_chat_histories[workspace_id] = workspace_chat_histories[workspace_id][-50:]
                
                # Broadcast to workspace
                await connection_manager.broadcast_to_workspace(
                    workspace_id=workspace_id,
                    message={
                        'type': 'chat_message',
                        'user_id': user_id,
                        'user_email': user_email,
                        'message': message
                    }
                )
                
                # Add history to AI agent
                chat_ai_agent.chat_history[workspace_id] = workspace_chat_histories[workspace_id]
                
                # Check if AI should respond
                should_respond, ai_response = await chat_ai_agent.handle_message(
                    message=message,
                    workspace_id=workspace_id,
                    user_id=user_id
                )
                
                if should_respond:
                    # Add AI response to history
                    workspace_chat_histories[workspace_id].append({
                        'user': 'AI Assistant',
                        'message': ai_response['message'],
                        'timestamp': time.time()
                    })
                    
                    # AI responds
                    await connection_manager.broadcast_to_workspace(
                        workspace_id=workspace_id,
                        message={
                            'type': 'ai_response',
                            'message': ai_response['message'],
                            'trade_suggestions': ai_response.get('trade_suggestions', [])
                        }
                    )
            
            elif message_type == 'watchlist_add':
                # Add symbol to shared watchlist
                symbol = data.get('symbol')
                
                await connection_manager.broadcast_to_workspace(
                    workspace_id=workspace_id,
                    message={
                        'type': 'watchlist_update',
                        'action': 'add',
                        'symbol': symbol,
                        'added_by': user_email
                    }
                )
            
            elif message_type == 'watchlist_remove':
                # Remove symbol from shared watchlist
                symbol = data.get('symbol')
                
                await connection_manager.broadcast_to_workspace(
                    workspace_id=workspace_id,
                    message={
                        'type': 'watchlist_update',
                        'action': 'remove',
                        'symbol': symbol,
                        'removed_by': user_email
                    }
                )
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        
        # Notify others
        await connection_manager.broadcast_to_workspace(
            workspace_id=workspace_id,
            message={
                'type': 'user_left',
                'user_id': user_id,
                'user_email': user_email
            }
        )
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        connection_manager.disconnect(websocket)

@app.get("/workspace/{workspace_id}/members")
async def get_workspace_members(workspace_id: str):
    """Get list of currently connected members in a workspace"""
    try:
        from streaming.websocket_server import connection_manager
        
        members = connection_manager.get_workspace_members(workspace_id)
        
        return {
            'workspace_id': workspace_id,
            'members': members,
            'count': len(members)
        }
    
    except Exception as e:
        logger.error(f"Error getting workspace members: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PORTFOLIO MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/portfolio/execute-recommendation")
async def execute_recommendation(
    user_id: str,
    recommendation_id: str,
    fill_price: float,
    quantity: int,
    notes: str = None
):
    """
    Manually record that user executed a recommendation
    
    This is MVP manual entry. Post-MVP will auto-sync from broker.
    """
    try:
        from portfolio.position_manager import position_manager
        
        position = await position_manager.create_position_from_recommendation(
            user_id=user_id,
            recommendation_id=recommendation_id,
            fill_price=fill_price,
            quantity=quantity,
            notes=notes
        )
        return {"status": "success", "position": position}
    
    except Exception as e:
        logger.error(f"Error executing recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/close-position")
async def close_position_endpoint(
    position_id: str,
    close_price: float,
    notes: str = None
):
    """Close a position and calculate P&L"""
    try:
        from portfolio.position_manager import position_manager
        
        position = await position_manager.close_position(
            position_id=position_id,
            close_price=close_price,
            notes=notes
        )
        return {"status": "success", "position": position}
    
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/utils/market-hours/{exchange}")
async def get_market_hours(exchange: str):
    """Get market hours information for an exchange"""
    try:
        from utils.market_hours import market_hours
        
        info = market_hours.get_market_info(exchange.upper())
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Exchange {exchange} not found")
        
        return info
    
    except Exception as e:
        logger.error(f"Error getting market hours: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/utils/active-markets")
async def get_active_markets():
    """Get list of currently open markets"""
    try:
        from utils.market_hours import market_hours
        
        active = market_hours.get_active_markets()
        
        return {
            "active_markets": active,
            "count": len(active)
        }
    
    except Exception as e:
        logger.error(f"Error getting active markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

