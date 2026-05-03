"""
Technical Analysis Agent
Provides technical analysis, trading signals, and chart pattern analysis.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from agents.shared_prompts import build_prompt
from workflows.state import State


def technical_analysis_agent(state: State) -> State:
    """Technical Analysis Agent - Provides technical analysis and trading signals"""
    try:
        llm = get_llm()

        financial_data = state.get("financial_data") or {}
        if not financial_data:
            state["technical_analysis"] = "Technical analysis unavailable: financial data not present."
            return state

        stock_data = financial_data.get("raw_data", {}) or {}

        # Extract technical indicators
        technical_summary = {}
        for symbol, data in stock_data.items():
            if "error" not in data and "technical_indicators" in data:
                technical_summary[symbol] = data["technical_indicators"]

        prompt = build_prompt(
            role="Technical Analysis Specialist",
            question=state.get("question", ""),
            symbols=state.get("symbols") or [],
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(technical_summary, default=str)[:3000],
            analysis_points=[
                "Chart Patterns - Identify key chart patterns and formations",
                "Support & Resistance - Key price levels and their significance",
                "Moving Averages - Trend analysis using moving averages",
                "Momentum Indicators - RSI, MACD, and other momentum signals",
                "Volume Analysis - Volume patterns and their implications",
                "Trading Signals - Buy/sell/hold recommendations with entry/exit points",
                "Risk Management - Stop-loss levels and position sizing suggestions",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["technical_analysis"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("technical_analysis_agent error: %s", exc, exc_info=True)
        state["error"] = f"Technical analysis error: {exc}"
        state["technical_analysis"] = f"Analysis unavailable: {exc}"

    return state
