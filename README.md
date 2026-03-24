# MarketSage Analytics

A multi-agent financial analysis system built with LangGraph and powered by Groq LLM. MarketSage provides comprehensive financial analysis through specialized AI agents working in a coordinated workflow, delivering intelligent market insights, technical indicators, and interactive visualizations.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.16-purple.svg)
![Groq](https://img.shields.io/badge/Groq-LLM-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-4.x-orange.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.24-blue.svg)

---

## Features

### Multi-Agent Architecture

| Agent | Responsibility |
|-------|---------------|
| Market Research Agent | Real-time market data and trend analysis |
| Financial Data Agent | Financial metrics, ratios, and fundamentals |
| Technical Analysis Agent | Chart patterns, moving averages, RSI, MACD |
| Risk Assessment Agent | Portfolio risk evaluation and volatility analysis |
| Sentiment Analysis Agent | Market mood and news sentiment |
| Portfolio Analysis Agent | Asset allocation and optimization |
| Sector Analysis Agent | Sector performance and rotation analysis |
| Crypto Analysis Agent | Cryptocurrency market analysis with on-chain metrics |

### Analysis Types

- **Comprehensive** — Full multi-agent pipeline across all domains
- **Quick** — Fast stock price and basic fundamentals
- **Technical** — Chart patterns, RSI, MACD, moving averages
- **Risk** — Volatility analysis and risk mitigation strategies
- **Sentiment** — Market mood and news sentiment scoring
- **Portfolio** — Diversification analysis and optimization
- **Crypto** — Cryptocurrency trends, indicators, and correlation

### Interactive Visualizations

- Price history charts (stocks and crypto)
- Technical indicators (RSI, MACD) with subplots
- Portfolio allocation pie chart
- Sector performance comparison
- Correlation heatmap across symbols
- Volume analysis with color-coded bars
- Performance comparison bar chart

### Data Sources

- **Stocks:** Yahoo Finance (yfinance)
- **Crypto:** CoinGecko API (pycoingecko)
- **News:** DuckDuckGo Search

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Gradio 4.x + Plotly |
| Backend | FastAPI |
| AI Workflow | LangGraph |
| LLM | Groq (`llama-3.3-70b-versatile`) with mock fallback |
| Data | Yahoo Finance, CoinGecko, DuckDuckGo |

---

## Installation

### Prerequisites

- Python 3.8+
- Groq API key — get one free at [console.groq.com](https://console.groq.com) *(optional — falls back to mock LLM)*
- Git

### Setup

```bash
# 1. Clone the repo
git clone <repository-url>
cd MarketSage-Analytics

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp env.example .env
# Edit .env and add your GROQ_API_KEY
```

---

## Running the App

### Option A: Standard Frontend

```bash
# Terminal 1 — Start backend
python main.py

# Terminal 2 — Start frontend
python run_frontend.py
```

### Option B: Frontend with Interactive Visualizations (recommended)

```bash
# Terminal 1 — Start backend
python main.py

# Terminal 2 — Start enhanced frontend with charts
bash run_frontend_with_viz.sh
```

> **Note:** If no `GROQ_API_KEY` is set, the backend starts with a mock LLM that returns template responses. Charts and data fetching work fully regardless.

### Access

| Service | URL |
|---------|-----|
| Frontend (Gradio) | http://localhost:7860 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Usage

### Web Interface

1. Open http://localhost:7860
2. Use a **Quick Start Template** or configure manually:
   - Select **Analysis Type** (comprehensive, technical, risk, etc.)
   - Enter **Symbols** — stocks (`AAPL, MSFT`) or crypto (`BTC, ETH`)
   - Choose **Timeframe** (`1d`, `1mo`, `1y`, etc.)
   - Set **Risk Tolerance** (conservative / moderate / aggressive)
3. Click **Run Analysis with Visualizations**
4. View AI analysis results and interactive charts

The **Quick Charts** tab generates charts instantly without running AI analysis.

### REST API

**Financial analysis:**
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

**Portfolio analysis:**
```python
response = requests.post("http://localhost:8000/portfolio", json={
    "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
    "risk_tolerance": "moderate"
})
print(response.json()["data"]["final_analysis"])
```

**Crypto analysis:**
```python
response = requests.post("http://localhost:8000/analyze", json={
    "question": "Analyze Bitcoin and Ethereum market trends",
    "analysis_type": "crypto",
    "symbols": ["BTC", "ETH", "SOL"],
    "timeframe": "1mo",
    "risk_tolerance": "aggressive"
})

result = response.json()
print(result["data"]["individual_analyses"]["crypto_analysis"])
```

---

## Project Structure

```
MarketSage-Analytics/
├── src/
│   ├── agents/                        # Individual agent implementations
│   ├── tools/
│   │   ├── gorq_llm.py               # Groq LLM integration + mock fallback
│   │   ├── financial_tools.py        # Financial data fetching tools
│   │   └── crypto_data_tools.py      # CoinGecko crypto data client
│   ├── workflows/
│   │   ├── financial_analysis_workflow.py  # LangGraph workflow definition
│   │   └── state.py                  # Workflow state schema
│   ├── api/
│   │   ├── main.py                   # FastAPI routes
│   │   └── models.py                 # Pydantic request/response models
│   └── frontend/
│       ├── gradio_app.py             # Standard Gradio frontend
│       └── gradio_app_with_viz.py    # Enhanced frontend with Plotly charts
├── tests/                            # Test files
├── docs/                             # Documentation
├── main.py                           # Backend entry point
├── run_frontend.py                   # Standard frontend entry point
├── run_frontend_with_viz.sh          # Enhanced frontend launcher (with charts)
├── requirements.txt
├── env.example                       # Environment variables template
└── README.md
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Recommended | Groq API key for LLM inference |
| `OPENAI_API_KEY` | Optional | Fallback if Groq is unavailable |
| `API_BASE_URL` | Optional | Backend URL (default: `http://localhost:8000`) |
| `COINGECKO_API_KEY` | Optional | Higher rate limits for crypto data |

### Supported Symbols

- **Stocks:** Any valid Yahoo Finance ticker (e.g., `AAPL`, `TSLA`, `SPY`)
- **Crypto:** `BTC`, `ETH`, `SOL`, `BNB`, `XRP`, `ADA`, `DOGE`, `MATIC`, and more
- Symbols must be letters only (A–Z), max 10 characters each

---

## Testing

```bash
# Run all tests
pytest tests/

# With coverage report
pytest --cov=src tests/

# Run a specific test
pytest tests/test_workflow.py
```

---

## Deployment

### Hugging Face Spaces

1. Create a new Space (Gradio SDK)
2. Upload project files
3. Add `GROQ_API_KEY` in Space secrets
4. Set `API_BASE_URL` to your deployed backend URL

### Docker

```bash
docker build -t marketsage-analytics .
docker run -p 8000:8000 -p 7860:7860 marketsage-analytics
```

### Cloud Platforms

- **Railway / Render:** Deploy FastAPI backend, expose port 8000
- **Hugging Face Spaces:** Host the Gradio frontend

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## Disclaimer

This application is for educational and research purposes only. The financial analysis provided does not constitute investment advice. Always consult a qualified financial professional before making investment decisions.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*MarketSage Analytics — Intelligent market insights powered by LangGraph and Groq LLM*
