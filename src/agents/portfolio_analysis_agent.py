"""
Portfolio Analysis Agent
Provides portfolio optimization recommendations, allocation strategies, and performance analysis.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from tools.financial_tools import calculate_portfolio_metrics
from agents.shared_prompts import build_prompt
from workflows.state import State


def portfolio_analysis_agent(state: State) -> State:
    """Portfolio Analysis Agent - Provides portfolio optimization recommendations"""
    try:
        llm = get_llm()

        symbols = state.get("symbols") or []
        if not symbols:
            state["portfolio_analysis"] = "Portfolio analysis unavailable: no symbols provided."
            return state

        # Calculate portfolio metrics
        portfolio_metrics = calculate_portfolio_metrics.invoke({"symbols": symbols})

        prompt = build_prompt(
            role=f"Portfolio Optimization Specialist (risk tolerance: {state.get('risk_tolerance', 'moderate')})",
            question=state.get("question", ""),
            symbols=symbols,
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(portfolio_metrics, default=str)[:3000],
            analysis_points=[
                "Portfolio Composition - Current allocation and diversification",
                "Risk-Return Profile - Expected returns and risk levels",
                "Diversification Analysis - Sector and asset diversification",
                "Optimization Recommendations - Suggested allocation changes",
                "Rebalancing Strategy - When and how to rebalance",
                "Alternative Investments - Additional investment opportunities",
                "Tax Efficiency - Tax-optimized investment strategies",
                "Performance Monitoring - Key metrics to track",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["portfolio_analysis"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("portfolio_analysis_agent error: %s", exc, exc_info=True)
        state["error"] = f"Portfolio analysis error: {exc}"
        state["portfolio_analysis"] = f"Analysis unavailable: {exc}"

    return state
