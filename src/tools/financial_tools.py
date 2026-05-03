"""
Financial Analysis Tools for LangGraph Financial Analyst
"""

from langchain.tools import tool
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from duckduckgo_search import DDGS
from datetime import datetime

# Crypto detection
CRYPTO_SYMBOLS = [
    'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'MATIC', 'DOT', 
    'AVAX', 'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'FIL', 'NEAR', 'ALGO',
    'USDT', 'USDC', 'SHIB', 'TRX', 'DAI', 'WBTC', 'LEO', 'PEPE'
]

def is_crypto_symbol(symbol: str) -> bool:
    """Check if symbol is a cryptocurrency"""
    return symbol.upper() in CRYPTO_SYMBOLS

def get_price_history(symbol: str, timeframe: str) -> pd.DataFrame:
    """Get price history from appropriate source (crypto or stock)"""
    if is_crypto_symbol(symbol):
        # Use CryptoDataClient for crypto
        try:
            from tools.crypto_data_tools import get_crypto_client
            
            # Convert timeframe to days
            days_map = {
                "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180,
                "1y": 365, "2y": 730, "5y": 1825, "10y": 3650,
                "ytd": 365, "max": 1825
            }
            days = days_map.get(timeframe, 365)
            
            client = get_crypto_client()
            df = client.get_market_chart(symbol, days=days)
            
            # Standardize to yfinance format
            if not df.empty:
                df = df.rename(columns={'price': 'Close', 'volume': 'Volume'})
                df['Open'] = df['Close']
                df['High'] = df['Close']
                df['Low'] = df['Close']
            return df
        except Exception as e:
            print(f"Error fetching crypto data for {symbol}: {e}")
            return pd.DataFrame()
    else:
        # Use yfinance for stocks
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=timeframe)
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()

@tool
def get_stock_data(symbols: List[str], timeframe: str = "1y") -> Dict[str, Any]:
    """
    Get comprehensive stock/crypto data for given symbols and timeframe
    
    Uses CoinGecko for crypto symbols, Yahoo Finance for stocks
    
    Args:
        symbols: List of stock/crypto symbols to analyze
        timeframe: Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        Dictionary containing data for each symbol
    """
    stock_data = {}
    
    for symbol in symbols:
        try:
            # Get price history from appropriate source
            hist = get_price_history(symbol, timeframe)
            
            # Get additional info (only for stocks via yfinance)
            if not is_crypto_symbol(symbol):
                ticker = yf.Ticker(symbol)
                info = ticker.info
            else:
                # For crypto, create minimal info
                info = {
                    'longName': symbol,
                    'symbol': symbol,
                    'sector': 'Cryptocurrency',
                    'industry': 'Digital Assets',
                    'currency': 'USD'
                }
            
            # Calculate additional metrics
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            volume = hist['Volume'].iloc[-1] if not hist.empty else None
            
            # Technical indicators
            technical_indicators = {}
            if not hist.empty and len(hist) > 1:
                # Moving averages
                technical_indicators['sma_20'] = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else None
                technical_indicators['sma_50'] = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else None
                
                # RSI calculation
                if len(hist) >= 14:
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
                    if loss == 0:
                        rsi = 100.0
                    elif gain == 0:
                        rsi = 0.0
                    else:
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                    technical_indicators['rsi'] = rsi
                
                # MACD
                if len(hist) >= 26:
                    ema_12 = hist['Close'].ewm(span=12).mean()
                    ema_26 = hist['Close'].ewm(span=26).mean()
                    technical_indicators['macd'] = (ema_12 - ema_26).iloc[-1]
                    technical_indicators['macd_signal'] = (ema_12 - ema_26).ewm(span=9).mean().iloc[-1]
                
                # Volatility (annualized)
                returns = hist['Close'].pct_change().dropna()
                technical_indicators['volatility'] = returns.std() * (252 ** 0.5)
                
                # Price change
                if len(hist) >= 2:
                    price_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    technical_indicators['daily_change_pct'] = price_change
            
            stock_data[symbol] = {
                'info': {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', None),
                    'pb_ratio': info.get('priceToBook', None),
                    'dividend_yield': info.get('dividendYield', None),
                    'beta': info.get('beta', None),
                    'currency': info.get('currency', 'USD')
                },
                'price_data': {
                    'current_price': current_price,
                    'volume': volume,
                    'high_52w': hist['High'].max() if not hist.empty else None,
                    'low_52w': hist['Low'].min() if not hist.empty else None,
                    'avg_volume': hist['Volume'].mean() if not hist.empty else None
                },
                'technical_indicators': technical_indicators,
                'historical_data': hist.to_dict() if not hist.empty else {},
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            stock_data[symbol] = {
                'error': str(e),
                'symbol': symbol,
                'last_updated': datetime.now().isoformat()
            }
    
    return stock_data

@tool
def search_financial_news(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Search for financial news using DuckDuckGo
    
    Args:
        query: Search query for financial news
        max_results: Maximum number of results to return
    
    Returns:
        List of news articles with title, content, and URL
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
            
            news_articles = []
            for article in results:
                news_articles.append({
                    'title': article.get('title', 'No title'),
                    'content': article.get('body', 'No content'),
                    'url': article.get('url', ''),
                    'published': article.get('date', ''),
                    'source': article.get('source', 'Unknown')
                })
            
            return news_articles
            
    except Exception as e:
        return [{
            'title': 'Error',
            'content': f'Failed to fetch news: {str(e)}',
            'url': '',
            'published': '',
            'source': 'Error'
        }]

@tool
def calculate_portfolio_metrics(symbols: List[str], weights: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Calculate portfolio-level metrics for given symbols and weights
    
    Args:
        symbols: List of stock symbols in the portfolio
        weights: Optional list of weights for each symbol (defaults to equal weight)
    
    Returns:
        Dictionary containing portfolio metrics
    """
    if not symbols:
        return {'error': 'No symbols provided'}
    
    # Default to equal weights if not provided
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)
    
    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    try:
        # Get stock data
        stock_data = get_stock_data.invoke({"symbols": symbols, "timeframe": "1y"})
        
        portfolio_metrics = {
            'symbols': symbols,
            'weights': weights,
            'total_weight': sum(weights),
            'stocks': {},
            'portfolio_metrics': {}
        }
        
        # Calculate individual stock metrics
        total_market_cap = 0
        weighted_returns = []
        weighted_volatility = []
        
        for i, symbol in enumerate(symbols):
            if symbol in stock_data and 'error' not in stock_data[symbol]:
                stock_info = stock_data[symbol]
                weight = weights[i]
                
                portfolio_metrics['stocks'][symbol] = {
                    'weight': weight,
                    'market_cap': stock_info['info']['market_cap'],
                    'sector': stock_info['info']['sector'],
                    'current_price': stock_info['price_data']['current_price'],
                    'volatility': stock_info['technical_indicators'].get('volatility', 0)
                }
                
                total_market_cap += stock_info['info']['market_cap'] * weight
                
                # Calculate returns (simplified)
                if 'historical_data' in stock_info and stock_info['historical_data']:
                    hist_data = pd.DataFrame(stock_info['historical_data'])
                    if not hist_data.empty and 'Close' in hist_data.columns:
                        returns = hist_data['Close'].pct_change().dropna()
                        if not returns.empty:
                            weighted_returns.append(returns * weight)
                            weighted_volatility.append(stock_info['technical_indicators'].get('volatility', 0) * weight)
        
        # Calculate portfolio-level metrics
        if weighted_returns:
            portfolio_returns = pd.concat(weighted_returns, axis=1).sum(axis=1)
            portfolio_metrics['portfolio_metrics'] = {
                'total_market_cap': total_market_cap,
                'expected_return': portfolio_returns.mean() * 252,  # Annualized
                'volatility': np.sqrt(np.sum([v**2 for v in weighted_volatility])),  # Simplified
                'sharpe_ratio': (portfolio_returns.mean() * 252) / (np.sqrt(np.sum([v**2 for v in weighted_volatility])) + 1e-8),
                'diversification_ratio': len(symbols) / len(set([portfolio_metrics['stocks'][s]['sector'] for s in symbols if s in portfolio_metrics['stocks']]))
            }
        
        return portfolio_metrics
        
    except Exception as e:
        return {'error': f'Portfolio calculation failed: {str(e)}'}

@tool
def analyze_sector_performance(sectors: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze performance of different sectors using real sector ETF data
    
    Args:
        sectors: List of sectors to analyze (if None, analyzes all major sectors)
    
    Returns:
        Dictionary containing sector performance analysis with real data
    """
    # Default sectors if none provided
    if sectors is None:
        sectors = [
            'Technology', 'Healthcare', 'Financial Services', 'Consumer Discretionary',
            'Consumer Staples', 'Energy', 'Industrials', 'Materials', 'Utilities',
            'Real Estate', 'Communication Services'
        ]
    
    # Sector ETF mapping for real data
    sector_etfs = {
        'Technology': 'XLK',           # Technology Select Sector SPDR Fund
        'Healthcare': 'XLV',           # Health Care Select Sector SPDR Fund
        'Financial Services': 'XLF',   # Financial Select Sector SPDR Fund
        'Consumer Discretionary': 'XLY', # Consumer Discretionary Select Sector SPDR Fund
        'Consumer Staples': 'XLP',     # Consumer Staples Select Sector SPDR Fund
        'Energy': 'XLE',               # Energy Select Sector SPDR Fund
        'Industrials': 'XLI',          # Industrial Select Sector SPDR Fund
        'Materials': 'XLB',            # Materials Select Sector SPDR Fund
        'Utilities': 'XLU',            # Utilities Select Sector SPDR Fund
        'Real Estate': 'XLRE',         # Real Estate Select Sector SPDR Fund
        'Communication Services': 'XLC' # Communication Services Select Sector SPDR Fund
    }
    
    try:
        sector_analysis = {
            'sectors': sectors,
            'analysis_date': datetime.now().isoformat(),
            'performance': {},
            'data_source': 'Real Sector ETF Data (yfinance)'
        }
        
        # Get REAL data for each sector using sector ETFs
        for sector in sectors:
            if sector in sector_etfs:
                etf_symbol = sector_etfs[sector]
                
                try:
                    # Get real ETF data using yfinance
                    ticker = yf.Ticker(etf_symbol)
                    
                    # Get historical data for different time periods
                    hist_1m = ticker.history(period="1mo")
                    hist_3m = ticker.history(period="3mo")
                    hist_1y = ticker.history(period="1y")
                    
                    # Calculate REAL performance metrics
                    performance_1m = 0
                    performance_3m = 0
                    performance_1y = 0
                    volatility = 0
                    
                    if not hist_1m.empty and len(hist_1m) > 1:
                        performance_1m = (hist_1m['Close'].iloc[-1] / hist_1m['Close'].iloc[0] - 1)
                    
                    if not hist_3m.empty and len(hist_3m) > 1:
                        performance_3m = (hist_3m['Close'].iloc[-1] / hist_3m['Close'].iloc[0] - 1)
                    
                    if not hist_1y.empty and len(hist_1y) > 1:
                        performance_1y = (hist_1y['Close'].iloc[-1] / hist_1y['Close'].iloc[0] - 1)
                        
                        # Calculate REAL volatility (annualized)
                        returns = hist_1y['Close'].pct_change().dropna()
                        if not returns.empty:
                            volatility = returns.std() * (252 ** 0.5)
                    
                    # Determine trend based on REAL performance
                    if performance_1y > 0.05:
                        trend = 'bullish'
                    elif performance_1y < -0.05:
                        trend = 'bearish'
                    else:
                        trend = 'neutral'
                    
                    sector_analysis['performance'][sector] = {
                        'etf_symbol': etf_symbol,
                        'performance_1m': round(performance_1m, 4),      # ✅ REAL DATA
                        'performance_3m': round(performance_3m, 4),      # ✅ REAL DATA
                        'performance_1y': round(performance_1y, 4),      # ✅ REAL DATA
                        'volatility': round(volatility, 4),              # ✅ REAL DATA
                        'trend': trend,                                  # ✅ REAL DATA
                        'current_price': hist_1y['Close'].iloc[-1] if not hist_1y.empty else None
                    }
                    
                except Exception as e:
                    # Fallback to placeholder if ETF data fails
                    sector_analysis['performance'][sector] = {
                        'etf_symbol': etf_symbol,
                        'performance_1m': 0.0,
                        'performance_3m': 0.0,
                        'performance_1y': 0.0,
                        'volatility': 0.0,
                        'trend': 'neutral',
                        'error': f'Failed to fetch data for {etf_symbol}: {str(e)}'
                    }
            else:
                # Sector not in ETF mapping
                sector_analysis['performance'][sector] = {
                    'error': f'No ETF mapping found for sector: {sector}'
                }
        
        return sector_analysis
        
    except Exception as e:
        return {'error': f'Sector analysis failed: {str(e)}'}

@tool
def get_market_sentiment(symbols: List[str]) -> Dict[str, Any]:
    """
    Analyze market sentiment for given symbols
    
    Args:
        symbols: List of stock symbols to analyze sentiment for
    
    Returns:
        Dictionary containing sentiment analysis
    """
    try:
        sentiment_data = {
            'symbols': symbols,
            'analysis_date': datetime.now().isoformat(),
            'sentiment_scores': {},
            'overall_sentiment': 'neutral'
        }
        
        # Search for news for each symbol
        for symbol in symbols:
            news_articles = search_financial_news.invoke({"query": f"{symbol} stock news", "max_results": 5})
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['bullish', 'positive', 'growth', 'gain', 'rise', 'up', 'strong', 'beat', 'exceed']
            negative_keywords = ['bearish', 'negative', 'decline', 'fall', 'down', 'weak', 'miss', 'disappoint', 'concern']
            
            positive_count = 0
            negative_count = 0
            
            for article in news_articles:
                text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
                positive_count += sum(1 for word in positive_keywords if word in text)
                negative_count += sum(1 for word in negative_keywords if word in text)
            
            # Calculate sentiment score
            total_sentiment = positive_count + negative_count
            if total_sentiment > 0:
                sentiment_score = (positive_count - negative_count) / total_sentiment
            else:
                sentiment_score = 0
            
            sentiment_data['sentiment_scores'][symbol] = {
                'score': sentiment_score,
                'positive_signals': positive_count,
                'negative_signals': negative_count,
                'sentiment': 'bullish' if sentiment_score > 0.1 else 'bearish' if sentiment_score < -0.1 else 'neutral'
            }
        
        # Calculate overall sentiment
        if sentiment_data['sentiment_scores']:
            avg_sentiment = np.mean([data['score'] for data in sentiment_data['sentiment_scores'].values()])
            sentiment_data['overall_sentiment'] = 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral'
            sentiment_data['average_sentiment_score'] = avg_sentiment
        
        return sentiment_data
        
    except Exception as e:
        return {'error': f'Sentiment analysis failed: {str(e)}'}
