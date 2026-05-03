"""
Intelligent Input Detection System
Automatically detects whether user input requires Yahoo Finance (stocks) or crypto analysis
"""

from typing import Dict, List, Any

from utils.crypto_symbols import CRYPTO_SYMBOLS as _CANONICAL_CRYPTO_SYMBOLS


class InputDetector:
    """
    Intelligent detector for determining analysis type based on user input

    Two detection strategies:
    1. Symbol-based detection (recommended for accuracy)
    2. Context-based detection (uses question text)
    """

    # Crypto symbols sourced from utils.crypto_symbols (single source of truth)
    CRYPTO_SYMBOLS = _CANONICAL_CRYPTO_SYMBOLS
    
    # Crypto-related keywords for context detection
    CRYPTO_KEYWORDS = {
        'crypto', 'cryptocurrency', 'bitcoin', 'blockchain', 'altcoin',
        'defi', 'nft', 'token', 'coin', 'satoshi', 'mining', 'staking',
        'wallet', 'metamask', 'binance', 'coinbase', 'kraken',
        'gas fee', 'smart contract', 'dapp', 'web3', 'layer 2',
        'proof of stake', 'proof of work', 'consensus', 'validator'
    }
    
    # Stock/traditional finance keywords
    STOCK_KEYWORDS = {
        'stock', 'equity', 'share', 'dividend', 'earnings',
        'nasdaq', 'nyse', 's&p', 'dow jones', 'index fund',
        'mutual fund', 'etf', 'quarterly report', 'eps',
        'market cap', 'pe ratio', 'book value', 'wallstreet'
    }
    
    @classmethod
    def detect_analysis_type(
        cls, 
        symbols: List[str], 
        question: str = "",
        use_context: bool = True
    ) -> Dict[str, Any]:
        """
        Main detection method - determines what type of analysis is needed
        
        Args:
            symbols: List of symbols to analyze
            question: User's question/query
            use_context: Whether to use context-based detection as secondary check
            
        Returns:
            Dictionary with detection results and recommendations
        """
        # Step 1: Symbol-based detection (Primary method - most accurate)
        symbol_analysis = cls._detect_by_symbols(symbols)
        
        # Step 2: Context-based detection (Secondary method - catches edge cases)
        context_analysis = cls._detect_by_context(question) if use_context and question else None
        
        # Step 3: Determine final recommendation
        recommendation = cls._make_recommendation(symbol_analysis, context_analysis)
        
        return {
            'analysis_type': recommendation['type'],
            'confidence': recommendation['confidence'],
            'crypto_symbols': symbol_analysis['crypto_symbols'],
            'stock_symbols': symbol_analysis['stock_symbols'],
            'mixed_portfolio': symbol_analysis['is_mixed'],
            'reasoning': recommendation['reasoning'],
            'symbol_detection': symbol_analysis,
            'context_detection': context_analysis
        }
    
    @classmethod
    def _detect_by_symbols(cls, symbols: List[str]) -> Dict[str, Any]:
        """
        Detect analysis type based on symbol names (Primary method)
        
        This is the most accurate method because symbols are explicit.
        """
        crypto_symbols = []
        stock_symbols = []
        unknown_symbols = []
        
        for symbol in symbols:
            symbol_upper = symbol.upper().strip()
            
            # Check if it's a known crypto symbol
            if symbol_upper in cls.CRYPTO_SYMBOLS:
                crypto_symbols.append(symbol_upper)
            # Check if it looks like a stock (typically 1-5 letters)
            elif cls._looks_like_stock_symbol(symbol):
                stock_symbols.append(symbol_upper)
            else:
                unknown_symbols.append(symbol)
        
        # Determine type
        has_crypto = len(crypto_symbols) > 0
        has_stocks = len(stock_symbols) > 0
        
        if has_crypto and has_stocks:
            analysis_type = 'mixed'
            confidence = 'high'
        elif has_crypto:
            analysis_type = 'crypto'
            confidence = 'high'
        elif has_stocks:
            analysis_type = 'stock'
            confidence = 'high' if len(unknown_symbols) == 0 else 'medium'
        else:
            analysis_type = 'unknown'
            confidence = 'low'
        
        return {
            'type': analysis_type,
            'confidence': confidence,
            'crypto_symbols': crypto_symbols,
            'stock_symbols': stock_symbols,
            'unknown_symbols': unknown_symbols,
            'is_mixed': has_crypto and has_stocks
        }
    
    @classmethod
    def _detect_by_context(cls, question: str) -> Dict[str, Any]:
        """
        Detect analysis type based on question context (Secondary method)
        
        Uses keywords and patterns in the question text.
        """
        question_lower = question.lower()
        
        # Count crypto and stock keywords
        crypto_score = sum(1 for keyword in cls.CRYPTO_KEYWORDS if keyword in question_lower)
        stock_score = sum(1 for keyword in cls.STOCK_KEYWORDS if keyword in question_lower)
        
        # Determine type based on scores
        if crypto_score > stock_score:
            analysis_type = 'crypto'
            confidence = 'high' if crypto_score >= 2 else 'medium'
        elif stock_score > crypto_score:
            analysis_type = 'stock'
            confidence = 'high' if stock_score >= 2 else 'medium'
        elif crypto_score > 0 and stock_score > 0:
            analysis_type = 'mixed'
            confidence = 'medium'
        else:
            analysis_type = 'unknown'
            confidence = 'low'
        
        return {
            'type': analysis_type,
            'confidence': confidence,
            'crypto_score': crypto_score,
            'stock_score': stock_score,
            'matched_keywords': {
                'crypto': [kw for kw in cls.CRYPTO_KEYWORDS if kw in question_lower],
                'stock': [kw for kw in cls.STOCK_KEYWORDS if kw in question_lower]
            }
        }
    
    @classmethod
    def _make_recommendation(
        cls, 
        symbol_analysis: Dict[str, Any],
        context_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make final recommendation based on both detection methods
        
        Priority: Symbol detection > Context detection
        """
        # Symbol detection has highest priority (it's explicit)
        if symbol_analysis['confidence'] in ['high', 'medium']:
            return {
                'type': symbol_analysis['type'],
                'confidence': symbol_analysis['confidence'],
                'reasoning': f"Based on symbol analysis: {len(symbol_analysis['crypto_symbols'])} crypto, {len(symbol_analysis['stock_symbols'])} stocks detected"
            }
        
        # Fall back to context if symbols are unclear
        if context_analysis and context_analysis['confidence'] in ['high', 'medium']:
            return {
                'type': context_analysis['type'],
                'confidence': 'medium',  # Lower confidence when relying on context alone
                'reasoning': f"Based on question context: detected {context_analysis['crypto_score']} crypto keywords, {context_analysis['stock_score']} stock keywords"
            }
        
        # Default to stock if nothing else works
        return {
            'type': 'stock',
            'confidence': 'low',
            'reasoning': "Unable to determine clearly - defaulting to stock analysis"
        }
    
    @classmethod
    def _looks_like_stock_symbol(cls, symbol: str) -> bool:
        """
        Check if a symbol looks like a stock ticker
        
        Stock tickers are typically:
        - 1-5 uppercase letters
        - May contain periods (for different share classes)
        """
        # Remove periods
        clean_symbol = symbol.replace('.', '').upper()
        
        # Check if it's 1-5 letters
        if len(clean_symbol) >= 1 and len(clean_symbol) <= 5:
            return clean_symbol.isalpha()
        
        return False
    
    @classmethod
    def suggest_data_source(cls, analysis_type: str) -> str:
        """
        Suggest appropriate data source based on analysis type
        
        Args:
            analysis_type: Type of analysis ('crypto', 'stock', 'mixed')
            
        Returns:
            Recommended data source
        """
        recommendations = {
            'crypto': 'CoinGecko API (crypto_data_tools)',
            'stock': 'Yahoo Finance API (financial_tools)',
            'mixed': 'Both: Yahoo Finance for stocks, CoinGecko for crypto',
            'unknown': 'Yahoo Finance (default fallback)'
        }
        
        return recommendations.get(analysis_type, 'Yahoo Finance (default)')


# Convenience functions for easy use
def detect_input_type(symbols: List[str], question: str = "") -> str:
    """
    Quick function to detect analysis type
    
    Args:
        symbols: List of symbols
        question: User question
        
    Returns:
        Analysis type: 'crypto', 'stock', or 'mixed'
    """
    result = InputDetector.detect_analysis_type(symbols, question)
    return result['analysis_type']


def should_use_crypto_agent(symbols: List[str], question: str = "") -> bool:
    """
    Determine if crypto agent should be used
    
    Args:
        symbols: List of symbols
        question: User question
        
    Returns:
        True if crypto analysis is needed
    """
    result = InputDetector.detect_analysis_type(symbols, question)
    return result['analysis_type'] in ['crypto', 'mixed']


def should_use_stock_agent(symbols: List[str], question: str = "") -> bool:
    """
    Determine if stock agent should be used
    
    Args:
        symbols: List of symbols
        question: User question
        
    Returns:
        True if stock analysis is needed
    """
    result = InputDetector.detect_analysis_type(symbols, question)
    return result['analysis_type'] in ['stock', 'mixed']


def get_analysis_recommendation(symbols: List[str], question: str = "") -> Dict[str, Any]:
    """
    Get detailed analysis recommendation
    
    Args:
        symbols: List of symbols
        question: User question
        
    Returns:
        Complete detection results with recommendations
    """
    return InputDetector.detect_analysis_type(symbols, question, use_context=True)


# Example usage
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            'symbols': ['BTC', 'ETH', 'SOL'],
            'question': 'Analyze cryptocurrency trends'
        },
        {
            'symbols': ['AAPL', 'MSFT', 'GOOGL'],
            'question': 'Stock market analysis'
        },
        {
            'symbols': ['AAPL', 'BTC', 'MSFT', 'ETH'],
            'question': 'Analyze my mixed portfolio'
        },
        {
            'symbols': ['TSLA'],
            'question': 'What is the outlook for blockchain technology?'
        }
    ]
    
    print("=" * 80)
    print("INPUT DETECTOR TEST CASES")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Symbols: {test['symbols']}")
        print(f"Question: {test['question']}")
        
        result = get_analysis_recommendation(test['symbols'], test['question'])
        
        print(f"\nDetection Result:")
        print(f"  Analysis Type: {result['analysis_type']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"  Crypto Symbols: {result['crypto_symbols']}")
        print(f"  Stock Symbols: {result['stock_symbols']}")
        print(f"  Data Source: {InputDetector.suggest_data_source(result['analysis_type'])}")
        print("-" * 80)

