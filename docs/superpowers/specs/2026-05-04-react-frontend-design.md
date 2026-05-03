# MarketSage React Frontend Design Spec

**Goal:** Replace the Gradio frontend with a modern React SPA that looks and feels like a professional financial analytics product — polished enough to showcase, fast enough to run locally.

**Deployment target:** Local showcase / portfolio demo. Runs alongside the existing FastAPI backend on port 8000.

---

## Design Direction

- **Style:** Modern Light SaaS — clean white backgrounds, slate text, indigo (#6366f1) primary accent, shadcn/ui components throughout
- **Layout model:** Split panel on the Analyst page (query + result left, charts + agent progress right)
- **Navigation:** Multi-page SPA with a dark sidebar (slate-900) and three pages

---

## Tech Stack

| Concern | Choice |
|---------|--------|
| Framework | React 18 + Vite |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui (Button, Badge, Card, Accordion, Progress, Select, Tabs) |
| Charts | Recharts |
| Routing | React Router v6 |
| HTTP | Axios |
| Icons | lucide-react |

---

## File Structure

New directory: `src/frontend_react/`. The existing Gradio frontend files are deleted: `src/frontend/gradio_app.py`, `src/frontend/gradio_app_with_viz.py`, `run_frontend.py`, `run_frontend_with_viz.sh`.

```
src/frontend_react/
├── package.json
├── vite.config.js
├── tailwind.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── App.jsx                        # Router: /, /history, /portfolio
    ├── api/
    │   └── client.js                  # axios instance → http://localhost:8000
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.jsx            # Dark sidebar, nav links, backend health indicator
    │   │   └── Layout.jsx             # Wraps every page with Sidebar + main content area
    │   ├── analyst/
    │   │   ├── QueryPanel.jsx         # Question textarea, SymbolInput, analysis type pills, selectors, submit button
    │   │   ├── AnalysisResult.jsx     # Typewriter-animated final_analysis + agent accordion
    │   │   ├── AgentProgress.jsx      # 8-agent step tracker with timed animation
    │   │   └── SymbolInput.jsx        # Tag-based symbol input (add/remove chips)
    │   └── charts/
    │       ├── PriceChart.jsx         # Line chart: multi-symbol price history
    │       ├── TechnicalChart.jsx     # Composite: price + RSI + MACD subcharts
    │       ├── VolumeChart.jsx        # Bar chart: trading volume per symbol
    │       ├── AllocationChart.jsx    # Pie chart: portfolio weights
    │       ├── SectorChart.jsx        # Bar chart: sector performance
    │       └── ChartPanel.jsx         # Tab switcher: Price | RSI/MACD | Volume | Allocation | Sector
    ├── pages/
    │   ├── Analyst.jsx                # Split panel page (hero)
    │   ├── History.jsx                # Query log page
    │   └── Portfolio.jsx              # Portfolio builder page
    └── hooks/
        ├── useAnalysis.js             # Fetch state machine: idle → loading → done | error
        ├── useChartData.js            # GET /chart-data fetch, keyed by symbols+timeframe
        └── useHealth.js               # Polls GET /health every 30s for sidebar indicator
```

---

## Backend Changes

One new endpoint added to `src/api/main.py`:

```
GET /chart-data?symbols=AAPL,MSFT&timeframe=1y
```

- Validates symbols and timeframe using existing Pydantic validators
- Calls the existing `get_stock_data` tool from `financial_tools.py`
- Returns per-symbol OHLCV arrays shaped for Recharts:

```json
{
  "AAPL": [{"date": "2024-01-02", "close": 185.2, "volume": 82000000}, ...],
  "MSFT": [...]
}
```

All other backend routes, agents, and workflow are untouched.

---

## Page Designs

### Analyst Page (`/`)

**Layout:** Two-column split. Left panel 420px fixed, right panel fills remaining width.

**Top bar:** App title ("AI Market Analyst"), subtitle ("Powered by 8 specialized agents"), status badges (Groq LLM, LangGraph).

**Left panel — Query:**
- Textarea for the question (max 1000 chars)
- `SymbolInput`: tag-based chip input — type a symbol and press Enter/comma to add, click ✕ to remove. Max 20 symbols.
- Analysis type pills (single-select): Comprehensive · Technical · Risk · Sentiment · Portfolio · Crypto · Quick
- Timeframe select: 1d / 5d / 1mo / 3mo / 6mo / 1y / 2y / 5y
- Risk tolerance select: Conservative / Moderate / Aggressive
- "Run Analysis →" button — disabled while loading, shows spinner

**Left panel — Result (appears after response):**
- `AnalysisResult`: renders `final_analysis` text with a typewriter effect — `setInterval` at 15ms, appends 3 chars per tick (a 1000-char response completes in ~5 seconds)
- Accordion below: one item per agent output (`market_research`, `technical_analysis`, `risk_assessment`, `sentiment_analysis`, `portfolio_analysis`, `sector_analysis`, `crypto_analysis`). Only items with non-null content are shown. Collapsed by default, expand on click.

**Right panel — Agent Progress:**
- `AgentProgress`: 2-column grid of 8 agent rows. Each row: status icon (○ pending / ⟳ running / ✓ done) + agent name + elapsed time (shown when done).
- Animation: when request fires, a `useEffect` walks through agents sequentially on a timer. Market Research starts immediately (1.5s), then Financial Data (2s), then parallel group (Technical, Risk, Sentiment, Portfolio, Sector, Crypto — each 1–2s staggered), then Final Synthesis (1.5s). On response arrival, all remaining agents flip to done.
- Progress bar below the grid: percentage based on agents completed / 8.

**Right panel — Charts:**
- `ChartPanel` with tabs: Price | RSI/MACD | Volume | Allocation | Sector
- Price tab active by default. Fetches from `GET /chart-data` when symbols are present.
- Charts only render when symbols are set. Empty state: "Add symbols to see charts."
- All charts use the indigo palette (`#6366f1`, `#818cf8`, `#a5b4fc`, `#06b6d4`, `#10b981`).

---

### History Page (`/history`)

**Stats bar:** Three KPI cards — Total Queries, Avg Processing Time, Most Analyzed Symbol. Data from `GET /stats`.

**Query table:** Columns — Question (truncated at 60 chars), Symbols (comma-joined, truncated at 3 + "…"), Analysis Type (color-coded badge), Processing Time, Replay button.

**Replay:** Clicking "↗ Replay" navigates to `/` and pre-fills the QueryPanel with that query's parameters, then auto-submits. Implemented via React Router `navigate` with location state.

Data from `GET /history` (last 20 queries).

---

### Portfolio Page (`/portfolio`)

**Symbol builder:** List of symbol rows — each row has a chip label, a weight slider (0–100), and a numeric input. Weights must sum to 100%; a validation message shows if they don't. Max 50 symbols per the existing `PortfolioRequest` model.

**"Analyze Portfolio →" button:** POSTs to `POST /portfolio`. Disabled if weights don't sum to 100%.

**Results section (appears after response):**
- Left: `AllocationChart` — donut/pie chart of weights by symbol, Recharts `PieChart`.
- Right: AI analysis text (from `final_analysis`). No structured metric extraction — the LLM prose naturally includes risk and return commentary.

---

### Sidebar

- Dark background (`slate-900`)
- Logo: "MarketSage" (white, bold) + "AI Analytics" (indigo, small)
- Nav links: Analyst / History / Portfolio — active link has indigo background highlight
- Bottom: backend health indicator — polls `GET /health` every 30s. Shows "● Backend online" (green) or "● Backend offline" (red) + URL.

---

## State Management

No Redux or Zustand. All state is local to each page via React hooks:

- `useAnalysis` hook encapsulates the `/analyze` POST: `{ status, result, error, run, reset }`. Status enum: `idle | loading | done | error`.
- `useChartData` hook encapsulates `GET /chart-data` fetches, keyed by symbols+timeframe.
- History and Portfolio pages use plain `useState` + `useEffect` for their fetches.

---

## Error Handling

- Network errors: shown as an inline error card in the result area. "Backend unreachable — make sure `python main.py` is running."
- Validation errors (422): field-level messages shown below the relevant input.
- Partial agent failures: if `error` field in response is non-empty, show a yellow warning banner above the result.

---

## Running the Frontend

```powershell
cd src/frontend_react
npm install
npm run dev    # → http://localhost:5173
```

Backend must be running at `http://localhost:8000`.

Update `CLAUDE.md` under Development Workflows — replace Gradio frontend instructions with:

```powershell
# Terminal 2 — React frontend
cd src/frontend_react && npm run dev   # → http://localhost:5173
```

---

## Out of Scope

- Authentication / user accounts
- Deployment / hosting configuration
- Dark mode toggle
- Mobile responsiveness beyond 1024px minimum
- WebSocket streaming from backend agents (progress is animated client-side)
