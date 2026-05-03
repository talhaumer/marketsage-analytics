"""
Shared Data Fetcher Utilities
Centralized data fetching with caching and error handling
"""

import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import hashlib
import json


class DataCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, tuple] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache if not expired
        
        Args:
            key: Cache key
            ttl: Time-to-live override (uses default if None)
            
        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            self.misses += 1
            return None
        
        value, timestamp = self._cache[key]
        ttl = ttl or self.default_ttl
        
        if time.time() - timestamp > ttl:
            del self._cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any):
        """Set value in cache with current timestamp"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total,
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_size': len(self._cache)
        }


# Global cache instances
_stock_cache = DataCache(default_ttl=300)  # 5 minutes for stock data
_crypto_cache = DataCache(default_ttl=180)  # 3 minutes for crypto (more volatile)
_news_cache = DataCache(default_ttl=600)   # 10 minutes for news


class DataFetcher:
    """Centralized data fetching with caching and error handling"""
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate a unique cache key from arguments"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def fetch_with_cache(
        cache: DataCache,
        fetch_func: Callable,
        *args,
        cache_key: Optional[str] = None,
        ttl: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Fetch data with caching
        
        Args:
            cache: Cache instance to use
            fetch_func: Function to fetch data
            *args: Arguments for fetch_func
            cache_key: Optional custom cache key
            ttl: Optional TTL override
            **kwargs: Keyword arguments for fetch_func
            
        Returns:
            Fetched or cached data
        """
        # Generate cache key
        if cache_key is None:
            cache_key = DataFetcher.generate_cache_key(
                fetch_func.__name__, *args, **kwargs
            )
        
        # Try to get from cache
        cached_data = cache.get(cache_key, ttl)
        if cached_data is not None:
            print(f"[DataFetcher] Cache HIT for {fetch_func.__name__}")
            return cached_data
        
        # Fetch fresh data
        print(f"[DataFetcher] Cache MISS for {fetch_func.__name__}, fetching...")
        try:
            data = fetch_func(*args, **kwargs)
            cache.set(cache_key, data)
            return data
        except Exception as e:
            print(f"[DataFetcher] Error fetching data: {str(e)}")
            raise
    
    @staticmethod
    def fetch_stock_data(*args, **kwargs):
        """Fetch stock data with caching"""
        from tools.financial_tools import get_stock_data
        
        return DataFetcher.fetch_with_cache(
            _stock_cache,
            get_stock_data.invoke,
            *args,
            **kwargs
        )
    
    @staticmethod
    def fetch_crypto_data(*args, **kwargs):
        """Fetch crypto data with caching"""
        from tools.crypto_data_tools import get_crypto_data
        
        return DataFetcher.fetch_with_cache(
            _crypto_cache,
            get_crypto_data.invoke,
            *args,
            **kwargs
        )
    
    @staticmethod
    def fetch_news(*args, **kwargs):
        """Fetch news with caching"""
        from tools.financial_tools import search_financial_news
        
        return DataFetcher.fetch_with_cache(
            _news_cache,
            search_financial_news.invoke,
            *args,
            **kwargs
        )
    
    @staticmethod
    def fetch_market_data(symbols: List[str]) -> Dict[str, Any]:
        """
        Intelligently fetch market data for mixed stock/crypto symbols
        
        Args:
            symbols: List of stock/crypto symbols
            
        Returns:
            Combined market data for all symbols
        """
        from agents.base_agent import FinancialDataAgent
        
        # Categorize symbols
        agent = FinancialDataAgent()
        stock_symbols, crypto_symbols = agent.validate_symbols(symbols)
        
        result = {
            'stocks': {},
            'crypto': {},
            'metadata': {
                'stock_symbols': stock_symbols,
                'crypto_symbols': crypto_symbols,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Fetch stock data
        if stock_symbols:
            try:
                stock_data = DataFetcher.fetch_stock_data(
                    {"symbols": stock_symbols, "timeframe": "1y"}
                )
                result['stocks'] = stock_data
            except Exception as e:
                print(f"[DataFetcher] Error fetching stock data: {str(e)}")
        
        # Fetch crypto data
        if crypto_symbols:
            try:
                crypto_data = DataFetcher.fetch_crypto_data(
                    {"symbols": crypto_symbols, "timeframe": "7d"}
                )
                result['crypto'] = crypto_data
            except Exception as e:
                print(f"[DataFetcher] Error fetching crypto data: {str(e)}")
        
        return result
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Get statistics for all caches"""
        return {
            'stock_cache': _stock_cache.get_stats(),
            'crypto_cache': _crypto_cache.get_stats(),
            'news_cache': _news_cache.get_stats()
        }
    
    @staticmethod
    def clear_all_caches():
        """Clear all caches"""
        _stock_cache.clear()
        _crypto_cache.clear()
        _news_cache.clear()
        print("[DataFetcher] All caches cleared")


class BatchDataFetcher:
    """Batch data fetching for improved performance"""
    
    @staticmethod
    def fetch_all_for_analysis(
        symbols: List[str],
        timeframe: str = "1y",
        include_news: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch all necessary data for comprehensive analysis
        
        Args:
            symbols: List of symbols to analyze
            timeframe: Data timeframe
            include_news: Whether to fetch news
            
        Returns:
            Complete dataset for analysis
        """
        from agents.base_agent import FinancialDataAgent
        
        agent = FinancialDataAgent()
        stock_symbols, crypto_symbols = agent.validate_symbols(symbols)
        
        result = {
            'market_data': {},
            'news': [],
            'metadata': {
                'symbols': symbols,
                'stock_symbols': stock_symbols,
                'crypto_symbols': crypto_symbols,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Fetch all data in parallel (conceptually - actual implementation would use asyncio)
        # For now, fetch sequentially with caching
        
        # Market data
        result['market_data'] = DataFetcher.fetch_market_data(symbols)
        
        # News
        if include_news and symbols:
            try:
                query = f"{', '.join(symbols)} stock market analysis"
                news = DataFetcher.fetch_news({"query": query, "max_results": 10})
                result['news'] = news
            except Exception as e:
                print(f"[BatchDataFetcher] Error fetching news: {str(e)}")
                result['news'] = []
        
        return result


# Export convenience functions
def get_cached_stock_data(*args, **kwargs):
    """Convenience function for cached stock data"""
    return DataFetcher.fetch_stock_data(*args, **kwargs)


def get_cached_crypto_data(*args, **kwargs):
    """Convenience function for cached crypto data"""
    return DataFetcher.fetch_crypto_data(*args, **kwargs)


def get_cached_news(*args, **kwargs):
    """Convenience function for cached news"""
    return DataFetcher.fetch_news(*args, **kwargs)


def clear_caches():
    """Convenience function to clear all caches"""
    DataFetcher.clear_all_caches()


def get_cache_statistics():
    """Convenience function to get cache statistics"""
    return DataFetcher.get_cache_stats()

