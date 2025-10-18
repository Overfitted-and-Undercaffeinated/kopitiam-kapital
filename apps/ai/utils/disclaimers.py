"""
Compliance disclaimers for trading recommendations
"""
from .config import settings

RECOMMENDATION_DISCLAIMER = """
⚠️ IMPORTANT DISCLAIMER

This recommendation is for educational and informational purposes only and does not constitute financial, investment, trading, or other advice. Past performance is not indicative of future results.

Trading and investing involve substantial risk of loss and are not suitable for all investors. You should carefully consider whether trading or investing is appropriate for you in light of your financial condition.

Kopitiam Capital is NOT a licensed financial advisor in Singapore or any other jurisdiction. We do not provide personalized investment advice tailored to your financial situation, investment objectives, or risk tolerance.

Before making any investment decision, you should:
- Consult with a licensed financial advisor
- Conduct your own research and due diligence
- Understand the risks involved
- Only invest capital you can afford to lose

By using this recommendation, you acknowledge that you understand these risks and that Kopitiam Capital bears no responsibility for any trading losses you may incur.

---
"""

ALERT_DISCLAIMER = """
⚠️ This alert is for informational purposes only and does not constitute investment advice. Please conduct your own research before making any trading decisions.
"""

BRIEF_DISCLAIMER = """
⚠️ The information in this brief is for educational purposes only. Not financial advice. Trade at your own risk.
"""

def add_disclaimer_to_recommendation(recommendation: dict) -> dict:
    """
    Add compliance disclaimer to recommendation
    
    Args:
        recommendation: Recommendation dict
    
    Returns:
        Recommendation with disclaimer added
    """
    if settings.enable_disclaimers:
        recommendation['disclaimer'] = RECOMMENDATION_DISCLAIMER
    
    return recommendation

def add_disclaimer_to_brief(brief_text: str) -> str:
    """Add disclaimer to morning/EOD brief text"""
    if settings.enable_disclaimers:
        return brief_text + "\n\n" + BRIEF_DISCLAIMER
    
    return brief_text

def add_disclaimer_to_alert(alert: dict) -> dict:
    """Add disclaimer to alert"""
    if settings.enable_disclaimers:
        alert['disclaimer'] = ALERT_DISCLAIMER
    
    return alert

