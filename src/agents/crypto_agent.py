"""
src/agents/crypto_agent.py

CryptoAgent implementation.
- Uses CoinGecko (pycoingecko) by default to fetch market time-series
- Computes simple indicators (RSI, MACD)
- Returns a JSON-serializable analysis payload suitable for the frontend
  or FastAPI endpoint

A richer connector (CryptoQuant, Glassnode, LunarCrush) lives in
src/tools/crypto_data_tools.py and may be passed in via the ``data_client``
constructor argument.
"""
import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from langchain_core.messages import HumanMessage

from agents.base_agent import BaseAgent
from agents.shared_prompts import build_prompt
from tools.groq_llm import get_llm
from workflows.state import State

# pycoingecko is an optional dependency; the agent can still be constructed
# with an injected data client when it is unavailable.
try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    CoinGeckoAPI = None


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI using exponential smoothing for average gains/losses."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_macd(series: pd.Series, span_short: int = 12, span_long: int = 26, span_signal: int = 9):
    """Return (macd, signal, hist) as pd.Series."""
    ema_short = series.ewm(span=span_short, adjust=False).mean()
    ema_long = series.ewm(span=span_long, adjust=False).mean()
    macd = ema_short - ema_long
    signal = macd.ewm(span=span_signal, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist


class _CoinGeckoClient:
    """Small wrapper around pycoingecko.CoinGeckoAPI for getting price series.

    - symbol_to_id: best-effort mapping from ticker (eg 'BTC') to CoinGecko id (eg 'bitcoin')
    - get_market_chart: returns a DataFrame indexed by timestamp with a `price` column

    This is intentionally minimal; in production you should use a dedicated connector in src/tools/crypto_data_tools.py that
    supports rate-limiting, retries, API keys (for other providers) and caching.
    """

    def __init__(self):
        if CoinGeckoAPI is None:
            raise ImportError("pycoingecko is required. Install via `pip install pycoingecko`")
        self.cg = CoinGeckoAPI()
        self._symbol_map: Optional[Dict[str, str]] = None

    def _load_symbol_map(self):
        if self._symbol_map is not None:
            return
        coins = self.cg.get_coins_list()
        self._symbol_map = {}
        for c in coins:
            sym = c.get("symbol", "").upper()
            id_ = c.get("id")
            if sym and id_:
                # keep the first mapping we encounter for a symbol
                if sym not in self._symbol_map:
                    self._symbol_map[sym] = id_
        # common fallbacks
        self._symbol_map.update({"BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether"})

    def symbol_to_id(self, symbol: str) -> str:
        self._load_symbol_map()
        return self._symbol_map.get(symbol.upper(), symbol.lower())

    def get_market_chart(self, symbol: str, vs_currency: str = "usd", days: int = 7) -> pd.DataFrame:
        """Fetch `days` worth of market data for `symbol` and return DataFrame with index=timestamp and column `price`.

        days follows CoinGecko API convention (1,7,14,30,90,365, max)
        """
        coin_id = self.symbol_to_id(symbol)
        data = self.cg.get_coin_market_chart_by_id(coin_id, vs_currency, days)
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])  # timestamp in ms
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df


class CryptoAgent(BaseAgent):
    """MVP agent that returns up-to-date price summaries + technical indicators.

    - analyze(symbols, timeframe): timeframe accepts strings like '7d', '1d', '24h' (hours are approximated to days)
    - Returns a JSON-serializable dict with summary metrics and time-series for each symbol
    """

    def __init__(self, data_client: Optional[Any] = None, use_advanced_tools: bool = True):
        """Initialize CryptoAgent.
        
        Args:
            data_client: Optional data client (defaults to _CoinGeckoClient)
            use_advanced_tools: If True, use tools from crypto_data_tools.py
        """
        self.use_advanced_tools = use_advanced_tools
        if use_advanced_tools:
            try:
                from tools.crypto_data_tools import get_crypto_client
                self.data_client = get_crypto_client()
            except ImportError:
                self.data_client = data_client or _CoinGeckoClient()
        else:
            self.data_client = data_client or _CoinGeckoClient()

    def analyze(self, symbols: List[str], timeframe: str = "7d") -> Dict[str, Any]:
        days = self._parse_timeframe(timeframe)
        results: Dict[str, Any] = {}
        price_frames: Dict[str, pd.DataFrame] = {}

        for sym in symbols:
            df = self.data_client.get_market_chart(sym, days=days)
            if df.empty:
                price_frames[sym] = df
                results[sym] = {"last_price": None, "rsi": None, "macd": None, "macd_signal": None}
                continue

            df["rsi"] = compute_rsi(df["price"])
            macd, signal, hist = compute_macd(df["price"])
            df["macd"] = macd
            df["macd_signal"] = signal
            df["macd_hist"] = hist

            price_frames[sym] = df

            results[sym] = {
                "last_price": float(df["price"].iloc[-1]),
                "rsi": float(df["rsi"].iloc[-1]),
                "macd": float(df["macd"].iloc[-1]),
                "macd_signal": float(df["macd_signal"].iloc[-1]),
            }

        # build correlation matrix across fetched symbols using returns
        if len(price_frames) >= 2:
            price_df = pd.concat([price_frames[s]["price"].rename(s) for s in price_frames], axis=1)
            # resample to hourly, forward-fill, compute pct_change
            try:
                returns = price_df.resample("1H").last().ffill().pct_change()
                corr = returns.corr()
                results["correlation"] = corr.fillna(0).to_dict()
            except Exception:
                results["correlation"] = {}
        else:
            results["correlation"] = {}

        # placeholders for sentiment and on-chain data (to be provided by crypto_data_tools)
        results["sentiment"] = {s: None for s in symbols}
        results["onchain"] = {s: None for s in symbols}

        # attach time-series payload (serialize timestamps as ISO strings)
        results["time_series"] = {
            s: df[["price", "rsi", "macd", "macd_signal", "macd_hist"]].reset_index().to_dict(orient="records")
            for s, df in price_frames.items()
        }

        results["meta"] = {"timeframe_days": days, "symbols_count": len(symbols)}
        return results

    def _parse_timeframe(self, timeframe: str) -> int:
        if isinstance(timeframe, int):
            return timeframe
        tf = str(timeframe).lower().strip()
        if tf.endswith("d"):
            try:
                return int(tf[:-1])
            except Exception:
                return 7
        if tf.endswith("h"):
            try:
                hours = int(tf[:-1])
                return max(1, int((hours + 23) / 24))
            except Exception:
                return 1
        try:
            return int(tf)
        except Exception:
            return 7


def crypto_agent(state: State) -> State:
    """
    Crypto Analysis Agent for LangGraph workflow.
    Analyzes cryptocurrency markets, technical indicators, and trends.
    """
    try:
        # Check if any symbols are crypto assets (single source of truth)
        from utils.crypto_symbols import split_symbols
        stock_symbols, crypto_symbols = split_symbols(
            [s.upper() for s in state.get('symbols', [])]
        )
        
        # If no crypto symbols detected, provide a brief note
        if not crypto_symbols:
            state['crypto_analysis'] = "No cryptocurrency symbols detected in the analysis request. This agent focuses on crypto assets like BTC, ETH, SOL, etc."
            return state
        
        # Use CryptoAgent to analyze
        agent = CryptoAgent(use_advanced_tools=True)
        crypto_data = agent.analyze(crypto_symbols, timeframe=state.get('timeframe', '7d'))
        
        # Use LLM to provide intelligent analysis
        llm = get_llm()
        
        # Create compact summary for LLM (exclude time_series to reduce token usage)
        crypto_summary = {
            'symbols': {},
            'correlation': crypto_data.get('correlation', {}),
            'meta': crypto_data.get('meta', {})
        }
        
        # Add only essential metrics per symbol (no time_series)
        for symbol in crypto_symbols:
            if symbol in crypto_data:
                crypto_summary['symbols'][symbol] = {
                    'last_price': crypto_data[symbol].get('last_price'),
                    'rsi': crypto_data[symbol].get('rsi'),
                    'macd': crypto_data[symbol].get('macd'),
                    'macd_signal': crypto_data[symbol].get('macd_signal')
                }
        
        # Convert to JSON for prompt (much smaller now!)
        crypto_summary_json = json.dumps(crypto_summary, default=str)

        prompt = build_prompt(
            role="Cryptocurrency Analysis Specialist",
            question=state.get("question", "Analyze the crypto market"),
            symbols=crypto_symbols,
            timeframe=state.get("timeframe", "7d"),
            data_summary=crypto_summary_json[:3000],
            analysis_points=[
                "Price Analysis - Current prices, trends, and momentum",
                "Technical Indicators - RSI, MACD interpretation and signals",
                "Volatility Assessment - Risk levels and price stability",
                "Correlation Analysis - How assets move together",
                "Market Sentiment - Bullish/bearish indicators",
                "Trading Signals - Entry/exit recommendations (if applicable)",
                "Risk Factors - Specific crypto-related risks",
            ],
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        state['crypto_analysis'] = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as exc:
        logging.getLogger(__name__).error("crypto_agent error: %s", exc, exc_info=True)
        state["error"] = f"crypto_agent error: {exc}"
        state["crypto_analysis"] = f"Analysis unavailable: {exc}"
        return state

    return state


if __name__ == "__main__":
    # quick local demo
    agent = CryptoAgent()
    out = agent.analyze(["BTC", "ETH"], timeframe="7d")

    print(json.dumps(out, indent=2, default=str))
