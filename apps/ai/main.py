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
from models.schemas import RouterRequest, RouterResponse
from agents.router import RouterAgent

# Create FastAPI app
app = FastAPI(
    title="Kopitiam Capital AI",
    description="AI-powered trading intelligence API",
    version="1.0.0"
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

@app.post("/ai/longctx")
async def analyze_filing(ticker: str, filing_type: str):
    """Analyze long-form financial documents"""
    # TODO: Implement long-context analyst
    return {"message": "Not implemented yet"}

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
    - News sentiment (Exa.ai + LLM scoring) - 40% weight
    - Reddit sentiment (r/wallstreetbets, r/stocks) - 30% weight
    - StockTwits sentiment - 30% weight
    
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
                
                # Check if AI should respond
                should_respond, ai_response = await chat_ai_agent.handle_message(
                    message=message,
                    workspace_id=workspace_id,
                    user_id=user_id
                )
                
                if should_respond:
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

