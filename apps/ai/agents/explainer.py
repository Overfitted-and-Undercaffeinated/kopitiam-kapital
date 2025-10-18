"""
Explainer Agent
Provides educational explanations adapted to user's knowledge level
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime

# Flexible imports
try:
    from ..utils.tier_manager import tier_manager, Feature, UserTier
    from ..utils.clients import get_openai_client
    from ..memory.mem0_service import mem0_service
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.tier_manager import tier_manager, Feature, UserTier
    from utils.clients import get_openai_client
    from memory.mem0_service import mem0_service
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class KnowledgeLevel(str):
    """User knowledge levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TopicCategory(str):
    """Explanation topic categories"""
    TRADING_CONCEPTS = "trading_concepts"
    PLATFORM_FEATURES = "platform_features"
    MARKET_MECHANICS = "market_mechanics"
    STRATEGIES = "strategies"


# Topic examples by category
TOPIC_EXAMPLES = {
    TopicCategory.TRADING_CONCEPTS: [
        "RSI", "MACD", "moving averages", "support and resistance",
        "candlestick patterns", "volume analysis", "volatility",
        "stop loss", "take profit", "position sizing"
    ],
    TopicCategory.PLATFORM_FEATURES: [
        "morning briefs", "EOD reports", "sentiment analysis",
        "backtesting", "alerts", "watchlists", "collaboration"
    ],
    TopicCategory.MARKET_MECHANICS: [
        "bid-ask spread", "market orders", "limit orders",
        "liquidity", "market makers", "after-hours trading"
    ],
    TopicCategory.STRATEGIES: [
        "swing trading", "day trading", "trend following",
        "mean reversion", "momentum trading", "risk management"
    ]
}


class ExplainerAgent:
    """
    Explains trading concepts based on user's knowledge level
    
    Features by tier:
    - FREE: Trading concepts (beginner level)
    - PRO: Trading concepts + platform features (intermediate level)
    - ENTERPRISE: All topics + advanced strategies (expert level)
    
    Knowledge level adaptation:
    - Checks Mem0 for user's trading experience
    - Allows manual override per request
    - Adjusts explanation depth and terminology
    """
    
    def __init__(self):
        self.name = "explainer"
        self.client = get_openai_client()
        self.model = "gpt-4o-mini"
        logger.info("Initialized Explainer Agent")
    
    async def explain(
        self,
        topic: str,
        user_id: str,
        level_override: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Explain a trading concept to the user
        
        Args:
            topic: Topic to explain (e.g., "RSI", "sentiment analysis")
            user_id: User ID
            level_override: Optional override for knowledge level
            category: Optional category hint
        
        Returns:
            Explanation with examples and next steps
        """
        logger.info(f"Explaining '{topic}' to user {user_id}")
        
        # Get user tier and allowed topics
        tier = await tier_manager.get_user_tier(user_id)
        tier_config = tier_manager.get_feature_config(Feature.EXPLAINER, tier)
        allowed_topics = tier_config.get("topics", [TopicCategory.TRADING_CONCEPTS])
        depth = tier_config.get("depth", "basic")
        
        # Determine topic category
        if not category:
            category = self._classify_topic(topic)
        
        # Check if topic is allowed for tier
        if category not in allowed_topics:
            required_tier = self._required_tier_for_topic(category)
            return {
                "error": f"Topic '{category}' requires {required_tier} tier",
                "upgrade_message": f"Upgrade to {required_tier} to learn about {category}",
                "available_topics": allowed_topics
            }
        
        # Get user's knowledge level
        knowledge_level = await self._get_user_level(user_id, level_override)
        
        logger.info(
            f"Explaining {topic} (category: {category}, level: {knowledge_level}, "
            f"depth: {depth}, tier: {tier.value})"
        )
        
        try:
            # Generate explanation
            explanation = await self._generate_explanation(
                topic=topic,
                category=category,
                knowledge_level=knowledge_level,
                depth=depth,
                tier=tier
            )
            
            return {
                "topic": topic,
                "category": category,
                "knowledge_level": knowledge_level,
                "depth": depth,
                "tier": tier.value,
                "explanation": explanation["text"],
                "examples": explanation.get("examples", []),
                "key_points": explanation.get("key_points", []),
                "next_steps": explanation.get("next_steps", []),
                "related_topics": explanation.get("related_topics", []),
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating explanation: {e}", exc_info=True)
            raise
    
    async def _get_user_level(
        self,
        user_id: str,
        level_override: Optional[str] = None
    ) -> str:
        """
        Determine user's knowledge level
        
        Priority:
        1. Manual override (if provided)
        2. Mem0 user profile
        3. Default to beginner
        
        Args:
            user_id: User ID
            level_override: Optional manual override
        
        Returns:
            Knowledge level (beginner/intermediate/advanced)
        """
        # Use override if provided
        if level_override:
            return level_override.lower()
        
        # Check Mem0 for user's trading experience
        if mem0_service.enabled:
            try:
                memories = await mem0_service.search_memories(
                    user_id=user_id,
                    query="trading experience level knowledge",
                    limit=3
                )
                
                for memory in memories:
                    content = memory.get('content', '').lower()
                    
                    if any(word in content for word in ['advanced', 'expert', 'experienced', 'professional']):
                        return KnowledgeLevel.ADVANCED
                    elif any(word in content for word in ['intermediate', 'some experience', 'learning']):
                        return KnowledgeLevel.INTERMEDIATE
                    elif any(word in content for word in ['beginner', 'new', 'learning']):
                        return KnowledgeLevel.BEGINNER
            
            except Exception as e:
                logger.error(f"Error checking Mem0 for knowledge level: {e}")
        
        # Default to beginner
        return KnowledgeLevel.BEGINNER
    
    async def _generate_explanation(
        self,
        topic: str,
        category: str,
        knowledge_level: str,
        depth: str,
        tier: UserTier
    ) -> Dict:
        """
        Generate explanation using GPT-4o-mini
        
        Args:
            topic: Topic to explain
            category: Topic category
            knowledge_level: User's knowledge level
            depth: Explanation depth
            tier: User tier
        
        Returns:
            Structured explanation
        """
        # Build system prompt based on level and tier
        system_prompt = self._build_system_prompt(knowledge_level, depth, tier)
        
        # Build user prompt
        user_prompt = f"""Explain "{topic}" (category: {category}).

Provide:
1. Clear explanation (2-3 paragraphs)
2. Practical examples (2-3)
3. Key points to remember (3-5 bullet points)
4. Next steps for learning
5. Related topics to explore

Adapt to {knowledge_level} level trader.

IMPORTANT: Use HTML formatting:
- Use <h3>Clear Explanation</h3> for headers
- Use <b>bold text</b> for emphasis
- Do NOT use markdown syntax like **bold** or ### headers
- Use <br> for line breaks if needed"""
        
        # Add tier-specific instructions
        if tier == UserTier.PRO:
            user_prompt += "\n\nInclude intermediate-level insights and practical applications."
        elif tier == UserTier.ENTERPRISE:
            user_prompt += "\n\nProvide advanced analysis, edge cases, and professional strategies."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            explanation_text = response.choices[0].message.content
            
            # Track cost
            await cost_tracker.log_cost(
                user_id="system",
                service="openai-explainer",
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                metadata={"tier": tier.value, "topic": topic}
            )
            
            # Parse explanation (simple parsing)
            sections = self._parse_explanation(explanation_text)
            
            return {
                "text": explanation_text,
                "examples": sections.get("examples", []),
                "key_points": sections.get("key_points", []),
                "next_steps": sections.get("next_steps", []),
                "related_topics": sections.get("related_topics", [])
            }
        
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            raise
    
    def _build_system_prompt(self, knowledge_level: str, depth: str, tier: UserTier) -> str:
        """Build system prompt based on user attributes"""
        base_prompt = "You are a patient and knowledgeable trading educator. Use HTML formatting: <h3> for headers, <b> for bold text. Do NOT use markdown syntax."
        
        if knowledge_level == KnowledgeLevel.BEGINNER:
            base_prompt += " Explain concepts clearly using simple language and analogies. Avoid jargon."
        elif knowledge_level == KnowledgeLevel.INTERMEDIATE:
            base_prompt += " Provide detailed explanations with some technical terminology. Focus on practical applications."
        else:  # ADVANCED
            base_prompt += " Provide in-depth technical analysis. Use industry terminology and discuss edge cases."
        
        if tier == UserTier.FREE:
            base_prompt += " Keep explanations concise and focused on fundamentals."
        elif tier == UserTier.PRO:
            base_prompt += " Include intermediate strategies and real-world examples."
        else:  # ENTERPRISE
            base_prompt += " Provide comprehensive analysis with advanced strategies and professional insights."
        
        return base_prompt
    
    def _parse_explanation(self, text: str) -> Dict:
        """Parse explanation text into structured sections"""
        # Simple parsing - look for common section markers
        sections = {
            "examples": [],
            "key_points": [],
            "next_steps": [],
            "related_topics": []
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            if 'example' in line.lower() and ':' in line:
                current_section = "examples"
            elif 'key point' in line.lower() or 'remember' in line.lower():
                current_section = "key_points"
            elif 'next step' in line.lower():
                current_section = "next_steps"
            elif 'related' in line.lower():
                current_section = "related_topics"
            
            # Add to current section if it's a bullet or numbered point
            if current_section and (line.startswith('-') or line.startswith('•') or line[0:2].replace('.', '').isdigit()):
                cleaned = line.lstrip('-•0123456789. ')
                if cleaned:
                    sections[current_section].append(cleaned)
        
        return sections
    
    def _classify_topic(self, topic: str) -> str:
        """Classify topic into a category"""
        topic_lower = topic.lower()
        
        # Check each category
        for category, examples in TOPIC_EXAMPLES.items():
            if any(example.lower() in topic_lower for example in examples):
                return category
        
        # Default to trading concepts
        return TopicCategory.TRADING_CONCEPTS
    
    def _required_tier_for_topic(self, category: str) -> str:
        """Get required tier for a topic category"""
        if category == TopicCategory.PLATFORM_FEATURES:
            return "Pro"
        elif category == TopicCategory.STRATEGIES:
            return "Enterprise"
        return "Free"


# Global instance
explainer_agent = ExplainerAgent()
