"""
Financial Data Agent
Analyzes stock data, financial metrics, and provides comprehensive financial analysis.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.groq_llm import get_llm
from tools.financial_tools import get_stock_data
from workflows.state import State


def financial_data_agent(state: State) -> State:
    """Financial Data Agent - Analyzes stock data and financial metrics"""
    try:
        llm = get_llm()
        
        # Get comprehensive stock data
        stock_data = get_stock_data.invoke({"symbols": state['symbols'], "timeframe": state['timeframe']})
        
        # Prepare data summary for LLM
        data_summary = {}
        for symbol, data in stock_data.items():
            if 'error' not in data:
                data_summary[symbol] = {
                    'basic_info': data['info'],
                    'price_data': data['price_data'],
                    'technical_indicators': data['technical_indicators']
                }
        
        prompt = f"""
        As a Financial Data Analyst, analyze the following stock data:
        
        **Question:** {state['question']}
        **Analysis Type:** {state['analysis_type']}
        **Timeframe:** {state['timeframe']}
        
        **Stock Data:**
        {json.dumps(data_summary, default=str, indent=2)}
        
        Provide a comprehensive financial analysis including:
        1. **Price Analysis** - Current prices, trends, and key levels
        2. **Financial Metrics** - P/E ratios, market cap, and other key ratios
        3. **Technical Indicators** - Moving averages, RSI, MACD, and volatility
        4. **Performance Comparison** - How stocks compare to each other and market
        5. **Investment Metrics** - Risk-return profiles and investment attractiveness
        6. **Sector Analysis** - Industry positioning and competitive landscape
        
        Format your response with clear tables, charts, and actionable insights.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        state['financial_data'] = {
            'analysis': response.content if hasattr(response, 'content') else str(response),
            'raw_data': stock_data
        }
        
    except Exception as e:
        state['error'] = f"Financial data analysis error: {str(e)}"
    
    return state
