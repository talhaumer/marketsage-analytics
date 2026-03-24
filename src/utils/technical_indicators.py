"""
Shared Technical Indicators Module
Reusable technical analysis functions for stocks and crypto
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


class TechnicalIndicators:
    """Shared technical indicator calculations for all agents"""
    
    @staticmethod
    def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Compute RSI using exponential smoothing for average gains/losses
        
        Args:
            series: Price series
            period: RSI period (default: 14)
            
        Returns:
            RSI series
        """
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
        
        rs = avg_gain / (avg_loss.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)
    
    @staticmethod
    def compute_macd(
        series: pd.Series, 
        span_short: int = 12, 
        span_long: int = 26, 
        span_signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute MACD (Moving Average Convergence Divergence)
        
        Args:
            series: Price series
            span_short: Short EMA period (default: 12)
            span_long: Long EMA period (default: 26)
            span_signal: Signal line period (default: 9)
            
        Returns:
            Tuple of (macd, signal, histogram)
        """
        ema_short = series.ewm(span=span_short, adjust=False).mean()
        ema_long = series.ewm(span=span_long, adjust=False).mean()
        
        macd = ema_short - ema_long
        signal = macd.ewm(span=span_signal, adjust=False).mean()
        histogram = macd - signal
        
        return macd, signal, histogram
    
    @staticmethod
    def compute_bollinger_bands(
        series: pd.Series, 
        period: int = 20, 
        num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute Bollinger Bands
        
        Args:
            series: Price series
            period: Moving average period (default: 20)
            num_std: Number of standard deviations (default: 2.0)
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def compute_moving_averages(
        series: pd.Series, 
        periods: list = None
    ) -> dict:
        """
        Compute multiple moving averages
        
        Args:
            series: Price series
            periods: List of periods (default: [20, 50, 200])
            
        Returns:
            Dictionary of {period: MA value}
        """
        if periods is None:
            periods = [20, 50, 200]
        
        mas = {}
        for period in periods:
            if len(series) >= period:
                mas[f'sma_{period}'] = series.rolling(window=period).mean().iloc[-1]
                mas[f'ema_{period}'] = series.ewm(span=period, adjust=False).mean().iloc[-1]
        
        return mas
    
    @staticmethod
    def compute_volatility(
        series: pd.Series, 
        window: int = 30, 
        annualize: bool = True,
        periods_per_year: int = 252
    ) -> float:
        """
        Compute volatility (standard deviation of returns)
        
        Args:
            series: Price series
            window: Rolling window (default: 30)
            annualize: Whether to annualize (default: True)
            periods_per_year: Trading periods per year (252 for stocks, 365 for crypto)
            
        Returns:
            Volatility value
        """
        returns = series.pct_change().dropna()
        if len(returns) < window:
            window = len(returns)
        
        volatility = returns.rolling(window=window).std().iloc[-1]
        
        if annualize and not pd.isna(volatility):
            volatility = volatility * np.sqrt(periods_per_year)
        
        return float(volatility) if not pd.isna(volatility) else 0.0
    
    @staticmethod
    def compute_support_resistance(
        series: pd.Series, 
        window: int = 20
    ) -> Tuple[float, float]:
        """
        Compute support and resistance levels
        
        Args:
            series: Price series
            window: Lookback window (default: 20)
            
        Returns:
            Tuple of (support, resistance)
        """
        if len(series) < window:
            window = len(series)
        
        recent = series.iloc[-window:]
        support = float(recent.min())
        resistance = float(recent.max())
        
        return support, resistance
    
    @staticmethod
    def compute_momentum(
        series: pd.Series, 
        period: int = 10
    ) -> float:
        """
        Compute price momentum
        
        Args:
            series: Price series
            period: Lookback period (default: 10)
            
        Returns:
            Momentum value (percentage change)
        """
        if len(series) < period + 1:
            period = len(series) - 1
        
        if period <= 0:
            return 0.0
        
        momentum = ((series.iloc[-1] - series.iloc[-period-1]) / series.iloc[-period-1]) * 100
        return float(momentum) if not pd.isna(momentum) else 0.0
    
    @staticmethod
    def compute_atr(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        period: int = 14
    ) -> pd.Series:
        """
        Compute Average True Range (ATR)
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period (default: 14)
            
        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()
        
        return atr
    
    @staticmethod
    def compute_stochastic(
        high: pd.Series, 
        low: pd.Series, 
        close: pd.Series, 
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Compute Stochastic Oscillator (%K and %D)
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Lookback period (default: 14)
            smooth_k: %K smoothing (default: 3)
            smooth_d: %D smoothing (default: 3)
            
        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        k = k.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
    
    @staticmethod
    def compute_all_indicators(
        df: pd.DataFrame, 
        price_col: str = 'Close',
        high_col: Optional[str] = 'High',
        low_col: Optional[str] = 'Low',
        volume_col: Optional[str] = 'Volume'
    ) -> dict:
        """
        Compute all technical indicators at once
        
        Args:
            df: DataFrame with OHLCV data
            price_col: Name of price column
            high_col: Name of high column (optional)
            low_col: Name of low column (optional)
            volume_col: Name of volume column (optional)
            
        Returns:
            Dictionary of all indicators
        """
        indicators = {}
        
        if price_col not in df.columns:
            return indicators
        
        price_series = df[price_col]
        
        # RSI
        if len(price_series) >= 14:
            rsi = TechnicalIndicators.compute_rsi(price_series)
            indicators['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else None
        
        # MACD
        if len(price_series) >= 26:
            macd, signal, hist = TechnicalIndicators.compute_macd(price_series)
            indicators['macd'] = float(macd.iloc[-1]) if not macd.empty else None
            indicators['macd_signal'] = float(signal.iloc[-1]) if not signal.empty else None
            indicators['macd_histogram'] = float(hist.iloc[-1]) if not hist.empty else None
        
        # Bollinger Bands
        if len(price_series) >= 20:
            upper, middle, lower = TechnicalIndicators.compute_bollinger_bands(price_series)
            indicators['bb_upper'] = float(upper.iloc[-1]) if not upper.empty else None
            indicators['bb_middle'] = float(middle.iloc[-1]) if not middle.empty else None
            indicators['bb_lower'] = float(lower.iloc[-1]) if not lower.empty else None
        
        # Moving Averages
        mas = TechnicalIndicators.compute_moving_averages(price_series)
        indicators.update(mas)
        
        # Volatility
        indicators['volatility'] = TechnicalIndicators.compute_volatility(price_series)
        
        # Support/Resistance
        support, resistance = TechnicalIndicators.compute_support_resistance(price_series)
        indicators['support'] = support
        indicators['resistance'] = resistance
        
        # Momentum
        indicators['momentum_10d'] = TechnicalIndicators.compute_momentum(price_series, 10)
        
        # ATR (if high/low available)
        if high_col in df.columns and low_col in df.columns and len(df) >= 14:
            atr = TechnicalIndicators.compute_atr(df[high_col], df[low_col], price_series)
            indicators['atr'] = float(atr.iloc[-1]) if not atr.empty else None
        
        # Stochastic (if high/low available)
        if high_col in df.columns and low_col in df.columns and len(df) >= 14:
            k, d = TechnicalIndicators.compute_stochastic(df[high_col], df[low_col], price_series)
            indicators['stochastic_k'] = float(k.iloc[-1]) if not k.empty else None
            indicators['stochastic_d'] = float(d.iloc[-1]) if not d.empty else None
        
        return indicators
    
    @staticmethod
    def interpret_rsi(rsi: float) -> str:
        """Interpret RSI value"""
        if pd.isna(rsi):
            return "N/A"
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    @staticmethod
    def interpret_macd(macd: float, signal: float) -> str:
        """Interpret MACD signals"""
        if pd.isna(macd) or pd.isna(signal):
            return "N/A"
        if macd > signal:
            return "Bullish (MACD above signal)"
        else:
            return "Bearish (MACD below signal)"

