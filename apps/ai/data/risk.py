"""
Risk metric calculations for backtesting and portfolio management

Includes:
- Value at Risk (VaR)
- Conditional Value at Risk (CVaR / Expected Shortfall)
- Position sizing
- Risk metrics
"""
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_var(
    returns: List[float],
    confidence_level: float = 0.95,
    method: str = "historical"
) -> float:
    """
    Calculate Value at Risk (VaR)
    
    VaR estimates the maximum loss over a given time period at a given confidence level.
    For example, a 95% VaR of -5% means there's a 5% chance of losing more than 5%.
    
    Args:
        returns: List of returns (as decimals, e.g., 0.05 = 5% gain, -0.03 = 3% loss)
        confidence_level: Confidence level (default 0.95 = 95%)
        method: "historical" (empirical) or "parametric" (assumes normal distribution)
    
    Returns:
        VaR as a decimal (negative value represents loss)
        Example: -0.05 means 5% worst-case loss at given confidence level
    
    Example:
        returns = [0.02, -0.01, 0.03, -0.05, 0.01, -0.08]
        var_95 = calculate_var(returns, 0.95)
        # Result: -0.08 (at 95% confidence, worst loss is 8%)
    """
    if not returns or len(returns) == 0:
        logger.warning("No returns provided for VaR calculation")
        return 0.0
    
    returns_array = np.array(returns)
    
    if method == "historical":
        # Historical VaR: use empirical distribution
        # Sort returns and find the percentile
        sorted_returns = np.sort(returns_array)
        index = int((1 - confidence_level) * len(sorted_returns))
        
        # Ensure index is valid
        index = max(0, min(index, len(sorted_returns) - 1))
        
        var = sorted_returns[index]
        
        logger.debug(
            f"Historical VaR ({confidence_level*100}%): {var*100:.2f}% "
            f"based on {len(returns)} returns"
        )
        
        return float(var)
    
    elif method == "parametric":
        # Parametric VaR: assumes normal distribution
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        # Z-score for confidence level
        # For 95%: z = -1.645, for 99%: z = -2.326
        from scipy import stats
        z_score = stats.norm.ppf(1 - confidence_level)
        
        var = mean_return + z_score * std_return
        
        logger.debug(
            f"Parametric VaR ({confidence_level*100}%): {var*100:.2f}% "
            f"(mean: {mean_return*100:.2f}%, std: {std_return*100:.2f}%)"
        )
        
        return float(var)
    
    else:
        raise ValueError(f"Unknown VaR method: {method}. Use 'historical' or 'parametric'")

def calculate_cvar(
    returns: List[float],
    confidence_level: float = 0.95
) -> float:
    """
    Calculate Conditional Value at Risk (CVaR), also known as Expected Shortfall
    
    CVaR is the expected loss given that the loss exceeds VaR.
    It's a more conservative risk measure than VaR as it considers tail risk.
    
    Args:
        returns: List of returns (as decimals)
        confidence_level: Confidence level (default 0.95 = 95%)
    
    Returns:
        CVaR as a decimal (negative value represents expected loss in tail)
    
    Example:
        returns = [0.02, -0.01, 0.03, -0.05, 0.01, -0.08, -0.10]
        cvar_95 = calculate_cvar(returns, 0.95)
        # Result: -0.09 (average loss in worst 5% of cases)
    """
    if not returns or len(returns) == 0:
        logger.warning("No returns provided for CVaR calculation")
        return 0.0
    
    returns_array = np.array(returns)
    
    # First calculate VaR
    var = calculate_var(returns, confidence_level, method="historical")
    
    # CVaR is the average of all returns below VaR threshold
    tail_returns = returns_array[returns_array <= var]
    
    if len(tail_returns) == 0:
        # No returns in tail, return VaR
        cvar = var
    else:
        cvar = np.mean(tail_returns)
    
    logger.debug(
        f"CVaR ({confidence_level*100}%): {cvar*100:.2f}% "
        f"based on {len(tail_returns)} tail returns"
    )
    
    return float(cvar)

def calculate_position_size(nav: float, entry: float, stop: float, risk_pct: float):
    """
    Calculate position size based on risk parameters
    
    Args:
        nav: Net Asset Value (portfolio size)
        entry: Entry price
        stop: Stop loss price
        risk_pct: Risk percentage (e.g., 2.0 for 2% risk)
    
    Returns:
        Number of shares/units to buy
    """
    risk_amount = nav * (risk_pct / 100)
    price_risk = abs(entry - stop)
    
    if price_risk == 0:
        return 0
    
    position_size = risk_amount / price_risk
    return position_size

def calculate_risk_metrics(returns: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive risk metrics for a return series
    
    Args:
        returns: List of returns (as decimals)
    
    Returns:
        Dictionary with risk metrics:
        - var_95: Value at Risk (95%)
        - var_99: Value at Risk (99%)
        - cvar_95: Conditional VaR (95%)
        - cvar_99: Conditional VaR (99%)
        - volatility: Standard deviation of returns
        - downside_deviation: Std dev of negative returns only
        - max_loss: Maximum single-period loss
        - avg_loss: Average loss in losing periods
    """
    if not returns or len(returns) == 0:
        return {
            'var_95': 0.0,
            'var_99': 0.0,
            'cvar_95': 0.0,
            'cvar_99': 0.0,
            'volatility': 0.0,
            'downside_deviation': 0.0,
            'max_loss': 0.0,
            'avg_loss': 0.0
        }
    
    returns_array = np.array(returns)
    
    # VaR and CVaR at different confidence levels
    var_95 = calculate_var(returns, 0.95)
    var_99 = calculate_var(returns, 0.99)
    cvar_95 = calculate_cvar(returns, 0.95)
    cvar_99 = calculate_cvar(returns, 0.99)
    
    # Volatility measures
    volatility = np.std(returns_array)
    
    # Downside deviation (only negative returns)
    negative_returns = returns_array[returns_array < 0]
    downside_deviation = np.std(negative_returns) if len(negative_returns) > 0 else 0.0
    
    # Loss metrics
    max_loss = np.min(returns_array)
    avg_loss = np.mean(negative_returns) if len(negative_returns) > 0 else 0.0
    
    return {
        'var_95': float(var_95),
        'var_99': float(var_99),
        'cvar_95': float(cvar_95),
        'cvar_99': float(cvar_99),
        'volatility': float(volatility),
        'downside_deviation': float(downside_deviation),
        'max_loss': float(max_loss),
        'avg_loss': float(avg_loss)
    }

