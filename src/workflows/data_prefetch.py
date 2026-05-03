"""
Pre-fetch market data once at workflow start.
Downstream agents read from state['shared_market_data'].
"""
from typing import Any, Dict, List


def prefetch_market_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch market data for all symbols once and stash on state."""
    symbols: List[str] = state.get("symbols") or []
    timeframe: str = state.get("timeframe", "1mo")

    if not symbols:
        return {"shared_market_data": {}}

    try:
        from utils.crypto_symbols import CRYPTO_SYMBOLS
    except ImportError:
        CRYPTO_SYMBOLS = frozenset({"BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE"})

    stock_syms = [s for s in symbols if s.upper() not in CRYPTO_SYMBOLS]
    crypto_syms = [s for s in symbols if s.upper() in CRYPTO_SYMBOLS]

    shared: Dict[str, Any] = {}

    if stock_syms:
        try:
            import yfinance as yf
            tickers = yf.download(
                stock_syms, period=timeframe, auto_adjust=True,
                progress=False, timeout=15,
            )
            shared["stock_data"] = tickers.to_dict() if not tickers.empty else {}
        except Exception as exc:
            shared["stock_data"] = {}
            shared["stock_data_error"] = str(exc)

    if crypto_syms:
        try:
            from tools.crypto_data_tools import get_crypto_client
            client = get_crypto_client()
            shared["crypto_data"] = client.get_multiple_coins_data(crypto_syms, timeframe)
        except Exception as exc:
            shared["crypto_data"] = {}
            shared["crypto_data_error"] = str(exc)

    return {"shared_market_data": shared}
