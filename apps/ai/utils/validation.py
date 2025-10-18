"""Input validation utilities"""

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    if not symbol or len(symbol) < 1 or len(symbol) > 10:
        return False
    return symbol.isalnum()

def validate_risk_percentage(risk_pct: float) -> bool:
    """Validate risk percentage is within reasonable bounds"""
    return 0 < risk_pct <= 100

