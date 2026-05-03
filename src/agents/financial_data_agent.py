"""
Financial Data Agent
Analyzes stock data, financial metrics, and provides comprehensive financial analysis.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from tools.financial_tools import get_stock_data
from agents.shared_prompts import build_prompt
from workflows.state import State


def financial_data_agent(state: State) -> State:
    """Financial Data Agent - Analyzes stock data and financial metrics"""
    try:
        llm = get_llm()

        symbols = state.get("symbols") or []
        # Get comprehensive stock data
        stock_data = get_stock_data.invoke({"symbols": symbols, "timeframe": state.get("timeframe", "1mo")})

        # Prepare data summary for LLM
        data_summary = {}
        for symbol, data in stock_data.items():
            if "error" not in data:
                data_summary[symbol] = {
                    "basic_info": data["info"],
                    "price_data": data["price_data"],
                    "technical_indicators": data["technical_indicators"],
                }

        prompt = build_prompt(
            role="Financial Data Analyst",
            question=state.get("question", ""),
            symbols=symbols,
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(data_summary, default=str)[:3000],
            analysis_points=[
                "Price Analysis - Current prices, trends, and key levels",
                "Financial Metrics - P/E ratios, market cap, and other key ratios",
                "Technical Indicators - Moving averages, RSI, MACD, and volatility",
                "Performance Comparison - How stocks compare to each other and market",
                "Investment Metrics - Risk-return profiles and investment attractiveness",
                "Sector Analysis - Industry positioning and competitive landscape",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["financial_data"] = {
            "analysis": response.content if hasattr(response, "content") else str(response),
            "raw_data": stock_data,
        }

    except Exception as exc:
        logging.getLogger(__name__).error("financial_data_agent error: %s", exc, exc_info=True)
        state["error"] = f"Financial data analysis error: {exc}"
        state["financial_data"] = {"analysis": f"Analysis unavailable: {exc}", "error": str(exc)}

    return state
