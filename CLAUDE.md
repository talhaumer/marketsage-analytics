# CLAUDE.md

Guidance for Claude Code when working in the **MarketSage Analytics** repository.

---

## Project Overview

MarketSage Analytics is a multi-agent financial analysis system. Eight specialized agents coordinate through a LangGraph workflow to deliver market research, financial data analysis, technical indicators, risk assessment, sentiment scoring, portfolio optimization, sector rotation insights, and crypto analysis — surfaced through a FastAPI backend and a Gradio + Plotly frontend.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8+ |
| Frontend | Gradio 5.47 + Plotly 5.24 |
| Backend | FastAPI 0.117 |
| AI Workflow | LangGraph 0.6.7 |
| LLM | Groq (`llama-3.3-70b-versatile`) via `langchain-groq`, with mock fallback |
| Stock Data | Yahoo Finance (`yfinance` 0.2.50) |
| Crypto Data | CoinGecko (`pycoingecko` 3.1.0) |
| News | DuckDuckGo Search (`duckduckgo-search` 7.2.0) |
| Validation | Pydantic 2.x |
| Testing | pytest |
| Lint | ruff 0.13.2 |
| Env Mgmt | python-dotenv, virtualenv |

---

## Project Structure

```
MarketSage-Analytics/
├── src/
│   ├── agents/                       # Individual agent implementations (one file per agent)
│   │   ├── base_agent.py             # BaseAgent, FinancialDataAgent, AnalysisAgent
│   │   ├── market_research_agent.py
│   │   ├── financial_data_agent.py
│   │   ├── technical_analysis_agent.py
│   │   ├── risk_assessment_agent.py
│   │   ├── sentiment_analysis_agent.py
│   │   ├── portfolio_analysis_agent.py
│   │   ├── sector_analysis_agent.py
│   │   ├── crypto_agent.py
│   │   └── final_synthesis_agent.py
│   ├── tools/
│   │   ├── gorq_llm.py               # Groq LLM factory + mock fallback
│   │   ├── financial_tools.py        # Yahoo Finance + news search tools
│   │   └── crypto_data_tools.py      # CoinGecko crypto data client
│   ├── workflows/
│   │   ├── financial_analysis_workflow.py  # LangGraph StateGraph
│   │   ├── smart_router.py           # Symbol/context-based agent routing
│   │   └── state.py                  # State TypedDict + reducers
│   ├── utils/
│   │   ├── input_detector.py         # Crypto vs stock vs mixed detection
│   │   ├── data_fetcher.py
│   │   └── technical_indicators.py
│   ├── api/
│   │   ├── main.py                   # FastAPI routes
│   │   └── models.py                 # Pydantic request/response models
│   └── frontend/
│       ├── gradio_app.py             # Standard Gradio frontend
│       └── gradio_app_with_viz.py    # Enhanced frontend with Plotly charts
├── tests/                            # pytest tests
├── docs/                             # Architecture, agent, API, and spec docs
├── main.py                           # Backend entry point (sets PYTHONPATH and starts FastAPI)
├── run_frontend.py                   # Standard frontend entry point
├── run_frontend_with_viz.sh          # Enhanced frontend launcher (bash; see Workflows for Windows)
├── requirements.txt
└── env.example                       # Environment variables template
```

---

## Agent Architecture

All agents follow the same shape: a function `agent_name(state: State) -> State` that reads from and writes to the shared `State` TypedDict. The graph entry point is `market_research`; after it completes, the seven analysis agents run **in parallel** (LangGraph fan-out); when they all complete, `final_synthesis` runs and produces `final_analysis`.

| Agent | File | Reads (state keys) | Writes (state keys) | Mode |
|-------|------|-------------------|---------------------|------|
| Market Research | `market_research_agent.py` | `question`, `symbols`, `timeframe`, `analysis_type` | `market_research` | Entry |
| Financial Data | `financial_data_agent.py` | `symbols`, `timeframe`, `question` | `financial_data` (dict: `analysis` + `raw_data`) | Parallel |
| Technical Analysis | `technical_analysis_agent.py` | `symbols`, `timeframe` | `technical_analysis` | Parallel |
| Risk Assessment | `risk_assessment_agent.py` | `symbols`, `risk_tolerance`, `financial_data` | `risk_assessment` | Parallel |
| Sentiment Analysis | `sentiment_analysis_agent.py` | `symbols`, `question`, `market_research` | `sentiment_analysis` | Parallel |
| Portfolio Analysis | `portfolio_analysis_agent.py` | `symbols`, `risk_tolerance` | `portfolio_analysis` | Parallel |
| Sector Analysis | `sector_analysis_agent.py` | `symbols` | `sector_analysis` | Parallel |
| Crypto Analysis | `crypto_agent.py` | `symbols` (filtered to crypto) | `crypto_analysis` | Parallel |
| Final Synthesis | `final_synthesis_agent.py` | All `*_analysis` keys + `analysis_type` | `final_analysis` | Terminal |

`SmartAnalysisRouter` (`src/workflows/smart_router.py`) decides which agents are *useful* for a given input (e.g., crypto-only inputs skip stock agents). The current production graph fans out to all agents and lets each agent no-op gracefully when its inputs are empty; routing helpers exist for future conditional-edge wiring.

---

## LangGraph Workflow Guide

### State

Defined in `src/workflows/state.py`. It's a `TypedDict` with `Annotated[..., reducer]` fields so LangGraph can merge updates from parallel branches:

- `string_reducer` — keeps the latest non-None value (used for all string fields).
- `dict_reducer` — keeps the latest non-None dict (used for `financial_data`).
- `error_reducer` — concatenates errors with `; ` so multi-agent errors don't clobber each other.

### Graph

Defined in `src/workflows/financial_analysis_workflow.py`:

```
                              ┌─> financial_data
                              ├─> technical_analysis
                              ├─> risk_assessment
START → market_research ─────>┤─> sentiment_analysis ──> final_synthesis → END
                              ├─> portfolio_analysis
                              ├─> sector_analysis
                              └─> crypto_analysis
```

### Smart Router

`SmartAnalysisRouter.route_analysis(state)` returns a dict of `use_*` booleans driven by `InputDetector` (symbol DB + keyword scoring). Conditional helpers `should_run_financial_agent`, `should_run_crypto_agent`, `should_run_sector_agent` map state to branch names for future `add_conditional_edges` wiring.

### Adding a new agent

1. Create `src/agents/<name>_agent.py` with a function `<name>_agent(state: State) -> State` that catches its own errors and writes them to `state['error']` via the agent's `handle_error` pattern.
2. Export it from `src/agents/__init__.py` (both the import and `__all__`).
3. Add a state key in `src/workflows/state.py` using `Annotated[Optional[str], string_reducer]` (or the appropriate reducer).
4. Register the node and edges in `create_financial_analysis_workflow()`: `workflow.add_node(...)`, then `workflow.add_edge("market_research", "<name>")` and `workflow.add_edge("<name>", "final_synthesis")`.
5. Add the field to `IndividualAnalyses` in `src/api/models.py` and surface it in the `/analyze` response in `src/api/main.py`.
6. Add a tailored branch in `final_synthesis_agent.py` if the agent introduces a new `analysis_type`.

### Adding a new analysis type

1. Add the value to `AnalysisType` in `src/api/models.py`.
2. Add an `elif analysis_type == '<name>':` branch in `final_synthesis_agent.py` with a tailored prompt.
3. (Optional) Adjust `SmartAnalysisRouter.route_analysis` to activate or deactivate specific agents for that type.

---

## Development Workflows

### Run backend + standard frontend (two terminals)

```powershell
# Terminal 1 — backend
python main.py

# Terminal 2 — standard frontend
python run_frontend.py
```

### Run backend + enhanced frontend (with Plotly visualizations)

`run_frontend_with_viz.sh` is a bash launcher. On Windows, run the Python entry point directly:

```powershell
# Terminal 1 — backend
python main.py

# Terminal 2 — enhanced frontend (Windows)
$env:PYTHONPATH = "src"
python src/frontend/gradio_app_with_viz.py
```

On macOS/Linux:

```bash
bash run_frontend_with_viz.sh
```

### Service URLs

| Service | URL |
|---------|-----|
| Frontend (Gradio) | http://localhost:7860 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### Exercise the API

Use the Swagger UI at `http://localhost:8000/docs` for interactive testing, or `curl`:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"question":"AI stocks outlook","symbols":["AAPL","MSFT"],"analysis_type":"comprehensive","timeframe":"1y","risk_tolerance":"moderate"}'
```

---

## Debugging Guide

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Mock LLM template responses appear in output (e.g., "I've completed a comprehensive analysis…") | `GROQ_API_KEY` is missing or invalid; `gorq_llm.get_llm()` printed `No GROQ_API_KEY found in environment, using mock LLM...` | Add `GROQ_API_KEY=...` to `.env`, restart the backend. Get a key at console.groq.com. |
| `ModuleNotFoundError: No module named 'workflows'` (or `agents`, `tools`, `api`) | `PYTHONPATH` does not include `src/` | Run via `python main.py` (it prepends `src/` to `sys.path`), or `$env:PYTHONPATH = "src"` then run the module. The repo's `.claude/settings.json` sets this for Claude Code sessions automatically. |
| `yfinance` returns empty data or raises `Too Many Requests` | Yahoo Finance rate limit | Reduce symbol count per request, increase timeframe granularity, or wait ~60 s. The `BaseAgent.cache_set` / `cache_get` helpers (5-minute TTL) reduce repeat calls during a session. |
| CoinGecko returns `429 Too Many Requests` | Free-tier CoinGecko limit (~30 req/min) | Set `COINGECKO_API_KEY` for higher limits, throttle calls in `crypto_data_tools.py`, or rely on the agent's local cache. |
| `bash: command not found` when running `run_frontend_with_viz.sh` | Windows PowerShell doesn't run `.sh` natively | Use the Python entry point: `python src/frontend/gradio_app_with_viz.py` with `$env:PYTHONPATH = "src"` set. |
| Gradio frontend shows "Backend unreachable" | `API_BASE_URL` mismatch or backend not running | Confirm `python main.py` is running on port 8000; verify `API_BASE_URL` (env var) matches; the repo `.claude/settings.json` sets it to `http://localhost:8000`. |
| Final synthesis is missing data from one agent | That agent failed silently and wrote to `state['error']` | Check the backend logs for `error_reducer` concatenations; each agent prints `[<timestamp>] <Name>: ...` lines. |

---

## Common Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py

# Run standard frontend
python run_frontend.py

# Run frontend with charts (Windows)
$env:PYTHONPATH = "src"; python src/frontend/gradio_app_with_viz.py

# Run frontend with charts (Unix)
bash run_frontend_with_viz.sh

# Tests
pytest tests/
pytest --cov=src tests/
pytest tests/test_workflow.py

# Lint
ruff check src/
ruff format src/
```

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GROQ_API_KEY` | Recommended | Groq LLM inference; falls back to mock LLM if absent |
| `OPENAI_API_KEY` | Optional | Reserved fallback LLM provider |
| `API_BASE_URL` | Optional | Backend URL the frontend calls (default `http://localhost:8000`) |
| `COINGECKO_API_KEY` | Optional | Higher CoinGecko rate limits |
| `PYTHONPATH` | Implicit | Must include `src/`. Set automatically by `main.py` and by Claude Code via `.claude/settings.json`. |

Use `env.example` as the template. Never commit `.env`.

---

## Coding Rules

- Follow existing module structure — agents in `src/agents/`, tools in `src/tools/`, workflow logic in `src/workflows/`, request/response shapes in `src/api/models.py`.
- Use Pydantic models for all FastAPI request/response payloads.
- Symbol validation: letters only (A–Z), max 10 characters, max 20 symbols per request (50 for portfolio).
- The mock LLM fallback path must keep working — never assume `GROQ_API_KEY` is set.
- Don't add new top-level dependencies without updating `requirements.txt`.
- Prefer editing existing files over creating new ones.
- Don't write code comments unless the *why* is non-obvious.
- Don't create new markdown documentation files unless explicitly requested.
- Validate user-supplied symbols and timeframes before passing to data fetchers.

---

## Git Rules

**Author identity — strict:**

- All commits MUST be authored by **Talha Umer**.
- Never include `Claude`, `Anthropic`, `Co-Authored-By: Claude`, or any AI attribution in commit messages, commit bodies, or PR descriptions.
- Never add the "Generated with Claude Code" footer.
- Never use `--author` to override the configured git user.
- The configured git user (`talhaumer`) is the only author that should appear in `git log`.

**Commit style:**

- Imperative subject (e.g., `Add crypto correlation heatmap`, `Fix RSI calculation off-by-one`).
- Subject line under 72 characters.
- Use the body to explain *why*, not *what*, when needed.

**Workflow:**

- Never force-push to `main`.
- Never skip hooks (`--no-verify`).
- Never amend commits that have been pushed.
- After a hook failure, fix the issue and create a NEW commit (the failed commit didn't happen — `--amend` would touch the previous commit).
- Stage files explicitly by name — avoid `git add -A` / `git add .` to prevent accidentally committing `.env`, secrets, or build artifacts.
- Don't commit unless the user explicitly asks.

**Branching:**

- Feature branches: `feature/<short-description>`
- Bug fixes: `fix/<short-description>`
- Open PRs against `main`.

---

## Security

- Never commit API keys, `.env` files, or credentials.
- Treat `GROQ_API_KEY`, `OPENAI_API_KEY`, and `COINGECKO_API_KEY` as secrets.
- Validate all user-supplied symbols and timeframes before passing to data fetchers.
- Sanitize any user-provided strings injected into LLM prompts.

---

## Disclaimer

This project is for educational and research purposes only. Output is not investment advice.
