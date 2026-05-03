"""
Smart Router for Multi-Asset Analysis
Automatically routes to appropriate agents based on input detection.

Crypto detection delegates to ``utils.crypto_symbols`` (single source of truth).
"""

from typing import Dict, Any
from workflows.state import State
from utils.crypto_symbols import is_crypto, split_symbols
from utils.input_detector import InputDetector, get_analysis_recommendation


class SmartAnalysisRouter:
    """
    Intelligent router that determines which agents to activate based on user input

    Two routing strategies:
    1. Automatic (recommended) - Detects and routes automatically
    2. Manual - User explicitly specifies analysis type
    """

    @staticmethod
    def route_analysis(state: State) -> Dict[str, Any]:
        """
        Determine which agents should be activated based on input.

        Returns a dict with both legacy ``use_*`` flags and the canonical
        ``run_*`` flags consumed by workflow conditional edges.
        """
        symbols = state.get('symbols', []) or []
        question = state.get('question', '')
        analysis_type = state.get('analysis_type', 'comprehensive')

        # Symbol-level split via canonical crypto set
        stock_syms, crypto_syms = split_symbols([s.upper() for s in symbols])
        has_crypto = bool(crypto_syms)
        has_stocks = bool(stock_syms)

        # Get detection results (still useful for context-detection on
        # questions like "analyze blockchain trends" with no symbols)
        detection = get_analysis_recommendation(symbols, question)

        # Store detection results in state for transparency
        state['detection_info'] = detection

        # Decide on agent activation
        if analysis_type == 'crypto':
            run_crypto, run_financial, run_sector = True, False, False
        elif has_crypto and has_stocks:
            run_crypto, run_financial, run_sector = True, True, True
        elif has_crypto:
            run_crypto, run_financial, run_sector = True, False, False
        elif has_stocks:
            run_crypto, run_financial, run_sector = False, True, True
        else:
            # No symbols: fall back to context detection
            detected = detection.get('analysis_type', 'unknown')
            if detected == 'crypto':
                run_crypto, run_financial, run_sector = True, False, False
            elif detected == 'mixed':
                run_crypto, run_financial, run_sector = True, True, True
            else:
                run_crypto, run_financial, run_sector = False, True, True

        routing = {
            # Canonical keys (consumed by workflow conditional edges and tests)
            'run_crypto_agent': run_crypto,
            'run_financial_agent': run_financial,
            'run_sector_agent': run_sector,
            'run_technical_agent': run_financial,
            'run_risk_agent': True,
            'run_sentiment_agent': True,
            'run_portfolio_agent': len(symbols) > 1,

            # Legacy keys (kept for back-compat with existing callers)
            'use_financial_agent': run_financial,
            'use_crypto_agent': run_crypto,
            'use_technical_agent': True,
            'use_risk_agent': True,
            'use_sentiment_agent': True,
            'use_portfolio_agent': len(symbols) > 1,
            'use_sector_agent': run_sector,

            'detected_type': detection.get('analysis_type', 'unknown'),
            'confidence': detection.get('confidence', 'low'),
        }

        return routing

    @staticmethod
    def should_skip_agent(agent_name: str, routing: Dict[str, Any]) -> bool:
        """Check if an agent should be skipped based on routing decisions."""
        skip_map = {
            'financial_data': not routing.get('run_financial_agent', True),
            'crypto_analysis': not routing.get('run_crypto_agent', False),
            'sector_analysis': not routing.get('run_sector_agent', False),
            'portfolio_analysis': not routing.get('run_portfolio_agent', False),
        }
        return skip_map.get(agent_name, False)

    @staticmethod
    def get_routing_summary(routing: Dict[str, Any]) -> str:
        """Generate human-readable routing summary."""
        active_agents = []

        if routing.get('run_financial_agent'):
            active_agents.append("Financial Data (Yahoo Finance)")
        if routing.get('run_crypto_agent'):
            active_agents.append("Crypto Data (CoinGecko)")
        if routing.get('run_technical_agent'):
            active_agents.append("Technical Analysis")
        if routing.get('run_risk_agent'):
            active_agents.append("Risk Assessment")
        if routing.get('run_sentiment_agent'):
            active_agents.append("Sentiment Analysis")
        if routing.get('run_portfolio_agent'):
            active_agents.append("Portfolio Analysis")
        if routing.get('run_sector_agent'):
            active_agents.append("Sector Analysis")

        agents_block = "\n".join(f"  - {agent}" for agent in active_agents)
        return (
            "**Smart Routing Decision:**\n"
            f"- Detection Type: {routing.get('detected_type', 'unknown')}\n"
            f"- Confidence: {routing.get('confidence', 'low')}\n"
            f"- Active Agents: {len(active_agents)}\n{agents_block}\n"
        )


# Conditional node functions for LangGraph
def should_run_financial_agent(state: State) -> str:
    """Determine if financial agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_financial" if routing['run_financial_agent'] else "skip_financial"


def should_run_crypto_agent(state: State) -> str:
    """Determine if crypto agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_crypto" if routing['run_crypto_agent'] else "skip_crypto"


def should_run_sector_agent(state: State) -> str:
    """Determine if sector agent should run"""
    routing = SmartAnalysisRouter.route_analysis(state)
    return "run_sector" if routing['run_sector_agent'] else "skip_sector"


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
