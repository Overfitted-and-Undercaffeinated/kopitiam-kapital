"""
Strategy Builder - Converts JSON definitions to executable functions
Compatible with existing BacktestEngine
"""
from typing import Dict, Callable, Any, Optional
import logging
import pandas as pd

# Flexible imports
try:
    from ..data.indicators import add_indicators_to_dataframe
except ImportError:
    from data.indicators import add_indicators_to_dataframe

logger = logging.getLogger(__name__)

class StrategyBuilder:
    """
    Builds executable strategy functions from JSON definitions
    
    Strategy JSON Format:
    {
        "name": "RSI Oversold",
        "description": "Buy when RSI < 30, sell when RSI > 70",
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
            "value": 0.1  # 10% of capital per trade
        }
    }
    """
    
    def __init__(self):
        logger.info("Initialized Strategy Builder")
    
    async def build_strategy(self, strategy_def: Dict) -> Callable:
        """
        Build executable strategy function from JSON definition
        
        Args:
            strategy_def: Strategy definition dictionary
        
        Returns:
            Callable strategy function compatible with BacktestEngine
            Signature: async def strategy(data: pd.DataFrame) -> Optional[Dict]
        """
        # Extract strategy components
        indicators = strategy_def.get('indicators', [])
        entry_rules = strategy_def.get('entry_rules', [])
        exit_rules = strategy_def.get('exit_rules', [])
        position_sizing = strategy_def.get('position_sizing', {'type': 'fixed', 'value': 1})
        
        # Create wrapper that matches BacktestEngine's expected signature
        async def strategy_wrapper(data: pd.DataFrame) -> Optional[Dict]:
            """
            Strategy wrapper compatible with BacktestEngine
            
            BacktestEngine expects:
            - Signature: async def strategy(data: pd.DataFrame) -> Optional[Dict]
            - Returns: {'direction': 'BUY', 'entry': price, 'stop': price, 'target': price} or None
            """
            # Normalize column names (yfinance uses Capital, we need lowercase)
            data = data.copy()
            data.columns = data.columns.str.lower()
            
            # Add indicators to data
            data = add_indicators_to_dataframe(data, indicators)
            
            # ADD: Log available indicators
            logger.debug(f"Available columns after indicators: {data.columns.tolist()}")
            logger.debug(f"Current row values: {current.to_dict()}")
            
            # Get current row (latest data point)
            current = data.iloc[-1]
            
            # Check entry rules (we're always looking for new entries in backtest)
            should_enter = self._evaluate_rules(entry_rules, current, data)
            
            # ADD: Log rule evaluation results
            logger.debug(f"Entry rules evaluation: {should_enter}")
            
            if should_enter:
                entry_price = current['close']
                
                # Calculate stop and target based on risk management with MCP
                risk_mgmt = strategy_def.get('risk_management', {})
                
                # Try to use MCP for ATR-based stop optimization
                from utils.mcp_client import mcp_risk_client
                from data.indicators import calculate_atr
                
                try:
                    # Calculate ATR for dynamic stops
                    atr_values = calculate_atr(data, period=14)
                    current_atr = atr_values.iloc[-1] if len(atr_values) > 0 else 0
                    
                    # Use MCP for ATR-based stop optimization
                    if mcp_risk_client.enabled and current_atr > 0:
                        stop_result = await mcp_risk_client.optimize_stop_loss(
                            entry_price=entry_price,
                            atr=current_atr,
                            risk_tolerance=risk_mgmt.get('risk_tolerance', 'moderate'),
                            direction='BUY'
                        )
                        
                        if not stop_result:
                            raise RuntimeError("MCP stop loss optimization failed")
                        
                        stop_price = stop_result['stop_loss']
                        logger.info(f"MCP optimized stop: ${stop_price} ({stop_result['atr_multiplier']}x ATR)")
                    else:
                        if not mcp_risk_client.enabled:
                            raise RuntimeError("MCP Risk Tools required for dynamic stop optimization")
                        # Fallback if ATR is 0
                        stop_loss_pct = risk_mgmt.get('stop_loss_percent', 0.05)
                        stop_price = entry_price * (1 - stop_loss_pct)
                except Exception as e:
                    # Fallback to fixed percentage if MCP fails
                    logger.warning(f"MCP stop optimization unavailable: {e}, using fixed %")
                    stop_loss_pct = risk_mgmt.get('stop_loss_percent', 0.05)
                    stop_price = entry_price * (1 - stop_loss_pct)
                
                # Take profit remains percentage-based
                take_profit_pct = risk_mgmt.get('take_profit_percent', 0.10)
                target_price = entry_price * (1 + take_profit_pct)
                
                return {
                    'direction': 'BUY',
                    'entry': entry_price,
                    'stop': stop_price,
                    'target': target_price
                }
            
            # No signal
            return None
        
        return strategy_wrapper
    
    def _evaluate_rules(self, rules: list, current: pd.Series, data: pd.DataFrame) -> bool:
        """
        Evaluate a list of rules
        All rules must be True for overall True (AND logic)
        """
        if not rules:
            return False
        
        for rule in rules:
            if not self._evaluate_single_rule(rule, current, data):
                return False
        
        return True
    
    def _evaluate_single_rule(self, rule: Dict, current: pd.Series, data: pd.DataFrame) -> bool:
        """
        Evaluate a single rule
        
        Rule formats:
        1. Simple comparison: {"indicator": "rsi", "condition": "<", "value": 30}
        2. Indicator comparison: {"indicator": "macd", "condition": ">", "value": "macd_signal"}
        3. Crossover: {"indicator": "price", "condition": "crosses_above", "value": "sma_20"}
        """
        indicator = rule.get('indicator')
        condition = rule.get('condition')
        value = rule.get('value')
        
        # Get indicator value
        if indicator == 'price':
            ind_value = current['close']
        else:
            ind_value = current.get(indicator)
        
        # Handle missing indicator
        if ind_value is None or pd.isna(ind_value):
            return False
        
        # Get comparison value
        if isinstance(value, str):
            # Compare to another indicator
            comp_value = current.get(value)
            if comp_value is None or pd.isna(comp_value):
                return False
        else:
            comp_value = value
        
        # Evaluate condition
        if condition == '>':
            return ind_value > comp_value
        elif condition == '<':
            return ind_value < comp_value
        elif condition == '>=':
            return ind_value >= comp_value
        elif condition == '<=':
            return ind_value <= comp_value
        elif condition == '==':
            return ind_value == comp_value
        elif condition == '!=':
            return ind_value != comp_value
        elif condition == 'crosses_above':
            # Check if indicator crossed above value
            if len(data) < 2:
                return False
            prev = data.iloc[-2]
            prev_ind = prev.get(indicator) if indicator != 'price' else prev['close']
            prev_comp = prev.get(value) if isinstance(value, str) else value
            
            return (prev_ind <= prev_comp) and (ind_value > comp_value)
        
        elif condition == 'crosses_below':
            # Check if indicator crossed below value
            if len(data) < 2:
                return False
            prev = data.iloc[-2]
            prev_ind = prev.get(indicator) if indicator != 'price' else prev['close']
            prev_comp = prev.get(value) if isinstance(value, str) else value
            
            return (prev_ind >= prev_comp) and (ind_value < comp_value)
        
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
    
    def _calculate_position_size(
        self,
        sizing: Dict,
        capital: float,
        price: float
    ) -> int:
        """
        Calculate position size based on sizing rules
        
        Types:
        - fixed: Fixed number of shares
        - fixed_percent: Fixed percentage of capital
        - atr: Based on ATR (risk-based sizing)
        """
        sizing_type = sizing.get('type', 'fixed')
        
        if sizing_type == 'fixed':
            return int(sizing.get('value', 1))
        
        elif sizing_type == 'fixed_percent':
            percent = sizing.get('value', 0.1)  # Default: 10%
            position_value = capital * percent
            quantity = int(position_value / price)
            return max(1, quantity)  # At least 1 share
        
        elif sizing_type == 'atr':
            # TODO: Implement ATR-based sizing (requires ATR in data)
            # For now, use fixed percent
            return self._calculate_position_size(
                {'type': 'fixed_percent', 'value': 0.1},
                capital,
                price
            )
        
        else:
            logger.warning(f"Unknown sizing type: {sizing_type}, using fixed")
            return 1
    
    def _format_entry_reason(self, rules: list, current: pd.Series) -> str:
        """Format entry signal reason"""
        reasons = []
        for rule in rules:
            indicator = rule.get('indicator')
            condition = rule.get('condition')
            value = rule.get('value')
            
            ind_value = current.get(indicator)
            if ind_value is not None:
                reasons.append(f"{indicator}={ind_value:.2f} {condition} {value}")
        
        return "; ".join(reasons)
    
    def _format_exit_reason(self, rules: list, current: pd.Series) -> str:
        """Format exit signal reason"""
        reasons = []
        for rule in rules:
            indicator = rule.get('indicator')
            condition = rule.get('condition')
            value = rule.get('value')
            
            ind_value = current.get(indicator)
            if ind_value is not None:
                reasons.append(f"{indicator}={ind_value:.2f} {condition} {value}")
        
        return "; ".join(reasons)
    
    def validate_strategy(self, strategy_def: Dict) -> tuple[bool, str]:
        """
        Validate strategy definition
        
        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        if 'name' not in strategy_def:
            return False, "Missing 'name' field"
        
        if 'entry_rules' not in strategy_def or not strategy_def['entry_rules']:
            return False, "Missing or empty 'entry_rules'"
        
        if 'exit_rules' not in strategy_def or not strategy_def['exit_rules']:
            return False, "Missing or empty 'exit_rules'"
        
        # Validate indicators
        indicators = strategy_def.get('indicators', [])
        for ind in indicators:
            if 'type' not in ind:
                return False, f"Indicator missing 'type' field: {ind}"
        
        # Validate rules
        entry_rules = strategy_def.get('entry_rules', [])
        exit_rules = strategy_def.get('exit_rules', [])
        
        for rule in entry_rules + exit_rules:
            if 'indicator' not in rule:
                return False, f"Rule missing 'indicator' field: {rule}"
            if 'condition' not in rule:
                return False, f"Rule missing 'condition' field: {rule}"
            if 'value' not in rule:
                return False, f"Rule missing 'value' field: {rule}"
        
        return True, "Valid"

# Global instance
strategy_builder = StrategyBuilder()

