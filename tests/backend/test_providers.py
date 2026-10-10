"""AI Provider Architecture and Fallback Tests."""

import sys
import pytest
sys.path.insert(0, r"D:\ECHO")

from ai.providers.factory import provider_registry
from ai.providers.base import ProviderStatus
from ai.providers.llm import LLMGenerationRequest


@pytest.mark.asyncio
async def test_all_providers_health_reporting():
    """Verify all 6 providers report readiness without requiring live paid API keys."""
    health_reports = provider_registry.get_all_health()
    assert len(health_reports) == 6
    
    for h in health_reports:
        # All foundation mock providers should report MOCK_MODE or CONFIGURED/UNCONFIGURED safely
        assert h.status in [ProviderStatus.MOCK_MODE, ProviderStatus.CONFIGURED, ProviderStatus.UNCONFIGURED]


@pytest.mark.asyncio
async def test_mock_llm_grounded_generation():
    """Verify Mock LLM grounds response in evidence context or refuses unevidenced claims."""
    llm = provider_registry.llm_provider
    
    # Request with evidence
    req_with_evidence = LLMGenerationRequest(
        prompt="Tell me about the degree",
        evidence_context=["Conferred Degree of Master of Arts on 22 June 1968"]
    )
    resp = await llm.generate(req_with_evidence)
    assert resp.is_grounded is True
    assert "Based on preserved archival records" in resp.content
    assert "1968" in resp.content

    # Request without evidence
    req_empty = LLMGenerationRequest(prompt="What was your secret dream?")
    resp_empty = await llm.generate(req_empty)
    assert resp_empty.is_grounded is False
    assert "No preserved archival evidence" in resp_empty.content
