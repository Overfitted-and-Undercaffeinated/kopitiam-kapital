"""
Orchestrator Agent - Routes requests between specialized agents
Coordinates multi-step workflows
"""
from typing import Dict, Optional
import logging

# Flexible imports
try:
    from ..agents.router import RouterAgent
    from ..agents.recommend import recommendation_agent
    from ..sentiment.aggregator import sentiment_aggregator
    from ..models.schemas import IntentType
except ImportError:
    from agents.router import RouterAgent
    from agents.recommend import recommendation_agent
    from sentiment.aggregator import sentiment_aggregator
    from models.schemas import IntentType

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Orchestrates workflows between specialized agents
    
    Flow:
    1. Router classifies intent
    2. Orchestrator routes to appropriate agent(s)
    3. Coordinates multi-agent workflows
    4. Returns unified response
    
    Supported Intents:
    - RECOMMEND → Recommendation Agent (sentiment + backtest + AI)
    - RESEARCH → Sentiment + RAG Pipeline
    - PORTFOLIO → Direct DB query
    - ALERTS → Monitor Agent
    - EXPLAIN → Explainer Agent
    """
    
    def __init__(self):
        self.router = RouterAgent()
        logger.info("Initialized Orchestrator Agent")
    
    async def handle_request(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Handle user request end-to-end
        
        Args:
            query: User's natural language query
            user_id: User ID
            context: Optional context (portfolio, preferences, etc.)
        
        Returns:
            Complete response with data from appropriate agents
        """
        logger.info(f"Orchestrating request: '{query[:100]}...'")
        
        try:
            # Step 1: Classify intent
            classification = await self.router.classify_intent(
                query=query,
                user_id=user_id
            )
            
            intent = classification.intent
            entities = classification.entities
            
            logger.info(f"Intent classified as: {intent}")
            
            # Step 2: Route to appropriate handler
            if intent == IntentType.RECOMMEND:
                return await self._handle_recommend(entities, user_id, context)
            
            elif intent == IntentType.RESEARCH:
                return await self._handle_research(entities, user_id, context)
            
            elif intent == IntentType.PORTFOLIO:
                return await self._handle_portfolio(user_id, context)
            
            elif intent == IntentType.ALERTS:
                return await self._handle_alerts(user_id, entities, context)
            
            elif intent == IntentType.EXPLAIN:
                return await self._handle_explain(entities, user_id, context)
            
            else:
                logger.warning(f"Unknown intent: {intent}")
                return {
                    'error': f'Unsupported intent: {intent}',
                    'suggestion': 'Try asking about a specific stock or trading strategy'
                }
        
        except Exception as e:
            logger.error(f"Orchestration error: {e}", exc_info=True)
            return {
                'error': 'Failed to process request',
                'detail': str(e)
            }
    
    async def _handle_recommend(
        self,
        entities: Dict,
        user_id: str,
        context: Optional[Dict]
    ) -> Dict:
        """
        Handle RECOMMEND intent
        
        Flow: Sentiment → Backtest → Recommendation
        """
        symbols = entities.get('symbols', [])
        
        if not symbols:
            return {
                'error': 'No symbol specified',
                'suggestion': 'Please specify a stock symbol (e.g., "Should I buy NVDA?")'
            }
        
        # Get first symbol
        symbol = symbols[0]
        
        logger.info(f"Generating recommendation for {symbol}")
        
        # Call recommendation agent (already does sentiment + backtest)
        recommendation = await recommendation_agent.generate_recommendation(
            symbol=symbol,
            user_id=user_id,
            user_context=context
        )
        
        return {
            'intent': 'RECOMMEND',
            'result': recommendation
        }
    
    async def _handle_research(
        self,
        entities: Dict,
        user_id: str,
        context: Optional[Dict]
    ) -> Dict:
        """
        Handle RESEARCH intent
        
        Flow: Sentiment → RAG Pipeline → Summary
        """
        symbols = entities.get('symbols', [])
        
        if not symbols:
            return {
                'error': 'No symbol specified',
                'suggestion': 'Please specify a stock symbol for research'
            }
        
        symbol = symbols[0]
        
        logger.info(f"Research request for {symbol}")
        
        # Get comprehensive sentiment
        sentiment = await sentiment_aggregator.get_sentiment(
            symbol=symbol,
            user_id=user_id
        )
        
        # TODO: Add RAG pipeline for deeper research
        # For now, return sentiment as research
        
        return {
            'intent': 'RESEARCH',
            'symbol': symbol,
            'result': {
                'sentiment': sentiment,
                'analysis': f"Comprehensive sentiment analysis for {symbol} based on {sentiment['volume']['news_articles']} news articles.",
                'recommendation': 'See /ai/recommend for trading recommendation'
            }
        }
    
    async def _handle_portfolio(
        self,
        user_id: str,
        context: Optional[Dict]
    ) -> Dict:
        """
        Handle PORTFOLIO intent
        
        Returns user's portfolio positions and P&L
        """
        logger.info(f"Portfolio request for user {user_id}")
        
        # TODO: Integrate with portfolio manager
        return {
            'intent': 'PORTFOLIO',
            'result': {
                'message': 'Portfolio feature coming soon',
                'positions': [],
                'total_pnl': 0.0
            }
        }
    
    async def _handle_alerts(
        self,
        user_id: str,
        entities: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """
        Handle ALERTS intent
        
        Manages price alerts, sentiment alerts, etc.
        """
        logger.info(f"Alerts request for user {user_id}")
        
        return {
            'intent': 'ALERTS',
            'result': {
                'message': 'Alerts feature coming soon',
                'active_alerts': []
            }
        }
    
    async def _handle_explain(
        self,
        entities: Dict,
        user_id: str,
        context: Optional[Dict]
    ) -> Dict:
        """
        Handle EXPLAIN intent
        
        Provides educational explanations
        """
        topic = entities.get('topic', 'general')
        
        logger.info(f"Explanation request: {topic}")
        
        return {
            'intent': 'EXPLAIN',
            'result': {
                'message': 'Explainer feature coming soon',
                'topic': topic
            }
        }

# Global instance
orchestrator_agent = OrchestratorAgent()
