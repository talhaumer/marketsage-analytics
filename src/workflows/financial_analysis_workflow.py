"""
LangGraph Financial Analysis Workflow

Builds the multi-agent analysis graph. The graph fans out from a shared
data-prefetch node, then runs market research, then several agents in
parallel. financial_data gates the agents that depend on its output
(technical_analysis, risk_assessment) before all branches converge on
final_synthesis.
"""

from langgraph.graph import StateGraph, END
from workflows.state import State
from workflows.smart_router import SmartAnalysisRouter
from agents import (
    market_research_agent,
    financial_data_agent,
    technical_analysis_agent,
    risk_assessment_agent,
    sentiment_analysis_agent,
    portfolio_analysis_agent,
    sector_analysis_agent,
    crypto_agent,
    final_synthesis_agent,
)


_router = SmartAnalysisRouter()


def _data_prefetch_node(state: State) -> dict:
    from workflows.data_prefetch import prefetch_market_data
    return prefetch_market_data(state)


def _route_crypto(state: State) -> str:
    """Route between crypto_analysis and skipping straight to final_synthesis."""
    try:
        routing = _router.route_analysis(state)
        return "crypto_analysis" if routing.get("run_crypto_agent", True) else "final_synthesis"
    except Exception:
        return "crypto_analysis"


def create_financial_analysis_workflow() -> StateGraph:
    """Create and compile the LangGraph workflow for financial analysis."""
    workflow = StateGraph(State)

    workflow.add_node("data_prefetch", _data_prefetch_node)
    workflow.add_node("market_research", market_research_agent)
    workflow.add_node("financial_data", financial_data_agent)
    workflow.add_node("technical_analysis", technical_analysis_agent)
    workflow.add_node("risk_assessment", risk_assessment_agent)
    workflow.add_node("sentiment_analysis", sentiment_analysis_agent)
    workflow.add_node("portfolio_analysis", portfolio_analysis_agent)
    workflow.add_node("sector_analysis", sector_analysis_agent)
    workflow.add_node("crypto_analysis", crypto_agent)
    workflow.add_node("final_synthesis", final_synthesis_agent)

    workflow.set_entry_point("data_prefetch")
    workflow.add_edge("data_prefetch", "market_research")

    # market_research fans out to agents that don't need financial_data
    workflow.add_edge("market_research", "financial_data")
    workflow.add_edge("market_research", "sentiment_analysis")
    workflow.add_edge("market_research", "portfolio_analysis")
    workflow.add_edge("market_research", "sector_analysis")
    # crypto_analysis runs only when the symbol set warrants it (smart router)
    workflow.add_conditional_edges(
        "market_research",
        _route_crypto,
        {"crypto_analysis": "crypto_analysis", "final_synthesis": "final_synthesis"},
    )

    # financial_data gates risk and technical
    workflow.add_edge("financial_data", "technical_analysis")
    workflow.add_edge("financial_data", "risk_assessment")

    # All analysis agents converge on final_synthesis
    workflow.add_edge("sentiment_analysis", "final_synthesis")
    workflow.add_edge("portfolio_analysis", "final_synthesis")
    workflow.add_edge("sector_analysis", "final_synthesis")
    workflow.add_edge("crypto_analysis", "final_synthesis")
    workflow.add_edge("technical_analysis", "final_synthesis")
    workflow.add_edge("risk_assessment", "final_synthesis")

    workflow.add_edge("final_synthesis", END)

    return workflow.compile()


# Create the workflow instance
financial_analysis_workflow = create_financial_analysis_workflow()
