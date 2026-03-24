# 🧠 MarketSage Analytics

A sophisticated multi-agent financial analysis system built with LangGraph and powered by Gorq LLM. MarketSage Analytics provides comprehensive financial analysis through specialized AI agents working in a coordinated workflow, delivering intelligent market insights and investment recommendations.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.16-purple.svg)
![Gorq](https://img.shields.io/badge/Gorq-LLM-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)

## 🚀 Features

### 🤖 Multi-Agent Architecture
- **Market Research Agent** - Real-time market data and trends analysis
- **Financial Data Agent** - Comprehensive financial metrics and ratios
- **Technical Analysis Agent** - Chart patterns and technical indicators
- **Risk Assessment Agent** - Portfolio risk evaluation and management
- **Sentiment Analysis Agent** - Market sentiment and news analysis
- **Portfolio Analysis Agent** - Asset allocation and optimization
- **Sector Analysis Agent** - Sector performance and rotation analysis
- **Crypto Analysis Agent** - Cryptocurrency market analysis with technical indicators

### 📊 Analysis Types
- **Comprehensive Analysis** - Full multi-agent analysis
- **Quick Analysis** - Fast stock price and basic info
- **Technical Analysis** - Chart patterns, moving averages, RSI, MACD
- **Risk Assessment** - Volatility analysis and risk mitigation
- **Sentiment Analysis** - Market mood and news sentiment
- **Portfolio Analysis** - Diversification and optimization
- **Crypto Analysis** - Cryptocurrency market analysis with price trends and indicators

### 🎯 Key Capabilities
- Real-time stock data via Yahoo Finance
- Cryptocurrency data via CoinGecko API
- Live market news via DuckDuckGo Search
- Interactive Gradio interface
- FastAPI backend with comprehensive endpoints
- Portfolio risk assessment and optimization
- Technical indicator calculations (RSI, MACD, volatility)
- Market sentiment analysis
- Crypto correlation analysis
- Query history tracking and statistics

## 🛠️ Tech Stack

- **Frontend:** Gradio
- **Backend:** FastAPI
- **AI Framework:** LangGraph (multi-agent workflow system)
- **LLM:** Groq LLM (with OpenAI fallback)
- **Data Sources:** Yahoo Finance, CoinGecko, DuckDuckGo Search
- **Crypto Data:** pycoingecko (with support for CryptoQuant, Glassnode, LunarCrush)
- **Deployment:** Docker-ready, Hugging Face Spaces compatible

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (or OpenAI API key as fallback)
- Git (for cloning)
- Optional: API keys for advanced crypto data (CryptoQuant, Glassnode, LunarCrush)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MarketSage-Analytics
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the system:**
   
   **Option A: Run backend and frontend separately**
   ```bash
   # Terminal 1 - Backend
   python main.py
   
   # Terminal 2 - Frontend
   python run_frontend.py
   ```
   
   **Option B: Run with Docker (coming soon)**
   ```bash
   docker-compose up
   ```

6. **Access the application:**
   - Frontend: http://localhost:7860
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎮 Usage

### Quick Start
1. **Select Analysis Type** from the sidebar (comprehensive, quick, technical, risk, sentiment, portfolio, crypto)
2. **Enter Stock or Crypto Symbols** 
   - Stocks: AAPL, MSFT, GOOGL
   - Crypto: BTC, ETH, SOL, DOGE
3. **Choose Timeframe** (1d, 1mo, 1y, etc.)
4. **Click "Run LangGraph Analysis"**
5. **View Results** in the main panel

### API Usage

#### Financial Analysis
```python
import requests

response = requests.post("http://localhost:8000/analyze", json={
    "question": "What's the market outlook for AI stocks?",
    "analysis_type": "comprehensive",
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "timeframe": "1y",
    "risk_tolerance": "moderate"
})

result = response.json()
print(result["data"]["final_analysis"])
```

#### Portfolio Analysis
```python
response = requests.post("http://localhost:8000/portfolio", json={
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
    "risk_tolerance": "moderate"
})

result = response.json()
print(result["data"]["final_analysis"])
```

#### Crypto Analysis
```python
response = requests.post("http://localhost:8000/analyze", json={
    "question": "Analyze the crypto market trends for Bitcoin and Ethereum",
    "analysis_type": "crypto",
    "symbols": ["BTC", "ETH", "SOL"],
    "timeframe": "7d",
    "risk_tolerance": "moderate"
})

result = response.json()
print(result["data"]["final_analysis"])
# Access crypto-specific data
print(result["data"]["individual_analyses"]["crypto_analysis"])
```

## 📁 Project Structure

```
MarketSage-Analytics/
├── src/
│   ├── agents/              # Individual agent implementations
│   ├── tools/               # Financial tools and Gorq LLM integration
│   │   ├── gorq_llm.py     # Gorq LLM integration
│   │   └── financial_tools.py  # Financial analysis tools
│   ├── workflows/           # LangGraph workflow definitions
│   │   └── financial_analysis_workflow.py
│   ├── api/                 # FastAPI backend
│   │   └── main.py
│   └── frontend/            # Streamlit frontend
│       └── app.py
├── tests/                   # Test files
├── docs/                    # Documentation
├── main.py                  # Backend entry point
├── run_frontend.py          # Frontend entry point
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)
- `GROQ_BASE_URL`: Groq API base URL (optional)
- `GROQ_MODEL`: Groq model name (optional)
- `OPENAI_API_KEY`: OpenAI API key (fallback if Groq unavailable)
- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)

### Crypto Data Providers (Optional)
- `COINGECKO_API_KEY`: Free tier works, API key optional for higher limits
- `CRYPTOQUANT_API_KEY`: For on-chain metrics (placeholder - requires implementation)
- `GLASSNODE_API_KEY`: For blockchain analytics (placeholder - requires implementation)
- `LUNARCRUSH_API_KEY`: For social sentiment (placeholder - requires implementation)

### Customization
- Modify agent instructions in `src/workflows/financial_analysis_workflow.py`
- Add new analysis types in the frontend
- Customize UI styling in the Gradio app
- Add new data sources or tools
- Integrate advanced crypto data providers (CryptoQuant, Glassnode, LunarCrush) in `src/tools/crypto_data_tools.py`

## 🚀 Deployment

### Hugging Face Spaces
1. Create a new Space on Hugging Face
2. Upload the project files
3. Add your API keys in Space settings
4. Deploy and share your live app!

### Docker Deployment
```bash
# Build the image
docker build -t marketsage-analytics .

# Run the container
docker run -p 8000:8000 -p 8501:8501 marketsage-analytics
```

### Cloud Deployment
- **Railway:** Deploy FastAPI backend
- **Render:** Host both frontend and backend
- **Heroku:** Full-stack deployment
- **Vercel:** Frontend-only deployment

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_workflow.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph Framework** for multi-agent workflow capabilities
- **Gorq LLM** for advanced language model capabilities
- **Yahoo Finance** for financial data
- **DuckDuckGo** for news search
- **Streamlit** for the web interface
- **FastAPI** for the backend API

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-username/marketsage-analytics/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-username/marketsage-analytics/discussions)
- **Email:** your-email@example.com

## ⚠️ Disclaimer

This application is for educational and research purposes only. The financial analysis provided should not be considered as investment advice. Always consult with qualified financial professionals before making investment decisions.

---

**Made with ❤️ by [Your Name]**

*MarketSage Analytics - Intelligent financial analysis powered by AI agents and LangGraph*
