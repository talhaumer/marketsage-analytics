"""
Quick test script to verify visualization capabilities
"""

import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

def test_basic_chart():
    """Test basic chart creation"""
    print("📊 Testing visualization capabilities...")
    print("=" * 60)
    
    # Test 1: Create simple chart
    print("\n1. Testing Plotly installation...")
    try:
        fig = go.Figure(data=[go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2])])
        fig.update_layout(title="Test Chart")
        print("✅ Plotly is working correctly!")
    except Exception as e:
        print(f"❌ Plotly error: {e}")
        return False
    
    # Test 2: Fetch stock data
    print("\n2. Testing stock data retrieval...")
    try:
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1mo")
        if not hist.empty:
            print(f"✅ Retrieved {len(hist)} days of AAPL data")
            print(f"   Latest price: ${hist['Close'].iloc[-1]:.2f}")
        else:
            print("⚠️  No data retrieved")
    except Exception as e:
        print(f"❌ YFinance error: {e}")
        return False
    
    # Test 3: Create stock price chart
    print("\n3. Testing stock price chart creation...")
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name='AAPL',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title="AAPL Stock Price (1 Month)",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template='plotly_white'
        )
        print("✅ Stock price chart created successfully!")
    except Exception as e:
        print(f"❌ Chart creation error: {e}")
        return False
    
    # Test 4: Create technical indicators
    print("\n4. Testing technical indicator calculation...")
    try:
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        if not rsi.empty:
            print(f"✅ RSI calculated - Current value: {rsi.iloc[-1]:.2f}")
        
        # Calculate MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        
        print(f"✅ MACD calculated - Current value: {macd.iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ Technical indicator error: {e}")
        return False
    
    # Test 5: Multiple symbols
    print("\n5. Testing multi-symbol analysis...")
    try:
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            if not hist.empty:
                ret = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                data[symbol] = ret
                print(f"   {symbol}: {ret:+.2f}% (1 month)")
        
        if data:
            print("✅ Multi-symbol analysis successful!")
    except Exception as e:
        print(f"❌ Multi-symbol error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All visualization tests passed!")
    print("\n📊 You can now use the enhanced frontend with visualizations!")
    print("   Run: ./run_frontend_with_viz.sh")
    print("   Or:  python src/frontend/gradio_app_with_viz.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_basic_chart()

