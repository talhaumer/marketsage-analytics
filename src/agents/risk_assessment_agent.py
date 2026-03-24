"""
Risk Assessment Agent
Evaluates investment risks, provides risk mitigation strategies, and risk-reward analysis.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.gorq_llm import get_llm
from api.models import FinancialAnalysisState
from workflows.state import State


def risk_assessment_agent(state: State) -> State:
    """Risk Assessment Agent - Evaluates investment risks"""
    try:
        llm = get_llm()
        
        if 'financial_data' in state and state['financial_data']:
            stock_data = state['financial_data']['raw_data']
            
            # Calculate risk metrics
            risk_metrics = {}
            for symbol, data in stock_data.items():
                if 'error' not in data:
                    risk_metrics[symbol] = {
                        'volatility': data['technical_indicators'].get('volatility', 0),
                        'beta': data['info'].get('beta', 1.0),
                        'market_cap': data['info'].get('market_cap', 0),
                        'sector': data['info'].get('sector', 'Unknown'),
                        'pe_ratio': data['info'].get('pe_ratio', None)
                    }
            
            prompt = f"""
            As a Risk Management Specialist, assess the risks for the following investments:
            
            **Question:** {state['question']}
            **Risk Tolerance:** {state.get('risk_tolerance', 'moderate')}
            
            **Risk Metrics:**
            {json.dumps(risk_metrics, default=str, indent=2)}
            
            Provide a comprehensive risk assessment including:
            1. **Market Risk** - Overall market exposure and volatility
            2. **Company-Specific Risk** - Individual company risks and concerns
            3. **Sector Risk** - Industry and sector-specific risks
            4. **Liquidity Risk** - Trading volume and market depth concerns
            5. **Concentration Risk** - Portfolio concentration and diversification
            6. **Regulatory Risk** - Regulatory and compliance concerns
            7. **Risk Mitigation** - Strategies to reduce and manage risks
            8. **Risk-Reward Analysis** - Expected returns vs. risk levels
            
            Format your response with clear risk assessments and mitigation strategies.
            """
            
            response = llm.invoke([HumanMessage(content=prompt)])
            state['risk_assessment'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Risk assessment error: {str(e)}"
    
    return state
