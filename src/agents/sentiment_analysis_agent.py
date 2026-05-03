"""
Sentiment Analysis Agent
Analyzes market sentiment, news sentiment, and social media sentiment.
"""

import json
import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from tools.financial_tools import get_market_sentiment
from agents.shared_prompts import build_prompt
from workflows.state import State


def sentiment_analysis_agent(state: State) -> State:
    """Sentiment Analysis Agent - Analyzes market sentiment"""
    try:
        llm = get_llm()

        symbols = state.get("symbols") or []
        # Get market sentiment data
        sentiment_data = get_market_sentiment.invoke({"symbols": symbols})

        prompt = build_prompt(
            role="Market Sentiment Analyst",
            question=state.get("question", ""),
            symbols=symbols,
            timeframe=state.get("timeframe", "1mo"),
            data_summary=json.dumps(sentiment_data, default=str)[:3000],
            analysis_points=[
                "News Sentiment - Analysis of news sentiment and media coverage",
                "Social Media Sentiment - Social media and retail investor sentiment",
                "Institutional Sentiment - Analyst ratings and institutional flows",
                "Market Psychology - Fear/greed indicators and market mood",
                "Contrarian Signals - Opportunities from contrarian sentiment",
                "Sentiment Trends - How sentiment has changed over time",
                "Sentiment Impact - How sentiment might affect prices",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["sentiment_analysis"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("sentiment_analysis_agent error: %s", exc, exc_info=True)
        state["error"] = f"Sentiment analysis error: {exc}"
        state["sentiment_analysis"] = f"Analysis unavailable: {exc}"

    return state
