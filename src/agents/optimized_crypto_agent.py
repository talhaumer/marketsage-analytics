"""
Optimized Crypto Agent using shared components
Demonstrates best practices for component reuse and optimization
"""

from typing import List, Dict, Any
import pandas as pd
import json

# Import shared components
from src.agents.base_agent import FinancialDataAgent
from src.utils.technical_indicators import TechnicalIndicators
from src.utils.data_fetcher import DataFetcher
from src.workflows.state import State


class OptimizedCryptoAgent(FinancialDataAgent):
    """
    Optimized Crypto Agent using shared components:
    - Inherits from FinancialDataAgent for common functionality
    - Uses TechnicalIndicators for all calculations
    - Uses DataFetcher for caching
    - Follows consistent patterns with other agents
    """
    
    def __init__(self):
        super().__init__(name="OptimizedCryptoAgent")
        self.ti = TechnicalIndicators()
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        start_time = self.log_analysis_start()
        
        try:
            # Extract state information
            symbols = state.get('symbols', [])
            timeframe = state.get('timeframe', '7d')
            question = state.get('question', '')
            
            # Validate and categorize symbols
            stock_symbols, crypto_symbols = self.validate_symbols(symbols)
            
            # Skip if no crypto symbols
            if not crypto_symbols:
                state['crypto_analysis'] = (
                    "No cryptocurrency symbols detected. "
                    "This agent analyzes crypto assets like BTC, ETH, SOL, etc."
                )
                return state
            
            # Fetch crypto data with caching
            crypto_data = self._fetch_crypto_data_cached(crypto_symbols, timeframe)
            
            # Compute technical indicators using shared module
            enriched_data = self._enrich_with_indicators(crypto_data)
            
            # Compute correlation matrix
            correlation = self._compute_correlation(enriched_data)
            
            # Generate LLM analysis
            analysis = self._generate_llm_analysis(
                crypto_symbols=crypto_symbols,
                data=enriched_data,
                correlation=correlation,
                question=question,
                timeframe=timeframe
            )
            
            state['crypto_analysis'] = analysis
            
        except Exception as e:
            state = self.handle_error(state, e)
            state['crypto_analysis'] = f"Crypto analysis error: {str(e)}"
        
        return state
    
    def _fetch_crypto_data_cached(self, symbols: List[str], timeframe: str) -> Dict[str, Any]:
        """Fetch crypto data with caching"""
        cache_key = f"crypto_{'-'.join(sorted(symbols))}_{timeframe}"
        
        # Try cache first
        cached = self.cache_get(cache_key)
        if cached:
            return cached
        
        # Fetch fresh data using DataFetcher
        data = DataFetcher.fetch_crypto_data({
            "symbols": symbols,
            "timeframe": timeframe
        })
        
        # Cache the result
        self.cache_set(cache_key, data)
        
        return data
    
    def _enrich_with_indicators(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich crypto data with technical indicators using shared module
        """
        enriched = {}
        
        for symbol, data in crypto_data.items():
            if 'error' in data:
                enriched[symbol] = data
                continue
            
            # Get historical data
            hist_data = data.get('historical_data', {})
            if not hist_data:
                enriched[symbol] = data
                continue
            
            # Convert to DataFrame
            df = pd.DataFrame(hist_data)
            if df.empty or 'price' not in df.columns:
                enriched[symbol] = data
                continue
            
            # Compute all indicators using shared module
            indicators = self.ti.compute_all_indicators(
                df, 
                price_col='price',
                high_col='price',  # Crypto often doesn't have OHLC, use price
                low_col='price',
                volume_col='volume' if 'volume' in df.columns else None
            )
            
            # Add interpretations
            if 'rsi' in indicators:
                indicators['rsi_interpretation'] = self.ti.interpret_rsi(indicators['rsi'])
            
            if 'macd' in indicators and 'macd_signal' in indicators:
                indicators['macd_interpretation'] = self.ti.interpret_macd(
                    indicators['macd'], 
                    indicators['macd_signal']
                )
            
            # Update data
            enriched[symbol] = {
                **data,
                'technical_indicators': indicators
            }
        
        return enriched
    
    def _compute_correlation(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute correlation matrix between crypto assets"""
        try:
            price_data = {}
            
            for symbol, data in crypto_data.items():
                if 'error' not in data and 'historical_data' in data:
                    hist = data['historical_data']
                    if hist and 'price' in hist:
                        df = pd.DataFrame(hist)
                        if not df.empty:
                            price_data[symbol] = df.set_index('timestamp')['price'] if 'timestamp' in df else df['price']
            
            if len(price_data) >= 2:
                price_df = pd.DataFrame(price_data)
                # Compute returns and correlation
                returns = price_df.pct_change().dropna()
                corr = returns.corr()
                return corr.fillna(0).to_dict()
            
        except Exception as e:
            print(f"[OptimizedCryptoAgent] Error computing correlation: {str(e)}")
        
        return {}
    
    def _generate_llm_analysis(
        self,
        crypto_symbols: List[str],
        data: Dict[str, Any],
        correlation: Dict[str, Any],
        question: str,
        timeframe: str
    ) -> str:
        """Generate LLM-powered analysis using base agent methods"""
        
        # Format data for LLM
        data_summary = self._format_data_summary(data, correlation)
        
        # Create analysis prompt using base agent method
        prompt = self.create_analysis_prompt(
            role="Cryptocurrency Analysis Specialist",
            question=question,
            data=data_summary,
            analysis_points=[
                "**Price Analysis** - Current prices, trends, and momentum",
                "**Technical Indicators** - RSI, MACD interpretation and signals",
                "**Volatility Assessment** - Risk levels and price stability",
                "**Correlation Analysis** - How assets move together",
                "**Market Sentiment** - Bullish/bearish indicators",
                "**Trading Signals** - Entry/exit recommendations (if applicable)",
                "**Risk Factors** - Specific crypto-related risks"
            ],
            symbols=crypto_symbols,
            timeframe=timeframe
        )
        
        # Invoke LLM using base agent method
        return self.invoke_llm(prompt)
    
    def _format_data_summary(
        self, 
        data: Dict[str, Any], 
        correlation: Dict[str, Any]
    ) -> str:
        """Format data for LLM consumption"""
        summary_parts = []
        
        for symbol, info in data.items():
            if 'error' in info:
                summary_parts.append(f"**{symbol}**: Error - {info['error']}")
                continue
            
            price_data = info.get('price_data', {})
            indicators = info.get('technical_indicators', {})
            
            symbol_summary = f"""
**{symbol}**:
- Current Price: ${price_data.get('current_price', 'N/A'):,.2f}
- 24h High/Low: ${price_data.get('high', 'N/A'):,.2f} / ${price_data.get('low', 'N/A'):,.2f}
- RSI: {indicators.get('rsi', 'N/A'):.2f} ({indicators.get('rsi_interpretation', 'N/A')})
- MACD: {indicators.get('macd', 'N/A'):.4f} ({indicators.get('macd_interpretation', 'N/A')})
- Volatility: {indicators.get('volatility', 0):.2%}
- Momentum (10d): {indicators.get('momentum_10d', 0):.2f}%
"""
            summary_parts.append(symbol_summary)
        
        # Add correlation if available
        if correlation:
            summary_parts.append("\n**Correlation Matrix**:")
            summary_parts.append(json.dumps(correlation, indent=2))
        
        return "\n".join(summary_parts)


# Workflow integration function
def optimized_crypto_agent(state: State) -> State:
    """
    Optimized crypto analysis agent for LangGraph workflow
    Uses shared components for better performance
    """
    agent = OptimizedCryptoAgent()
    return agent.analyze(state)

