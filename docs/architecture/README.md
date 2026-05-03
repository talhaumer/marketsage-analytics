# Architecture Documentation

System design, data flow, and sequence diagrams for MarketSage Analytics.

## What goes here

- High-level architecture diagrams (LangGraph workflow, agent orchestration, data sources).
- Sequence diagrams for end-to-end requests (`/analyze`, `/portfolio`).
- State and reducer diagrams for `src/workflows/state.py`.
- Data flow between agents and external APIs (Yahoo Finance, CoinGecko, DuckDuckGo).
- ADRs (architecture decision records) for major changes.

## Naming convention

- ISO date prefix: `YYYY-MM-DD-<slug>.md` (e.g., `2026-05-03-langgraph-fanout-design.md`).
- ADRs: `adr-NNN-<slug>.md` (e.g., `adr-001-mock-llm-fallback.md`).

## See also

- `../../CLAUDE.md` — Agent Architecture and LangGraph Workflow Guide sections.
- `../agents/` — per-agent documentation.
- `../README.md` — top-level docs index.
