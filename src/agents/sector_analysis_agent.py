"""
Sector Analysis Agent
Analyzes sector performance, trends, and provides sector allocation recommendations.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.gorq_llm import get_llm
from tools.financial_tools import analyze_sector_performance
from api.models import FinancialAnalysisState
from workflows.state import State


def sector_analysis_agent(state: State) -> State:
    """Sector Analysis Agent - Analyzes sector performance and trends"""
    try:
        llm = get_llm()
        
        # Get sector analysis
        sector_data = analyze_sector_performance.invoke({})
        
        prompt = f"""
            As a Sector Analysis Specialist, analyze sector performance and trends:
            
            **Question:** {state['question']}
            **Symbols:** {', '.join(state['symbols'])}
            
            **Sector Data:**
            {json.dumps(sector_data, default=str, indent=2)}
            
            Provide comprehensive sector analysis including:
            1. **Sector Performance** - How different sectors are performing
            2. **Sector Rotation** - Current sector rotation trends
            3. **Sector Opportunities** - Attractive sectors for investment
            4. **Sector Risks** - Sectors to avoid or underweight
            5. **Economic Impact** - How economic factors affect sectors
            6. **Sector Correlation** - How sectors move relative to each other
            7. **Sector Allocation** - Recommended sector allocation strategies
            
            Format your response with clear sector insights and allocation recommendations.
            """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        state['sector_analysis'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        state['error'] = f"Sector analysis error: {str(e)}"
    
    return state
