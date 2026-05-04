# MarketSage React Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Gradio frontend with a React 18 + Vite + Tailwind CSS v4 SPA featuring a split-panel Analyst page, History page with replay, and Portfolio builder — all backed by the existing FastAPI API on port 8000.

**Architecture:** A standalone SPA lives in `src/frontend_react/`. One new `GET /chart-data` endpoint is added to the FastAPI backend; everything else in `src/` is untouched. The React app calls the FastAPI backend directly via Axios. Agent progress is animated client-side (no WebSocket). Chart data is fetched via `get_price_history` from `financial_tools.py`, which handles both stocks and crypto.

**Tech Stack:** React 18, Vite 5, Tailwind CSS v4 (via @tailwindcss/vite), Recharts 2, React Router v6, Axios, lucide-react, Vitest + @testing-library/react for tests.

---

## Context for the implementer

- **Working directory:** `C:\Users\talha\Downloads\MarketSage-Analytics`
- **Python path:** `src/` is on `sys.path` (set via `.claude/settings.json`). All Python imports are relative to `src/`.
- **Backend:** FastAPI runs on port 8000 via `python main.py`. The backend's CORS must allow `http://localhost:5173`.
- **No AI attribution** in any commit message — no `Co-Authored-By` or "Generated with" footer.
- **Commits** are imperative-mood, under 72 chars, authored by `talhaumer` only.
- **Ruff** runs as a pre-commit hook: fix lint before committing Python files (`ruff check src/`).

---

## File Map

**Deleted:**
- `src/frontend/gradio_app.py`
- `src/frontend/gradio_app_with_viz.py`
- `run_frontend.py`
- `run_frontend_with_viz.sh`

**Modified (backend):**
- `src/api/main.py` — add `GET /chart-data`, update CORS default, re-add `HTTPException` import, add `get_price_history` import

**Created (React app):**
```
src/frontend_react/
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── index.css
    ├── App.jsx
    ├── api/client.js
    ├── hooks/
    │   ├── useAnalysis.js
    │   ├── useChartData.js
    │   └── useHealth.js
    ├── utils/chartUtils.js
    ├── components/
    │   ├── layout/Sidebar.jsx
    │   ├── layout/Layout.jsx
    │   ├── analyst/SymbolInput.jsx
    │   ├── analyst/AgentProgress.jsx
    │   ├── analyst/QueryPanel.jsx
    │   ├── analyst/AnalysisResult.jsx
    │   └── charts/
    │       ├── PriceChart.jsx
    │       ├── VolumeChart.jsx
    │       ├── TechnicalChart.jsx
    │       ├── SectorChart.jsx
    │       ├── AllocationChart.jsx
    │       └── ChartPanel.jsx
    ├── pages/
    │   ├── Analyst.jsx
    │   ├── History.jsx
    │   └── Portfolio.jsx
    └── test/
        ├── setup.js
        ├── chartUtils.test.js
        └── hooks.test.js
```

**Modified (docs):**
- `CLAUDE.md` — replace Gradio instructions with React instructions

---

## Task 1: Backend — /chart-data endpoint + CORS update

**Files:**
- Modify: `src/api/main.py`
- Test: `tests/test_chart_data.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_chart_data.py`:

```python
"""Tests for GET /chart-data endpoint."""
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


def _mock_hist():
    idx = pd.DatetimeIndex([pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")])
    return pd.DataFrame(
        {
            "Close": [185.2, 186.0],
            "Volume": [82000000, 75000000],
            "High": [187.0, 187.5],
            "Low": [184.0, 185.5],
            "Open": [184.5, 185.8],
        },
        index=idx,
    )


def test_chart_data_returns_ohlcv_shape(client):
    with patch("api.main.get_price_history", return_value=_mock_hist()):
        response = client.get("/chart-data?symbols=AAPL&timeframe=1y")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data
    assert len(data["AAPL"]) == 2
    row = data["AAPL"][0]
    for field in ("date", "close", "volume", "high", "low", "open"):
        assert field in row


def test_chart_data_multiple_symbols(client):
    with patch("api.main.get_price_history", return_value=_mock_hist()):
        response = client.get("/chart-data?symbols=AAPL,MSFT&timeframe=1y")
    assert response.status_code == 200
    data = response.json()
    assert "AAPL" in data and "MSFT" in data


def test_chart_data_rejects_invalid_symbol(client):
    response = client.get("/chart-data?symbols=BAD!SYM&timeframe=1y")
    assert response.status_code == 422


def test_chart_data_empty_symbols_returns_400(client):
    response = client.get("/chart-data?symbols=&timeframe=1y")
    assert response.status_code == 400


def test_chart_data_empty_hist_returns_empty_list(client):
    with patch("api.main.get_price_history", return_value=pd.DataFrame()):
        response = client.get("/chart-data?symbols=FAKE&timeframe=1y")
    assert response.status_code == 200
    assert response.json()["FAKE"] == []
```

- [ ] **Step 2: Run the test to verify it fails**

```powershell
pytest tests/test_chart_data.py -v
```

Expected: `FAILED` — `ImportError` or `404` because the endpoint doesn't exist yet.

- [ ] **Step 3: Add the endpoint and update CORS in `src/api/main.py`**

Replace the top imports block:

```python
"""
FastAPI Backend for LangGraph Financial Analyst with Gorq LLM
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
import os
import re as _re
from datetime import datetime
import time

from workflows.financial_analysis_workflow import financial_analysis_workflow
from tools.financial_tools import get_price_history
from .models import (
    AnalysisRequest,
    PortfolioRequest,
    AnalysisResponse,
    HistoryResponse,
    AnalysisStats,
    HealthResponse,
    APIInfo,
)

_CHART_SYM_RE = _re.compile(r"^[A-Za-z0-9.]{1,10}$")
```

Change the CORS default to include the React dev port (replace the `_ALLOWED_ORIGINS` line):

```python
_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
```

Add the new endpoint after the existing `/stats` route and before `if __name__ == "__main__":`:

```python
@app.get("/chart-data")
async def get_chart_data(symbols: str, timeframe: str = "1y"):
    """Return OHLCV data per symbol shaped for Recharts."""
    if not symbols.strip():
        raise HTTPException(status_code=400, detail="symbols parameter is required")

    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="No valid symbols provided")

    for sym in symbol_list:
        if not _CHART_SYM_RE.match(sym):
            raise HTTPException(status_code=422, detail=f"Invalid symbol: {sym}")

    result = {}
    for sym in symbol_list[:10]:
        try:
            hist = get_price_history(sym, timeframe)
            if hist.empty:
                result[sym] = []
                continue
            result[sym] = [
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row.get("Volume", 0)),
                    "high": round(float(row.get("High", row["Close"])), 2),
                    "low": round(float(row.get("Low", row["Close"])), 2),
                    "open": round(float(row.get("Open", row["Close"])), 2),
                }
                for idx, row in hist.iterrows()
            ]
        except Exception:
            result[sym] = []

    return result
```

Also update the `/` root endpoint to list `/chart-data` in the endpoints dict:

```python
endpoints={
    "/analyze": "Main financial analysis endpoint",
    "/portfolio": "Portfolio analysis endpoint",
    "/health": "Health check endpoint",
    "/history": "Query history endpoint",
    "/stats": "Analysis statistics endpoint",
    "/chart-data": "OHLCV chart data endpoint",
}
```

- [ ] **Step 4: Run the tests to verify they pass**

```powershell
pytest tests/test_chart_data.py -v
```

Expected: all 5 tests `PASSED`.

- [ ] **Step 5: Run full test suite to confirm no regressions**

```powershell
pytest tests/ -q
```

Expected: 49 passed (44 existing + 5 new), 0 failed.

- [ ] **Step 6: Run ruff**

```powershell
ruff check src/
```

Expected: `All checks passed!`

- [ ] **Step 7: Commit**

```powershell
git add src/api/main.py tests/test_chart_data.py
git commit -m "Add GET /chart-data endpoint and update CORS for React dev server"
```

---

## Task 2: Delete Gradio files and scaffold React project

**Files:**
- Delete: `src/frontend/gradio_app.py`, `src/frontend/gradio_app_with_viz.py`, `run_frontend.py`, `run_frontend_with_viz.sh`
- Create: all scaffold files listed below

- [ ] **Step 1: Delete Gradio frontend files**

```powershell
git rm src/frontend/gradio_app.py src/frontend/gradio_app_with_viz.py run_frontend.py run_frontend_with_viz.sh
```

Expected: 4 files staged for deletion.

- [ ] **Step 2: Create `src/frontend_react/package.json`**

```json
{
  "name": "marketsage-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "lucide-react": "^0.446.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "recharts": "^2.12.7"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@vitejs/plugin-react": "^4.3.2",
    "jsdom": "^25.0.1",
    "tailwindcss": "^4.0.0",
    "vite": "^5.4.8",
    "vitest": "^2.1.2"
  }
}
```

- [ ] **Step 3: Create `src/frontend_react/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173 },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.js',
  },
})
```

- [ ] **Step 4: Create `src/frontend_react/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MarketSage Analytics</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Create `src/frontend_react/src/index.css`**

```css
@import "tailwindcss";

*, *::before, *::after { box-sizing: border-box; }
html, body, #root { height: 100%; margin: 0; padding: 0; }
```

- [ ] **Step 6: Create `src/frontend_react/src/main.jsx`**

```jsx
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(<App />)
```

- [ ] **Step 7: Create `src/frontend_react/src/App.jsx`** (placeholder — replaced in Task 5)

```jsx
export default function App() {
  return <div className="p-8 text-slate-700">MarketSage loading…</div>
}
```

- [ ] **Step 8: Create `src/frontend_react/src/test/setup.js`**

```js
import '@testing-library/jest-dom'
```

- [ ] **Step 9: Install dependencies**

```powershell
cd src/frontend_react
npm install
```

Expected: `node_modules/` created, no errors. May take 30–60 seconds.

- [ ] **Step 10: Verify the build works**

```powershell
npm run build
```

Expected: `dist/` created, output ends with `✓ built in X.Xs`. If it fails, check that all dependency versions resolved correctly in `package-lock.json`.

- [ ] **Step 11: Return to project root and commit**

```powershell
cd ../..
git add src/frontend_react/ src/frontend/
git commit -m "Replace Gradio frontend with React+Vite scaffold"
```

Note: `src/frontend/` directory will be empty after the `git rm` — git will remove it automatically.

---

## Task 3: API client + custom hooks + tests

**Files:**
- Create: `src/frontend_react/src/api/client.js`
- Create: `src/frontend_react/src/hooks/useAnalysis.js`
- Create: `src/frontend_react/src/hooks/useChartData.js`
- Create: `src/frontend_react/src/hooks/useHealth.js`
- Create: `src/frontend_react/src/test/hooks.test.js`

- [ ] **Step 1: Write the failing tests**

Create `src/frontend_react/src/test/hooks.test.js`:

```js
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAnalysis } from '../hooks/useAnalysis'

vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import client from '../api/client'

describe('useAnalysis', () => {
  beforeEach(() => vi.clearAllMocks())

  it('starts in idle state', () => {
    const { result } = renderHook(() => useAnalysis())
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('transitions to done on successful response', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: true, data: { final_analysis: 'Bull market ahead' } },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: ['AAPL'] })
    })
    expect(result.current.status).toBe('done')
    expect(result.current.result.data.final_analysis).toBe('Bull market ahead')
  })

  it('transitions to error on network failure', async () => {
    client.post.mockRejectedValueOnce(new Error('Network Error'))
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBeTruthy()
  })

  it('transitions to error when success is false', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: false, error: 'Agent failed' },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Agent failed')
  })

  it('reset returns to idle', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: true, data: { final_analysis: 'Done' } },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    act(() => result.current.reset())
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
  })
})
```

- [ ] **Step 2: Run to verify they fail**

```powershell
cd src/frontend_react
npm test
```

Expected: `FAIL` — `Cannot find module '../hooks/useAnalysis'`.

- [ ] **Step 3: Create `src/frontend_react/src/api/client.js`**

```js
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

export default client
```

- [ ] **Step 4: Create `src/frontend_react/src/hooks/useAnalysis.js`**

```js
import { useState, useCallback } from 'react'
import client from '../api/client'

export function useAnalysis() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const run = useCallback(async (payload) => {
    setStatus('loading')
    setResult(null)
    setError(null)
    try {
      const { data } = await client.post('/analyze', payload)
      if (data.success) {
        setResult(data)
        setStatus('done')
      } else {
        setError(data.error || 'Analysis failed')
        setStatus('error')
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        'Backend unreachable — make sure python main.py is running.'
      setError(msg)
      setStatus('error')
    }
  }, [])

  const reset = useCallback(() => {
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [])

  return { status, result, error, run, reset }
}
```

- [ ] **Step 5: Create `src/frontend_react/src/hooks/useChartData.js`**

```js
import { useState, useEffect } from 'react'
import client from '../api/client'

export function useChartData(symbols, timeframe) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const key = (symbols || []).join(',')

  useEffect(() => {
    if (!symbols || symbols.length === 0) {
      setData(null)
      return
    }
    setLoading(true)
    setError(null)
    client
      .get('/chart-data', { params: { symbols: key, timeframe } })
      .then(({ data: d }) => {
        setData(d)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [key, timeframe])

  return { data, loading, error }
}
```

- [ ] **Step 6: Create `src/frontend_react/src/hooks/useHealth.js`**

```js
import { useState, useEffect } from 'react'
import client from '../api/client'

export function useHealth() {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    const check = () =>
      client
        .get('/health')
        .then(() => setOnline(true))
        .catch(() => setOnline(false))
    check()
    const id = setInterval(check, 30000)
    return () => clearInterval(id)
  }, [])

  return online
}
```

- [ ] **Step 7: Run tests to verify they pass**

```powershell
npm test
```

Expected: `5 tests passed`.

- [ ] **Step 8: Commit**

```powershell
cd ../..
git add src/frontend_react/src/api/ src/frontend_react/src/hooks/ src/frontend_react/src/test/
git commit -m "Add API client and custom hooks with Vitest tests"
```

---

## Task 4: Chart utility functions + tests

**Files:**
- Create: `src/frontend_react/src/utils/chartUtils.js`
- Create: `src/frontend_react/src/test/chartUtils.test.js`

- [ ] **Step 1: Write the failing tests**

Create `src/frontend_react/src/test/chartUtils.test.js`:

```js
import { describe, it, expect } from 'vitest'
import { mergeByDate, computeRSI, computeReturn } from '../utils/chartUtils'

describe('mergeByDate', () => {
  it('merges two symbols by date on the given field', () => {
    const data = {
      AAPL: [
        { date: '2024-01-01', close: 100, volume: 1000 },
        { date: '2024-01-02', close: 102, volume: 1100 },
      ],
      MSFT: [
        { date: '2024-01-01', close: 200, volume: 2000 },
        { date: '2024-01-02', close: 205, volume: 2100 },
      ],
    }
    const result = mergeByDate(data, 'close')
    expect(result).toHaveLength(2)
    expect(result[0]).toEqual({ date: '2024-01-01', AAPL: 100, MSFT: 200 })
    expect(result[1]).toEqual({ date: '2024-01-02', AAPL: 102, MSFT: 205 })
  })

  it('returns sorted by date ascending', () => {
    const data = {
      X: [
        { date: '2024-01-03', close: 10 },
        { date: '2024-01-01', close: 8 },
      ],
    }
    const result = mergeByDate(data, 'close')
    expect(result[0].date).toBe('2024-01-01')
    expect(result[1].date).toBe('2024-01-03')
  })
})

describe('computeRSI', () => {
  it('returns nulls for the first 14 periods', () => {
    const closes = Array.from({ length: 14 }, (_, i) => 100 + i)
    const rsi = computeRSI(closes)
    expect(rsi).toHaveLength(14)
    expect(rsi.every((v) => v === null)).toBe(true)
  })

  it('returns values between 0 and 100 for period 15+', () => {
    const closes = Array.from({ length: 25 }, (_, i) => 100 + Math.sin(i) * 5)
    const rsi = computeRSI(closes)
    const values = rsi.filter((v) => v !== null)
    expect(values.length).toBeGreaterThan(0)
    values.forEach((v) => {
      expect(v).toBeGreaterThanOrEqual(0)
      expect(v).toBeLessThanOrEqual(100)
    })
  })

  it('returns 100 when all price moves are gains', () => {
    const closes = Array.from({ length: 20 }, (_, i) => 100 + i)
    const rsi = computeRSI(closes)
    expect(rsi[rsi.length - 1]).toBe(100)
  })

  it('returns 0 when all price moves are losses', () => {
    const closes = Array.from({ length: 20 }, (_, i) => 200 - i)
    const rsi = computeRSI(closes)
    expect(rsi[rsi.length - 1]).toBe(0)
  })
})

describe('computeReturn', () => {
  it('computes percent return correctly', () => {
    const rows = [{ close: 100 }, { close: 50 }, { close: 110 }]
    expect(computeReturn(rows)).toBe(10)
  })

  it('returns 0 for empty or single-element arrays', () => {
    expect(computeReturn([])).toBe(0)
    expect(computeReturn([{ close: 100 }])).toBe(0)
  })

  it('handles negative return', () => {
    const rows = [{ close: 100 }, { close: 90 }]
    expect(computeReturn(rows)).toBe(-10)
  })
})
```

- [ ] **Step 2: Run to verify they fail**

```powershell
cd src/frontend_react
npm test
```

Expected: `FAIL — Cannot find module '../utils/chartUtils'`.

- [ ] **Step 3: Create `src/frontend_react/src/utils/chartUtils.js`**

```js
/**
 * Merges per-symbol OHLCV arrays into a flat array keyed by date.
 * Used by PriceChart and VolumeChart.
 * @param {Object} chartData - { SYMBOL: [{date, close, volume, ...}] }
 * @param {string} field - 'close' | 'volume'
 */
export function mergeByDate(chartData, field) {
  const dateMap = {}
  Object.entries(chartData).forEach(([sym, rows]) => {
    rows.forEach((row) => {
      if (!dateMap[row.date]) dateMap[row.date] = { date: row.date }
      dateMap[row.date][sym] = row[field]
    })
  })
  return Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))
}

/**
 * Computes 14-period RSI from an array of close prices.
 * Returns an array of the same length; the first 14 entries are null.
 */
export function computeRSI(closes, period = 14) {
  if (closes.length < period + 1) return closes.map(() => null)

  const rsi = new Array(period).fill(null)
  let gains = 0
  let losses = 0

  for (let i = 1; i <= period; i++) {
    const d = closes[i] - closes[i - 1]
    if (d > 0) gains += d
    else losses -= d
  }

  let avgGain = gains / period
  let avgLoss = losses / period
  rsi.push(avgLoss === 0 ? 100 : avgGain === 0 ? 0 : 100 - 100 / (1 + avgGain / avgLoss))

  for (let i = period + 1; i < closes.length; i++) {
    const d = closes[i] - closes[i - 1]
    avgGain = (avgGain * (period - 1) + Math.max(d, 0)) / period
    avgLoss = (avgLoss * (period - 1) + Math.max(-d, 0)) / period
    rsi.push(avgLoss === 0 ? 100 : avgGain === 0 ? 0 : 100 - 100 / (1 + avgGain / avgLoss))
  }

  return rsi
}

/**
 * Computes the period % return: (last_close - first_close) / first_close * 100.
 */
export function computeReturn(rows) {
  if (!rows || rows.length < 2) return 0
  const first = rows[0].close
  const last = rows[rows.length - 1].close
  return parseFloat((((last - first) / first) * 100).toFixed(2))
}
```

- [ ] **Step 4: Run tests to verify all pass**

```powershell
npm test
```

Expected: `14 tests passed` (5 hook tests + 9 utility tests).

- [ ] **Step 5: Commit**

```powershell
cd ../..
git add src/frontend_react/src/utils/ src/frontend_react/src/test/chartUtils.test.js
git commit -m "Add chart utility functions (mergeByDate, computeRSI, computeReturn) with tests"
```

---

## Task 5: Layout — Sidebar + Layout wrapper + App routing

**Files:**
- Create: `src/frontend_react/src/components/layout/Sidebar.jsx`
- Create: `src/frontend_react/src/components/layout/Layout.jsx`
- Replace: `src/frontend_react/src/App.jsx`

- [ ] **Step 1: Create `src/frontend_react/src/components/layout/Sidebar.jsx`**

```jsx
import { NavLink } from 'react-router-dom'
import { BarChart2, Clock, PieChart } from 'lucide-react'
import { useHealth } from '../../hooks/useHealth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const NAV = [
  { to: '/', end: true, icon: BarChart2, label: 'Analyst' },
  { to: '/history', end: false, icon: Clock, label: 'History' },
  { to: '/portfolio', end: false, icon: PieChart, label: 'Portfolio' },
]

export function Sidebar() {
  const online = useHealth()

  return (
    <aside className="w-52 bg-slate-900 flex flex-col h-screen fixed left-0 top-0 p-3 z-10">
      <div className="px-2 py-4 border-b border-slate-800 mb-3">
        <div className="text-white font-bold text-sm tracking-tight">MarketSage</div>
        <div className="text-indigo-400 text-xs mt-0.5">AI Analytics</div>
      </div>

      <nav className="flex flex-col gap-1 flex-1">
        {NAV.map(({ to, end, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? 'bg-indigo-500/20 border border-indigo-500/30 text-white font-medium'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div
        className={`p-2.5 rounded-md text-xs border ${
          online
            ? 'bg-emerald-950/50 border-emerald-800 text-emerald-400'
            : 'bg-red-950/50 border-red-800 text-red-400'
        }`}
      >
        <div className="font-medium">{online ? '● Backend online' : '● Backend offline'}</div>
        <div className="text-slate-500 mt-0.5 truncate">{API_BASE}</div>
      </div>
    </aside>
  )
}
```

- [ ] **Step 2: Create `src/frontend_react/src/components/layout/Layout.jsx`**

```jsx
import { Sidebar } from './Sidebar'

export function Layout({ children }) {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <main className="flex-1 ml-52 overflow-auto flex flex-col">{children}</main>
    </div>
  )
}
```

- [ ] **Step 3: Replace `src/frontend_react/src/App.jsx`**

```jsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Analyst } from './pages/Analyst'
import { History } from './pages/History'
import { Portfolio } from './pages/Portfolio'

const router = createBrowserRouter([
  { path: '/', element: <Layout><Analyst /></Layout> },
  { path: '/history', element: <Layout><History /></Layout> },
  { path: '/portfolio', element: <Layout><Portfolio /></Layout> },
])

export default function App() {
  return <RouterProvider router={router} />
}
```

- [ ] **Step 4: Create placeholder pages so App.jsx compiles**

Create `src/frontend_react/src/pages/Analyst.jsx`:

```jsx
export function Analyst() {
  return <div className="p-8 text-slate-700">Analyst page — coming in Task 10</div>
}
```

Create `src/frontend_react/src/pages/History.jsx`:

```jsx
export function History() {
  return <div className="p-8 text-slate-700">History page — coming in Task 11</div>
}
```

Create `src/frontend_react/src/pages/Portfolio.jsx`:

```jsx
export function Portfolio() {
  return <div className="p-8 text-slate-700">Portfolio page — coming in Task 12</div>
}
```

- [ ] **Step 5: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs` with no errors.

- [ ] **Step 6: Commit**

```powershell
cd ../..
git add src/frontend_react/src/components/layout/ src/frontend_react/src/App.jsx src/frontend_react/src/pages/
git commit -m "Add Sidebar navigation, Layout wrapper, and React Router page structure"
```

---

## Task 6: SymbolInput chip component

**Files:**
- Create: `src/frontend_react/src/components/analyst/SymbolInput.jsx`

- [ ] **Step 1: Create `src/frontend_react/src/components/analyst/SymbolInput.jsx`**

```jsx
import { useState } from 'react'
import { X } from 'lucide-react'

export function SymbolInput({ symbols, onChange, maxSymbols = 20 }) {
  const [input, setInput] = useState('')

  const addSymbol = (raw) => {
    const sym = raw.trim().toUpperCase().replace(/[^A-Z0-9.]/g, '')
    if (sym && !symbols.includes(sym) && symbols.length < maxSymbols) {
      onChange([...symbols, sym])
    }
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addSymbol(input)
    } else if (e.key === 'Backspace' && !input && symbols.length > 0) {
      onChange(symbols.slice(0, -1))
    }
  }

  return (
    <div className="flex flex-wrap gap-1.5 p-2 border border-slate-200 rounded-md bg-white min-h-[40px] cursor-text focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-shadow">
      {symbols.map((sym) => (
        <span
          key={sym}
          className="flex items-center gap-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded px-2 py-0.5 text-xs font-medium"
        >
          {sym}
          <button
            type="button"
            onClick={() => onChange(symbols.filter((s) => s !== sym))}
            className="hover:text-indigo-900 transition-colors"
            aria-label={`Remove ${sym}`}
          >
            <X size={10} />
          </button>
        </span>
      ))}
      {symbols.length < maxSymbols && (
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => input.trim() && addSymbol(input)}
          placeholder={symbols.length === 0 ? 'AAPL, MSFT… (Enter to add)' : ''}
          className="flex-1 min-w-[100px] outline-none text-xs bg-transparent placeholder-slate-400 text-slate-700"
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 3: Commit**

```powershell
cd ../..
git add src/frontend_react/src/components/analyst/SymbolInput.jsx
git commit -m "Add SymbolInput chip component"
```

---

## Task 7: AgentProgress tracker

**Files:**
- Create: `src/frontend_react/src/components/analyst/AgentProgress.jsx`

- [ ] **Step 1: Create `src/frontend_react/src/components/analyst/AgentProgress.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Loader2 } from 'lucide-react'

// Timing matches realistic LangGraph execution order:
// market_research → financial_data → parallel group → final_synthesis
const AGENTS = [
  { key: 'market_research',    label: 'Market Research',    delay: 0,    duration: 1500 },
  { key: 'financial_data',     label: 'Financial Data',     delay: 1500, duration: 2000 },
  { key: 'technical_analysis', label: 'Technical Analysis', delay: 3500, duration: 1800 },
  { key: 'risk_assessment',    label: 'Risk Assessment',    delay: 3700, duration: 2000 },
  { key: 'sentiment_analysis', label: 'Sentiment',          delay: 3900, duration: 1600 },
  { key: 'portfolio_analysis', label: 'Portfolio',          delay: 4100, duration: 1700 },
  { key: 'sector_analysis',    label: 'Sector Analysis',    delay: 4300, duration: 1500 },
  { key: 'crypto_analysis',    label: 'Crypto',             delay: 4500, duration: 1500 },
  { key: 'final_synthesis',    label: 'Final Synthesis',    delay: 6000, duration: 1500 },
]

const INIT_STATES = () => AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: 'pending' }), {})
const INIT_ELAPSED = () => AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: null }), {})

export function AgentProgress({ status }) {
  const [agentStates, setAgentStates] = useState(INIT_STATES)
  const [elapsed, setElapsed] = useState(INIT_ELAPSED)

  useEffect(() => {
    if (status === 'idle') {
      setAgentStates(INIT_STATES())
      setElapsed(INIT_ELAPSED())
      return
    }
    if (status === 'done' || status === 'error') {
      setAgentStates(AGENTS.reduce((acc, a) => ({ ...acc, [a.key]: 'done' }), {}))
      return
    }
    if (status !== 'loading') return

    const startTime = Date.now()
    const timers = []

    AGENTS.forEach((agent) => {
      timers.push(
        setTimeout(() => {
          setAgentStates((prev) => ({ ...prev, [agent.key]: 'running' }))
        }, agent.delay),
      )
      timers.push(
        setTimeout(() => {
          const sec = ((Date.now() - startTime) / 1000).toFixed(1)
          setAgentStates((prev) => ({ ...prev, [agent.key]: 'done' }))
          setElapsed((prev) => ({ ...prev, [agent.key]: sec }))
        }, agent.delay + agent.duration),
      )
    })

    return () => timers.forEach(clearTimeout)
  }, [status])

  const doneCount = Object.values(agentStates).filter((s) => s === 'done').length
  const pct = Math.round((doneCount / AGENTS.length) * 100)

  return (
    <div>
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
        Agent Pipeline
      </div>
      <div className="grid grid-cols-2 gap-1 mb-3">
        {AGENTS.map((agent) => {
          const s = agentStates[agent.key]
          return (
            <div
              key={agent.key}
              className={`flex items-center gap-2 px-2 py-1.5 rounded text-xs ${
                s === 'running' ? 'bg-amber-50' : ''
              }`}
            >
              {s === 'done' ? (
                <CheckCircle2 size={13} className="text-emerald-500 shrink-0" />
              ) : s === 'running' ? (
                <Loader2 size={13} className="text-amber-500 animate-spin shrink-0" />
              ) : (
                <Circle size={13} className="text-slate-300 shrink-0" />
              )}
              <span className={s === 'pending' ? 'text-slate-400' : 'text-slate-700 font-medium'}>
                {agent.label}
              </span>
              {elapsed[agent.key] && (
                <span className="ml-auto text-slate-400">{elapsed[agent.key]}s</span>
              )}
            </div>
          )
        })}
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-indigo-400 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 3: Commit**

```powershell
cd ../..
git add src/frontend_react/src/components/analyst/AgentProgress.jsx
git commit -m "Add AgentProgress tracker with timed animation for 9 agents"
```

---

## Task 8: QueryPanel + AnalysisResult

**Files:**
- Create: `src/frontend_react/src/components/analyst/QueryPanel.jsx`
- Create: `src/frontend_react/src/components/analyst/AnalysisResult.jsx`

- [ ] **Step 1: Create `src/frontend_react/src/components/analyst/QueryPanel.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { SymbolInput } from './SymbolInput'

const ANALYSIS_TYPES = [
  'comprehensive', 'technical', 'risk', 'sentiment', 'portfolio', 'crypto', 'quick',
]
const TIMEFRAMES = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
const RISK_LEVELS = ['conservative', 'moderate', 'aggressive']

export function QueryPanel({ onRun, loading, onSymbolsChange, onTimeframeChange }) {
  const location = useLocation()
  const replay = location.state?.replay

  const [question, setQuestion] = useState(replay?.question || '')
  const [symbols, setSymbols] = useState(replay?.symbols || [])
  const [analysisType, setAnalysisType] = useState(replay?.analysis_type || 'comprehensive')
  const [timeframe, setTimeframe] = useState('1y')
  const [risk, setRisk] = useState('moderate')
  const [didAutoRun, setDidAutoRun] = useState(false)

  useEffect(() => {
    onSymbolsChange?.(symbols)
  }, [symbols])

  useEffect(() => {
    onTimeframeChange?.(timeframe)
  }, [timeframe])

  // Auto-submit when arriving from History replay
  useEffect(() => {
    if (replay && !didAutoRun && question) {
      setDidAutoRun(true)
      onRun({ question, symbols, analysis_type: analysisType, timeframe, risk_tolerance: risk })
    }
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!question.trim() || loading) return
    onRun({ question, symbols, analysis_type: analysisType, timeframe, risk_tolerance: risk })
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-b border-slate-100">
      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
        Query
      </div>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        maxLength={1000}
        rows={3}
        placeholder="What's the outlook for AAPL this quarter?"
        className="w-full resize-none bg-slate-50 border border-slate-200 rounded-md p-2.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-2.5 transition-shadow"
      />

      <div className="mb-2.5">
        <div className="text-xs text-slate-400 mb-1">Symbols</div>
        <SymbolInput symbols={symbols} onChange={setSymbols} />
      </div>

      <div className="flex flex-wrap gap-1.5 mb-2.5">
        {ANALYSIS_TYPES.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setAnalysisType(t)}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              analysisType === t
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div>
          <div className="text-xs text-slate-400 mb-1">Timeframe</div>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="w-full border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {TIMEFRAMES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <div className="text-xs text-slate-400 mb-1">Risk Tolerance</div>
          <select
            value={risk}
            onChange={(e) => setRisk(e.target.value)}
            className="w-full border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {RISK_LEVELS.map((r) => (
              <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !question.trim()}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg py-2.5 text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
      >
        {loading ? (
          <>
            <Loader2 size={14} className="animate-spin" />
            Analyzing…
          </>
        ) : (
          'Run Analysis →'
        )}
      </button>
    </form>
  )
}
```

- [ ] **Step 2: Create `src/frontend_react/src/components/analyst/AnalysisResult.jsx`**

```jsx
import { useEffect, useState, useRef } from 'react'
import { AlertTriangle } from 'lucide-react'

const AGENT_LABELS = {
  market_research: '📰 Market Research',
  technical_analysis: '📊 Technical Analysis',
  risk_assessment: '⚠️ Risk Assessment',
  sentiment_analysis: '💬 Sentiment Analysis',
  portfolio_analysis: '📈 Portfolio Analysis',
  sector_analysis: '🏭 Sector Analysis',
  crypto_analysis: '₿ Crypto Analysis',
}

export function AnalysisResult({ result }) {
  const [displayed, setDisplayed] = useState('')
  const [expanded, setExpanded] = useState({})
  const intervalRef = useRef(null)

  const fullText = result?.data?.final_analysis || ''

  useEffect(() => {
    clearInterval(intervalRef.current)
    setDisplayed('')
    if (!fullText) return

    let idx = 0
    intervalRef.current = setInterval(() => {
      idx = Math.min(idx + 3, fullText.length)
      setDisplayed(fullText.slice(0, idx))
      if (idx >= fullText.length) clearInterval(intervalRef.current)
    }, 15)

    return () => clearInterval(intervalRef.current)
  }, [fullText])

  const individual = result?.data?.individual_analyses || {}
  const agentEntries = Object.entries(AGENT_LABELS).filter(([k]) => individual[k])

  return (
    <div>
      {result?.error && (
        <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-md p-3 mb-3 text-xs text-amber-800">
          <AlertTriangle size={13} className="shrink-0 mt-0.5" />
          <span>Some agents reported issues: {result.error}</span>
        </div>
      )}

      <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap mb-4">
        {displayed}
        {displayed.length < fullText.length && (
          <span className="inline-block w-0.5 h-4 bg-indigo-500 animate-pulse ml-0.5 align-middle" />
        )}
      </div>

      {agentEntries.length > 0 && (
        <div className="border border-slate-200 rounded-md overflow-hidden">
          <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wide">
            Agent Outputs
          </div>
          {agentEntries.map(([key, label]) => (
            <div key={key} className="border-b border-slate-100 last:border-0">
              <button
                type="button"
                onClick={() => setExpanded((p) => ({ ...p, [key]: !p[key] }))}
                className="w-full flex justify-between items-center px-3 py-2.5 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors text-left"
              >
                {label}
                <span className="text-slate-400 ml-2 flex-shrink-0">{expanded[key] ? '▾' : '›'}</span>
              </button>
              {expanded[key] && (
                <div className="px-3 pb-3 text-xs text-slate-600 leading-relaxed whitespace-pre-wrap bg-slate-50 border-t border-slate-100">
                  {individual[key]}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 4: Commit**

```powershell
cd ../..
git add src/frontend_react/src/components/analyst/QueryPanel.jsx src/frontend_react/src/components/analyst/AnalysisResult.jsx
git commit -m "Add QueryPanel form and AnalysisResult with typewriter animation"
```

---

## Task 9: Chart components

**Files:**
- Create: `src/frontend_react/src/components/charts/PriceChart.jsx`
- Create: `src/frontend_react/src/components/charts/VolumeChart.jsx`
- Create: `src/frontend_react/src/components/charts/TechnicalChart.jsx`
- Create: `src/frontend_react/src/components/charts/SectorChart.jsx`
- Create: `src/frontend_react/src/components/charts/AllocationChart.jsx`
- Create: `src/frontend_react/src/components/charts/ChartPanel.jsx`

- [ ] **Step 1: Create `src/frontend_react/src/components/charts/PriceChart.jsx`**

```jsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { mergeByDate } from '../../utils/chartUtils'

const COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function PriceChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null
  const symbols = Object.keys(data)
  const merged = mergeByDate(data, 'close')

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={merged} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          tickFormatter={(v) => v.slice(5)}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fontSize: 10 }}
          width={58}
          tickFormatter={(v) => `$${v.toFixed(0)}`}
        />
        <Tooltip
          formatter={(v) => [`$${Number(v).toFixed(2)}`]}
          labelStyle={{ fontSize: 11 }}
          contentStyle={{ fontSize: 11 }}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {symbols.map((sym, i) => (
          <Line
            key={sym}
            type="monotone"
            dataKey={sym}
            stroke={COLORS[i % COLORS.length]}
            dot={false}
            strokeWidth={1.5}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 2: Create `src/frontend_react/src/components/charts/VolumeChart.jsx`**

```jsx
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { mergeByDate } from '../../utils/chartUtils'

const COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

function fmtVol(v) {
  if (v >= 1e9) return `${(v / 1e9).toFixed(1)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(1)}K`
  return String(v)
}

export function VolumeChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null
  const symbols = Object.keys(data)
  const merged = mergeByDate(data, 'volume')

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={merged} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          tickFormatter={(v) => v.slice(5)}
          interval="preserveStartEnd"
        />
        <YAxis tick={{ fontSize: 10 }} width={45} tickFormatter={fmtVol} />
        <Tooltip formatter={(v) => [fmtVol(Number(v))]} labelStyle={{ fontSize: 11 }} contentStyle={{ fontSize: 11 }} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {symbols.map((sym, i) => (
          <Bar key={sym} dataKey={sym} fill={COLORS[i % COLORS.length]} opacity={0.8} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 3: Create `src/frontend_react/src/components/charts/TechnicalChart.jsx`**

```jsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { computeRSI } from '../../utils/chartUtils'

export function TechnicalChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null
  const firstSymbol = Object.keys(data)[0]
  const rows = data[firstSymbol]
  if (!rows || rows.length === 0) return null

  const closes = rows.map((r) => r.close)
  const rsiValues = computeRSI(closes)
  const chartData = rows
    .map((r, i) => ({
      date: r.date,
      rsi: rsiValues[i] !== null ? parseFloat(Number(rsiValues[i]).toFixed(1)) : null,
    }))
    .filter((r) => r.rsi !== null)

  return (
    <div className="flex flex-col h-full gap-1">
      <div className="text-xs font-medium text-slate-500">
        {firstSymbol} — RSI (14-period)
      </div>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickFormatter={(v) => v.slice(5)}
              interval="preserveStartEnd"
            />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} width={32} />
            <Tooltip
              formatter={(v) => [Number(v).toFixed(1), 'RSI']}
              labelStyle={{ fontSize: 11 }}
              contentStyle={{ fontSize: 11 }}
            />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2"
              label={{ value: 'OB 70', fontSize: 9, fill: '#ef4444', position: 'right' }} />
            <ReferenceLine y={30} stroke="#10b981" strokeDasharray="4 2"
              label={{ value: 'OS 30', fontSize: 9, fill: '#10b981', position: 'right' }} />
            <Line type="monotone" dataKey="rsi" stroke="#6366f1" dot={false} strokeWidth={1.5} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create `src/frontend_react/src/components/charts/SectorChart.jsx`**

```jsx
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer,
} from 'recharts'
import { computeReturn } from '../../utils/chartUtils'

export function SectorChart({ data }) {
  if (!data || Object.keys(data).length === 0) return null

  const chartData = Object.entries(data).map(([sym, rows]) => ({
    name: sym,
    return: computeReturn(rows),
  }))

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={45} />
        <Tooltip
          formatter={(v) => [`${v}%`, 'Return']}
          labelStyle={{ fontSize: 11 }}
          contentStyle={{ fontSize: 11 }}
        />
        <Bar dataKey="return" radius={[0, 3, 3, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 5: Create `src/frontend_react/src/components/charts/AllocationChart.jsx`**

```jsx
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#6366f1', '#818cf8', '#a5b4fc', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function AllocationChart({ symbols, weights }) {
  if (!symbols || symbols.length === 0) return null
  const total = weights.reduce((s, w) => s + Number(w), 0) || 1
  const chartData = symbols.map((sym, i) => ({
    name: sym,
    value: parseFloat(((Number(weights[i]) / total) * 100).toFixed(1)),
  }))

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius="38%"
          outerRadius="65%"
          dataKey="value"
          nameKey="name"
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v) => [`${v}%`]} contentStyle={{ fontSize: 11 }} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 6: Create `src/frontend_react/src/components/charts/ChartPanel.jsx`**

```jsx
import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { PriceChart } from './PriceChart'
import { TechnicalChart } from './TechnicalChart'
import { VolumeChart } from './VolumeChart'
import { SectorChart } from './SectorChart'

const TABS = ['Price', 'RSI', 'Volume', 'Sector']

export function ChartPanel({ chartData, loading, error }) {
  const [activeTab, setActiveTab] = useState('Price')

  if (!chartData && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-sm text-slate-400">Add symbols to see charts</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-0.5 p-1 bg-slate-100 rounded-lg w-fit mb-3 flex-shrink-0">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              activeTab === tab
                ? 'bg-white text-slate-800 font-medium shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-full text-slate-400 text-sm gap-2">
            <Loader2 size={15} className="animate-spin" />
            Loading chart data…
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-400 text-sm">
            Chart data unavailable
          </div>
        ) : (
          <>
            {activeTab === 'Price' && <PriceChart data={chartData} />}
            {activeTab === 'RSI' && <TechnicalChart data={chartData} />}
            {activeTab === 'Volume' && <VolumeChart data={chartData} />}
            {activeTab === 'Sector' && <SectorChart data={chartData} />}
          </>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 8: Commit**

```powershell
cd ../..
git add src/frontend_react/src/components/charts/
git commit -m "Add Recharts chart components: Price, Volume, RSI, Sector, Allocation, ChartPanel"
```

---

## Task 10: Analyst page (the hero split panel)

**Files:**
- Replace: `src/frontend_react/src/pages/Analyst.jsx`

- [ ] **Step 1: Replace `src/frontend_react/src/pages/Analyst.jsx`**

```jsx
import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { QueryPanel } from '../components/analyst/QueryPanel'
import { AnalysisResult } from '../components/analyst/AnalysisResult'
import { AgentProgress } from '../components/analyst/AgentProgress'
import { ChartPanel } from '../components/charts/ChartPanel'
import { useAnalysis } from '../hooks/useAnalysis'
import { useChartData } from '../hooks/useChartData'

export function Analyst() {
  const { status, result, error, run } = useAnalysis()
  const [symbols, setSymbols] = useState([])
  const [timeframe, setTimeframe] = useState('1y')
  const { data: chartData, loading: chartLoading, error: chartError } = useChartData(
    symbols,
    timeframe,
  )

  const handleRun = (payload) => {
    run(payload)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="bg-white border-b border-slate-200 px-5 py-3 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-sm font-bold text-slate-900">AI Market Analyst</h1>
          <p className="text-xs text-slate-400 mt-0.5">Powered by 8 specialized agents</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full text-xs font-medium">
            Groq LLM
          </span>
          <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full text-xs font-medium">
            LangGraph
          </span>
        </div>
      </div>

      {/* Split body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel: query form + result */}
        <div className="w-[420px] flex-shrink-0 border-r border-slate-200 flex flex-col bg-white overflow-y-auto">
          <QueryPanel
            onRun={handleRun}
            loading={status === 'loading'}
            onSymbolsChange={setSymbols}
            onTimeframeChange={setTimeframe}
          />

          {status === 'error' && (
            <div className="mx-4 mt-3 flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 rounded-md p-3 text-xs">
              <AlertCircle size={13} className="shrink-0 mt-0.5" />
              <span>{error || 'Backend unreachable — make sure python main.py is running.'}</span>
            </div>
          )}

          {status === 'done' && result && (
            <div className="p-4 flex-1">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                AI Analysis
              </div>
              <AnalysisResult result={result} />
            </div>
          )}
        </div>

        {/* Right panel: agent progress + charts */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          <div className="bg-white border-b border-slate-200 p-4 flex-shrink-0">
            <AgentProgress status={status} />
          </div>
          <div className="flex-1 p-4 overflow-hidden flex flex-col min-h-0">
            <ChartPanel
              chartData={chartData}
              loading={chartLoading}
              error={chartError}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 3: Commit**

```powershell
cd ../..
git add src/frontend_react/src/pages/Analyst.jsx
git commit -m "Implement Analyst split-panel page with query form, AI result, agent tracker, and charts"
```

---

## Task 11: History page

**Files:**
- Replace: `src/frontend_react/src/pages/History.jsx`

- [ ] **Step 1: Replace `src/frontend_react/src/pages/History.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Clock, BarChart2, Hash } from 'lucide-react'
import client from '../api/client'

const TYPE_COLORS = {
  comprehensive: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  technical:     'bg-amber-50 text-amber-700 border-amber-200',
  risk:          'bg-red-50 text-red-700 border-red-200',
  sentiment:     'bg-purple-50 text-purple-700 border-purple-200',
  portfolio:     'bg-emerald-50 text-emerald-700 border-emerald-200',
  crypto:        'bg-pink-50 text-pink-700 border-pink-200',
  quick:         'bg-slate-50 text-slate-600 border-slate-200',
}

export function History() {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([client.get('/history'), client.get('/stats')])
      .then(([h, s]) => {
        setHistory(h.data.history || [])
        setStats(s.data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleReplay = (record) => {
    navigate('/', {
      state: {
        replay: {
          question: record.question,
          symbols: record.symbols,
          analysis_type: record.analysis_type,
        },
      },
    })
  }

  return (
    <div className="p-6 max-w-5xl mx-auto w-full">
      <h1 className="text-lg font-bold text-slate-900 mb-5">Query History</h1>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { icon: Hash, label: 'Total Queries', value: stats.total_queries, color: 'text-slate-900' },
            { icon: Clock, label: 'Avg Time', value: `${stats.average_processing_time}s`, color: 'text-slate-900' },
            {
              icon: BarChart2,
              label: 'Top Symbol',
              value: stats.most_analyzed_symbols[0]?.[0] || '—',
              color: 'text-indigo-600',
            },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="bg-white border border-slate-200 rounded-lg p-4">
              <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1.5">
                <Icon size={12} />
                {label}
              </div>
              <div className={`text-2xl font-bold ${color}`}>{value}</div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="grid grid-cols-[1fr_110px_120px_70px_80px] px-4 py-2.5 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wide">
          <span>Question</span>
          <span>Symbols</span>
          <span>Type</span>
          <span>Time</span>
          <span />
        </div>

        {loading ? (
          <div className="text-center py-10 text-slate-400 text-sm">Loading…</div>
        ) : error ? (
          <div className="text-center py-10 text-red-400 text-sm">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-sm">
            No queries yet — run your first analysis on the Analyst page.
          </div>
        ) : (
          history.map((record, i) => (
            <div
              key={i}
              className="grid grid-cols-[1fr_110px_120px_70px_80px] px-4 py-3 border-b border-slate-100 last:border-0 items-center hover:bg-slate-50 transition-colors"
            >
              <span className="text-sm text-slate-700 truncate pr-4">
                {record.question.length > 60
                  ? `${record.question.slice(0, 60)}…`
                  : record.question}
              </span>
              <span className="text-xs text-indigo-600 truncate">
                {record.symbols.slice(0, 3).join(', ')}
                {record.symbols.length > 3 ? '…' : ''}
              </span>
              <span>
                <span
                  className={`text-xs border rounded px-1.5 py-0.5 ${
                    TYPE_COLORS[record.analysis_type] || TYPE_COLORS.comprehensive
                  }`}
                >
                  {record.analysis_type}
                </span>
              </span>
              <span className="text-xs text-slate-400">
                {record.processing_time?.toFixed(1)}s
              </span>
              <button
                type="button"
                onClick={() => handleReplay(record)}
                className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
              >
                <ExternalLink size={11} />
                Replay
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 3: Commit**

```powershell
cd ../..
git add src/frontend_react/src/pages/History.jsx
git commit -m "Implement History page with stats bar and one-click replay"
```

---

## Task 12: Portfolio page

**Files:**
- Replace: `src/frontend_react/src/pages/Portfolio.jsx`

- [ ] **Step 1: Replace `src/frontend_react/src/pages/Portfolio.jsx`**

```jsx
import { useState } from 'react'
import { Plus, Trash2, Loader2 } from 'lucide-react'
import { AllocationChart } from '../components/charts/AllocationChart'
import client from '../api/client'

export function Portfolio() {
  const [rows, setRows] = useState([{ symbol: '', weight: 100 }])
  const [risk, setRisk] = useState('moderate')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const totalWeight = rows.reduce((s, r) => s + Number(r.weight), 0)
  const weightsValid = Math.abs(totalWeight - 100) < 0.5
  const symbolsValid = rows.every((r) => /^[A-Z0-9.]{1,10}$/.test(r.symbol.trim()))
  const canSubmit = weightsValid && symbolsValid && rows.length >= 1 && !loading

  const updateRow = (i, field, value) =>
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)))

  const addRow = () =>
    setRows((prev) => [...prev, { symbol: '', weight: 0 }])

  const removeRow = (i) =>
    setRows((prev) => prev.filter((_, idx) => idx !== i))

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const symbols = rows.map((r) => r.symbol.trim().toUpperCase())
      const weights = rows.map((r) => parseFloat((Number(r.weight) / 100).toFixed(4)))
      const { data } = await client.post('/portfolio', {
        symbols,
        weights,
        risk_tolerance: risk,
      })
      if (data.success) setResult(data)
      else setError(data.error || 'Portfolio analysis failed')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Backend unreachable — make sure python main.py is running.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto w-full">
      <h1 className="text-lg font-bold text-slate-900 mb-5">Portfolio Analyzer</h1>

      <div className="grid grid-cols-[360px_1fr] gap-6 items-start">
        {/* Builder */}
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Build Portfolio
          </div>

          <div className="flex flex-col gap-2 mb-3">
            {rows.map((row, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  value={row.symbol}
                  onChange={(e) => updateRow(i, 'symbol', e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  maxLength={10}
                  className="w-20 border border-slate-200 rounded px-2 py-1 text-xs text-slate-700 uppercase focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={row.weight}
                  onChange={(e) => updateRow(i, 'weight', e.target.value)}
                  className="flex-1 accent-indigo-600"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={row.weight}
                  onChange={(e) => updateRow(i, 'weight', e.target.value)}
                  className="w-14 border border-slate-200 rounded px-2 py-1 text-xs text-center focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-400">%</span>
                {rows.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeRow(i)}
                    className="text-slate-300 hover:text-red-400 transition-colors"
                    aria-label="Remove symbol"
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addRow}
            disabled={rows.length >= 50}
            className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 transition-colors mb-4 disabled:opacity-40"
          >
            <Plus size={12} />
            Add symbol
          </button>

          <div
            className={`text-xs mb-3 font-medium ${
              weightsValid ? 'text-emerald-600' : 'text-amber-600'
            }`}
          >
            Total: {totalWeight.toFixed(1)}%{' '}
            {weightsValid ? '✓ ready' : '— must equal 100%'}
          </div>

          <div className="mb-3">
            <div className="text-xs text-slate-400 mb-1">Risk Tolerance</div>
            <select
              value={risk}
              onChange={(e) => setRisk(e.target.value)}
              className="w-full border border-slate-200 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg py-2 text-sm font-semibold flex items-center justify-center gap-2 transition-colors"
          >
            {loading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Analyzing…
              </>
            ) : (
              'Analyze Portfolio →'
            )}
          </button>

          {error && (
            <div className="mt-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded p-2">
              {error}
            </div>
          )}
        </div>

        {/* Result */}
        <div>
          {result ? (
            <div className="flex flex-col gap-4">
              <div className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                  Allocation
                </div>
                <div className="h-52">
                  <AllocationChart
                    symbols={rows.map((r) => r.symbol.toUpperCase())}
                    weights={rows.map((r) => Number(r.weight))}
                  />
                </div>
              </div>
              <div className="bg-white border border-slate-200 rounded-lg p-4">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                  AI Analysis
                </div>
                <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {result.data?.final_analysis}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-10 text-center text-slate-400 text-sm">
              Build your portfolio on the left and click Analyze to see results.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify build passes**

```powershell
cd src/frontend_react
npm run build
```

Expected: `✓ built in X.Xs`.

- [ ] **Step 3: Commit**

```powershell
cd ../..
git add src/frontend_react/src/pages/Portfolio.jsx
git commit -m "Implement Portfolio builder page with weight sliders and allocation chart"
```

---

## Task 13: Update CLAUDE.md + final verification

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the Development Workflows section in `CLAUDE.md`**

Find the section that contains Gradio frontend run instructions (around the "Run backend + standard frontend" and "Run backend + enhanced frontend" subsections) and replace it with:

```markdown
### Run backend + React frontend (two terminals)

```powershell
# Terminal 1 — backend
python main.py

# Terminal 2 — React frontend
cd src/frontend_react
npm run dev   # → http://localhost:5173
```

### Service URLs

| Service | URL |
|---------|-----|
| Frontend (React) | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
```

Also update the Common Commands section — remove Gradio-specific commands and add:

```powershell
# Install React frontend dependencies (first time only)
cd src/frontend_react && npm install

# Run React frontend (dev mode)
cd src/frontend_react && npm run dev

# Build React frontend (production)
cd src/frontend_react && npm run build

# Run React frontend tests
cd src/frontend_react && npm test
```

- [ ] **Step 2: Run the full Python test suite**

```powershell
pytest tests/ -q
```

Expected: 49 passed, 0 failed.

- [ ] **Step 3: Run ruff**

```powershell
ruff check src/
```

Expected: `All checks passed!`

- [ ] **Step 4: Run the React test suite**

```powershell
cd src/frontend_react
npm test
```

Expected: 14 tests passed.

- [ ] **Step 5: Run a production build to confirm no import errors**

```powershell
npm run build
```

Expected: `✓ built in X.Xs` with no TypeScript/JSX errors.

- [ ] **Step 6: Commit**

```powershell
cd ../..
git add CLAUDE.md
git commit -m "Update CLAUDE.md with React frontend instructions"
```

---

## Done

At this point the implementation is complete:

- `GET /chart-data` backend endpoint with 5 pytest tests
- Gradio files deleted, React project scaffolded
- API client + 3 custom hooks, 5 hook tests
- 3 chart utility functions, 9 unit tests
- Sidebar, Layout, App routing with React Router v6
- SymbolInput chip component
- AgentProgress 9-agent tracker with timed animation
- QueryPanel form + AnalysisResult typewriter display
- 5 Recharts chart components + ChartPanel tab switcher
- Analyst split-panel hero page
- History page with stats and one-click Replay
- Portfolio builder with weight sliders + allocation pie chart
- CLAUDE.md updated

Run `python main.py` in one terminal and `cd src/frontend_react && npm run dev` in another. Open http://localhost:5173.
