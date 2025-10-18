"""
Market Monitor Agent
Monitors markets, positions, and triggers alerts based on user-defined conditions
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# Flexible imports
try:
    from ..utils.tier_manager import tier_manager, Feature, UserTier
    from ..data.market_data import market_data_service
    from ..sentiment.aggregator import sentiment_aggregator
    from ..utils.clients import get_openai_client
except ImportError:
    from utils.tier_manager import tier_manager, Feature, UserTier
    from data.market_data import market_data_service
    from sentiment.aggregator import sentiment_aggregator
    from utils.clients import get_openai_client

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Types of alerts supported"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    VOLATILITY_SPIKE = "volatility_spike"  # PRO tier
    SENTIMENT_CHANGE = "sentiment_change"  # PRO tier
    NEWS_EVENT = "news_event"  # ENTERPRISE tier
    TECHNICAL_SIGNAL = "technical_signal"  # ENTERPRISE tier


class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MarketMonitorAgent:
    """
    Monitors market conditions and triggers alerts
    
    Features by tier:
    - FREE: Price threshold alerts only
    - PRO: Price + volatility + sentiment alerts
    - ENTERPRISE: Full suite (price, volatility, sentiment, news, technical signals)
    
    Alert throttling:
    - FREE: 3 alerts per day
    - PRO: 50 alerts per day
    - ENTERPRISE: Unlimited
    """
    
    def __init__(self):
        self.name = "monitor"
        self.client = get_openai_client()
        logger.info("Initialized Market Monitor Agent")
    
    async def check_alerts(self, user_id: str) -> List[Dict]:
        """
        Check if any alert conditions are met for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of triggered alerts
        """
        logger.info(f"Checking alerts for user {user_id}")
        
        # Check feature access
        access = await tier_manager.check_feature_access(
            Feature.MONITOR_ALERTS,
            user_id,
            check_usage=True
        )
        
        if not access["allowed"]:
            logger.warning(f"User {user_id} exceeded alert limit: {access['message']}")
            return []
        
        triggered_alerts = []
        
        try:
            # Get user's alert rules
            alert_rules = await self._get_user_alert_rules(user_id)
            
            if not alert_rules:
                logger.debug(f"No alert rules for user {user_id}")
                return []
            
            # Get user tier for feature filtering
            tier = access["tier"]
            allowed_types = tier_manager.get_feature_config(Feature.MONITOR_ALERTS, tier).get("types", ["price"])
            
            # Check each alert rule
            for rule in alert_rules:
                alert_type = rule.get("type")
                
                # Skip if alert type not allowed for tier
                if self._get_alert_category(alert_type) not in allowed_types:
                    continue
                
                # Check if condition is met
                is_triggered = await self._check_alert_condition(rule)
                
                if is_triggered:
                    alert = await self._create_alert(rule, user_id)
                    triggered_alerts.append(alert)
                    
                    # Increment usage
                    await tier_manager.increment_usage(Feature.MONITOR_ALERTS, user_id)
                    
                    # Check if we've hit the limit
                    remaining = access.get("remaining")
                    if remaining is not None and len(triggered_alerts) >= remaining:
                        logger.info(f"User {user_id} reached alert limit for today")
                        break
            
            logger.info(f"Triggered {len(triggered_alerts)} alerts for user {user_id}")
            return triggered_alerts
        
        except Exception as e:
            logger.error(f"Error checking alerts for user {user_id}: {e}", exc_info=True)
            return []
    
    async def monitor_positions(self, user_id: str) -> List[Dict]:
        """
        Monitor user's open positions for alerts
        
        Args:
            user_id: User ID
        
        Returns:
            List of position alerts
        """
        logger.info(f"Monitoring positions for user {user_id}")
        
        position_alerts = []
        
        try:
            # TODO: Get user positions from Supabase
            # positions = await supabase_client.get_open_positions(user_id)
            
            # For now, return empty list
            positions = []
            
            for position in positions:
                symbol = position['symbol']
                entry_price = position['entry_price']
                stop_loss = position.get('stop_loss')
                take_profit = position.get('take_profit')
                
                # Get current price
                current_price = await market_data_service.get_latest_price(symbol)
                
                if not current_price:
                    continue
                
                # Check stop loss hit
                if stop_loss and current_price <= stop_loss:
                    position_alerts.append({
                        'type': 'stop_loss_hit',
                        'symbol': symbol,
                        'position_id': position['id'],
                        'current_price': current_price,
                        'stop_loss': stop_loss,
                        'message': f"Stop loss hit for {symbol} at ${current_price:.2f}",
                        'priority': AlertPriority.HIGH
                    })
                
                # Check take profit hit
                if take_profit and current_price >= take_profit:
                    position_alerts.append({
                        'type': 'take_profit_hit',
                        'symbol': symbol,
                        'position_id': position['id'],
                        'current_price': current_price,
                        'take_profit': take_profit,
                        'message': f"Take profit hit for {symbol} at ${current_price:.2f}",
                        'priority': AlertPriority.MEDIUM
                    })
            
            return position_alerts
        
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}", exc_info=True)
            return []
    
    async def create_alert_rule(
        self,
        user_id: str,
        symbol: str,
        alert_type: AlertType,
        condition: Dict
    ) -> Dict:
        """
        Create a new alert rule for a user
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            alert_type: Type of alert
            condition: Alert condition (e.g., {"price": 100, "direction": "above"})
        
        Returns:
            Created alert rule
        """
        # Check feature access
        access = await tier_manager.check_feature_access(
            Feature.MONITOR_ALERTS,
            user_id,
            check_usage=False
        )
        
        tier = access["tier"]
        allowed_types = tier_manager.get_feature_config(Feature.MONITOR_ALERTS, tier).get("types", ["price"])
        
        # Check if alert type is allowed for tier
        alert_category = self._get_alert_category(alert_type)
        if alert_category not in allowed_types:
            raise ValueError(
                f"Alert type '{alert_type}' requires {self._required_tier_for_type(alert_type)} tier. "
                f"Current tier: {tier.value}"
            )
        
        # TODO: Store in Supabase alerts table
        alert_rule = {
            'id': f"alert_{datetime.now().timestamp()}",
            'user_id': user_id,
            'symbol': symbol,
            'type': alert_type,
            'condition': condition,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        logger.info(f"Created alert rule for {user_id}: {symbol} {alert_type}")
        return alert_rule
    
    async def _get_user_alert_rules(self, user_id: str) -> List[Dict]:
        """Get user's active alert rules from database"""
        # TODO: Query Supabase alerts table
        # return await supabase_client.get_active_alerts(user_id)
        
        # For now, return empty list
        return []
    
    async def _check_alert_condition(self, rule: Dict) -> bool:
        """
        Check if an alert condition is met
        
        Args:
            rule: Alert rule
        
        Returns:
            True if condition is met
        """
        alert_type = rule['type']
        symbol = rule['symbol']
        condition = rule['condition']
        
        try:
            # Price alerts (FREE tier)
            if alert_type == AlertType.PRICE_ABOVE:
                current_price = await market_data_service.get_latest_price(symbol)
                target_price = condition.get('price')
                return current_price and current_price >= target_price
            
            elif alert_type == AlertType.PRICE_BELOW:
                current_price = await market_data_service.get_latest_price(symbol)
                target_price = condition.get('price')
                return current_price and current_price <= target_price
            
            # TODO: PRO tier - Volatility alerts
            elif alert_type == AlertType.VOLATILITY_SPIKE:
                # Check if ATR has spiked above threshold
                pass
            
            # TODO: PRO tier - Sentiment change alerts
            elif alert_type == AlertType.SENTIMENT_CHANGE:
                # Check if sentiment has changed significantly
                pass
            
            # TODO: ENTERPRISE tier - News event alerts
            elif alert_type == AlertType.NEWS_EVENT:
                # Check for breaking news via Exa
                pass
            
            # TODO: ENTERPRISE tier - Technical signal alerts
            elif alert_type == AlertType.TECHNICAL_SIGNAL:
                # Check for technical indicators (RSI, MACD, etc.)
                pass
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking alert condition: {e}")
            return False
    
    async def _create_alert(self, rule: Dict, user_id: str) -> Dict:
        """
        Create an alert notification
        
        Args:
            rule: Alert rule that was triggered
            user_id: User ID
        
        Returns:
            Alert notification
        """
        symbol = rule['symbol']
        alert_type = rule['type']
        condition = rule['condition']
        
        # Get current price
        current_price = await market_data_service.get_latest_price(symbol)
        
        # Generate alert message
        if alert_type == AlertType.PRICE_ABOVE:
            message = f"{symbol} price ${current_price:.2f} is above your alert threshold ${condition['price']:.2f}"
            priority = AlertPriority.MEDIUM
        
        elif alert_type == AlertType.PRICE_BELOW:
            message = f"{symbol} price ${current_price:.2f} is below your alert threshold ${condition['price']:.2f}"
            priority = AlertPriority.MEDIUM
        
        else:
            message = f"Alert triggered for {symbol}: {alert_type}"
            priority = AlertPriority.LOW
        
        alert = {
            'id': f"alert_{datetime.now().timestamp()}",
            'user_id': user_id,
            'rule_id': rule.get('id'),
            'symbol': symbol,
            'type': alert_type,
            'message': message,
            'priority': priority,
            'current_price': current_price,
            'triggered_at': datetime.now().isoformat()
        }
        
        # TODO: Store in Supabase
        # await supabase_client.create_alert(alert)
        
        # TODO: Broadcast via WebSocket
        # await websocket_manager.broadcast_to_user(user_id, {
        #     'type': 'alert',
        #     'data': alert
        # })
        
        return alert
    
    def _get_alert_category(self, alert_type: AlertType) -> str:
        """Map alert type to feature category for tier checking"""
        if alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW]:
            return "price"
        elif alert_type in [AlertType.VOLATILITY_SPIKE, AlertType.SENTIMENT_CHANGE]:
            return "volatility" if alert_type == AlertType.VOLATILITY_SPIKE else "sentiment"
        elif alert_type == AlertType.NEWS_EVENT:
            return "news"
        elif alert_type == AlertType.TECHNICAL_SIGNAL:
            return "technical"
        return "price"
    
    def _required_tier_for_type(self, alert_type: AlertType) -> str:
        """Get required tier for an alert type"""
        if alert_type in [AlertType.VOLATILITY_SPIKE, AlertType.SENTIMENT_CHANGE]:
            return "Pro"
        elif alert_type in [AlertType.NEWS_EVENT, AlertType.TECHNICAL_SIGNAL]:
            return "Enterprise"
        return "Free"


# Global instance
market_monitor_agent = MarketMonitorAgent()
