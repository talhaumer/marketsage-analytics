"""
Market Research Agent
Analyzes market trends, news, and provides comprehensive market research insights.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
from tools.groq_llm import get_llm
from tools.financial_tools import search_financial_news
from workflows.state import State


def market_research_agent(state: State) -> State:
    """Market Research Agent - Analyzes market trends and news"""
    try:
        llm = get_llm()
        
        # Search for relevant news
        news_query = f"{state['question']} {', '.join(state['symbols'])} financial markets"
        news_articles = search_financial_news.invoke({"query": news_query, "max_results": 8})
        
        # Create news summary
        news_summary = "\n".join([
            f"**{article['title']}**\n{article['content'][:200]}...\nSource: {article['source']}\n"
            for article in news_articles[:5]
        ])
        
        prompt = f"""
        As a Market Research Specialist, analyze the following market information:
        
        **Question:** {state['question']}
        **Symbols:** {', '.join(state['symbols']) if state['symbols'] else 'General market analysis'}
        **Timeframe:** {state['timeframe']}
        **Analysis Type:** {state['analysis_type']}
        
        **Recent News:**
        {news_summary}
        
        Provide a comprehensive market research analysis including:
        1. **Current Market Trends** - Key developments and patterns
        2. **News Analysis** - Impact of recent news on the market
        3. **Sector Insights** - Relevant sector-specific information
        4. **Regulatory Environment** - Any regulatory changes or concerns
        5. **Economic Indicators** - Relevant economic factors
        6. **Market Sentiment** - Overall market mood and investor behavior
        
        Format your response in clear, professional markdown with specific insights and actionable information.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        state['market_research'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Market research error: {str(e)}"
    
    return state
