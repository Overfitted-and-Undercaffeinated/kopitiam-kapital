"""
Sample workspace data for demo
🚨 WARNING: This is demo data for presentation purposes
"""
import logging
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)

# Sample workspace
DEMO_WORKSPACE = {
    "id": "demo-workspace-001",
    "name": "Quantum Trading Team",
    "description": "Elite trading team focused on tech stocks",
    "tier": "Enterprise",
    "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
    "member_count": 4,
    "is_active": True
}

# Sample members
DEMO_MEMBERS = [
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_001",
        "email": "marcus@quantumtrading.com",
        "role": "owner",
        "joined_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "can_trade": True,
        "can_chat": True,
        "can_invite": True
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_002",
        "email": "sarah@quantumtrading.com",
        "role": "admin",
        "joined_at": (datetime.now() - timedelta(days=25)).isoformat(),
        "can_trade": True,
        "can_chat": True,
        "can_invite": True
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_003",
        "email": "david@quantumtrading.com",
        "role": "member",
        "joined_at": (datetime.now() - timedelta(days=20)).isoformat(),
        "can_trade": True,
        "can_chat": True,
        "can_invite": False
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "ai_agent",
        "email": "ai@kopitiamcapital.com",
        "role": "member",
        "joined_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "can_trade": False,
        "can_chat": True,
        "can_invite": False
    }
]

# Sample chat history
DEMO_CHAT_HISTORY = [
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_001",
        "message_type": "user",
        "message": "Morning team! What are we watching today?",
        "created_at": (datetime.now() - timedelta(hours=3)).isoformat()
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_002",
        "message_type": "user",
        "message": "NVDA looking strong. Sentiment is 82% bullish across all sources.",
        "created_at": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
        "symbols_mentioned": ["NVDA"]
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "ai_agent",
        "message_type": "ai",
        "message": "Great observation Sarah! NVDA sentiment breakdown:\n• News: 75% (45 articles)\n• Reddit: 88% (1,823 mentions)\n• StockTwits: 84% (542 messages)\n\nBacktest validation: RSI oversold strategy shows 67% win rate over 45 trades. Consider entry around $485 with 5% stop.",
        "created_at": (datetime.now() - timedelta(hours=2, minutes=43)).isoformat(),
        "symbols_mentioned": ["NVDA"],
        "trade_suggestions": [
            {
                "symbol": "NVDA",
                "action": "BUY",
                "confidence": 0.78,
                "sentiment_score": 0.82
            }
        ]
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_003",
        "message_type": "user",
        "message": "I'm in. Bought 100 shares at $487. Added to our watchlist.",
        "created_at": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
        "symbols_mentioned": ["NVDA"]
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "user_001",
        "message_type": "user",
        "message": "Nice! Also watching TSLA. Thoughts?",
        "created_at": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
        "symbols_mentioned": ["TSLA"]
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "user_id": "ai_agent",
        "message_type": "ai",
        "message": "TSLA sentiment is moderately bullish at 68%:\n• Mixed news coverage (65%)\n• Strong Reddit interest (72%)\n• 2,156 mentions in past 24h\n\nBacktest shows 58% win rate. Slightly lower than NVDA but still positive. Watch for entry around $250.",
        "created_at": (datetime.now() - timedelta(hours=1, minutes=14)).isoformat(),
        "symbols_mentioned": ["TSLA"]
    }
]

# Sample shared watchlist
DEMO_WATCHLIST = [
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "symbol": "NVDA",
        "added_by": "user_002",
        "added_at": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
        "current_price": 487.50,
        "sentiment_score": 0.82,
        "last_analyzed_at": datetime.now().isoformat(),
        "notes": "Strong AI chip demand",
        "alerts_enabled": True
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "symbol": "TSLA",
        "added_by": "user_001",
        "added_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "current_price": 251.30,
        "sentiment_score": 0.68,
        "last_analyzed_at": datetime.now().isoformat(),
        "notes": "Monitoring for entry",
        "alerts_enabled": True
    },
    {
        "id": str(uuid4()),
        "workspace_id": "demo-workspace-001",
        "symbol": "AMD",
        "added_by": "user_003",
        "added_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "current_price": 142.80,
        "sentiment_score": 0.76,
        "last_analyzed_at": datetime.now().isoformat(),
        "notes": "Alternative to NVDA",
        "alerts_enabled": True
    }
]

def get_demo_workspace():
    """Get demo workspace data"""
    logger.warning("🚨 DEMO MODE - Returning sample workspace")
    return {
        'workspace': DEMO_WORKSPACE,
        'members': DEMO_MEMBERS,
        'chat_history': DEMO_CHAT_HISTORY,
        'watchlist': DEMO_WATCHLIST
    }

demo_workspace_data = {
    'workspace': DEMO_WORKSPACE,
    'members': DEMO_MEMBERS,
    'chat_history': DEMO_CHAT_HISTORY,
    'watchlist': DEMO_WATCHLIST
}

