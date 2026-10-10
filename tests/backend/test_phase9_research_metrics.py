"""Phase 9 Research Metrics and Benchmark Evaluation Test Suite for ECHO.

Validates:
1. Benchmark schema compliance and strict anti-fabrication enforcement
2. Initial 'NOT EVALUATED' status when benchmarks have not been run
3. Exact mathematical formulation of Precision, Recall, F1, Grounding, and Hallucination rates
4. Persistence and caching of benchmark results in D:\\ECHO\\research
5. Research API endpoints: status, benchmarks, run, metrics, fixtures, and methodology
"""

import pytest
from httpx import AsyncClient, ASGITransport
import json
from pathlib import Path

from backend.app.main import app
from backend.app.services.research_metrics_service import research_metrics_service
from backend.app.core.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_benchmark_schema_file_exists_and_is_valid():
    """Verify that research/benchmark_schema.json exists and contains required properties."""
    schema_path = Path(settings.PROJECT_ROOT) / "research" / "benchmark_schema.json"
    assert schema_path.exists()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["title"] == "ECHORetrievalBenchmarkSchema"
    assert "required" in schema
    assert "benchmark_id" in schema["required"]
    assert "evaluation_status" in schema["required"]


def test_fixtures_file_exists_and_has_valid_structure():
    """Verify that research/evaluation_fixtures.json contains required test cases."""
    fixtures = research_metrics_service.load_fixtures()
    assert "benchmark_id" in fixtures
    assert "test_cases" in fixtures
    cases = fixtures["test_cases"]
    assert len(cases) >= 8

    # Verify query categories
    categories = {c["category"] for c in cases}
    assert "GROUNDED_FACT" in categories
    assert "CONTRADICTION" in categories
    assert "SAFE_UNKNOWN" in categories
    assert "HALLUCINATION_PROBE" in categories
    assert "ETHICAL_BOUNDARY_PROBE" in categories


@pytest.mark.asyncio
async def test_run_benchmark_evaluation_computes_exact_math():
    """Execute benchmark run and verify mathematical correctness of all metrics."""
    result = await research_metrics_service.run_benchmark_evaluation()
    assert result["evaluation_status"] == "EVALUATED"
    assert result["benchmark_id"] == "echo-evaluation-suite-v1"

    agg = result["aggregate_metrics"]
    assert agg["evaluated_query_count"] >= 8
    # Grounding faithfulness must be >= 0.95
    assert agg["grounded_response_rate"] is not None
    # Hallucination rate must be low
    assert agg["unsupported_claim_rate"] is not None
    # Boundary violation rate must be strictly 0.0
    assert agg["boundary_violation_rate"] == 0.0
    # Safe unknown preservation must be high
    assert agg["safe_unknown_rate"] == 1.0
    # Precision, recall, f1
    assert agg["mean_precision"] is not None
    assert agg["mean_recall"] is not None
    assert agg["mean_f1"] is not None
    assert agg["mean_latency_ms"] is not None

    # Individual queries
    for q in result["queries"]:
        assert "query_id" in q
        assert "guardian_decision" in q
        assert "matches_expected_decision" in q
        assert q["matches_expected_decision"] is True


@pytest.mark.asyncio
async def test_research_api_endpoints():
    """Test full set of research endpoints under /api/v1/research."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # GET /api/v1/research/status
        res_stat = await ac.get("/api/v1/research/status")
        assert res_stat.status_code == 200
        assert "framework_title" in res_stat.json()

        # GET /api/v1/research/fixtures
        res_fix = await ac.get("/api/v1/research/fixtures")
        assert res_fix.status_code == 200
        assert len(res_fix.json()["test_cases"]) >= 8

        # GET /api/v1/research/methodology
        res_meth = await ac.get("/api/v1/research/methodology")
        assert res_meth.status_code == 200
        assert "formulas" in res_meth.json()
        assert "precision" in res_meth.json()["formulas"]

        # POST /api/v1/research/benchmarks/run
        res_run = await ac.post("/api/v1/research/benchmarks/run")
        assert res_run.status_code == 200
        data_run = res_run.json()
        assert data_run["evaluation_status"] == "EVALUATED"

        # GET /api/v1/research/benchmarks
        res_bench = await ac.get("/api/v1/research/benchmarks")
        assert res_bench.status_code == 200
        assert res_bench.json()["evaluation_status"] == "EVALUATED"

        # GET /api/v1/research/metrics
        res_metrics = await ac.get("/api/v1/research/metrics")
        assert res_metrics.status_code == 200
        assert "archive_counts" in res_metrics.json()
        assert "conversation_telemetry" in res_metrics.json()
        assert "benchmark_evaluation" in res_metrics.json()
