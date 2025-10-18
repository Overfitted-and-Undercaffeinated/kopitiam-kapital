warning: in the working copy of 'apps/ai/agents/longctx.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/apps/ai/agents/longctx.py b/apps/ai/agents/longctx.py[m
[1mindex a6fbff1..15e792f 100644[m
[1m--- a/apps/ai/agents/longctx.py[m
[1m+++ b/apps/ai/agents/longctx.py[m
[36m@@ -1,16 +1,265 @@[m
[31m-"""Long Context Analyst - Analyzes lengthy documents"""[m
[32m+[m[32m"""[m
[32m+[m[32mLong Context Analyst[m
[32m+[m[32mAnalyzes lengthy financial documents using Claude's 200K context window[m
[32m+[m[32m"""[m
[32m+[m[32mimport logging[m
[32m+[m[32mfrom typing import Dict, Optional[m
[32m+[m[32mimport json[m
[32m+[m[32mfrom datetime import datetime[m
[32m+[m
[32m+[m[32m# Flexible imports[m
[32m+[m[32mtry:[m
[32m+[m[32m    from ..utils.tier_manager import tier_manager, Feature, UserTier[m
[32m+[m[32m    from ..utils.clients import get_anthropic_client[m
[32m+[m[32m    from ..utils.cost_tracker import cost_tracker[m
[32m+[m[32mexcept ImportError:[m
[32m+[m[32m    from utils.tier_manager import tier_manager, Feature, UserTier[m
[32m+[m[32m    from utils.clients import get_anthropic_client[m
[32m+[m[32m    from utils.cost_tracker import cost_tracker[m
[32m+[m
[32m+[m[32mlogger = logging.getLogger(__name__)[m
[32m+[m
 [m
 class LongContextAnalyst:[m
[31m-    """Analyzes long-form financial documents like 10-Ks, annual reports"""[m
[32m+[m[32m    """[m
[32m+[m[32m    Analyzes long-form financial documents like 10-Ks, annual reports, earnings calls[m
[32m+[m[41m    [m
[32m+[m[32m    Features by tier:[m
[32m+[m[32m    - FREE: Basic summary + key metrics (1 per month)[m
[32m+[m[32m    - PRO: Summary + risks + opportunities + AI insights (10 per month)[m
[32m+[m[32m    - ENTERPRISE: Full analysis with competitive positioning (unlimited)[m
[32m+[m[41m    [m
[32m+[m[32m    Uses Anthropic Claude for 200K token context window[m
[32m+[m[32m    """[m
     [m
     def __init__(self):[m
         self.name = "longctx"[m
[32m+[m[32m        try:[m
[32m+[m[32m            self.client = get_anthropic_client()[m
[32m+[m[32m            # Using latest Claude 3.5 Sonnet - check Anthropic docs for current version[m
[32m+[m[32m            # Alternative: "claude-3-opus-20240229" for even longer context[m
[32m+[m[32m            self.model = "claude-3-5-sonnet-20241022"  # Stable version (2024-10-22)[m
[32m+[m[32m            self.enabled = True[m
[32m+[m[32m        except Exception as e:[m
[32m+[m[32m            logger.warning(f"Anthropic client not available: {e}")[m
[32m+[m[32m            self.client = None[m
[32m+[m[32m            self.enabled = False[m
[32m+[m[41m        [m
[32m+[m[32m        logger.info(f"Initialized Long Context Analyst (enabled: {self.enabled})")[m
[32m+[m[41m    [m
[32m+[m[32m    async def analyze_document([m
[32m+[m[32m        self,[m
[32m+[m[32m        text: str,[m
[32m+[m[32m        document_type: str,[m
[32m+[m[32m        user_id: str,[m
[32m+[m[32m        ticker: Optional[str] = None[m
[32m+[m[32m    ) -> Dict:[m
[32m+[m[32m        """[m
[32m+[m[32m        Analyze a long-form financial document[m
[32m+[m[41m        [m
[32m+[m[32m        Args:[m
[32m+[m[32m            text: Document text[m
[32m+[m[32m            document_type: Type of document (e.g., "10-K", "annual_report", "earnings_call")[m
[32m+[m[32m            user_id: User ID[m
[32m+[m[32m            ticker: Optional stock ticker[m
[32m+[m[41m        [m
[32m+[m[32m        Returns:[m
[32m+[m[32m            Analysis results based on user tier[m
[32m+[m[32m        """[m
[32m+[m[32m        if not self.enabled:[m
[32m+[m[32m            raise RuntimeError("Long context analysis not available - Anthropic client not configured")[m
[32m+[m[41m        [m
[32m+[m[32m        # Check feature access[m
[32m+[m[32m        access = await tier_manager.check_feature_access([m
[32m+[m[32m            Feature.LONG_CONTEXT_ANALYSIS,[m
[32m+[m[32m            user_id,[m
[32m+[m[32m            check_usage=True[m
[32m+[m[32m        )[m
[32m+[m[41m        [m
[32m+[m[32m        if not access["allowed"]:[m
[32m+[m[32m            raise PermissionError(access["message"])[m
[32m+[m[41m        [m
[32m+[m[32m        tier = access["tier"][m
[32m+[m[41m        [m
[32m+[m[32m        logger.info([m
[32m+[m[32m            f"Analyzing {document_type} for user {user_id} (tier: {tier.value}, "[m
[32m+[m[32m            f"usage: {access['current_usage']}/{access.get('remaining', 'unlimited')})"[m
[32m+[m[32m        )[m
[32m+[m[41m        [m
[32m+[m[32m        try:[m
[32m+[m[32m            # Route to appropriate analysis based on tier[m
[32m+[m[32m            if tier == UserTier.FREE:[m
[32m+[m[32m                result = await self._analyze_free_tier(text, document_type, ticker)[m
[32m+[m[32m            elif tier == UserTier.PRO:[m
[32m+[m[32m                # TODO: Implement Pro tier analysis[m
[32m+[m[32m                result = await self._analyze_pro_tier(text, document_type, ticker)[m
[32m+[m[32m            else:  # ENTERPRISE[m
[32m+[m[32m                # TODO: Implement Enterprise tier analysis[m
[32m+[m[32m                result = await self._analyze_enterprise_tier(text, document_type, ticker)[m
[32m+[m[41m            [m
[32m+[m[32m            # Increment usage[m
[32m+[m[32m            await tier_manager.increment_usage(Feature.LONG_CONTEXT_ANALYSIS, user_id)[m
[32m+[m[41m            [m
[32m+[m[32m            # Add metadata[m
[32m+[m[32m            result.update({[m
[32m+[m[32m                'tier': tier.value,[m
[32m+[m[32m                'document_type': document_type,[m
[32m+[m[32m                'ticker': ticker,[m
[32m+[m[32m                'analyzed_at': datetime.now().isoformat(),[m
[32m+[m[32m                'text_length': len(text)[m
[32m+[m[32m            })[m
[32m+[m[41m            [m
[32m+[m[32m            return result[m
[32m+[m[41m        [m
[32m+[m[32m        except Exception as e:[m
[32m+[m[32m            logger.error(f"Error analyzing document: {e}", exc_info=True)[m
[32m+[m[32m            raise[m
     [m
[31m-    async def analyze_filing(self, ticker: str, filing_type: str):[m
[31m-        """Analyze financial filing document"""[m
[31m-        # TODO: Implement long-context analysis[m
[31m-        # - Fetch filing from SEC or other source[m
[31m-        # - Process with long-context model (Claude)[m
[31m-        # - Extract key insights[m
[31m-        pass[m
[32m+[m[32m    async def _analyze_free_tier([m
[32m+[m[32m        self,[m
[32m+[m[32m        text: str,[m
[32m+[m[32m        document_type: str,[m
[32m+[m[32m        ticker: Optional[str] = None[m
[32m+[m[32m    ) -> Dict:[m
[32m+[m[32m        """[m
[32m+[m[32m        FREE tier: Basic summary + key metrics extraction[m
[32m+[m[41m        [m
[32m+[m[32m        Args:[m
[32m+[m[32m            text: Document text[m
[32m+[m[32m            document_type: Document type[m
[32m+[m[32m            ticker: Optional ticker[m
[32m+[m[41m        [m
[32m+[m[32m        Returns:[m
[32m+[m[32m            Basic analysis[m
[32m+[m[32m        """[m
[32m+[m[32m        logger.info(f"Running FREE tier analysis for {document_type}")[m
[32m+[m[41m        [m
[32m+[m[32m        # Truncate text if too long (keep first 100K chars for free tier)[m
[32m+[m[32m        max_chars = 100000[m
[32m+[m[32m        if len(text) > max_chars:[m
[32m+[m[32m            text = text[:max_chars][m
[32m+[m[32m            logger.warning(f"Text truncated to {max_chars} chars for FREE tier")[m
[32m+[m[41m        [m
[32m+[m[32m        prompt = f"""Analyze this {document_type} and provide a concise summary.[m
[32m+[m
[32m+[m[32mDocument:[m
[32m+[m[32m{text}[m
[32m+[m
[32m+[m[32mProvide:[m
[32m+