# Agent Documentation

Per-agent reference for the eight specialized agents plus the final synthesis agent.

## What goes here

One Markdown file per agent describing:

- Purpose and scope.
- State keys read and written.
- Prompt template overview.
- External dependencies (LLM, data sources).
- Failure modes and how errors propagate via `state['error']`.
- Example invocations and expected output shape.

## Naming convention

Lowercase agent name with hyphens: `<agent-name>.md`.

| Agent | File |
|-------|------|
| Market Research | `market-research.md` |
| Financial Data | `financial-data.md` |
| Technical Analysis | `technical-analysis.md` |
| Risk Assessment | `risk-assessment.md` |
| Sentiment Analysis | `sentiment-analysis.md` |
| Portfolio Analysis | `portfolio-analysis.md` |
| Sector Analysis | `sector-analysis.md` |
| Crypto Analysis | `crypto-analysis.md` |
| Final Synthesis | `final-synthesis.md` |

## See also

- `../../CLAUDE.md` — Agent Architecture table summarising every agent.
- `../../src/agents/` — agent implementations.
