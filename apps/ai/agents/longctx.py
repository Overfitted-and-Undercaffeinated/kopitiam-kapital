"""
Long Context Analyst
Analyzes lengthy financial documents using GPT-4o's 128K context window
"""
import logging
from typing import Dict, Optional
import json
from datetime import datetime

# Flexible imports
try:
    from ..utils.tier_manager import tier_manager, Feature, UserTier
    from ..utils.clients import get_openai_client
    from ..utils.cost_tracker import cost_tracker
except ImportError:
    from utils.tier_manager import tier_manager, Feature, UserTier
    from utils.clients import get_openai_client
    from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class LongContextAnalyst:
    """
    Analyzes long-form financial documents like 10-Ks, annual reports, earnings calls
    
    Features by tier:
    - FREE: Basic summary + key metrics (1 per month)
    - PRO: Summary + risks + opportunities + AI insights (10 per month)
    - ENTERPRISE: Full analysis with competitive positioning (unlimited)
    
    Uses OpenAI GPT-4o for 128K token context window
    """
    
    def __init__(self):
        self.name = "longctx"
        try:
            self.client = get_openai_client()
            # Using GPT-4o - latest OpenAI model with 128K context
            self.model = "gpt-4o"
            self.enabled = True
        except Exception as e:
            logger.warning(f"OpenAI client not available: {e}")
            self.client = None
            self.enabled = False
        
        logger.info(f"Initialized Long Context Analyst (enabled: {self.enabled})")
    
    async def analyze_document(
        self,
        text: str,
        document_type: str,
        user_id: str,
        ticker: Optional[str] = None
    ) -> Dict:
        """
        Analyze a long-form financial document
        
        Args:
            text: Document text
            document_type: Type of document (e.g., "10-K", "annual_report", "earnings_call")
            user_id: User ID
            ticker: Optional stock ticker
        
        Returns:
            Analysis results based on user tier
        """
        if not self.enabled:
            raise RuntimeError("Long context analysis not available - OpenAI client not configured")
        
        # Check feature access
        access = await tier_manager.check_feature_access(
            Feature.LONG_CONTEXT_ANALYSIS,
            user_id,
            check_usage=True
        )
        
        if not access["allowed"]:
            raise PermissionError(access["message"])
        
        tier = access["tier"]
        
        logger.info(
            f"Analyzing {document_type} for user {user_id} (tier: {tier.value}, "
            f"usage: {access['current_usage']}/{access.get('remaining', 'unlimited')})"
        )
        
        try:
            # Route to appropriate analysis based on tier
            if tier == UserTier.FREE:
                result = await self._analyze_free_tier(text, document_type, ticker)
            elif tier == UserTier.PRO:
                # TODO: Implement Pro tier analysis
                result = await self._analyze_pro_tier(text, document_type, ticker)
            else:  # ENTERPRISE
                # TODO: Implement Enterprise tier analysis
                result = await self._analyze_enterprise_tier(text, document_type, ticker)
            
            # Increment usage
            await tier_manager.increment_usage(Feature.LONG_CONTEXT_ANALYSIS, user_id)
            
            # Add metadata
            result.update({
                'tier': tier.value,
                'document_type': document_type,
                'ticker': ticker,
                'analyzed_at': datetime.now().isoformat(),
                'text_length': len(text)
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing document: {e}", exc_info=True)
            raise
    
    async def fetch_and_analyze(
        self,
        ticker: str,
        user_id: str,
        include_earnings_call: bool = True
    ) -> Dict:
        """
        Auto-fetch financial documents and analyze them
        
        Args:
            ticker: Stock ticker (e.g., "AAPL")
            user_id: User ID
            include_earnings_call: Whether to include earnings call alongside 10-K
        
        Returns:
            Combined analysis of fetched documents
        """
        if not self.enabled:
            raise RuntimeError("Long context analysis not available - OpenAI client not configured")
        
        logger.info(f"Auto-fetching and analyzing documents for {ticker}")
        
        try:
            from ..retrievers.exa_client import exa_client
        except ImportError:
            from retrievers.exa_client import exa_client
        
        try:
            # Check feature access
            access = await tier_manager.check_feature_access(
                Feature.LONG_CONTEXT_ANALYSIS,
                user_id,
                check_usage=True
            )
            
            if not access["allowed"]:
                raise PermissionError(access["message"])
            
            analyses = {}
            
            # Fetch 10-K
            logger.info(f"Fetching 10-K for {ticker}...")
            ten_k_doc = await exa_client.search_financial_documents(ticker, "10-K")
            
            if ten_k_doc and ten_k_doc.get("text"):
                logger.info(f"Found 10-K for {ticker} ({len(ten_k_doc['text'])} characters)")
                analyses["10-K"] = await self.analyze_document(
                    text=ten_k_doc["text"],
                    document_type="10-K",
                    user_id=user_id,
                    ticker=ticker
                )
                analyses["10-K"]["source"] = ten_k_doc
            else:
                logger.warning(f"No 10-K found for {ticker}")
                analyses["10-K"] = {"error": "10-K not found", "source": "exa"}
            
            # Fetch earnings call if requested
            if include_earnings_call:
                logger.info(f"Fetching earnings call for {ticker}...")
                earnings_doc = await exa_client.search_financial_documents(ticker, "earnings_call")
                
                if earnings_doc and earnings_doc.get("text"):
                    logger.info(f"Found earnings call for {ticker} ({len(earnings_doc['text'])} characters)")
                    analyses["earnings_call"] = await self.analyze_document(
                        text=earnings_doc["text"],
                        document_type="earnings_call",
                        user_id=user_id,
                        ticker=ticker
                    )
                    analyses["earnings_call"]["source"] = earnings_doc
                else:
                    logger.warning(f"No earnings call found for {ticker}")
                    analyses["earnings_call"] = {"error": "Earnings call not found", "source": "exa"}
            
            # Increment usage for each analysis
            for _ in analyses:
                await tier_manager.increment_usage(Feature.LONG_CONTEXT_ANALYSIS, user_id)
            
            return {
                "ticker": ticker,
                "analyses": analyses,
                "analyzed_at": datetime.now().isoformat(),
                "total_documents": len([a for a in analyses.values() if "error" not in a])
            }
        
        except Exception as e:
            logger.error(f"Error in fetch_and_analyze: {e}", exc_info=True)
            raise
    
    async def _analyze_free_tier(
        self,
        text: str,
        document_type: str,
        ticker: Optional[str] = None
    ) -> Dict:
        """
        FREE tier: Basic summary + key metrics extraction
        
        Args:
            text: Document text
            document_type: Document type
            ticker: Optional ticker
        
        Returns:
            Basic analysis
        """
        logger.info(f"Running FREE tier analysis for {document_type}")
        
        # Truncate text if too long (keep first 100K chars for free tier)
        max_chars = 100000
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} chars for FREE tier")
        
        prompt = f"""Analyze this {document_type} and provide a concise summary.

Document:
{text}

Provide:
1. Executive Summary (3-4 sentences)
2. Key Financial Metrics (revenue, profit, margins if available)
3. Main Takeaways (3 bullet points)

Format as JSON:
{{
  "summary": "...",
  "metrics": {{"revenue": "...", "profit": "...", "margin": "..."}},
  "takeaways": ["...", "...", "..."]
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response (OpenAI format)
            content = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if not valid JSON
                analysis = {
                    "summary": content[:500],
                    "metrics": {},
                    "takeaways": []
                }
            
            # Track cost
            await cost_tracker.log_cost(
                user_id="system",
                service="openai-longctx",
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                metadata={"tier": "free", "document_type": document_type}
            )
            
            return {
                "analysis_type": "basic",
                "summary": analysis.get("summary", ""),
                "metrics": analysis.get("metrics", {}),
                "takeaways": analysis.get("takeaways", [])
            }
        
        except Exception as e:
            logger.error(f"Error in FREE tier analysis: {e}")
            raise
    
    async def _analyze_pro_tier(
        self,
        text: str,
        document_type: str,
        ticker: Optional[str] = None
    ) -> Dict:
        """
        PRO tier: Summary + risks + opportunities + AI insights
        
        TODO: Implement Pro tier analysis
        - Deeper analysis of risks and opportunities
        - Forward-looking insights
        - Competitive context
        """
        logger.info(f"Running PRO tier analysis for {document_type}")
        
        # For now, use free tier analysis
        # TODO: Implement full Pro tier analysis
        basic_analysis = await self._analyze_free_tier(text, document_type, ticker)
        
        # Placeholder for Pro tier features
        basic_analysis.update({
            "analysis_type": "pro",
            "risks": [],  # TODO: Extract risks
            "opportunities": [],  # TODO: Extract opportunities
            "ai_insights": ""  # TODO: Generate AI insights
        })
        
        return basic_analysis
    
    async def _analyze_enterprise_tier(
        self,
        text: str,
        document_type: str,
        ticker: Optional[str] = None
    ) -> Dict:
        """
        ENTERPRISE tier: Full analysis with competitive positioning
        
        TODO: Implement Enterprise tier analysis
        - Complete financial analysis
        - Competitive positioning
        - Strategic recommendations
        - Industry comparison
        """
        logger.info(f"Running ENTERPRISE tier analysis for {document_type}")
        
        # For now, use pro tier analysis
        # TODO: Implement full Enterprise tier analysis
        pro_analysis = await self._analyze_pro_tier(text, document_type, ticker)
        
        # Placeholder for Enterprise tier features
        pro_analysis.update({
            "analysis_type": "enterprise",
            "competitive_position": {},  # TODO: Analyze competitive position
            "strategic_recommendations": [],  # TODO: Generate recommendations
            "industry_comparison": {}  # TODO: Compare to industry peers
        })
        
        return pro_analysis


# Global instance
long_context_analyst = LongContextAnalyst()
