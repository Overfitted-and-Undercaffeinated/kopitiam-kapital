"""Router Agent - Routes queries to appropriate agents using Groq"""
import json
import logging
import time
from typing import Optional
from openai import OpenAI

# Try relative imports first (when used as package), fall back to absolute
try:
    from ..models.schemas import RouterResponse, IntentType, UrgencyLevel
    from ..utils.clients import get_groq_client
except ImportError:
    from models.schemas import RouterResponse, IntentType, UrgencyLevel
    from utils.clients import get_groq_client

logger = logging.getLogger(__name__)

# System prompt for intent classification
ROUTER_SYSTEM_PROMPT = """You are an expert intent classifier for a trading intelligence platform.

Classify user queries into ONE of these intents:
- RESEARCH: Market research, news, analysis, "what's happening with..."
- RECOMMEND: Generate trading ideas, "should I buy...", "give me a trade"
- PORTFOLIO: View positions, P&L, performance, "show my portfolio"
- ALERTS: Check alerts, set monitoring, "alert me when..."
- EXPLAIN: Educational questions, "what is...", "how does... work"
- SETTINGS: User preferences, configuration

Extract entities:
- Stock tickers (e.g., AAPL, TSLA, GOOGL)
- Sectors (e.g., tech, healthcare, energy)
- Other relevant entities

Determine urgency:
- HIGH: Time-sensitive, breaking news, "urgent", "now"
- MEDIUM: Standard trading questions
- LOW: General research, learning

Examples:
1. "Should I buy AAPL?" → RECOMMEND, entities: ["AAPL"], urgency: MEDIUM
2. "What's happening with tech stocks?" → RESEARCH, entities: ["TECH"], urgency: MEDIUM
3. "Show my portfolio" → PORTFOLIO, entities: [], urgency: LOW
4. "Alert me when TSLA hits $300" → ALERTS, entities: ["TSLA"], urgency: MEDIUM
5. "What is RSI?" → EXPLAIN, entities: ["RSI"], urgency: LOW
6. "Change my risk profile" → SETTINGS, entities: [], urgency: LOW

Return ONLY valid JSON matching this schema:
{
  "intent": "RESEARCH|RECOMMEND|PORTFOLIO|ALERTS|EXPLAIN|SETTINGS",
  "entities": ["TICKER1", "TICKER2"],
  "confidence": 0.85,
  "urgency": "low|medium|high",
  "reasoning": "brief explanation"
}"""

class RouterAgent:
    """Routes user queries to the appropriate specialized agent using Groq"""
    
    def __init__(self, client: Optional[OpenAI] = None):
        self.name = "router"
        self.client = client or get_groq_client()
        # Using Llama 3.3 70B - fast and accurate for classification
        # Alternative: "llama-3.1-8b-instant" for even faster responses
        self.model = "llama-3.3-70b-versatile"
        logger.info(f"Initialized RouterAgent with model: {self.model}")
    
    async def classify_intent(
        self,
        query: str,
        user_id: Optional[str] = None
    ) -> RouterResponse:
        """
        Classify user query intent using Groq.
        
        Args:
            query: User query text
            user_id: Optional user ID for context
            
        Returns:
            RouterResponse with intent, entities, confidence, urgency
            
        Raises:
            ValueError: If query is empty or invalid
            Exception: If Groq API fails after retries
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        query = query.strip()
        logger.info(f"Classifying intent for query: '{query[:100]}...'")
        
        start_time = time.time()
        
        try:
            # Call Groq API
            response = await self._call_groq(query)
            
            # Parse and validate response
            router_response = self._parse_response(response, query)
            
            # Log latency
            latency = time.time() - start_time
            logger.info(
                f"Intent classified as {router_response.intent.value} "
                f"(confidence: {router_response.confidence:.2f}, "
                f"latency: {latency*1000:.0f}ms)"
            )
            
            if latency > 1.0:
                logger.warning(f"Router latency exceeded 1s: {latency:.2f}s")
            
            return router_response
            
        except Exception as e:
            logger.error(f"Router classification failed: {e}")
            # Fallback to keyword matching
            return self._fallback_classification(query)
    
    async def _call_groq(self, query: str, retry: bool = True) -> str:
        """Call Groq API with retry logic"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Groq")
            
            return content
            
        except Exception as e:
            if retry:
                logger.warning(f"Groq call failed, retrying: {e}")
                return await self._call_groq(query, retry=False)
            else:
                raise
    
    def _parse_response(self, response_text: str, original_query: str) -> RouterResponse:
        """Parse and validate Groq JSON response"""
        try:
            data = json.loads(response_text)
            
            # Map string intent to enum
            intent_str = data.get("intent", "RESEARCH").upper()
            try:
                intent = IntentType[intent_str]
            except KeyError:
                logger.warning(f"Unknown intent '{intent_str}', defaulting to RESEARCH")
                intent = IntentType.RESEARCH
            
            # Map urgency
            urgency_str = data.get("urgency", "medium").lower()
            try:
                urgency = UrgencyLevel[urgency_str.upper()]
            except KeyError:
                urgency = UrgencyLevel.MEDIUM
            
            # Create RouterResponse (Pydantic will validate)
            return RouterResponse(
                intent=intent,
                entities=data.get("entities", []),
                confidence=min(max(data.get("confidence", 0.8), 0.0), 1.0),
                urgency=urgency,
                reasoning=data.get("reasoning")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            return self._fallback_classification(original_query)
        except Exception as e:
            logger.error(f"Failed to validate response: {e}")
            return self._fallback_classification(original_query)
    
    def _fallback_classification(self, query: str) -> RouterResponse:
        """Fallback keyword-based classification when Groq fails"""
        logger.info("Using fallback keyword classification")
        
        query_lower = query.lower()
        
        # Simple keyword matching
        if any(word in query_lower for word in ["buy", "sell", "trade", "should i", "recommend"]):
            intent = IntentType.RECOMMEND
        elif any(word in query_lower for word in ["portfolio", "positions", "holdings", "p&l", "pnl"]):
            intent = IntentType.PORTFOLIO
        elif any(word in query_lower for word in ["alert", "notify", "watch", "monitor"]):
            intent = IntentType.ALERTS
        elif any(word in query_lower for word in ["what is", "how does", "explain", "teach", "learn"]):
            intent = IntentType.EXPLAIN
        elif any(word in query_lower for word in ["settings", "preferences", "config", "change"]):
            intent = IntentType.SETTINGS
        else:
            intent = IntentType.RESEARCH
        
        # Extract potential tickers (simple uppercase words 1-5 chars)
        import re
        potential_tickers = re.findall(r'\b[A-Z]{1,5}\b', query)
        
        return RouterResponse(
            intent=intent,
            entities=potential_tickers[:5],  # Limit to 5
            confidence=0.6,  # Lower confidence for fallback
            urgency=UrgencyLevel.MEDIUM,
            reasoning="Fallback keyword classification"
        )
    
    # Backward compatibility alias
    async def route(self, query: str) -> dict:
        """Legacy method - prefer classify_intent()"""
        response = await self.classify_intent(query)
        return {
            "intent": response.intent.value,
            "entities": response.entities,
            "confidence": response.confidence,
            "urgency": response.urgency.value
        }

