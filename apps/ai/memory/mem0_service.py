"""
Mem0 service for user memory and policy management
✅ REAL IMPLEMENTATION using Mem0 cloud API
"""
import logging
from typing import Dict, Optional, List
import json

# Flexible imports
try:
    from ..utils.config import settings
except ImportError:
    from utils.config import settings

logger = logging.getLogger(__name__)

# Default policy for new users
DEFAULT_POLICY = {
    'default_position_size_pct': 0.025,  # 2.5% of capital
    'default_stop_loss_pct': 0.05,  # 5% stop loss
    'default_take_profit_pct': 0.10,  # 10% take profit
    'max_position_size_pct': 0.10,  # Max 10% in single position
    'risk_tolerance': 'moderate',  # conservative, moderate, aggressive
    'preferred_holding_period': 'swing',  # day, swing, long
    'enable_auto_stop': True,
    'enable_trailing_stop': False,
    'preferred_sectors': [],
    'avoided_sectors': []
}

class Mem0Service:
    """
    Real Mem0 integration for user memory and personalization
    
    Features:
    - User trading preferences and risk tolerance
    - Historical trade outcomes
    - Learning from past decisions
    - Personalized recommendation parameters
    """
    
    def __init__(self):
        self.client = None
        self.enabled = settings.use_mem0
        
        if self.enabled:
            try:
                from mem0 import MemoryClient
                self.client = MemoryClient(api_key=settings.mem0_api_key)
                logger.info("✅ Initialized Mem0 client (cloud mode)")
            except ImportError:
                logger.warning("mem0ai not installed. Run: pip install mem0ai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Mem0: {e}")
                self.enabled = False
        
        if not self.enabled:
            logger.warning("⚠️ Mem0 disabled - using default policies")
    
    async def get_policy(self, user_id: str) -> Dict:
        """
        Get user's trading policy from memory
        
        Searches for:
        - Risk tolerance settings
        - Position sizing preferences
        - Stop loss preferences
        - Sector preferences
        
        Args:
            user_id: User identifier
        
        Returns:
            Policy dict with user preferences
        """
        if not self.enabled:
            logger.debug(f"Mem0 disabled - returning default policy for {user_id}")
            return DEFAULT_POLICY.copy()
        
        try:
            # Search user's memories for policy-related information
            policy_query = "trading policy preferences risk tolerance position sizing"
            
            # Mem0 v2 API requires filters parameter
            memories = self.client.search(
                query=policy_query,
                user_id=user_id,
                limit=10,
                filters={"user_id": user_id}  # Required by Mem0 API v2
            )
            
            # Parse memories to build policy
            policy = DEFAULT_POLICY.copy()
            
            if memories:
                for memory in memories:
                    # Mem0 returns different formats - handle both
                    if isinstance(memory, str):
                        content = memory.lower()
                    elif isinstance(memory, dict):
                        content = memory.get('memory', '').lower()
                    else:
                        continue
                    
                    # Extract risk tolerance
                    if 'conservative' in content or 'safe' in content or 'low risk' in content:
                        policy['risk_tolerance'] = 'conservative'
                        policy['default_position_size_pct'] = 0.015  # 1.5%
                        policy['default_stop_loss_pct'] = 0.03  # 3%
                    elif 'aggressive' in content or 'high risk' in content:
                        policy['risk_tolerance'] = 'aggressive'
                        policy['default_position_size_pct'] = 0.05  # 5%
                        policy['default_stop_loss_pct'] = 0.08  # 8%
                    
                    # Extract position size preference
                    if 'small position' in content:
                        policy['default_position_size_pct'] = 0.01
                    elif 'large position' in content:
                        policy['default_position_size_pct'] = 0.04
                    
                    # Extract holding period preference
                    if 'day trad' in content:
                        policy['preferred_holding_period'] = 'day'
                        policy['default_take_profit_pct'] = 0.03  # Tighter targets
                    elif 'long term' in content or 'buy and hold' in content:
                        policy['preferred_holding_period'] = 'long'
                        policy['default_take_profit_pct'] = 0.20  # Wider targets
                    
                    # Extract sector preferences
                    if 'like tech' in content or 'prefer tech' in content:
                        if 'tech' not in policy['preferred_sectors']:
                            policy['preferred_sectors'].append('tech')
                    if 'avoid' in content and 'financials' in content:
                        if 'financials' not in policy['avoided_sectors']:
                            policy['avoided_sectors'].append('financials')
                
                logger.info(f"Retrieved Mem0 policy for {user_id}: {policy['risk_tolerance']} trader")
            else:
                logger.info(f"No Mem0 memories found for {user_id}, using defaults")
            
            return policy
            
        except Exception as e:
            logger.error(f"Mem0 policy retrieval failed: {e}")
            return DEFAULT_POLICY.copy()
    
    async def get_context(self, user_id: str, symbol: str) -> Dict:
        """
        Get user context for a specific symbol
        
        Returns:
        - Past trades on this symbol
        - User's notes on this symbol
        - Watchlist status
        
        Args:
            user_id: User identifier
            symbol: Stock symbol
        
        Returns:
            Context dict with user's history for this symbol
        """
        if not self.enabled:
            return {'past_trades': [], 'notes': [], 'has_history': False}
        
        try:
            # Search memories related to this symbol
            query = f"trades notes thoughts on {symbol}"
            
            memories = self.client.search(
                query=query,
                user_id=user_id,
                limit=5,
                filters={"user_id": user_id}  # Required by Mem0 API v2
            )
            
            past_trades = []
            notes = []
            
            for memory in memories:
                # Mem0 returns different formats - handle both
                if isinstance(memory, str):
                    content = memory
                elif isinstance(memory, dict):
                    content = memory.get('memory', '')
                else:
                    continue
                
                # Check if it's a trade record
                if 'bought' in content.lower() or 'sold' in content.lower():
                    past_trades.append(content)
                else:
                    notes.append(content)
            
            return {
                'past_trades': past_trades,
                'notes': notes,
                'has_history': len(memories) > 0
            }
            
        except Exception as e:
            logger.error(f"Mem0 context retrieval failed: {e}")
            return {'past_trades': [], 'notes': [], 'has_history': False}
    
    async def record_outcome(self, user_id: str, trade: Dict) -> None:
        """
        Record trade outcome for learning
        
        Stores:
        - Trade details (symbol, entry, exit, P&L)
        - Outcome (win/loss)
        - Strategy used
        - Sentiment at entry
        
        Args:
            user_id: User identifier
            trade: Trade dict with outcome
        """
        if not self.enabled:
            logger.debug(f"Mem0 disabled - skipping outcome recording for {user_id}")
            return
        
        try:
            # Format trade as memory
            symbol = trade.get('symbol')
            action = trade.get('action')
            entry = trade.get('entry_price')
            exit_price = trade.get('exit_price')
            pnl_pct = trade.get('pnl_pct', 0)
            outcome = 'win' if pnl_pct > 0 else 'loss'
            
            memory_text = (
                f"Traded {symbol}: {action} at ${entry:.2f}, "
                f"exited at ${exit_price:.2f}. "
                f"P&L: {pnl_pct:.1%} ({outcome}). "
                f"Strategy: {trade.get('strategy', 'unknown')}. "
                f"Sentiment at entry: {trade.get('sentiment_score', 'N/A')}."
            )
            
            # Add to Mem0
            messages = [
                {"role": "assistant", "content": memory_text}
            ]
            
            self.client.add(messages, user_id=user_id)
            
            logger.info(f"✅ Recorded trade outcome in Mem0: {user_id} {symbol} {outcome}")
            
        except Exception as e:
            logger.error(f"Failed to record trade outcome in Mem0: {e}")
    
    async def search_memories(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """
        Search user's trading memories
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Max results
        
        Returns:
            List of matching memories
        """
        if not self.enabled:
            return []
        
        try:
            memories = self.client.search(
                query=query,
                user_id=user_id,
                limit=limit,
                filters={"user_id": user_id}  # Required by Mem0 API v2
            )
            
            # Handle both string and dict responses from Mem0
            return [
                {
                    'content': m if isinstance(m, str) else m.get('memory', ''),
                    'relevance': m.get('score', 0) if isinstance(m, dict) else 1.0,
                    'timestamp': m.get('created_at') if isinstance(m, dict) else None
                }
                for m in memories
            ]
            
        except Exception as e:
            logger.error(f"Mem0 search failed: {e}")
            return []
    
    async def add_user_preference(
        self,
        user_id: str,
        preference_type: str,
        value: str
    ) -> None:
        """
        Store a user preference
        
        Examples:
        - "I prefer conservative risk"
        - "I like tech stocks"
        - "I'm a day trader"
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            value: Preference value
        """
        if not self.enabled:
            logger.debug(f"Mem0 disabled - skipping preference storage for {user_id}")
            return
        
        try:
            memory_text = f"User preference - {preference_type}: {value}"
            
            messages = [
                {"role": "user", "content": memory_text}
            ]
            
            self.client.add(messages, user_id=user_id)
            
            logger.info(f"✅ Added Mem0 preference for {user_id}: {preference_type} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to add Mem0 preference: {e}")

# Global instance
mem0_service = Mem0Service()
