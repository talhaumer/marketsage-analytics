"""
Enhanced Gradio Frontend for MarketSage Analytics with Data Visualizations
Advanced Financial Analysis Platform with Multi-Agent AI and Interactive Charts
"""

import gradio as gr
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import os
import socket
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Global state for query history
query_history = []
analysis_results = {}

def get_local_ip():
    """Get the local IP address for network access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except OSError:
        return "localhost"

def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

def is_crypto_symbol(symbol):
    """Check if symbol is a cryptocurrency"""
    import sys
    import pathlib as _pl
    _src_path = _pl.Path(__file__).parent.parent.parent / "src"
    if str(_src_path) not in sys.path:
        sys.path.insert(0, str(_src_path))
    from utils.crypto_symbols import is_crypto
    return is_crypto(symbol)

def get_price_data(symbol, timeframe="1y"):
    """Get price data from appropriate source (crypto or stock)"""
    try:
        if is_crypto_symbol(symbol):
            # Use CryptoDataClient for crypto
            import sys
            import pathlib as _pl
            _src_path = _pl.Path(__file__).parent.parent.parent / "src"
            if str(_src_path) not in sys.path:
                sys.path.insert(0, str(_src_path))
            from tools.crypto_data_tools import get_crypto_client
            
            # Convert timeframe to days
            days_map = {
                "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, 
                "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
            }
            days = days_map.get(timeframe, 365)
            
            client = get_crypto_client()
            df = client.get_market_chart(symbol, days=days)
            
            # Rename columns to match yfinance format
            if not df.empty:
                df = df.rename(columns={'price': 'Close', 'volume': 'Volume'})
                # Add Open, High, Low for compatibility
                df['Open'] = df['Close']
                df['High'] = df['Close']
                df['Low'] = df['Close']
            return df
        else:
            # Use yfinance for stocks
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            return ticker.history(period=timeframe)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def create_stock_price_chart(symbols, timeframe="1y"):
    """Create interactive stock price chart"""
    try:
        fig = go.Figure()
        
        for symbol in symbols:
            # Use unified data fetcher (crypto or stock)
            hist = get_price_data(symbol, timeframe)
            
            if not hist.empty:
                source = "CoinGecko" if is_crypto_symbol(symbol) else "Yahoo Finance"
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines',
                    name=f"{symbol} ({source})",
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Stock Price History",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    except Exception as e:
        # Return empty figure if error
        fig = go.Figure()
        fig.add_annotation(text=f"Unable to load chart: {str(e)}", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig

def create_technical_indicators_chart(symbols, timeframe="1y"):
    """Create technical indicators chart with RSI and MACD"""
    try:
        if not symbols:
            return go.Figure()
        
        symbol = symbols[0]  # Use first symbol
        hist = get_price_data(symbol, timeframe)  # Use unified data fetcher
        
        if hist.empty:
            return go.Figure()
        
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'{symbol} Price', 'RSI', 'MACD'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price chart
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist['Close'], name='Price', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=hist.index, y=rsi, name='RSI', line=dict(color='purple', width=2)),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(x=hist.index, y=macd, name='MACD', line=dict(color='blue', width=2)),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=hist.index, y=signal, name='Signal', line=dict(color='orange', width=2)),
            row=3, col=1
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Unable to load indicators: {str(e)}", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig

def create_portfolio_allocation_chart(symbols):
    """Create portfolio allocation pie chart"""
    try:
        if not symbols:
            return go.Figure()
        
        # Equal weight allocation
        weights = [1.0 / len(symbols)] * len(symbols)
        
        fig = go.Figure(data=[go.Pie(
            labels=symbols,
            values=weights,
            hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title="Portfolio Allocation (Equal Weight)",
            height=400,
            template='plotly_white'
        )
        
        return fig
    except Exception:
        return go.Figure()

def create_sector_performance_chart():
    """Create sector performance comparison chart"""
    try:
        import yfinance as yf
        
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Industrials': 'XLI',
            'Consumer Staples': 'XLP',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE'
        }
        
        returns = {}
        for sector, etf in sector_etfs.items():
            ticker = yf.Ticker(etf)
            hist = ticker.history(period='1y')
            if not hist.empty and len(hist) > 1:
                ret = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                returns[sector] = ret
        
        sectors = list(returns.keys())
        values = list(returns.values())
        colors = ['green' if v > 0 else 'red' for v in values]
        
        fig = go.Figure(data=[
            go.Bar(x=sectors, y=values, marker_color=colors, text=[f"{v:.1f}%" for v in values], textposition='outside')
        ])
        
        fig.update_layout(
            title="Sector Performance (1 Year)",
            xaxis_title="Sector",
            yaxis_title="Return (%)",
            height=500,
            template='plotly_white'
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Unable to load sector data: {str(e)}", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig

def create_correlation_heatmap(symbols, timeframe="1y"):
    """Create correlation matrix heatmap"""
    try:
        if len(symbols) < 2:
            return go.Figure()
        
        # Get historical data for all symbols
        data = {}
        for symbol in symbols:
            hist = get_price_data(symbol, timeframe)  # Use unified data fetcher
            if not hist.empty:
                data[symbol] = hist['Close']
        
        # Create dataframe and calculate correlation
        df = pd.DataFrame(data)
        corr = df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Stock Correlation Matrix",
            height=500,
            template='plotly_white'
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Unable to load correlation: {str(e)}", 
                          xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig

def create_performance_comparison(symbols, timeframe="1y"):
    """Create performance comparison bar chart"""
    try:
        if not symbols:
            return go.Figure()
        
        performance = {}
        for symbol in symbols:
            hist = get_price_data(symbol, timeframe)  # Use unified data fetcher
            if not hist.empty and len(hist) > 1:
                ret = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                performance[symbol] = ret
        
        symbols_list = list(performance.keys())
        returns_list = list(performance.values())
        colors = ['green' if v > 0 else 'red' for v in returns_list]
        
        fig = go.Figure(data=[
            go.Bar(
                x=symbols_list, 
                y=returns_list, 
                marker_color=colors,
                text=[f"{v:.1f}%" for v in returns_list],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=f"Performance Comparison ({timeframe})",
            xaxis_title="Symbol",
            yaxis_title="Return (%)",
            height=400,
            template='plotly_white'
        )
        
        return fig
    except Exception:
        return go.Figure()

def create_volume_chart(symbols, timeframe="1y"):
    """Create volume analysis chart for all symbols"""
    try:
        from plotly.subplots import make_subplots
        
        if not symbols:
            return go.Figure()
        
        # Create subplots for each symbol
        num_symbols = len(symbols)
        subplot_titles = []
        for s in symbols:
            source = "CoinGecko" if is_crypto_symbol(s) else "Yahoo Finance"
            subplot_titles.append(f'{s} Trading Volume ({source})')
        
        fig = make_subplots(
            rows=num_symbols, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles
        )
        
        for idx, symbol in enumerate(symbols):
            # Use unified data fetcher (crypto or stock)
            hist = get_price_data(symbol, timeframe)
            
            if not hist.empty:
                colors = ['red' if hist['Close'].iloc[i] < hist['Open'].iloc[i] else 'green' 
                         for i in range(len(hist))]
                
                fig.add_trace(
                    go.Bar(x=hist.index, y=hist['Volume'], marker_color=colors, name=symbol),
                    row=idx+1, col=1
                )
        
        fig.update_layout(
            height=300 * num_symbols,  # Dynamic height based on symbols
            showlegend=False,
            template='plotly_white'
        )
        
        fig.update_xaxes(title_text="Date", row=num_symbols, col=1)
        fig.update_yaxes(title_text="Volume")
        
        return fig
    except Exception:
        return go.Figure()

def run_analysis_with_viz(question, analysis_type, symbols_input, timeframe, risk_tolerance, progress=gr.Progress()):
    """Run financial analysis and generate visualizations"""
    try:
        # Parse and validate symbols
        symbols = []
        if symbols_input and symbols_input.strip():
            for s in symbols_input.split(","):
                symbol = s.strip().upper()
                # Only include valid alphabetic symbols (API requirement)
                if symbol and symbol.isalpha() and len(symbol) <= 10:
                    symbols.append(symbol)
        
        # Ensure question is not empty
        if not question or not question.strip():
            return (
                "❌ **Error:** Please enter a question",
                go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()
            )
        
        payload = {
            "question": question.strip(),
            "analysis_type": analysis_type,
            "symbols": symbols,
            "timeframe": timeframe,
            "risk_tolerance": risk_tolerance
        }
        
        progress(0.2, desc="🤖 Initializing LangGraph workflow...")
        
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=300
        )
        
        progress(0.8, desc="📊 Processing results...")
        
        if response.status_code == 200:
            result = response.json()
            progress(1.0, desc="✅ Analysis complete!")
            
            # Store in history
            query_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "question": question,
                "analysis_type": analysis_type,
                "symbols": symbols,
                "processing_time": result.get('processing_time', 0),
                "framework": "LangGraph + Gorq"
            })
            
            # Generate visualizations
            price_chart = create_stock_price_chart(symbols, timeframe) if symbols else go.Figure()
            tech_chart = create_technical_indicators_chart(symbols, timeframe) if symbols else go.Figure()
            allocation_chart = create_portfolio_allocation_chart(symbols) if symbols else go.Figure()
            sector_chart = create_sector_performance_chart()
            corr_chart = create_correlation_heatmap(symbols, timeframe) if len(symbols) > 1 else go.Figure()
            perf_chart = create_performance_comparison(symbols, timeframe) if symbols else go.Figure()
            volume_chart = create_volume_chart(symbols, timeframe) if symbols else go.Figure()
            
            return (
                format_analysis_result(result),
                price_chart,
                tech_chart,
                allocation_chart,
                sector_chart,
                corr_chart,
                perf_chart,
                volume_chart
            )
        elif response.status_code == 422:
            # Validation error - show details
            try:
                error_detail = response.json()
                error_msg = "❌ **Validation Error:**\n\n"
                if 'detail' in error_detail:
                    if isinstance(error_detail['detail'], list):
                        for err in error_detail['detail']:
                            field = err.get('loc', ['unknown'])[-1]
                            msg = err.get('msg', 'Validation failed')
                            error_msg += f"- **{field}**: {msg}\n"
                    else:
                        error_msg += f"{error_detail['detail']}\n"
                error_msg += "\n**Tip:** Make sure:\n"
                error_msg += "- Question is not empty\n"
                error_msg += "- Symbols contain only letters (A-Z)\n"
                error_msg += "- Symbols are comma-separated (e.g., AAPL, MSFT)\n"
            except Exception:
                error_msg = "❌ **Validation Error:** Please check your input format"
            
            empty_fig = go.Figure()
            return (error_msg, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)
        else:
            empty_fig = go.Figure()
            error_msg = format_analysis_result({"error": f"API returned status {response.status_code}"})
            return (error_msg, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)
    
    except Exception as e:
        empty_fig = go.Figure()
        error_msg = format_analysis_result({"error": str(e)})
        return (error_msg, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)

def get_system_status():
    """Get system status information"""
    api_healthy, api_info = check_api_health()
    
    if api_healthy:
        status = f"""
        ✅ **API Connected**
        - Framework: {api_info.get("framework", "Unknown")}
        - LLM: {api_info.get("llm", "Unknown")}
        - Status: {api_info.get("status", "Unknown")}
        """
        return status
    else:
        status = f"""
        ❌ **API Connection Failed**
        - Error: {api_info.get('error', 'Unknown error')}
        """
        return status

def format_analysis_result(result):
    """Format analysis result for display"""
    if result.get('error'):
        return f"❌ **Analysis failed:** {result['error']}"
    
    if not result.get('success'):
        return f"❌ **Analysis failed:** {result.get('error', 'Unknown error')}"
    
    # Display metadata
    metadata_text = ""
    if 'data' in result and 'metadata' in result['data']:
        meta = result['data']['metadata']
        metadata_text = f"""
        **Analysis Metadata:**
        - Type: {meta.get('analysis_type', 'N/A').title()}
        - Symbols: {', '.join(meta.get('symbols', [])) if meta.get('symbols') else 'General Market Analysis'}
        - Timeframe: {meta.get('timeframe', 'N/A')}
        - Processing Time: {result.get('processing_time', 0):.2f}s
        
        ---
        """
    
    # Display the analysis
    analysis_text = ""
    if 'data' in result and 'final_analysis' in result['data']:
        analysis_text = result['data']['final_analysis']
    
    return metadata_text + analysis_text

# Create the Gradio interface
def create_interface():
    with gr.Blocks(
        title="MarketSage Analytics - Financial AI with Visualizations",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1800px !important;
        }
        .main-header {
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, #1f77b4, #ff7f0e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .info-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .quick-action-btn {
            margin: 0.5rem;
            padding: 1rem;
            border-radius: 8px;
            font-weight: bold;
        }
        .chart-container {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .status-good {
            background: #4caf50;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: inline-block;
        }
        .status-bad {
            background: #f44336;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: inline-block;
        }
        """
    ) as demo:
        
        gr.HTML('<h1 class="main-header">📈 MarketSage Analytics</h1>')
        gr.HTML('<p style="text-align: center; font-size: 1.3rem;">Advanced Financial Analysis with Interactive Visualizations | Powered by Multi-Agent AI</p>')
        
        # Network access info
        local_ip = get_local_ip()
        gr.HTML(f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center;">
            <h3>🌐 Network Access</h3>
            <p><strong>Local:</strong> http://localhost:7860 | <strong>Network:</strong> http://{local_ip}:7860</p>
        </div>
        ''')
        
        with gr.Tabs():
            # Analysis with Visualizations Tab
            with gr.Tab("📊 Analysis & Charts"):
                # Quick Templates Section
                gr.Markdown("### ⚡ Quick Start Templates")
                with gr.Row():
                    with gr.Column(scale=1):
                        template_btn1 = gr.Button("📈 Tech Stock Analysis", variant="secondary", size="sm")
                    with gr.Column(scale=1):
                        template_btn2 = gr.Button("💎 Crypto Sentiment", variant="secondary", size="sm")
                    with gr.Column(scale=1):
                        template_btn3 = gr.Button("📊 Portfolio Review", variant="secondary", size="sm")
                    with gr.Column(scale=1):
                        template_btn4 = gr.Button("⚠️ Risk Assessment", variant="secondary", size="sm")
                
                gr.Markdown("---")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎛️ Analysis Controls")
                        
                        # Using Accordion for better organization
                        with gr.Accordion("📋 Analysis Settings", open=True):
                            analysis_type = gr.Dropdown(
                                choices=["comprehensive", "quick", "technical", "risk", "sentiment", "portfolio", "crypto"],
                                value="comprehensive",
                                label="Analysis Type",
                                info="Choose your analysis focus"
                            )
                            
                            timeframe = gr.Dropdown(
                                choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
                                value="1y",
                                label="Timeframe",
                                info="Data period for analysis"
                            )
                            
                            risk_tolerance = gr.Dropdown(
                                choices=["conservative", "moderate", "aggressive"],
                                value="moderate",
                                label="Risk Tolerance",
                                info="Your investment risk profile"
                            )
                        
                        with gr.Accordion("🎯 Symbols & Question", open=True):
                            symbols_input = gr.Textbox(
                                label="Symbols (comma-separated)",
                                placeholder="AAPL, MSFT, GOOGL or BTC, ETH",
                                info="⚠️ Letters only (A-Z), max 10 chars per symbol. Leave empty for general market analysis."
                            )
                            
                            question = gr.Textbox(
                                label="Your Financial Question:",
                                value="Analyze the technology sector performance",
                                lines=4,
                                placeholder="Ask any financial question..."
                            )
                        
                        analyze_btn = gr.Button("🚀 Run Analysis with Visualizations", variant="primary", size="lg")
                        
                        # System status
                        with gr.Accordion("🔧 System Status", open=False):
                            status_display = gr.Markdown()
                            status_btn = gr.Button("🔄 Check Status", variant="secondary", size="sm")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📝 Analysis Results")
                        results_display = gr.Markdown()
                
                # Visualization Section
                with gr.Accordion("📊 Interactive Data Visualizations", open=True):
                    gr.Markdown("*Charts will appear here after analysis*")
                    
                    with gr.Tabs():
                        with gr.Tab("📈 Price & Volume"):
                            with gr.Row():
                                with gr.Column():
                                    price_chart = gr.Plot(label="Stock Price History")
                                with gr.Column():
                                    volume_chart = gr.Plot(label="Trading Volume")
                        
                        with gr.Tab("📊 Technical Indicators"):
                            tech_indicators_chart = gr.Plot(label="Technical Indicators (Price, RSI, MACD)")
                        
                        with gr.Tab("💼 Portfolio & Performance"):
                            with gr.Row():
                                with gr.Column():
                                    allocation_chart = gr.Plot(label="Portfolio Allocation")
                                with gr.Column():
                                    performance_chart = gr.Plot(label="Performance Comparison")
                        
                        with gr.Tab("🔗 Sector & Correlation"):
                            with gr.Row():
                                with gr.Column():
                                    sector_chart = gr.Plot(label="Sector Performance")
                                with gr.Column():
                                    correlation_chart = gr.Plot(label="Correlation Matrix")
                
                # Template button functions
                def load_tech_template():
                    return (
                        "technical",  # analysis_type
                        "3mo",        # timeframe
                        "moderate",   # risk_tolerance
                        "AAPL, MSFT, GOOGL, NVDA",  # symbols
                        "Analyze technical indicators and trading signals for major tech stocks. What are the buy/sell signals?"  # question
                    )
                
                def load_crypto_template():
                    return (
                        "sentiment",  # analysis_type
                        "1mo",        # timeframe
                        "aggressive", # risk_tolerance
                        "BTC, ETH",   # symbols
                        "What is the current market sentiment for Bitcoin and Ethereum? Are investors showing fear or greed?"  # question
                    )
                
                def load_portfolio_template():
                    return (
                        "portfolio",  # analysis_type
                        "1y",         # timeframe
                        "moderate",   # risk_tolerance
                        "AAPL, MSFT, GOOGL, AMZN, TSLA",  # symbols
                        "Analyze my portfolio allocation and provide optimization recommendations. How should I rebalance?"  # question
                    )
                
                def load_risk_template():
                    return (
                        "risk",       # analysis_type
                        "6mo",        # timeframe
                        "conservative",  # risk_tolerance
                        "SPY, GOLD, BTC",  # symbols
                        "What are the key risks in current market conditions? How can I hedge my portfolio?"  # question
                    )
                
                # Event handlers
                # Template buttons
                template_btn1.click(
                    load_tech_template,
                    outputs=[analysis_type, timeframe, risk_tolerance, symbols_input, question]
                )
                template_btn2.click(
                    load_crypto_template,
                    outputs=[analysis_type, timeframe, risk_tolerance, symbols_input, question]
                )
                template_btn3.click(
                    load_portfolio_template,
                    outputs=[analysis_type, timeframe, risk_tolerance, symbols_input, question]
                )
                template_btn4.click(
                    load_risk_template,
                    outputs=[analysis_type, timeframe, risk_tolerance, symbols_input, question]
                )
                
                status_btn.click(get_system_status, outputs=[status_display])
                
                analyze_btn.click(
                    run_analysis_with_viz,
                    inputs=[question, analysis_type, symbols_input, timeframe, risk_tolerance],
                    outputs=[
                        results_display, 
                        price_chart, 
                        tech_indicators_chart, 
                        allocation_chart,
                        sector_chart,
                        correlation_chart,
                        performance_chart,
                        volume_chart
                    ]
                )
                
                demo.load(get_system_status, outputs=[status_display])
            
            # Quick Charts Tab
            with gr.Tab("📈 Quick Charts"):
                gr.Markdown("### ⚡ Generate Charts Without AI Analysis (< 5 seconds)")
                gr.Markdown("*Perfect for quick visualization of stock/crypto data*")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        chart_symbols = gr.Textbox(
                            label="Symbols (comma-separated)",
                            placeholder="AAPL, MSFT, GOOGL",
                            value="AAPL, MSFT",
                            info="⚠️ Letters only (A-Z). Enter 2-5 symbols for best results."
                        )
                    with gr.Column(scale=1):
                        chart_timeframe = gr.Dropdown(
                            choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                            value="1y",
                            label="Timeframe",
                            info="Historical data period"
                        )
                    with gr.Column(scale=1):
                        chart_btn = gr.Button("📊 Generate Charts", variant="primary", size="lg")
                
                # Quick examples
                gr.Markdown("**💡 Quick Examples:**")
                with gr.Row():
                    ex_btn1 = gr.Button("Tech Giants (AAPL, MSFT, GOOGL)", variant="secondary", size="sm")
                    ex_btn2 = gr.Button("Crypto (BTC, ETH, SOL)", variant="secondary", size="sm")
                    ex_btn3 = gr.Button("Safe Havens (GOLD, BTC, SPY)", variant="secondary", size="sm")
                
                gr.Markdown("---")
                
                with gr.Tabs():
                    with gr.Tab("📈 Price History"):
                        quick_price_chart = gr.Plot(label="Price Chart")
                    
                    with gr.Tab("📊 Technical Indicators"):
                        quick_tech_chart = gr.Plot(label="Technical Analysis")
                    
                    with gr.Tab("🔗 Correlation"):
                        quick_corr_chart = gr.Plot(label="Correlation Matrix")
                
                def generate_quick_charts(symbols_str, tf):
                    symbols = [s.strip().upper() for s in symbols_str.split(",") if s.strip()]
                    return (
                        create_stock_price_chart(symbols, tf),
                        create_technical_indicators_chart(symbols, tf),
                        create_correlation_heatmap(symbols, tf)
                    )
                
                # Example button handlers
                ex_btn1.click(lambda: "AAPL, MSFT, GOOGL", outputs=[chart_symbols])
                ex_btn2.click(lambda: "BTC, ETH, SOL", outputs=[chart_symbols])
                ex_btn3.click(lambda: "GOLD, BTC, SPY", outputs=[chart_symbols])
                
                chart_btn.click(
                    generate_quick_charts,
                    inputs=[chart_symbols, chart_timeframe],
                    outputs=[quick_price_chart, quick_tech_chart, quick_corr_chart]
                )
        
        # Footer
        gr.HTML("""
        <div style='text-align: center; color: #666; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;'>
            <p><strong>MarketSage Analytics v3.1 Enhanced</strong> | Multi-Agent AI with Interactive Visualizations</p>
            <p>✨ <strong>New:</strong> Quick Templates, Better Organization, Enhanced Visual Management</p>
            <p>Built with FastAPI, Gradio, Plotly, Groq LLM, and LangGraph</p>
        </div>
        """)
    
    return demo

# Launch the interface
if __name__ == "__main__":
    demo = create_interface()
    
    local_ip = get_local_ip()
    
    print("🚀 Starting MarketSage Analytics with Visualizations...")
    print("📱 Local Access: http://localhost:7860")
    print(f"🌐 Network Access: http://{local_ip}:7860")
    print("📊 Features: AI Analysis + Interactive Charts")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

