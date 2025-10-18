"""
Tier Management Utility
Handles user tier checking, feature access control, and usage tracking
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

# Flexible imports
try:
    from ..memory.mem0_service import mem0_service
except ImportError:
    from memory.mem0_service import mem0_service

logger = logging.getLogger(__name__)


class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Feature(str, Enum):
    """Platform features with tier restrictions"""
    MONITOR_ALERTS = "monitor_alerts"
    LONG_CONTEXT_ANALYSIS = "long_context_analysis"
    EXPLAINER = "explainer"


# Feature limits per tier
FEATURE_LIMITS = {
    Feature.MONITOR_ALERTS: {
        UserTier.FREE: {"daily_limit": 3, "types": ["price"]},
        UserTier.PRO: {"daily_limit": 50, "types": ["price", "volatility", "sentiment"]},
        UserTier.ENTERPRISE: {"daily_limit": None, "types": ["price", "volatility", "sentiment", "news", "technical"]},
    },
    Feature.LONG_CONTEXT_ANALYSIS: {
        UserTier.FREE: {"monthly_limit": 1},
        UserTier.PRO: {"monthly_limit": 10},
        UserTier.ENTERPRISE: {"monthly_limit": None},
    },
    Feature.EXPLAINER: {
        UserTier.FREE: {"depth": "basic", "topics": ["trading_concepts"]},
        UserTier.PRO: {"depth": "intermediate", "topics": ["trading_concepts", "platform_features"]},
        UserTier.ENTERPRISE: {"depth": "advanced", "topics": ["trading_concepts", "platform_features", "strategies"]},
    },
}


class TierManager:
    """
    Manages user tiers, feature access, and usage tracking
    
    Tier storage:
    - Source of truth: Supabase users table (column: tier)
    - Cache: Mem0 user preferences for fast access
    """
    
    def __init__(self):
        self.usage_cache: Dict[str, Dict] = {}  # In-memory cache for usage counts
        logger.info("Initialized TierManager")
    
    async def get_user_tier(self, user_id: str) -> UserTier:
        """
        Get user's subscription tier
        
        Priority:
        1. Check Mem0 cache
        2. Query Supabase (TODO: implement when DB is ready)
        3. Default to FREE
        
        Args:
            user_id: User ID
        
        Returns:
            UserTier enum
        """
        try:
            # Try Mem0 cache first
            if mem0_service.enabled:
                memories = await mem0_service.search_memories(
                    user_id=user_id,
                    query="subscription tier",
                    limit=1
                )
                
                if memories:
                    content = memories[0].get('content', '').lower()
                    if 'enterprise' in content:
                        return UserTier.ENTERPRISE
                    elif 'pro' in content:
                        return UserTier.PRO
            
            # TODO: Query Supabase users table
            # tier_str = await supabase_client.get_user_tier(user_id)
            # return UserTier(tier_str)
            
            # Default to FREE
            logger.debug(f"User {user_id} defaulting to FREE tier")
            return UserTier.FREE
        
        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return UserTier.FREE
    
    async def check_feature_access(
        self,
        feature: Feature,
        user_id: str,
        check_usage: bool = True
    ) -> Dict[str, any]:
        """
        Check if user has access to a feature
        
        Args:
            feature: Feature to check
            user_id: User ID
            check_usage: Whether to check usage limits
        
        Returns:
            {
                "allowed": bool,
                "tier": UserTier,
                "limits": dict,
                "current_usage": int,
                "remaining": int or None,
                "message": str
            }
        """
        tier = await self.get_user_tier(user_id)
        limits = FEATURE_LIMITS.get(feature, {}).get(tier, {})
        
        result = {
            "allowed": True,
            "tier": tier,
            "limits": limits,
            "current_usage": 0,
            "remaining": None,
            "message": "Access granted"
        }
        
        # Check usage limits if enabled
        if check_usage:
            window = self._get_usage_window(feature)
            current_usage = await self.get_usage_count(feature, user_id, window)
            result["current_usage"] = current_usage
            
            # Check daily limits (for monitor alerts)
            if "daily_limit" in limits:
                daily_limit = limits["daily_limit"]
                if daily_limit is not None:  # None = unlimited
                    result["remaining"] = max(0, daily_limit - current_usage)
                    
                    if current_usage >= daily_limit:
                        result["allowed"] = False
                        result["message"] = f"Daily limit reached ({daily_limit}/{daily_limit}). Upgrade to {self._suggest_upgrade(tier)} for more."
            
            # Check monthly limits (for long context analysis)
            if "monthly_limit" in limits:
                monthly_limit = limits["monthly_limit"]
                if monthly_limit is not None:  # None = unlimited
                    result["remaining"] = max(0, monthly_limit - current_usage)
                    
                    if current_usage >= monthly_limit:
                        result["allowed"] = False
                        result["message"] = f"Monthly limit reached ({monthly_limit}/{monthly_limit}). Upgrade to {self._suggest_upgrade(tier)} for more."
        
        return result
    
    async def get_usage_count(
        self,
        feature: Feature,
        user_id: str,
        window: str = "day"
    ) -> int:
        """
        Get usage count for a feature within a time window
        
        Args:
            feature: Feature name
            user_id: User ID
            window: Time window ("day" or "month")
        
        Returns:
            Usage count
        """
        cache_key = f"{user_id}:{feature}:{window}"
        
        # Check in-memory cache
        if cache_key in self.usage_cache:
            cached = self.usage_cache[cache_key]
            # Check if cache is still valid
            if cached['expires_at'] > datetime.now():
                return cached['count']
        
        # TODO: Query Supabase usage_tracking table
        # count = await supabase_client.get_usage_count(user_id, feature, window)
        
        # For now, return 0 (no usage)
        count = 0
        
        # Cache for 5 minutes
        self.usage_cache[cache_key] = {
            'count': count,
            'expires_at': datetime.now() + timedelta(minutes=5)
        }
        
        return count
    
    async def increment_usage(
        self,
        feature: Feature,
        user_id: str
    ) -> None:
        """
        Increment usage count for a feature
        
        Args:
            feature: Feature name
            user_id: User ID
        """
        try:
            # Invalidate cache
            window = self._get_usage_window(feature)
            cache_key = f"{user_id}:{feature}:{window}"
            if cache_key in self.usage_cache:
                del self.usage_cache[cache_key]
            
            # TODO: Insert into Supabase usage_tracking table
            # await supabase_client.increment_usage(user_id, feature, datetime.now())
            
            logger.info(f"Incremented usage for {user_id}: {feature}")
        
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
    
    def get_feature_config(self, feature: Feature, tier: UserTier) -> Dict:
        """
        Get feature configuration for a tier
        
        Args:
            feature: Feature name
            tier: User tier
        
        Returns:
            Feature configuration dict
        """
        return FEATURE_LIMITS.get(feature, {}).get(tier, {})
    
    def _get_usage_window(self, feature: Feature) -> str:
        """Determine time window for feature usage tracking"""
        if feature == Feature.MONITOR_ALERTS:
            return "day"
        elif feature == Feature.LONG_CONTEXT_ANALYSIS:
            return "month"
        else:
            return "day"
    
    def _suggest_upgrade(self, current_tier: UserTier) -> str:
        """Suggest next tier upgrade"""
        if current_tier == UserTier.FREE:
            return "Pro"
        elif current_tier == UserTier.PRO:
            return "Enterprise"
        else:
            return "Enterprise"


# Global instance
tier_manager = TierManager()



