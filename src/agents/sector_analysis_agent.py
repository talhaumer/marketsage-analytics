"""
Sector Analysis Agent
Analyzes sector performance, trends, and provides sector allocation recommendations.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from tools.financial_tools import analyze_sector_performance
from agents.shared_prompts import build_prompt
from workflows.state import State


def sector_analysis_agent(state: State) -> State:
    """Sector Analysis Agent - Analyzes sector performance and trends"""
    try:
        llm = get_llm()

        # Get sector analysis
        sector_data = analyze_sector_performance.invoke({})

        prompt = build_prompt(
            role="Sector Analysis Specialist",
            question=state.get("question", ""),
            symbols=state.get("symbols") or [],
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(sector_data, default=str)[:3000],
            analysis_points=[
                "Sector Performance - How different sectors are performing",
                "Sector Rotation - Current sector rotation trends",
                "Sector Opportunities - Attractive sectors for investment",
                "Sector Risks - Sectors to avoid or underweight",
                "Economic Impact - How economic factors affect sectors",
                "Sector Correlation - How sectors move relative to each other",
                "Sector Allocation - Recommended sector allocation strategies",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["sector_analysis"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("sector_analysis_agent error: %s", exc, exc_info=True)
        state["error"] = f"Sector analysis error: {exc}"
        state["sector_analysis"] = f"Analysis unavailable: {exc}"

    return state
