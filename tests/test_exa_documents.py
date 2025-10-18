"""
Test Exa.ai financial document fetching and long-context analysis
Tests the auto-fetch-and-analyze workflow
"""
import pytest
import sys
from pathlib import Path

# Add apps/ai to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "ai"))

from utils.config import settings
from retrievers.exa_client import exa_client
from agents.longctx import long_context_analyst


@pytest.mark.unit
class TestExaDocumentFetcher:
    """Test Exa.ai document fetching"""
    
    @pytest.mark.asyncio
    async def test_search_financial_documents_mock(self):
        """Test searching for financial documents with mock data"""
        # Enable mock mode
        settings.use_mock_exa = True
        
        # Search for 10-K
        doc = await exa_client.search_financial_documents("AAPL", "10-K")
        
        assert doc is not None
        assert "title" in doc
        assert "text" in doc
        assert "url" in doc
        assert "published" in doc
        assert len(doc["text"]) > 0
        assert "AAPL" in doc["title"] or "10-K" in doc["title"]
        assert doc["source"] == "mock"
        
        print(f"✅ 10-K mock document: {len(doc['text'])} characters")
    
    @pytest.mark.asyncio
    async def test_search_earnings_call_mock(self):
        """Test searching for earnings call with mock data"""
        settings.use_mock_exa = True
        
        doc = await exa_client.search_financial_documents("TSLA", "earnings_call")
        
        assert doc is not None
        assert "text" in doc
        assert len(doc["text"]) > 0
        assert "TSLA" in doc["title"] or "earnings" in doc["title"].lower()
        assert "earnings call" in doc["text"].lower() or "revenue" in doc["text"].lower()
        
        print(f"✅ Earnings call mock document: {len(doc['text'])} characters")
    
    @pytest.mark.asyncio
    async def test_search_annual_report_mock(self):
        """Test searching for annual report with mock data"""
        settings.use_mock_exa = True
        
        doc = await exa_client.search_financial_documents("GOOGL", "annual_report")
        
        assert doc is not None
        assert "text" in doc
        assert len(doc["text"]) > 0
        
        print(f"✅ Annual report mock document: {len(doc['text'])} characters")
    
    @pytest.mark.asyncio
    async def test_search_document_not_found(self):
        """Test when document is not found"""
        settings.use_mock_exa = True
        
        # Even with mock, we should get a document
        doc = await exa_client.search_financial_documents("UNKNOWNTICKER", "10-K")
        
        # Mock should always return something
        assert doc is not None
        assert "text" in doc


@pytest.mark.unit
class TestLongContextAutoFetch:
    """Test long-context analysis with auto-fetching"""
    
    @pytest.mark.asyncio
    async def test_fetch_and_analyze_mock(self, test_user_id):
        """Test auto-fetching and analyzing documents"""
        settings.use_mock_exa = True
        
        if not long_context_analyst.enabled:
            pytest.skip("Claude client not available - test requires Claude API access")
        
        result = await long_context_analyst.fetch_and_analyze(
            ticker="AAPL",
            user_id=test_user_id,
            include_earnings_call=True
        )
        
        assert result is not None
        assert result["ticker"] == "AAPL"
        assert "analyses" in result
        assert "analyzed_at" in result
        assert "total_documents" in result
        
        # Should have analyses for 10-K and earnings call
        assert len(result["analyses"]) >= 1
        
        print(f"✅ Fetch and analyze: {result['total_documents']} documents analyzed")
        print(f"   Analyses keys: {list(result['analyses'].keys())}")
    
    @pytest.mark.asyncio
    async def test_fetch_and_analyze_single_document(self, test_user_id):
        """Test fetching only 10-K (no earnings call)"""
        settings.use_mock_exa = True
        
        if not long_context_analyst.enabled:
            pytest.skip("Claude client not available - test requires Claude API access")
        
        result = await long_context_analyst.fetch_and_analyze(
            ticker="MSFT",
            user_id=test_user_id,
            include_earnings_call=False
        )
        
        assert result is not None
        assert result["ticker"] == "MSFT"
        assert "analyses" in result
        
        # Should only have 10-K analysis
        analyses = [a for a in result["analyses"].values() if "error" not in a]
        assert len(analyses) >= 1
        
        print(f"✅ Single document analysis: {len(analyses)} document(s)")
    
    @pytest.mark.asyncio
    async def test_fetch_and_analyze_structure(self, test_user_id):
        """Test that analysis has correct structure"""
        settings.use_mock_exa = True
        
        if not long_context_analyst.enabled:
            pytest.skip("Claude client not available - test requires Claude API access")
        
        result = await long_context_analyst.fetch_and_analyze(
            ticker="NVDA",
            user_id=test_user_id,
            include_earnings_call=True
        )
        
        assert result is not None
        
        # Check structure of each analysis
        for doc_type, analysis in result["analyses"].items():
            if "error" not in analysis:
                # Should have analysis results
                assert "summary" in analysis or "analysis_type" in analysis
                print(f"✅ {doc_type} analysis structure valid")
    
    @pytest.mark.asyncio
    async def test_manual_analyze_with_text(self, test_user_id):
        """Test manual document analysis (existing functionality)"""
        if not long_context_analyst.enabled:
            pytest.skip("Claude client not available - test requires Claude API access")
        
        test_text = """
        SEC FORM 10-K: Test Company Annual Report
        
        BUSINESS OVERVIEW:
        Test Company operates in technology sector.
        
        FINANCIAL HIGHLIGHTS:
        - Revenue: $100 million
        - Net Income: $20 million
        - Operating Margin: 20%
        
        RISKS:
        - Market competition
        - Regulatory changes
        """
        
        result = await long_context_analyst.analyze_document(
            text=test_text,
            document_type="10-K",
            user_id=test_user_id,
            ticker="TEST"
        )
        
        assert result is not None
        assert "summary" in result or "analysis_type" in result
        assert result.get("document_type") == "10-K"
        assert result.get("ticker") == "TEST"
        
        print(f"✅ Manual document analysis works")


@pytest.mark.integration
class TestExaDocumentAPI:
    """Test the FastAPI endpoints"""
    
    @pytest.mark.asyncio
    async def test_auto_fetch_endpoint_simulation(self, test_user_id):
        """Simulate calling the auto-fetch endpoint"""
        settings.use_mock_exa = True
        
        if not long_context_analyst.enabled:
            pytest.skip("Claude client not available")
        
        # Simulate what the endpoint does
        result = await long_context_analyst.fetch_and_analyze(
            ticker="AAPL",
            user_id=test_user_id,
            include_earnings_call=True
        )
        
        assert result is not None
        assert "ticker" in result
        assert "analyses" in result
        
        print(f"✅ Auto-fetch endpoint simulation passed")
        print(f"   Response structure: {list(result.keys())}")


@pytest.mark.unit
class TestDocumentContent:
    """Test that documents contain expected content"""
    
    def test_mock_10k_content(self):
        """Test 10-K mock document has financial info"""
        doc_text = exa_client._get_mock_document("AAPL", "10-K")
        
        assert "10-K" in doc_text
        assert "Revenue" in doc_text or "revenue" in doc_text
        assert "billion" in doc_text
        assert len(doc_text) > 500  # Substantial document
        
        print(f"✅ 10-K mock document has realistic structure ({len(doc_text)} chars)")
    
    def test_mock_earnings_call_content(self):
        """Test earnings call mock document has expected structure"""
        doc_text = exa_client._get_mock_document("TSLA", "earnings_call")
        
        assert "earnings" in doc_text.lower() or "Q4" in doc_text or "revenue" in doc_text.lower()
        assert len(doc_text) > 500
        
        print(f"✅ Earnings call mock document has realistic structure ({len(doc_text)} chars)")
    
    def test_mock_annual_report_content(self):
        """Test annual report mock document"""
        doc_text = exa_client._get_mock_document("GOOGL", "annual_report")
        
        assert len(doc_text) > 500
        
        print(f"✅ Annual report mock document has content ({len(doc_text)} chars)")


@pytest.mark.unit
class TestDocumentTypes:
    """Test different document types"""
    
    @pytest.mark.asyncio
    async def test_all_document_types(self):
        """Test fetching all supported document types"""
        settings.use_mock_exa = True
        
        doc_types = ["10-K", "earnings_call", "annual_report"]
        
        for doc_type in doc_types:
            doc = await exa_client.search_financial_documents("TEST", doc_type)
            assert doc is not None
            assert "text" in doc
            assert len(doc["text"]) > 0
            print(f"✅ {doc_type} fetch successful")
    
    @pytest.mark.asyncio
    async def test_unknown_document_type(self):
        """Test unknown document type falls back gracefully"""
        settings.use_mock_exa = True
        
        doc = await exa_client.search_financial_documents("TEST", "unknown_type")
        
        # Should still return something with mock
        assert doc is not None
        assert "text" in doc
        
        print(f"✅ Unknown document type handled gracefully")
