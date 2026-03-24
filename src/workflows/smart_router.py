"""
Smart Router for Multi-Asset Analysis
Automatically routes to appropriate agents based on input detection
"""

from typing import Dict, Any
from workflows.state import State
from utils.input_detector import InputDetector, get_analysis_recommendation


class SmartAnalysisRouter:
    """
    Intelligent router that determines which agents to activate based on user input
    
    Two routing strategies:
    1. Automatic (recommended) - Detects and routes automatically
    2. Manual - User explicitly specifies analysis type
    """
    
    @staticmethod
    def route_analysis(state: State) -> Dict[str, bool]:
        """
        Determine which agents should be activated based on input
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary indicating which agents to activate
        """
        symbols = state.get('symbols', [])
        question = state.get('question', '')
        analysis_type = state.get('analysis_type', 'comprehensive')
        
        # Get detection results
        detection = get_analysis_recommendation(symbols, question)
        
        # Store detection results in state for transparency
        state['detection_info'] = detection
        
        # Determine agent activation based on detection
        routing = {
            'use_financial_agent': False,
            'use_crypto_agent': False,
            'use_technical_agent': True,  # Usually always useful
            'use_risk_agent': True,  # Usually always useful
            'use_sentiment_agent': True,  # Usually always useful
            'use_portfolio_agent': len(symbols) > 1,  # Only for multi-asset
            'use_sector_agent': False,
            'detected_type': detection['analysis_type'],
            'confidence': detection['confidence']
        }
        
        # Activate appropriate agents based on detection
        if detection['analysis_type'] == 'crypto':
            routing['use_crypto_agent'] = True
            routing['use_financial_agent'] = False
            
        elif detection['analysis_type'] == 'stock':
            routing['use_financial_agent'] = True
            routing['use_sector_agent'] = True
            routing['use_crypto_agent'] = False
            
        elif detection['analysis_type'] == 'mixed':
            routing['use_financial_agent'] = True
            routing['use_crypto_agent'] = True
            routing['use_sector_agent'] = True
            
        else:  # unknown - default to stock
            routing['use_financial_agent'] = True
            routing['use_sector_agent'] = True
        
        # Override with explicit analysis_type if provided
        if analysis_type == 'crypto':
            routing['use_crypto_agent'] = True
            routing['use_financial_agent'] = False
        
        return routing
    
    @staticmethod
    def should_skip_agent(agent_name: str, routing: Dict[str, bool]) -> bool:
        """
        Check if an agent should be skipped based on routing decisions
        
        Args:
            agent_name: Name of the agent to check
            routing: Routing decisions dictionary
            
        Returns:
            True if agent should be skipped
        """
        skip_map = {
            'financial_data': not routing.get('use_financial_agent', True),
            'crypto_analysis': not routing.get('use_crypto_agent', False),
            'sector_analysis': not routing.get('use_sector_agent', False),
            'portfolio_analysis': not routing.get('use_portfolio_agent', False)
        }
        
        return skip_map.get(agent_name, False)
    
    @staticmethod
    def get_routing_summary(routing: Dict[str, bool]) -> str:
        """
        Generate human-readable routing summary
        
        Args:
            routing: Routing decisions
            
        Returns:
            Summary string
        """
        active_agents = []
        
        if routing.get('use_financial_agent'):
            active_agents.append("Financial Data (Yahoo Finance)")
        if routing.get('use_crypto_agent'):
            active_agents.append("Crypto Data (CoinGecko)")
        if routing.get('use_technical_agent'):
            active_agents.append("Technical Analysis")
        if routing.get('use_risk_agent'):
            active_agents.append("Risk Assessment")
        if routing.get('use_sentiment_agent'):
            active_agents.append("Sentiment Analysis")
        if routing.get('use_portfolio_agent'):
            active_agents.append("Portfolio Analysis")
        if routing.get('use_sector_agent'):
            active_agents.append("Sector Analysis")
        
        summary = f"""
**Smart Routing Decision:**
- Detection Type: {routing['detected_type']}
- Confidence: {routing['confidence']}
- Active Agents: {len(active_agents)}
  - {chr(10).join([f'  • {agent}' for agent in active_agents])}
"""
        return summary


# Conditional node functions for LangGraph
def should_run_financial_agent(state: State) -> str:
    """Determine if financial agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_financial" if routing['use_financial_agent'] else "skip_financial"


def should_run_crypto_agent(state: State) -> str:
    """Determine if crypto agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_crypto" if routing['use_crypto_agent'] else "skip_crypto"


def should_run_sector_agent(state: State) -> str:
    """Determine if sector agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_sector" if routing['use_sector_agent'] else "skip_sector"


# Example usage in workflow
if __name__ == "__main__":
    # Test routing decisions
    test_cases = [
        {
            'symbols': ['BTC', 'ETH'],
            'question': 'Analyze crypto market',
            'analysis_type': 'comprehensive'
        },
        {
            'symbols': ['AAPL', 'MSFT'],
            'question': 'Stock analysis',
            'analysis_type': 'comprehensive'
        },
        {
            'symbols': ['AAPL', 'BTC', 'MSFT', 'ETH'],
            'question': 'Mixed portfolio analysis',
            'analysis_type': 'comprehensive'
        }
    ]
    
    print("=" * 80)
    print("SMART ROUTER TEST")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Symbols: {test['symbols']}")
        print(f"Question: {test['question']}")
        
        routing = SmartAnalysisRouter.route_analysis(test)
        summary = SmartAnalysisRouter.get_routing_summary(routing)
        
        print(summary)
        print("-" * 80)

