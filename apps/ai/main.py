"""
Kopitiam Capital - AI Backend
FastAPI application for AI agents and intelligence
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import time
from pathlib import Path

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

@app.post("/ai/recommend")
async def generate_recommendation(user_id: str, symbol: str = None):
    """Generate trading recommendation"""
    # TODO: Implement recommendation agent
    return {"message": "Not implemented yet"}

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

