"""
Chat AI Agent - Participates in team discussions
Detects when to respond and generates contextual trading insights
"""
from typing import Tuple, Dict, List, Optional
import logging
import re

# Flexible imports
try:
    from ..utils.clients import get_openai_client
    from ..sentiment.aggregator import sentiment_aggregator
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.clients import get_openai_client
    from sentiment.aggregator import sentiment_aggregator
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

# Trigger patterns for AI responses
AI_TRIGGERS = [
    r'@ai',  # Direct mention
    r'\?',  # Questions
    r'what.*think',  # "what do you think"
    r'should.*buy',  # "should I buy"
    r'should.*sell',  # "should I sell"
    r'sentiment.*on',  # "sentiment on NVDA"
    r'analysis.*of',  # "analysis of TSLA"
    r'thoughts.*on',  # "thoughts on AAPL"
]

# Symbol detection pattern
SYMBOL_PATTERN = r'\b([A-Z]{1,5})\b'  # 1-5 uppercase letters

class ChatAIAgent:
    """
    AI agent for team chat discussions
    
    Features:
    - Detects when to respond (mentions, questions, symbols)
    - Generates contextual responses with GPT-4o
    - Includes sentiment analysis
    - Suggests trades when appropriate
    - Maintains chat history context
    """
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"  # Fast and cheap for chat
        
        # Store recent chat history per workspace
        self.chat_history: Dict[str, List[Dict]] = {}
        
        logger.info("Initialized Chat AI Agent")
    
    async def handle_message(
        self,
        message: str,
        workspace_id: str,
        user_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Handle incoming chat message
        
        Args:
            message: Chat message text
            workspace_id: Workspace ID
            user_id: User ID who sent message
        
        Returns:
            (should_respond, response_dict)
        """
        # Check if AI should respond
        if not self._should_respond(message):
            return False, None
        
        logger.info(f"AI responding to message in workspace {workspace_id}: '{message[:50]}...'")
        
        # Extract mentioned symbols
        symbols = self._extract_symbols(message)
        
        # Get sentiment for symbols
        sentiment_data = {}
        if symbols:
            for symbol in list(symbols)[:3]:  # Limit to 3 symbols
                try:
                    sentiment = await sentiment_aggregator.get_sentiment(symbol)
                    sentiment_data[symbol] = sentiment
                except Exception as e:
                    logger.error(f"Error getting sentiment for {symbol}: {e}")
        
        # Build context from history
        context = self._build_context(workspace_id, message, sentiment_data)
        
        # Generate AI response
        response_text = await self._generate_response(context, user_id)
        
        # Extract trade suggestions if any
        trade_suggestions = self._extract_trade_suggestions(
            response_text,
            symbols,
            sentiment_data
        )
        
        return True, {
            'message': response_text,
            'trade_suggestions': trade_suggestions,
            'symbols_analyzed': list(symbols)
        }
    
    def _should_respond(self, message: str) -> bool:
        """Determine if AI should respond to this message"""
        message_lower = message.lower()
        
        # Always respond to @ai mentions
        if '@ai' in message_lower:
            return True
        
        # Check if question about stock/trading
        if '?' in message:
            # Must have either trading keywords or symbols
            has_trading_keywords = any(kw in message_lower for kw in ['buy', 'sell', 'trade', 'stock', 'sentiment', 'analysis', 'thoughts', 'think'])
            symbols = self._extract_symbols(message)
            
            if has_trading_keywords or symbols:
                return True
        
        return False
    
    def _extract_symbols(self, message: str) -> set:
        """Extract stock symbols from message (uppercase 1-5 letters)"""
        # Find all uppercase words
        matches = re.findall(SYMBOL_PATTERN, message)
        
        # Filter out common words
        common_words = {'I', 'A', 'AI', 'CEO', 'CFO', 'IPO', 'API', 'USA', 'UK', 'EU', 'OK', 'YES', 'NO'}
        
        symbols = set()
        for match in matches:
            # Skip if common word or too short
            if match not in common_words and len(match) >= 2:
                symbols.add(match)
        
        return symbols
    
    def _build_context(
        self,
        workspace_id: str,
        current_message: str,
        sentiment_data: Dict
    ) -> str:
        """
        Build context string for LLM
        
        Includes:
        - Recent chat history
        - Current message
        - Sentiment data for mentioned symbols
        """
        context_parts = []
        
        # Chat history (last 10 messages)
        if workspace_id in self.chat_history:
            history = self.chat_history[workspace_id][-10:]
            context_parts.append("## Recent Chat History:")
            for msg in history:
                context_parts.append(f"- {msg['user']}: {msg['message']}")
        
        # Current message
        context_parts.append(f"\n## Current Message:")
        context_parts.append(current_message)
        
        # Sentiment data
        if sentiment_data:
            context_parts.append("\n## Sentiment Analysis:")
            for symbol, data in sentiment_data.items():
                score = data['overall_score']
                direction = data['direction']
                trending = "TRENDING" if data['trending'] else ""
                
                context_parts.append(
                    f"- {symbol}: {score:.2f} ({direction}) {trending}"
                )
                context_parts.append(f"  News Sentiment: {data['sentiment_breakdown']['news']:.2f}, "
                                    f"Confidence: {data['confidence']:.2f}")
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, context: str, user_id: str) -> str:
        """Generate AI response using GPT-4o-mini"""
        system_prompt = """You are a helpful AI trading assistant in a team workspace.

Your role:
- Provide insightful, concise trading analysis
- Reference sentiment data when available
- Suggest trades when appropriate (with clear reasoning)
- Be conversational and friendly
- Keep responses under 150 words
- Use bullet points for clarity

IMPORTANT:
- Always cite sentiment scores when making recommendations
- Include disclaimers for risky trades
- Don't be overly bullish or bearish without data"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            # Track cost
            if user_id:
                await cost_tracker.log_cost(
                    user_id=user_id,
                    service="openai-chat-ai",
                    tokens_input=response.usage.prompt_tokens,
                    tokens_output=response.usage.completion_tokens
                )
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Sorry, I encountered an error generating a response. Please try again."
    
    def _extract_trade_suggestions(
        self,
        response_text: str,
        symbols: set,
        sentiment_data: Dict
    ) -> List[Dict]:
        """Extract trade suggestions from AI response"""
        suggestions = []
        
        # Simple heuristic: if response mentions "buy" or "sell" with a symbol
        response_lower = response_text.lower()
        
        for symbol in symbols:
            if symbol in sentiment_data:
                sentiment = sentiment_data[symbol]
                
                # Buy signal
                if 'buy' in response_lower and symbol.lower() in response_lower:
                    suggestions.append({
                        'symbol': symbol,
                        'action': 'BUY',
                        'confidence': sentiment['confidence'],
                        'sentiment_score': sentiment['overall_score'],
                        'reasoning': f"Sentiment: {sentiment['direction']} ({sentiment['overall_score']:.2f})"
                    })
                
                # Sell signal
                elif 'sell' in response_lower and symbol.lower() in response_lower:
                    suggestions.append({
                        'symbol': symbol,
                        'action': 'SELL',
                        'confidence': sentiment['confidence'],
                        'sentiment_score': sentiment['overall_score'],
                        'reasoning': f"Sentiment: {sentiment['direction']} ({sentiment['overall_score']:.2f})"
                    })
        
        return suggestions
    
    def add_to_history(self, workspace_id: str, user: str, message: str):
        """Add message to chat history"""
        if workspace_id not in self.chat_history:
            self.chat_history[workspace_id] = []
        
        self.chat_history[workspace_id].append({
            'user': user,
            'message': message
        })
        
        # Keep only last 50 messages
        if len(self.chat_history[workspace_id]) > 50:
            self.chat_history[workspace_id] = self.chat_history[workspace_id][-50:]

# Global instance
chat_ai_agent = ChatAIAgent()

