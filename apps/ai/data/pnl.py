"""P&L calculation utilities"""

def calculate_pnl(positions: list[dict]):
    """Calculate total P&L from positions"""
    total_pnl = 0.0
    pnl_by_symbol = {}
    
    for position in positions:
        # TODO: Implement P&L calculation
        # Handle both open and closed positions
        pass
    
    return {
        "total_pnl": total_pnl,
        "by_symbol": pnl_by_symbol
    }

def calculate_unrealized_pnl(position: dict, current_price: float):
    """Calculate unrealized P&L for open position"""
    qty = position.get("qty", 0)
    avg_price = position.get("avg_price", 0)
    
    return (current_price - avg_price) * qty

