"""
Crypto Data Tools for MarketSage Analytics
Provides advanced crypto market data connectors and analysis tools
"""

import os
import time as _time

from langchain.tools import tool
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# CoinGecko integration
try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    CoinGeckoAPI = None


# Module-level TTL cache for the CoinGecko symbol -> id map.
# CoinGecko's coin list rarely changes; cache for 1 hour to avoid the
# multi-second cold-start API hit on every CryptoDataClient instance.
_SYMBOL_MAP_CACHE: dict = {}
_SYMBOL_MAP_LOADED_AT: float = 0.0
_SYMBOL_MAP_TTL: float = 3600.0


class CryptoDataClient:
    """Advanced crypto data client supporting multiple providers.
    
    Providers:
    - CoinGecko (free, rate-limited)
    - CryptoQuant (placeholder - requires API key)
    - Glassnode (placeholder - requires API key)
    - LunarCrush (placeholder - requires API key)
    """
    
    def __init__(self, provider: str = "coingecko", api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.environ.get("COINGECKO_API_KEY")
        self.provider = provider.lower()
        self.api_key = api_key
        
        if self.provider == "coingecko":
            if CoinGeckoAPI is None:
                raise ImportError("pycoingecko is required. Install via `pip install pycoingecko`")
            self.client = CoinGeckoAPI()
        else:
            # Placeholder for other providers
            self.client = None

    @property
    def _symbol_map(self) -> dict:
        """Lazy-loaded, module-cached symbol -> CoinGecko id mapping (1h TTL)."""
        global _SYMBOL_MAP_CACHE, _SYMBOL_MAP_LOADED_AT
        if _time.time() - _SYMBOL_MAP_LOADED_AT > _SYMBOL_MAP_TTL:
            loaded = self._load_symbol_map()
            _SYMBOL_MAP_CACHE = loaded if loaded is not None else {}
            _SYMBOL_MAP_LOADED_AT = _time.time()
        return _SYMBOL_MAP_CACHE

    def _load_symbol_map(self) -> dict:
        """Fetch CoinGecko coin list and build symbol -> id mapping."""
        if self.provider != "coingecko" or not self.client:
            return {}

        coins = self.client.get_coins_list()
        symbol_map: Dict[str, str] = {}
        for c in coins:
            sym = c.get("symbol", "").upper()
            id_ = c.get("id")
            if sym and id_ and sym not in symbol_map:
                symbol_map[sym] = id_

        # Common fallbacks (preferred IDs override generic first-match)
        symbol_map.update({
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDT": "tether",
            "BNB": "binancecoin",
            "SOL": "solana",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "MATIC": "matic-network",
            "DOT": "polkadot",
        })
        return symbol_map

    def symbol_to_id(self, symbol: str) -> str:
        """Convert symbol to provider-specific ID"""
        if self.provider == "coingecko":
            return self._symbol_map.get(symbol.upper(), symbol.lower())
        return symbol.lower()
    
    def get_market_chart(self, symbol: str, vs_currency: str = "usd", days: int = 7) -> pd.DataFrame:
        """Fetch market chart data for a symbol"""
        if self.provider == "coingecko" and self.client:
            coin_id = self.symbol_to_id(symbol)
            try:
                data = self.client.get_coin_market_chart_by_id(coin_id, vs_currency, days)
                prices = data.get("prices", [])
                volumes = data.get("total_volumes", [])
                
                df = pd.DataFrame(prices, columns=["timestamp", "price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                
                if volumes:
                    vol_df = pd.DataFrame(volumes, columns=["timestamp", "volume"])
                    vol_df["timestamp"] = pd.to_datetime(vol_df["timestamp"], unit="ms")
                    df = df.merge(vol_df, on="timestamp", how="left")
                
                df.set_index("timestamp", inplace=True)
                return df
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                return pd.DataFrame()
        
        return pd.DataFrame()
    
    def get_coin_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed coin information"""
        if self.provider == "coingecko" and self.client:
            coin_id = self.symbol_to_id(symbol)
            try:
                data = self.client.get_coin_by_id(coin_id)
                return {
                    "id": data.get("id"),
                    "symbol": data.get("symbol", "").upper(),
                    "name": data.get("name"),
                    "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "market_cap_rank": data.get("market_cap_rank"),
                    "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                    "high_24h": data.get("market_data", {}).get("high_24h", {}).get("usd"),
                    "low_24h": data.get("market_data", {}).get("low_24h", {}).get("usd"),
                    "price_change_24h": data.get("market_data", {}).get("price_change_24h"),
                    "price_change_percentage_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                    "circulating_supply": data.get("market_data", {}).get("circulating_supply"),
                    "total_supply": data.get("market_data", {}).get("total_supply"),
                    "ath": data.get("market_data", {}).get("ath", {}).get("usd"),
                    "ath_date": data.get("market_data", {}).get("ath_date", {}).get("usd"),
                    "atl": data.get("market_data", {}).get("atl", {}).get("usd"),
                    "atl_date": data.get("market_data", {}).get("atl_date", {}).get("usd"),
                }
            except Exception as e:
                print(f"Error fetching info for {symbol}: {e}")
                return {"error": str(e)}
        
        return {}
    
    def get_global_market_data(self) -> Dict[str, Any]:
        """Get global crypto market data"""
        if self.provider == "coingecko" and self.client:
            try:
                data = self.client.get_global()
                return {
                    "total_market_cap_usd": data.get("data", {}).get("total_market_cap", {}).get("usd"),
                    "total_volume_24h_usd": data.get("data", {}).get("total_volume", {}).get("usd"),
                    "bitcoin_dominance": data.get("data", {}).get("market_cap_percentage", {}).get("btc"),
                    "ethereum_dominance": data.get("data", {}).get("market_cap_percentage", {}).get("eth"),
                    "active_cryptocurrencies": data.get("data", {}).get("active_cryptocurrencies"),
                    "markets": data.get("data", {}).get("markets"),
                }
            except Exception as e:
                print(f"Error fetching global data: {e}")
                return {"error": str(e)}
        
        return {}


# Initialize default client
_default_client = None

def get_crypto_client(provider: str = "coingecko", api_key: Optional[str] = None) -> CryptoDataClient:
    """Get or create crypto data client"""
    global _default_client
    if _default_client is None:
        _default_client = CryptoDataClient(provider, api_key)
    return _default_client


@tool
def get_crypto_data(symbols: List[str], timeframe: str = "7d") -> Dict[str, Any]:
    """
    Get comprehensive crypto data for given symbols and timeframe
    
    Args:
        symbols: List of crypto symbols to analyze (e.g., ['BTC', 'ETH', 'SOL'])
        timeframe: Time period for data (1d, 7d, 14d, 30d, 90d, 365d)
    
    Returns:
        Dictionary containing crypto data for each symbol with prices, volumes, and metrics
    """
    client = get_crypto_client()
    
    # Parse timeframe
    days = 7
    tf = str(timeframe).lower().strip()
    if tf.endswith("d"):
        try:
            days = int(tf[:-1])
        except ValueError:
            pass
    elif tf.endswith("h"):
        try:
            hours = int(tf[:-1])
            days = max(1, int((hours + 23) / 24))
        except ValueError:
            pass
    
    crypto_data = {}
    
    for symbol in symbols:
        try:
            # Get market chart data
            df = client.get_market_chart(symbol, days=days)
            
            # Get coin info
            info = client.get_coin_info(symbol)
            
            # Calculate technical indicators
            technical_indicators = {}
            if not df.empty and len(df) > 1:
                # RSI
                if len(df) >= 14:
                    delta = df["price"].diff()
                    gain = delta.clip(lower=0)
                    loss = -delta.clip(upper=0)
                    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
                    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
                    rs = avg_gain / (avg_loss.replace(0, np.nan))
                    rsi = 100 - (100 / (1 + rs))
                    technical_indicators["rsi"] = float(rsi.iloc[-1]) if not rsi.empty else None
                
                # MACD
                if len(df) >= 26:
                    ema_12 = df["price"].ewm(span=12, adjust=False).mean()
                    ema_26 = df["price"].ewm(span=26, adjust=False).mean()
                    macd = ema_12 - ema_26
                    signal = macd.ewm(span=9, adjust=False).mean()
                    technical_indicators["macd"] = float(macd.iloc[-1])
                    technical_indicators["macd_signal"] = float(signal.iloc[-1])
                    technical_indicators["macd_histogram"] = float((macd - signal).iloc[-1])
                
                # Volatility
                returns = df["price"].pct_change().dropna()
                if not returns.empty:
                    technical_indicators["volatility"] = float(returns.std() * np.sqrt(365))
                
                # Price changes
                if len(df) >= 2:
                    current_price = df["price"].iloc[-1]
                    prev_price = df["price"].iloc[-2]
                    technical_indicators["price_change_pct"] = float((current_price - prev_price) / prev_price * 100)
            
            crypto_data[symbol] = {
                "info": info,
                "price_data": {
                    "current_price": df["price"].iloc[-1] if not df.empty else None,
                    "high": df["price"].max() if not df.empty else None,
                    "low": df["price"].min() if not df.empty else None,
                    "avg_price": df["price"].mean() if not df.empty else None,
                    "volume": df["volume"].iloc[-1] if "volume" in df.columns and not df.empty else None,
                },
                "technical_indicators": technical_indicators,
                "historical_data": df.to_dict() if not df.empty else {},
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            crypto_data[symbol] = {
                "error": str(e),
                "symbol": symbol,
                "last_updated": datetime.now().isoformat()
            }
    
    return crypto_data


@tool
def get_crypto_sentiment(symbols: List[str]) -> Dict[str, Any]:
    """
    Analyze crypto sentiment for given symbols
    
    Args:
        symbols: List of crypto symbols to analyze
    
    Returns:
        Dictionary containing sentiment analysis for each symbol
    """
    # Placeholder for advanced sentiment analysis
    # In production, integrate with LunarCrush, Santiment, or other sentiment providers
    
    sentiment_data = {
        "symbols": symbols,
        "analysis_date": datetime.now().isoformat(),
        "sentiment_scores": {},
        "note": "Sentiment data requires integration with LunarCrush, Santiment, or similar providers"
    }
    
    for symbol in symbols:
        # Placeholder sentiment based on market data
        sentiment_data["sentiment_scores"][symbol] = {
            "score": None,
            "sentiment": "neutral",
            "social_volume": None,
            "social_dominance": None,
            "note": "Connect sentiment API for real-time data"
        }
    
    return sentiment_data


@tool
def get_crypto_onchain_metrics(symbols: List[str]) -> Dict[str, Any]:
    """
    Get on-chain metrics for crypto assets
    
    Args:
        symbols: List of crypto symbols to analyze
    
    Returns:
        Dictionary containing on-chain metrics
    """
    # Placeholder for on-chain metrics
    # In production, integrate with Glassnode, CryptoQuant, or similar providers
    
    onchain_data = {
        "symbols": symbols,
        "analysis_date": datetime.now().isoformat(),
        "metrics": {},
        "note": "On-chain data requires integration with Glassnode, CryptoQuant, or similar providers"
    }
    
    for symbol in symbols:
        # Placeholder on-chain metrics
        onchain_data["metrics"][symbol] = {
            "active_addresses": None,
            "transaction_count": None,
            "network_value": None,
            "exchange_inflow": None,
            "exchange_outflow": None,
            "whale_transactions": None,
            "note": "Connect on-chain API for real-time data"
        }
    
    return onchain_data


@tool
def get_global_crypto_market() -> Dict[str, Any]:
    """
    Get global cryptocurrency market data
    
    Returns:
        Dictionary containing global market metrics
    """
    client = get_crypto_client()
    
    try:
        global_data = client.get_global_market_data()
        global_data["last_updated"] = datetime.now().isoformat()
        return global_data
    except Exception as e:
        return {
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }


@tool
def calculate_crypto_portfolio_metrics(symbols: List[str], weights: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Calculate portfolio-level metrics for crypto assets
    
    Args:
        symbols: List of crypto symbols in the portfolio
        weights: Optional list of weights for each symbol (defaults to equal weight)
    
    Returns:
        Dictionary containing portfolio metrics
    """
    if not symbols:
        return {"error": "No symbols provided"}
    
    # Default to equal weights
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)
    
    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    try:
        # Get crypto data
        crypto_data = get_crypto_data.invoke({"symbols": symbols, "timeframe": "30d"})
        
        portfolio_metrics = {
            "symbols": symbols,
            "weights": weights,
            "assets": {},
            "portfolio_metrics": {}
        }
        
        weighted_returns = []
        weighted_volatility = []
        total_value = 0
        
        for i, symbol in enumerate(symbols):
            if symbol in crypto_data and "error" not in crypto_data[symbol]:
                asset_data = crypto_data[symbol]
                weight = weights[i]
                
                portfolio_metrics["assets"][symbol] = {
                    "weight": weight,
                    "current_price": asset_data["price_data"]["current_price"],
                    "volatility": asset_data["technical_indicators"].get("volatility", 0),
                    "market_cap": asset_data["info"].get("market_cap", 0)
                }
                
                # Calculate returns
                if "historical_data" in asset_data and asset_data["historical_data"]:
                    hist_data = pd.DataFrame(asset_data["historical_data"])
                    if not hist_data.empty and "price" in hist_data.columns:
                        returns = hist_data["price"].pct_change().dropna()
                        if not returns.empty:
                            weighted_returns.append(returns * weight)
                            vol = asset_data["technical_indicators"].get("volatility", 0)
                            weighted_volatility.append(vol * weight)
                            total_value += asset_data["price_data"]["current_price"] * weight
        
        # Calculate portfolio-level metrics
        if weighted_returns:
            portfolio_returns = pd.concat(weighted_returns, axis=1).sum(axis=1)
            portfolio_vol = np.sqrt(np.sum([v**2 for v in weighted_volatility]))
            
            portfolio_metrics["portfolio_metrics"] = {
                "total_value": total_value,
                "expected_return": float(portfolio_returns.mean() * 365),  # Annualized
                "volatility": float(portfolio_vol),
                "sharpe_ratio": float((portfolio_returns.mean() * 365) / (portfolio_vol + 1e-8)),
                "diversification": len(symbols)
            }
        
        return portfolio_metrics
        
    except Exception as e:
        return {"error": f"Portfolio calculation failed: {str(e)}"}

