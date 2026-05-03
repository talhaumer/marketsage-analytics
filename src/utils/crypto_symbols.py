"""Single source of truth for supported cryptocurrency symbols."""

CRYPTO_SYMBOLS: frozenset = frozenset({
    "BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "ADA", "DOGE",
    "MATIC", "DOT", "AVAX", "LINK", "UNI", "ATOM", "LTC", "ETC",
    "FIL", "NEAR", "ALGO", "AAVE", "MKR", "SNX", "COMP",
    "1INCH", "CRV", "YFI", "SUSHI", "BAL", "REN", "ZRX",
})


def is_crypto(symbol: str) -> bool:
    return symbol.upper() in CRYPTO_SYMBOLS


def split_symbols(symbols):
    """Return (stock_list, crypto_list) from a mixed symbol list."""
    stocks = [s for s in symbols if not is_crypto(s)]
    cryptos = [s for s in symbols if is_crypto(s)]
    return stocks, cryptos
