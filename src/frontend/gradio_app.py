"""
Enhanced Gradio Frontend for MarketSage Analytics
Advanced Financial Analysis Platform with Multi-Agent AI
"""

import gradio as gr
import requests
import pandas as pd
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
        # Connect to a remote server to determine local IP
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

def run_analysis(question, analysis_type, symbols_input, timeframe, risk_tolerance, progress=gr.Progress()):
    """Run financial analysis using the API"""
    try:
        # Parse symbols
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()] if symbols_input else []
        
        payload = {
            "question": question,
            "analysis_type": analysis_type,
            "symbols": symbols,
            "timeframe": timeframe,
            "risk_tolerance": risk_tolerance
        }
        
        progress(0.2, desc="🤖 Initializing LangGraph workflow...")
        
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=payload,
            timeout=300  # 5 minute timeout
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
            
            return format_analysis_result(result)
        else:
            return format_analysis_result({"error": f"API returned status {response.status_code}"})
    
    except requests.exceptions.RequestException as e:
        return format_analysis_result({"error": str(e)})

def run_portfolio_analysis(symbols_input, risk_tolerance, progress=gr.Progress()):
    """Run portfolio analysis using the API"""
    try:
        # Parse symbols
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()] if symbols_input else []
        
        payload = {
            "symbols": symbols,
            "weights": None,
            "risk_tolerance": risk_tolerance
        }
        
        progress(0.5, desc="📊 Analyzing portfolio composition and risk...")
        
        response = requests.post(
            f"{API_BASE_URL}/portfolio",
            json=payload,
            timeout=300
        )
        
        progress(1.0, desc="✅ Portfolio analysis complete!")
        
        if response.status_code == 200:
            return format_portfolio_result(response.json())
        else:
            return format_portfolio_result({"error": f"API returned status {response.status_code}"})
    
    except requests.exceptions.RequestException as e:
        return format_portfolio_result({"error": str(e)})

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

def get_query_history():
    """Get formatted query history"""
    if not query_history:
        return "📝 No query history available yet. Start by running some analyses!"
    
    df = pd.DataFrame(query_history)
    return df[['timestamp', 'question', 'analysis_type', 'symbols', 'processing_time', 'framework']].to_string(index=False)

def get_statistics():
    """Get analysis statistics"""
    api_healthy, _ = check_api_health()
    
    if not api_healthy:
        return "❌ Cannot load statistics - API not available"
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            
            stats_text = f"""
            **Analysis Statistics**
            
            - Total Queries: {stats.get('total_queries', 0)}
            - Average Processing Time: {stats.get('average_processing_time', 0):.2f}s
            - Framework: LangGraph + Groq
            
            **Analysis Types Distribution:**
            """
            
            if stats.get('analysis_types'):
                for analysis_type, count in stats['analysis_types'].items():
                    stats_text += f"\n- {analysis_type.title()}: {count}"
            
            stats_text += "\n\n**Most Analyzed Symbols:**"
            if stats.get('most_analyzed_symbols'):
                for symbol, count in stats['most_analyzed_symbols'][:10]:
                    stats_text += f"\n- {symbol}: {count}"
            
            return stats_text
        else:
            return "❌ Failed to load statistics"
    except Exception as e:
        return f"❌ Error loading statistics: {str(e)}"

def get_overview_content():
    """Get comprehensive overview content"""
    local_ip = get_local_ip()
    
    overview_content = f"""
    # 🚀 MarketSage Analytics - System Overview
    
    ## 🎯 What We Built
    
    **MarketSage Analytics** is an advanced financial analysis platform powered by **Multi-Agent AI** and **LangGraph**. It provides comprehensive, real-time financial analysis using multiple specialized AI agents working together.
    
    ### 🏗️ System Architecture
    
    **Backend Framework:**
    - **LangGraph**: Orchestrates multiple AI agents in a sophisticated workflow
    - **FastAPI**: High-performance REST API for financial analysis
    - **Groq LLM**: Lightning-fast inference for real-time analysis
    - **Multi-Agent System**: 8 specialized AI agents for different analysis types
    
    **Frontend:**
    - **Gradio**: Modern, responsive web interface
    - **Real-time Progress**: Live updates during analysis
    - **Network Accessible**: Available from any device on your network
    
    ## 🤖 AI Agents & Their Roles
    
    ### 1. 📊 Market Research Agent
    - **Purpose**: Analyzes market trends, news, and economic indicators
    - **Capabilities**: News sentiment, market conditions, regulatory environment
    - **Data Sources**: Financial news, market data, economic indicators
    
    ### 2. 💰 Financial Data Agent
    - **Purpose**: Processes stock data, financial metrics, and ratios
    - **Capabilities**: P/E ratios, market cap, revenue analysis, growth metrics
    - **Data Sources**: Yahoo Finance, real-time stock data
    
    ### 3. 📈 Technical Analysis Agent
    - **Purpose**: Provides technical indicators and trading signals
    - **Capabilities**: Moving averages, RSI, MACD, support/resistance levels
    - **Data Sources**: Historical price data, technical indicators
    
    ### 4. ⚠️ Risk Assessment Agent
    - **Purpose**: Evaluates investment risks and provides mitigation strategies
    - **Capabilities**: Volatility analysis, beta calculations, risk metrics
    - **Data Sources**: Historical volatility, correlation analysis
    
    ### 5. 😊 Sentiment Analysis Agent
    - **Purpose**: Analyzes market sentiment from news and social media
    - **Capabilities**: News sentiment, social media analysis, investor mood
    - **Data Sources**: Financial news, social media feeds
    
    ### 6. 📋 Portfolio Analysis Agent
    - **Purpose**: Optimizes portfolio allocation and diversification
    - **Capabilities**: Portfolio metrics, allocation recommendations, rebalancing
    - **Data Sources**: Portfolio composition, correlation matrices
    
    ### 7. 🏭 Sector Analysis Agent
    - **Purpose**: Analyzes sector performance and rotation opportunities
    - **Capabilities**: Sector trends, rotation analysis, sector allocation
    - **Data Sources**: Sector ETFs, industry performance data
    
    ### 8. 💎 Crypto Analysis Agent
    - **Purpose**: Analyzes cryptocurrency markets and digital assets
    - **Capabilities**: Crypto price analysis, RSI/MACD for crypto, volatility assessment, correlation analysis
    - **Data Sources**: CoinGecko, real-time crypto data
    
    ### 9. 🎯 Final Synthesis Agent
    - **Purpose**: Combines all analyses into comprehensive executive reports
    - **Capabilities**: Executive summaries, actionable recommendations, risk assessment
    - **Output**: Professional financial reports with clear insights
    
    ## 🔄 How It Works
    
    ### LangGraph Workflow:
    1. **Market Research** → Initial market context and news analysis
    2. **Parallel Analysis** → All 7 analysis agents work simultaneously
    3. **Final Synthesis** → Comprehensive report generation
    
    ### Analysis Types:
    - **Comprehensive**: Full multi-agent analysis (2-5 minutes)
    - **Quick**: Fast market overview (30-60 seconds)
    - **Technical**: Technical indicators and trading signals
    - **Risk**: Risk assessment and mitigation strategies
    - **Sentiment**: Market sentiment and psychology analysis
    - **Portfolio**: Portfolio optimization and allocation
    - **Crypto**: Cryptocurrency market analysis with technical indicators
    
    ## 🛠️ Why We Built It This Way
    
    ### 1. **Multi-Agent Architecture**
    - **Specialization**: Each agent is an expert in its domain
    - **Parallel Processing**: Multiple analyses run simultaneously
    - **Comprehensive Coverage**: No aspect of financial analysis is missed
    
    ### 2. **LangGraph Orchestration**
    - **Workflow Management**: Sophisticated agent coordination
    - **State Management**: Proper handling of complex data flows
    - **Error Handling**: Robust error recovery and fallback mechanisms
    
    ### 3. **Real-Time Analysis**
    - **Live Data**: Current market data and news
    - **Fast Inference**: Groq LLM for sub-second response times
    - **Progress Tracking**: Real-time updates during analysis
    
    ### 4. **Network Accessibility**
    - **Multi-Device Access**: Use from any device on your network
    - **Team Collaboration**: Share analyses with colleagues
    - **Remote Access**: Access from anywhere with network connectivity
    
    ## 🚀 How to Improve & Extend
    
    ### Immediate Improvements:
    1. **Add More Data Sources**: Bloomberg, Reuters, SEC filings
    2. **Enhanced Visualization**: Interactive charts and graphs
    3. **Historical Analysis**: Backtesting and performance tracking
    4. **Alert System**: Real-time notifications for market events
    
    ### Advanced Features:
    1. **Custom Models**: Fine-tuned models for specific sectors
    2. **API Integrations**: Connect to trading platforms
    3. **Database Storage**: Persistent analysis history
    4. **User Authentication**: Multi-user support with permissions
    
    ### Technical Enhancements:
    1. **Caching Layer**: Redis for faster repeated analyses
    2. **Load Balancing**: Handle multiple concurrent users
    3. **Monitoring**: System health and performance metrics
    4. **Deployment**: Docker containers for easy deployment
    
    ## 🌐 Network Access
    
    **Local Access**: http://localhost:7860
    **Network Access**: http://{local_ip}:7860
    
    **To access from other devices:**
    1. Make sure devices are on the same network
    2. Use the network IP address shown above
    3. Ensure firewall allows connections on port 7860
    
    ## 📊 System Status
    
    **Current Configuration:**
    - Framework: LangGraph + Groq LLM
    - API Endpoint: {API_BASE_URL}
    - Network IP: {local_ip}
    - Port: 7860
    
    **Ready for:**
    - ✅ Real-time financial analysis
    - ✅ Multi-agent AI processing
    - ✅ Network accessibility
    - ✅ Comprehensive reporting
    
    ---
    
    **Built with ❤️ using LangGraph, FastAPI, Gradio, and Multi-Agent AI**
    """
    
    return overview_content

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
        - Symbols: {len(meta.get('symbols', []))}
        - Timeframe: {meta.get('timeframe', 'N/A')}
        - Processing Time: {result.get('processing_time', 0):.2f}s
        
        ---
        """
    
    # Display the analysis
    analysis_text = ""
    if 'data' in result and 'final_analysis' in result['data']:
        analysis_text = result['data']['final_analysis']
    
    return metadata_text + analysis_text

def format_portfolio_result(result):
    """Format portfolio analysis result for display"""
    if result.get('error'):
        return f"❌ **Portfolio analysis failed:** {result['error']}"
    
    if not result.get('success'):
        return f"❌ **Portfolio analysis failed:** {result.get('error', 'Unknown error')}"
    
    if 'data' in result and 'final_analysis' in result['data']:
        return result['data']['final_analysis']
    
    return "No portfolio analysis results available."

# Create the Gradio interface
def create_interface():
    with gr.Blocks(
        title="MarketSage Analytics - Advanced Financial AI Platform",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
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
        .sub-header {
            font-size: 1.3rem;
            color: #2c3e50;
            margin-bottom: 1rem;
            text-align: center;
        }
        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .status-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .network-info {
            background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
        }
        """
    ) as demo:
        
        gr.HTML('<h1 class="main-header">🚀 MarketSage Analytics</h1>')
        gr.HTML('<p class="sub-header">Advanced Financial Analysis Platform | Powered by Multi-Agent AI & LangGraph</p>')
        
        # Network access information
        local_ip = get_local_ip()
        gr.HTML(f'''
        <div class="network-info">
            <h3>🌐 Network Access</h3>
            <p><strong>Local:</strong> http://localhost:7860</p>
            <p><strong>Network:</strong> http://{local_ip}:7860</p>
            <p>Access from any device on your network!</p>
        </div>
        ''')
        
        with gr.Tabs():
            # Overview Tab
            with gr.Tab("🏠 Overview"):
                gr.Markdown(get_overview_content())
            
            # Analysis Tab
            with gr.Tab("📊 Analysis"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎛️ Analysis Controls")
                        
                        analysis_type = gr.Dropdown(
                            choices=["comprehensive", "quick", "technical", "risk", "sentiment", "portfolio", "crypto"],
                            value="comprehensive",
                            label="Analysis Type",
                            info="Choose the type of analysis you want to perform"
                        )
                        
                        timeframe = gr.Dropdown(
                            choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                            value="1y",
                            label="Timeframe",
                            info="Select the time period for analysis"
                        )
                        
                        risk_tolerance = gr.Dropdown(
                            choices=["conservative", "moderate", "aggressive"],
                            value="moderate",
                            label="Risk Tolerance",
                            info="Select your risk tolerance level"
                        )
                        
                        symbols_input = gr.Textbox(
                            label="Stock/Crypto Symbols (comma-separated)",
                            placeholder="AAPL, MSFT, GOOGL or BTC, ETH, SOL",
                            info="Enter stock or crypto symbols to analyze (optional)",
                            interactive=True
                        )
                        
                        # System status
                        gr.Markdown("### 🔧 System Status")
                        status_display = gr.Markdown()
                        status_btn = gr.Button("🔄 Check Status", variant="secondary")
                        
                    with gr.Column(scale=2):
                        gr.Markdown("### Financial Analysis")
                        
                        # Default questions for different analysis types
                        default_questions = {
                            "comprehensive": "What's the comprehensive market outlook for AI and technology stocks?",
                            "quick": "What's the current stock price and basic info for AAPL?",
                            "technical": "Analyze the technical indicators for AAPL stock",
                            "risk": "What are the key risks for the technology sector?",
                            "sentiment": "What's the current market sentiment for electric vehicle stocks?",
                            "portfolio": "How should I diversify my tech-heavy portfolio?",
                            "crypto": "Analyze the cryptocurrency market for BTC and ETH"
                        }
                        
                        question = gr.Textbox(
                            label="Enter your financial query:",
                            value="What's the comprehensive market outlook for AI and technology stocks?",
                            lines=4,
                            info="Ask any financial question and our AI agents will provide comprehensive analysis",
                            interactive=True,
                            placeholder="Enter your financial question here..."
                        )
                        
                        # Expected analysis time
                        analysis_times = {
                            "comprehensive": "2-5 minutes",
                            "quick": "30-60 seconds",
                            "technical": "1-3 minutes",
                            "risk": "1-3 minutes",
                            "sentiment": "1-3 minutes",
                            "portfolio": "1-3 minutes",
                            "crypto": "1-3 minutes"
                        }
                        
                        time_info = gr.Markdown()
                        
                        # Question suggestion
                        question_suggestion = gr.Markdown()
                        
                        analyze_btn = gr.Button("🚀 Run LangGraph Analysis", variant="primary", size="lg")
                        
                        # Results display
                        results_display = gr.Markdown()
                
                # Event handlers for analysis tab
                def update_time_info(analysis_type):
                    return f"⏱️ **Expected analysis time:** {analysis_times.get(analysis_type, '1-3 minutes')}"
                
                def suggest_question(analysis_type):
                    """Suggest a question but don't override user input"""
                    suggestion = default_questions.get(analysis_type, "What's the market outlook for AI chip companies?")
                    return f"💡 **Suggestion for {analysis_type} analysis:** {suggestion}\n\nYou can modify this question or write your own:"
                
                analysis_type.change(update_time_info, inputs=[analysis_type], outputs=[time_info])
                analysis_type.change(suggest_question, inputs=[analysis_type], outputs=[question_suggestion])
                
                status_btn.click(get_system_status, outputs=[status_display])
                
                analyze_btn.click(
                    run_analysis,
                    inputs=[question, analysis_type, symbols_input, timeframe, risk_tolerance],
                    outputs=[results_display]
                )
                
                # Initialize status and suggestions
                demo.load(get_system_status, outputs=[status_display])
                demo.load(update_time_info, inputs=[analysis_type], outputs=[time_info])
                demo.load(suggest_question, inputs=[analysis_type], outputs=[question_suggestion])
            
            # Portfolio Tab
            with gr.Tab("📈 Portfolio"):
                gr.Markdown("### Portfolio Analysis")
                
                with gr.Row():
                    with gr.Column():
                        portfolio_symbols = gr.Textbox(
                            label="Portfolio Symbols",
                            placeholder="AAPL, MSFT, GOOGL, TSLA, NVDA",
                            info="Enter the stocks in your portfolio"
                        )
                        
                        portfolio_risk = gr.Dropdown(
                            choices=["conservative", "moderate", "aggressive"],
                            value="moderate",
                            label="Risk Tolerance"
                        )
                        
                        portfolio_btn = gr.Button("📊 Analyze Portfolio", variant="primary")
                    
                    with gr.Column():
                        portfolio_results = gr.Markdown()
                
                portfolio_btn.click(
                    run_portfolio_analysis,
                    inputs=[portfolio_symbols, portfolio_risk],
                    outputs=[portfolio_results]
                )
            
            # History Tab
            with gr.Tab("📋 History"):
                gr.Markdown("### Query History")
                
                history_display = gr.Textbox(
                    label="Analysis History",
                    lines=20,
                    max_lines=20,
                    interactive=False
                )
                
                refresh_history_btn = gr.Button("🔄 Refresh History", variant="secondary")
                
                refresh_history_btn.click(get_query_history, outputs=[history_display])
                
                # Initialize history
                demo.load(get_query_history, outputs=[history_display])
            
            # Statistics Tab
            with gr.Tab("📊 Statistics"):
                gr.Markdown("### Analysis Statistics")
                
                stats_display = gr.Markdown()
                refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="secondary")
                
                refresh_stats_btn.click(get_statistics, outputs=[stats_display])
                
                # Initialize statistics
                demo.load(get_statistics, outputs=[stats_display])
        
        # Footer
        gr.HTML("""
        <div style='text-align: center; color: #666; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;'>
            <p><strong>MarketSage Analytics v2.0</strong> | Powered by Multi-Agent AI & LangGraph</p>
            <p>Built with FastAPI, Gradio, Groq LLM, and Advanced AI Workflows</p>
            <p>🌐 Network Accessible | 🤖 Multi-Agent Architecture | ⚡ Real-Time Analysis</p>
        </div>
        """)
    
    return demo

# Create and launch the interface
if __name__ == "__main__":
    demo = create_interface()
    
    # Get local IP for network access
    local_ip = get_local_ip()
    
    print("🚀 Starting MarketSage Analytics Frontend...")
    print("📱 Local Access: http://localhost:7860")
    print(f"🌐 Network Access: http://{local_ip}:7860")
    print("🔧 Make sure the backend API is running on http://localhost:8000")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0",  # Allow access from any IP
        server_port=7860,
        share=False,  # Create public link
        show_error=True
    )
