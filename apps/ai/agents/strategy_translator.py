"""
Strategy Translator Agent - Converts natural language to backtestable strategy JSON
Uses the backtest_explainer to build strategies from user descriptions
"""
import logging
from typing import Dict, Optional

# Flexible imports
try:
    from .backtest_explainer import backtest_explainer
except ImportError:
    from backtest_explainer import backtest_explainer

logger = logging.getLogger(__name__)


class StrategyTranslatorAgent:
    """
    Translates natural language strategy descriptions into executable trading rules
    
    Bridges the gap between user chat input and the backtesting engine
    Handles strategy validation and error refinement
    """
    
    def __init__(self):
        self.name = "strategy_translator"
        self.explainer = backtest_explainer
        logger.info("Initialized StrategyTranslatorAgent")
    
    async def translate_strategy(
        self,
        natural_language: str,
        symbol: str = None
    ) -> Dict:
        """
        Convert natural language strategy description to backtestable JSON
        
        Args:
            natural_language: User's strategy description
            symbol: Stock symbol for context (optional)
        
        Returns:
            Strategy JSON dict ready for backtesting
            {
                "name": "Strategy Name",
                "description": "What it does",
                "category": "Trend Following|Mean Reversion|etc",
                "indicators": [...],
                "entry_rules": [...],
                "exit_rules": [...],
                "position_sizing": {...},
                "risk_management": {...}
            }
            
        Raises:
            ValueError: If strategy description cannot be converted (includes suggestion for refinement)
        """
        logger.info(f"Translating strategy: {natural_language[:80]}...")
        
        try:
            # Use backtest_explainer to build strategy
            strategy_dict = await self.explainer.build_strategy_from_description(
                description=natural_language,
                symbol=symbol
            )
            
            # Check if Groq returned an error
            if strategy_dict.get("error"):
                error_msg = strategy_dict.get("message", "Unknown error")
                suggestion = strategy_dict.get("suggestion", "Please try again")
                raise ValueError(f"{error_msg}. {suggestion}")
            
            # Validate required fields
            required_fields = ["name", "description", "category", "indicators", "entry_rules", "exit_rules", "position_sizing", "risk_management"]
            missing = [f for f in required_fields if f not in strategy_dict]
            
            if missing:
                logger.error(f"Strategy missing required fields: {missing}")
                raise ValueError(
                    f"Generated strategy is incomplete (missing: {', '.join(missing)}). "
                    f"Please try with a more detailed strategy description."
                )
            
            # Log success
            logger.info(
                f"Strategy translated: '{strategy_dict['name']}' "
                f"({strategy_dict['category']} - {strategy_dict['difficulty']})"
            )
            
            return strategy_dict
            
        except ValueError as e:
            logger.error(f"Strategy translation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during translation: {e}")
            raise ValueError(f"Failed to translate strategy: {str(e)}")


# Global instance
strategy_translator = StrategyTranslatorAgent()

