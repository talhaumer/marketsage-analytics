"""
Portfolio Analysis Agent
Provides portfolio optimization recommendations, allocation strategies, and performance analysis.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.gorq_llm import get_llm
from tools.financial_tools import calculate_portfolio_metrics
from api.models import FinancialAnalysisState
from workflows.state import State


def portfolio_analysis_agent(state: State) -> State:
    """Portfolio Analysis Agent - Provides portfolio optimization recommendations"""
    try:
        llm = get_llm()
        
        if state['symbols']:
            # Calculate portfolio metrics
            portfolio_metrics = calculate_portfolio_metrics.invoke({"symbols": state['symbols']})
            
            prompt = f"""
            As a Portfolio Optimization Specialist, provide portfolio recommendations:
            
            **Question:** {state['question']}
            **Symbols:** {', '.join(state['symbols'])}
            **Risk Tolerance:** {state.get('risk_tolerance', 'moderate')}
            
            **Portfolio Metrics:**
            {json.dumps(portfolio_metrics, default=str, indent=2)}
            
            Provide comprehensive portfolio analysis including:
            1. **Portfolio Composition** - Current allocation and diversification
            2. **Risk-Return Profile** - Expected returns and risk levels
            3. **Diversification Analysis** - Sector and asset diversification
            4. **Optimization Recommendations** - Suggested allocation changes
            5. **Rebalancing Strategy** - When and how to rebalance
            6. **Alternative Investments** - Additional investment opportunities
            7. **Tax Efficiency** - Tax-optimized investment strategies
            8. **Performance Monitoring** - Key metrics to track
            
            Format your response with clear portfolio recommendations and optimization strategies.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            state['portfolio_analysis'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Portfolio analysis error: {str(e)}"
    
    return state
