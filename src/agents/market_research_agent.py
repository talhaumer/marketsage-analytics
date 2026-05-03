"""
Market Research Agent
Analyzes market trends, news, and provides comprehensive market research insights.
"""

import logging
from langchain_core.messages import HumanMessage
from tools.groq_llm import get_llm
from tools.financial_tools import search_financial_news
from agents.shared_prompts import build_prompt
from workflows.state import State


def market_research_agent(state: State) -> State:
    """Market Research Agent - Analyzes market trends and news"""
    try:
        llm = get_llm()

        # Search for relevant news
        symbols = state.get("symbols") or []
        news_query = f"{state.get('question', '')} {', '.join(symbols)} financial markets"
        news_articles = search_financial_news.invoke({"query": news_query, "max_results": 8})

        # Create news summary
        news_summary = "\n".join([
            f"**{article['title']}**\n{article['content'][:200]}...\nSource: {article['source']}\n"
            for article in news_articles[:5]
        ])

        prompt = build_prompt(
            role="Market Research Specialist",
            question=state.get("question", ""),
            symbols=symbols,
            timeframe=state.get("timeframe", "1mo"),
            data_summary=news_summary,
            analysis_points=[
                "Current Market Trends - Key developments and patterns",
                "News Analysis - Impact of recent news on the market",
                "Sector Insights - Relevant sector-specific information",
                "Regulatory Environment - Any regulatory changes or concerns",
                "Economic Indicators - Relevant economic factors",
                "Market Sentiment - Overall market mood and investor behavior",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state["market_research"] = response.content if hasattr(response, "content") else str(response)

    except Exception as exc:
        logging.getLogger(__name__).error("market_research_agent error: %s", exc, exc_info=True)
        state["error"] = f"Market research error: {exc}"
        state["market_research"] = f"Analysis unavailable: {exc}"

    return state
