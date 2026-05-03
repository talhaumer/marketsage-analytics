import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from workflows.financial_analysis_workflow import create_financial_analysis_workflow
from workflows.state import State


def _make_state(**kwargs) -> dict:
    defaults = dict(
        question="Test question",
        analysis_type="comprehensive",
        symbols=["AAPL"],
        timeframe="1mo",
        risk_tolerance="moderate",
        shared_market_data=None,
        market_research=None,
        financial_data=None,
        technical_analysis=None,
        risk_assessment=None,
        sentiment_analysis=None,
        portfolio_analysis=None,
        sector_analysis=None,
        crypto_analysis=None,
        final_analysis=None,
        individual_analyses=None,
        processing_time=None,
        agents_used=[],
        detection_info=None,
        error=None,
        timestamp=None,
    )
    defaults.update(kwargs)
    return defaults


def test_workflow_compiles():
    wf = create_financial_analysis_workflow()
    assert wf is not None


def test_workflow_has_all_nodes():
    wf = create_financial_analysis_workflow()
    graph = wf.get_graph()
    node_names = set(graph.nodes.keys())
    expected = {
        "data_prefetch", "market_research", "financial_data",
        "technical_analysis", "risk_assessment", "sentiment_analysis",
        "portfolio_analysis", "sector_analysis", "crypto_analysis",
        "final_synthesis",
    }
    assert expected.issubset(node_names), f"Missing nodes: {expected - node_names}"


def test_financial_data_before_risk_and_technical():
    wf = create_financial_analysis_workflow()
    graph = wf.get_graph()
    edges = {(e.source, e.target) for e in graph.edges}
    assert ("financial_data", "risk_assessment") in edges
    assert ("financial_data", "technical_analysis") in edges
    assert ("market_research", "risk_assessment") not in edges
    assert ("market_research", "technical_analysis") not in edges


def test_crypto_only_input_routes_to_crypto_agent():
    from workflows.smart_router import SmartAnalysisRouter
    router = SmartAnalysisRouter()
    state = _make_state(symbols=["BTC", "ETH"], analysis_type="crypto")
    route = router.route_analysis(state)
    assert route.get("run_crypto_agent") is True
    assert route.get("run_sector_agent") is False


def test_stock_only_input_skips_crypto_agent():
    from workflows.smart_router import SmartAnalysisRouter
    router = SmartAnalysisRouter()
    state = _make_state(symbols=["AAPL", "MSFT"], analysis_type="quick")
    route = router.route_analysis(state)
    assert route.get("run_crypto_agent") is False
    assert route.get("run_financial_agent") is True
