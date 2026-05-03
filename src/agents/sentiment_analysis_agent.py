"""
Sentiment Analysis Agent
Analyzes market sentiment, news sentiment, and social media sentiment.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.groq_llm import get_llm
from tools.financial_tools import get_market_sentiment
from workflows.state import State


def sentiment_analysis_agent(state: State) -> State:
    """Sentiment Analysis Agent - Analyzes market sentiment"""
    try:
        llm = get_llm()
        
        # Get market sentiment data
        sentiment_data = get_market_sentiment.invoke({"symbols": state['symbols']})
        
        prompt = f"""
        As a Market Sentiment Analyst, analyze the sentiment for the following:
        
        **Question:** {state['question']}
        **Symbols:** {', '.join(state['symbols']) if state['symbols'] else 'General market'}
        
        **Sentiment Data:**
        {json.dumps(sentiment_data, default=str, indent=2)}
        
        Provide a comprehensive sentiment analysis including:
        1. **News Sentiment** - Analysis of news sentiment and media coverage
        2. **Social Media Sentiment** - Social media and retail investor sentiment
        3. **Institutional Sentiment** - Analyst ratings and institutional flows
        4. **Market Psychology** - Fear/greed indicators and market mood
        5. **Contrarian Signals** - Opportunities from contrarian sentiment
        6. **Sentiment Trends** - How sentiment has changed over time
        7. **Sentiment Impact** - How sentiment might affect prices
        
        Format your response with clear sentiment insights and market psychology analysis.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        state['sentiment_analysis'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Sentiment analysis error: {str(e)}"
    
    return state
