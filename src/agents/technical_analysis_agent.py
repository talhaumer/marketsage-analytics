"""
Technical Analysis Agent
Provides technical analysis, trading signals, and chart pattern analysis.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.gorq_llm import get_llm
from api.models import FinancialAnalysisState
from workflows.state import State


def technical_analysis_agent(state: State) -> State:
    """Technical Analysis Agent - Provides technical analysis and trading signals"""
    try:
        llm = get_llm()
        
        if 'financial_data' in state and state['financial_data']:
            stock_data = state['financial_data']['raw_data']
            
            # Extract technical indicators
            technical_summary = {}
            for symbol, data in stock_data.items():
                if 'error' not in data and 'technical_indicators' in data:
                    technical_summary[symbol] = data['technical_indicators']
            
            prompt = f"""
            As a Technical Analysis Specialist, analyze the following technical data:
            
            **Question:** {state['question']}
            **Symbols:** {', '.join(state['symbols'])}
            
            **Technical Indicators:**
            {json.dumps(technical_summary, default=str, indent=2)}
            
            Provide a comprehensive technical analysis including:
            1. **Chart Patterns** - Identify key chart patterns and formations
            2. **Support & Resistance** - Key price levels and their significance
            3. **Moving Averages** - Trend analysis using moving averages
            4. **Momentum Indicators** - RSI, MACD, and other momentum signals
            5. **Volume Analysis** - Volume patterns and their implications
            6. **Trading Signals** - Buy/sell/hold recommendations with entry/exit points
            7. **Risk Management** - Stop-loss levels and position sizing suggestions
            
            Format your response with clear technical analysis and actionable trading insights.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            state['technical_analysis'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Technical analysis error: {str(e)}"
    
    return state
