"""
Cost tracking for API usage
Monitors spending per user and service
"""
from datetime import datetime
from typing import Optional
import logging
from .config import settings, COST_PRICING

logger = logging.getLogger(__name__)

class CostTracker:
    """Track and monitor API costs"""
    
    def __init__(self):
        self.enabled = settings.enable_cost_tracking
    
    async def log_cost(
        self,
        user_id: str,
        service: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        units: int = 0,  # For non-token services (searches, characters)
        metadata: Optional[dict] = None
    ) -> float:
        """
        Log API cost to database
        
        Args:
            user_id: User ID
            service: Service name (e.g., 'gpt-4o', 'exa-search')
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            units: Other units (searches, characters)
            metadata: Additional context
        
        Returns:
            Cost in USD
        """
        if not self.enabled:
            return 0.0
        
        try:
            # Calculate cost
            cost = self._calculate_cost(service, tokens_input, tokens_output, units)
            
            # TODO: Store in database once supabase_client is implemented
            # For now, just log
            logger.info(
                f"Cost logged: user={user_id}, service={service}, "
                f"cost=${cost:.4f}, tokens_in={tokens_input}, tokens_out={tokens_output}"
            )
            
            # Check if user exceeded alert threshold
            await self._check_threshold(user_id, cost)
            
            return cost
        
        except Exception as e:
            logger.error(f"Error logging cost: {e}")
            return 0.0
    
    def _calculate_cost(
        self,
        service: str,
        tokens_input: int,
        tokens_output: int,
        units: int
    ) -> float:
        """Calculate cost based on service pricing"""
        
        # Token-based services
        if service in ['gpt-4o', 'gpt-4o-mini', 'claude-sonnet-4.5']:
            input_cost = (tokens_input / 1000) * COST_PRICING.get(service, 0)
            output_key = f"{service}-output"
            output_cost = (tokens_output / 1000) * COST_PRICING.get(output_key, 0)
            return input_cost + output_cost
        
        # Groq (free)
        if 'groq' in service.lower():
            return 0.0
        
        # Unit-based services
        if service == 'exa-search':
            return units * COST_PRICING.get('exa-search', 0)
        
        if service == 'elevenlabs-tts':
            return units * COST_PRICING.get('elevenlabs-tts', 0)
        
        logger.warning(f"Unknown service for cost calculation: {service}")
        return 0.0
    
    async def _check_threshold(self, user_id: str, new_cost: float):
        """Check if user exceeded cost threshold"""
        try:
            # TODO: Implement once we have proper database integration
            # For now, just log warnings
            if new_cost > settings.cost_alert_threshold_usd:
                logger.warning(
                    f"Single request cost ${new_cost:.2f} exceeds threshold "
                    f"${settings.cost_alert_threshold_usd}"
                )
        
        except Exception as e:
            logger.error(f"Error checking cost threshold: {e}")
    
    async def get_user_costs(
        self,
        user_id: str,
        days: int = 30
    ) -> dict:
        """
        Get cost summary for a user
        
        Returns:
            {
                'total_usd': float,
                'by_service': {service: cost},
                'by_day': {date: cost}
            }
        """
        try:
            # TODO: Implement once supabase_client is ready
            logger.info(f"Getting costs for user {user_id} (last {days} days)")
            
            return {
                'total_usd': 0.0,
                'by_service': {},
                'by_day': {}
            }
        
        except Exception as e:
            logger.error(f"Error getting user costs: {e}")
            return {'total_usd': 0.0, 'by_service': {}, 'by_day': {}}

# Global instance
cost_tracker = CostTracker()

