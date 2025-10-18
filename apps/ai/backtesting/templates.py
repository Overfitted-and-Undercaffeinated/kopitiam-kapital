"""
Pre-built strategy templates in JSON format
Compatible with StrategyBuilder
"""
from typing import Dict, List

# ============================================================================
# STRATEGY TEMPLATES LIBRARY
# ============================================================================

STRATEGY_TEMPLATES = {
    "rsi_oversold": {
        "name": "RSI Oversold",
        "description": "Buy when RSI drops below 30 (oversold), sell when RSI rises above 70 (overbought). Classic mean-reversion strategy.",
        "category": "Mean Reversion",
        "difficulty": "Beginner",
        "indicators": [
            {"type": "rsi", "period": 14}
        ],
        "entry_rules": [
            {"indicator": "rsi", "condition": "<", "value": 30}
        ],
        "exit_rules": [
            {"indicator": "rsi", "condition": ">", "value": 70}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.1  # 10% of capital
        },
        "risk_management": {
            "stop_loss_percent": 0.05,  # 5% stop loss
            "take_profit_percent": 0.10  # 10% take profit
        }
    },
    
    "momentum_breakout": {
        "name": "Momentum Breakout",
        "description": "Buy when price breaks above 20-day SMA, sell when price drops below. Trend-following strategy.",
        "category": "Trend Following",
        "difficulty": "Beginner",
        "indicators": [
            {"type": "sma", "period": 20}
        ],
        "entry_rules": [
            {"indicator": "price", "condition": "crosses_above", "value": "sma_20"}
        ],
        "exit_rules": [
            {"indicator": "price", "condition": "crosses_below", "value": "sma_20"}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.1
        },
        "risk_management": {
            "stop_loss_percent": 0.03,
            "take_profit_percent": 0.15
        }
    },
    
    "macd_crossover": {
        "name": "MACD Crossover",
        "description": "Buy when MACD crosses above signal line, sell when MACD crosses below signal line. Popular momentum strategy.",
        "category": "Momentum",
        "difficulty": "Intermediate",
        "indicators": [
            {"type": "macd"}  # Uses default 12/26/9
        ],
        "entry_rules": [
            {"indicator": "macd", "condition": "crosses_above", "value": "macd_signal"}
        ],
        "exit_rules": [
            {"indicator": "macd", "condition": "crosses_below", "value": "macd_signal"}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.12
        },
        "risk_management": {
            "stop_loss_percent": 0.04,
            "take_profit_percent": 0.12
        }
    },
    
    "sma_crossover": {
        "name": "SMA Crossover (Golden Cross)",
        "description": "Buy when fast SMA (50) crosses above slow SMA (200), sell when it crosses below. Classic trend strategy.",
        "category": "Trend Following",
        "difficulty": "Beginner",
        "indicators": [
            {"type": "sma", "period": 50},
            {"type": "sma", "period": 200}
        ],
        "entry_rules": [
            {"indicator": "sma_50", "condition": "crosses_above", "value": "sma_200"}
        ],
        "exit_rules": [
            {"indicator": "sma_50", "condition": "crosses_below", "value": "sma_200"}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.15
        },
        "risk_management": {
            "stop_loss_percent": 0.05,
            "take_profit_percent": 0.20
        }
    },
    
    "bollinger_mean_reversion": {
        "name": "Bollinger Band Mean Reversion",
        "description": "Buy when price touches lower band, sell when price touches upper band. Mean reversion on volatility bands.",
        "category": "Mean Reversion",
        "difficulty": "Intermediate",
        "indicators": [
            {"type": "bollinger", "period": 20, "std_dev": 2.0}
        ],
        "entry_rules": [
            {"indicator": "price", "condition": "<=", "value": "bb_lower"}
        ],
        "exit_rules": [
            {"indicator": "price", "condition": ">=", "value": "bb_upper"}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.08
        },
        "risk_management": {
            "stop_loss_percent": 0.06,
            "take_profit_percent": 0.08
        }
    },
    
    "rsi_macd_combo": {
        "name": "RSI + MACD Combo",
        "description": "Buy when RSI < 40 AND MACD crosses above signal. Multi-indicator confirmation strategy.",
        "category": "Combined",
        "difficulty": "Advanced",
        "indicators": [
            {"type": "rsi", "period": 14},
            {"type": "macd"}
        ],
        "entry_rules": [
            {"indicator": "rsi", "condition": "<", "value": 40},
            {"indicator": "macd", "condition": ">", "value": "macd_signal"}
        ],
        "exit_rules": [
            {"indicator": "rsi", "condition": ">", "value": 60},
            {"indicator": "macd", "condition": "<", "value": "macd_signal"}
        ],
        "position_sizing": {
            "type": "fixed_percent",
            "value": 0.12
        },
        "risk_management": {
            "stop_loss_percent": 0.04,
            "take_profit_percent": 0.10
        }
    }
}

# ============================================================================
# TEMPLATE ACCESS FUNCTIONS
# ============================================================================

def get_template(template_id: str) -> Dict:
    """
    Get a strategy template by ID
    
    Args:
        template_id: Template identifier (e.g. 'rsi_oversold')
    
    Returns:
        Template dictionary with full configuration
    """
    return STRATEGY_TEMPLATES.get(template_id)

def list_templates() -> List[Dict]:
    """
    List all available templates with metadata
    
    Returns:
        List of template summaries
    """
    return [
        {
            'id': key,
            'name': template['name'],
            'description': template['description'],
            'category': template['category'],
            'difficulty': template['difficulty']
        }
        for key, template in STRATEGY_TEMPLATES.items()
    ]

def get_templates_by_category(category: str) -> List[Dict]:
    """
    Get all templates in a specific category
    
    Args:
        category: Category name (e.g. 'Mean Reversion', 'Trend Following')
    
    Returns:
        List of templates in that category
    """
    return [
        {**template, 'id': key}
        for key, template in STRATEGY_TEMPLATES.items()
        if template['category'] == category
    ]

def get_beginner_templates() -> List[Dict]:
    """
    Get all beginner-friendly templates
    
    Returns:
        List of templates suitable for beginners
    """
    return [
        {**template, 'id': key}
        for key, template in STRATEGY_TEMPLATES.items()
        if template['difficulty'] == 'Beginner'
    ]

def get_categories() -> List[str]:
    """
    Get list of all template categories
    
    Returns:
        Unique category names
    """
    return list(set(template['category'] for template in STRATEGY_TEMPLATES.values()))

