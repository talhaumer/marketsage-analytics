"""
Crypto Data Agent - Robust Implementation
Mirrors financial_data_agent.py structure for consistency
Analyzes cryptocurrency data, market metrics, and provides comprehensive crypto analysis.
"""

from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
import json
from tools.gorq_llm import get_llm
from tools.crypto_data_tools import get_crypto_data, get_global_crypto_market
from api.models import FinancialAnalysisState
from workflows.state import State


def crypto_data_agent(state: State) -> State:
    """
    Crypto Data Agent - Analyzes cryptocurrency data and market metrics
    
    Mirrors financial_data_agent structure:
    1. Get LLM instance
    2. Fetch crypto data using tools
    3. Prepare data summary
    4. Create comprehensive prompt
    5. Invoke LLM with structured analysis
    6. Return formatted state
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with crypto_data analysis
    """
    try:
        # Step 1: Get LLM instance
        llm = get_llm()
        
        # Step 2: Get comprehensive crypto data
        crypto_data = get_crypto_data.invoke({
            "symbols": state['symbols'], 
            "timeframe": state['timeframe']
        })
        
        # Step 3: Get global market context (optional but valuable)
        try:
            global_market = get_global_crypto_market.invoke({})
        except:
            global_market = None
        
        # Step 4: Prepare data summary for LLM (mirror financial agent structure)
        data_summary = {}
        for symbol, data in crypto_data.items():
            if 'error' not in data:
                data_summary[symbol] = {
                    'basic_info': {
                        'symbol': symbol,
                        'name': data.get('info', {}).get('name', symbol),
                        'current_price': data.get('price_data', {}).get('current_price'),
                        'market_cap': data.get('info', {}).get('market_cap'),
                        'market_cap_rank': data.get('info', {}).get('market_cap_rank'),
                        '24h_high': data.get('price_data', {}).get('high'),
                        '24h_low': data.get('price_data', {}).get('low'),
                        'circulating_supply': data.get('info', {}).get('circulating_supply'),
                        'total_supply': data.get('info', {}).get('total_supply')
                    },
                    'price_data': data.get('price_data', {}),
                    'technical_indicators': data.get('technical_indicators', {})
                }
        
        # Step 5: Create comprehensive analysis prompt (mirror financial agent)
        prompt = f"""
        As a Cryptocurrency Data Analyst, analyze the following crypto data:
        
        **Question:** {state['question']}
        **Analysis Type:** {state['analysis_type']}
        **Timeframe:** {state['timeframe']}
        
        **Global Crypto Market Context:**
        {json.dumps(global_market, default=str, indent=2) if global_market else 'N/A'}
        
        **Cryptocurrency Data:**
        {json.dumps(data_summary, default=str, indent=2)}
        
        Provide a comprehensive cryptocurrency analysis including:
        1. **Price Analysis** - Current prices, trends, and key levels
        2. **Market Metrics** - Market cap, rank, supply metrics, and dominance
        3. **Technical Indicators** - RSI, MACD, volatility, and momentum
        4. **Performance Comparison** - How crypto assets compare to each other and market
        5. **Investment Metrics** - Risk-return profiles and investment attractiveness
        6. **Market Context** - Position within broader crypto market and trends
        7. **Volatility Assessment** - Risk levels and price stability analysis
        8. **Trading Signals** - Key support/resistance and entry/exit points
        
        Format your response with clear structure, data tables, and actionable insights.
        Consider that cryptocurrency markets are 24/7 and typically more volatile than traditional stocks.
        """
        
        # Step 6: Invoke LLM
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Step 7: Store in state (mirror financial agent structure)
        state['crypto_data'] = {
            'analysis': response.content if hasattr(response, 'content') else str(response),
            'raw_data': crypto_data,
            'global_market': global_market
        }
        
    except Exception as e:
        # Consistent error handling
        state['error'] = f"Crypto data analysis error: {str(e)}"
        # Provide fallback
        state['crypto_data'] = {
            'analysis': f"Unable to complete crypto analysis: {str(e)}",
            'raw_data': {},
            'global_market': None
        }
    
    return state


def validate_crypto_symbols(symbols: List[str]) -> tuple[List[str], List[str]]:
    """
    Validate and categorize symbols as crypto or stock
    
    Args:
        symbols: List of symbols to validate
        
    Returns:
        Tuple of (crypto_symbols, non_crypto_symbols)
    """
    # Comprehensive list of crypto symbols
    known_crypto = {
        # Major cryptocurrencies
        'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
        'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'WBTC', 'DAI', 'SHIB', 'LTC', 'BCH',
        
        # DeFi tokens
        'UNI', 'AAVE', 'MKR', 'COMP', 'SNX', 'CRV', 'SUSHI', 'YFI', '1INCH',
        
        # Layer 2 & Scaling
        'ARB', 'OP', 'IMX', 'LRC', 'METIS',
        
        # Altcoins
        'ATOM', 'XLM', 'ETC', 'FIL', 'NEAR', 'ALGO', 'VET', 'ICP', 'APT', 'HBAR',
        'QNT', 'LDO', 'APE', 'SAND', 'MANA', 'AXS', 'GALA', 'CHZ', 'ENJ',
        
        # Stablecoins
        'BUSD', 'TUSD', 'USDP', 'FRAX', 'LUSD'
    }
    
    crypto_symbols = []
    non_crypto_symbols = []
    
    for symbol in symbols:
        symbol_upper = symbol.upper().strip()
        if symbol_upper in known_crypto:
            crypto_symbols.append(symbol_upper)
        else:
            non_crypto_symbols.append(symbol)
    
    return crypto_symbols, non_crypto_symbols


def is_crypto_analysis_needed(symbols: List[str]) -> bool:
    """
    Determine if crypto analysis is needed based on symbols
    
    Args:
        symbols: List of symbols to check
        
    Returns:
        True if any crypto symbols are present
    """
    crypto_symbols, _ = validate_crypto_symbols(symbols)
    return len(crypto_symbols) > 0

