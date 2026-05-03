"""
Risk Assessment Agent
Evaluates investment risks, provides risk mitigation strategies, and risk-reward analysis.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from agents.shared_prompts import build_prompt
from workflows.state import State


def risk_assessment_agent(state: State) -> State:
    """Risk Assessment Agent - Evaluates investment risks"""
    try:
        llm = get_llm()

        financial_data = state.get("financial_data") or {}
        if not financial_data:
            state["risk_assessment"] = "Risk assessment unavailable: financial data not present."
            return state

        stock_data = financial_data.get("raw_data", {}) or {}

        # Calculate risk metrics
        risk_metrics = {}
        for symbol, data in stock_data.items():
            if "error" not in data:
                risk_metrics[symbol] = {
                    "volatility": data["technical_indicators"].get("volatility", 0),
                    "beta": data["info"].get("beta", 1.0),
                    "market_cap": data["info"].get("market_cap", 0),
                    "sector": data["info"].get("sector", "Unknown"),
                    "pe_ratio": data["info"].get("pe_ratio", None),
                }

        prompt = build_prompt(
            role=f"Risk Management Specialist (risk tolerance: {state.get('risk_tolerance', 'moderate')})",
            question=state.get("question", ""),
            symbols=state.get("symbols") or [],
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(risk_metrics, default=str)[:3000],
            analysis_points=[
                "Market Risk - Overall market exposure and volatility",
                "Company-Specific Risk - Individual company risks and concerns",
                "Sector Risk - Industry and sector-specific risks",
                "Liquidity Risk - Trading volume and market depth concerns",
                "Concentration Risk - Portfolio concentration and diversification",
                "Regulatory Risk - Regulatory and compliance concerns",
                "Risk Mitigation - Strategies to reduce and manage risks",
                "Risk-Reward Analysis - Expected returns vs. risk levels",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["risk_assessment"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("risk_assessment_agent error: %s", exc, exc_info=True)
        state["error"] = f"Risk assessment error: {exc}"
        state["risk_assessment"] = f"Analysis unavailable: {exc}"

    return state
