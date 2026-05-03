# Claude Code Project Setup — MarketSage Analytics

**Spec date:** 2026-05-03
**Author:** Talha Umer
**Status:** Approved (brainstorming complete)

---

## 1. Goal

Configure Claude Code to be effective and safe inside the MarketSage Analytics repository. Four artifacts are produced:

1. A repository-level `CLAUDE.md` that orients Claude Code on architecture, agents, the LangGraph workflow, common workflows, debugging, and strict project rules.
2. A repository-level `.claude/settings.json` with permissions, hooks, and environment variables.
3. A user-level memory directory at `C:\Users\talha\.claude\projects\C--Users-talha-Downloads-MarketSage-Analytics\memory\` with a project snapshot, gotchas, and developer preferences, indexed by `MEMORY.md`.
4. A `docs/` reorganization with `architecture/`, `agents/`, `api/`, and `superpowers/specs/` placeholders ready to be filled.

These four artifacts together let any new Claude Code session start productive immediately, follow Talha's strict commit rules, and avoid the project's known footguns (PYTHONPATH, mock LLM, rate limits).

---

## 2. Non-Goals

- Not changing application source code.
- Not adding new agents or workflow nodes.
- Not modifying CI / GitHub Actions.
- Not adding ruff/black configuration files (the `ruff` package is already in requirements.txt; the pre-commit hook just runs `ruff check`).
- Not generating per-agent documentation content (only directory scaffolding).

---

## 3. Artifact 1 — `CLAUDE.md`

### 3.1 Location

`C:\Users\talha\Downloads\MarketSage-Analytics\CLAUDE.md`

### 3.2 Section list (final order)

1. Project Overview
2. Tech Stack
3. Project Structure
4. Agent Architecture (NEW)
5. LangGraph Workflow Guide (NEW)
6. Development Workflows (NEW)
7. Debugging Guide (NEW)
8. Common Commands
9. Environment Variables
10. Coding Rules
11. Git Rules
12. Security
13. Disclaimer

### 3.3 Per-section design

**Project Overview** — Two-sentence pitch: multi-agent system, LangGraph + Groq, stocks + crypto + news. Keep it fast to read.

**Tech Stack** — Table of layer / technology, locked to versions in `requirements.txt`: Python 3.8+, Gradio 5.47, FastAPI 0.117, LangGraph 0.6.7, Groq via langchain-groq 0.3.8, yfinance 0.2.50, pycoingecko 3.1.0, duckduckgo-search 7.2.0, pytest, ruff 0.13.2.

**Project Structure** — Annotated directory tree showing `src/agents/`, `src/tools/`, `src/workflows/`, `src/api/`, `src/frontend/`, `src/utils/`, plus the entry points at the root.

**Agent Architecture** — Table of all 8 agents plus the synthesis agent: name, file, role, key inputs (state keys read), key outputs (state keys written), execution mode (parallel after market_research, then synthesis runs last). Explicitly notes that `market_research` is the entry node, all 7 analysis agents run in parallel, then `final_synthesis` collects everything.

**LangGraph Workflow Guide** — Explains:
- The `State` TypedDict in `src/workflows/state.py` and its reducer functions (`string_reducer`, `dict_reducer`, `error_reducer`).
- The graph structure in `src/workflows/financial_analysis_workflow.py` (entry point `market_research` → fan-out to 7 agents → fan-in to `final_synthesis` → END).
- The `SmartAnalysisRouter` in `src/workflows/smart_router.py` and the `should_run_*` conditional functions.
- A 5-step checklist for adding a new agent node:
  1. Create agent function in `src/agents/<name>_agent.py` with signature `(state: State) -> State`.
  2. Export it from `src/agents/__init__.py`.
  3. Add a state key in `src/workflows/state.py` with an appropriate `Annotated[..., reducer]`.
  4. Register the node and edges in `create_financial_analysis_workflow()`.
  5. Surface it in `src/api/main.py` `individual_analyses` and `src/api/models.py` `IndividualAnalyses`.

**Development Workflows** — Practical recipes:
- Running backend + frontend in two terminals (Windows-friendly, no `bash` requirement).
- Running the with-viz frontend on Windows when `run_frontend_with_viz.sh` is bash (suggest `python src/frontend/gradio_app_with_viz.py` directly with `PYTHONPATH=src` set).
- Adding a new analysis type (extend `AnalysisType` enum in `models.py`, add a branch in `final_synthesis_agent`, document expected input).
- Using the Swagger UI at `/docs` to exercise endpoints.

**Debugging Guide** — Symptom → cause → fix table for the 4 most common issues:
- "Mock LLM responses showing in output" — `GROQ_API_KEY` missing or invalid → set in `.env`, check stdout for `No GROQ_API_KEY found in environment, using mock LLM...`
- "ModuleNotFoundError: No module named 'workflows'" — `PYTHONPATH` not set → run via `python main.py` (which prepends `src/` to `sys.path`) or set `PYTHONPATH=src` explicitly.
- "yfinance: Too Many Requests" — Yahoo rate limit → reduce symbol count, increase timeframe granularity, or wait 60s; consider per-symbol caching in `BaseAgent.cache_set`.
- "CoinGecko: 429 Too Many Requests" — CoinGecko rate limit on free tier (~30 req/min) → add `COINGECKO_API_KEY`, reduce request frequency, or add backoff in `crypto_data_tools.py`.

**Common Commands** — Verbatim shell-friendly commands for install, run backend, run frontend, run with-viz frontend, run tests with coverage, lint with ruff. Includes Windows PowerShell equivalents where bash differs.

**Environment Variables** — Table of `GROQ_API_KEY`, `OPENAI_API_KEY`, `API_BASE_URL`, `COINGECKO_API_KEY` with required/optional and purpose. Notes `.env` is not committed and `env.example` is the template.

**Coding Rules** — Module placement, Pydantic for I/O, symbol validation rules, mock fallback must keep working, no new top-level deps without updating `requirements.txt`, prefer editing existing files, no new markdown docs unless requested, no comments unless the *why* is non-obvious.

**Git Rules** — The strict author identity, never use AI co-author lines, imperative messages under 72 chars, never force-push main, never `--no-verify`, never amend pushed commits, stage explicitly, don't commit unless asked, branching conventions (`feature/`, `fix/`).

**Security** — No commits of `.env` or keys, validate user input before passing to data fetchers.

**Disclaimer** — Educational/research only, not investment advice.

---

## 4. Artifact 2 — `.claude/settings.json`

### 4.1 Location

`C:\Users\talha\Downloads\MarketSage-Analytics\.claude\settings.json`

### 4.2 Schema choice

Uses Claude Code's documented settings.json schema with three top-level keys: `permissions`, `hooks`, `env`. Permissions use the `allow` array of patterns. Hooks use the standard event names `PostToolUse` and `PreToolUse` with matchers and a list of hooks.

### 4.3 Permissions

Allowlist (each `Bash(<glob>)` permits invocations matching the prefix; `:*` lets everything past the matched prefix through):

- `Bash(python:*)` — run main.py, run_frontend.py, ad-hoc scripts
- `Bash(python -m:*)` — module invocation (`python -m pytest`, `python -m uvicorn`)
- `Bash(pytest:*)` — direct pytest
- `Bash(pip:*)` — install, list, freeze
- `Bash(pip install:*)` — explicit install patterns
- `Bash(ruff:*)` — `ruff check`, `ruff format`
- `Bash(uvicorn:*)` — direct uvicorn invocation
- `Bash(gradio:*)` — direct gradio CLI
- `Bash(git status:*)`, `Bash(git status)` — read-only
- `Bash(git log:*)`, `Bash(git log)` — read-only
- `Bash(git diff:*)`, `Bash(git diff)` — read-only
- `Bash(git show:*)` — read-only
- `Bash(git branch:*)` — list/create branches; destructive `git branch -D` still triggers a prompt because of the `--%-D` parsing nuance, and the careful skill should be used for any destructive branch operations.
- `Bash(git add:*)` — staging
- `Bash(git commit:*)` — committing (still subject to the pre-commit hook below)
- `Bash(git checkout:*)` — branch switching (the careful skill should still be used before `git checkout --` discards)
- `Bash(ls:*)`, `Bash(pwd)`, `Bash(cat:*)`, `Bash(echo:*)` — common read-only utilities

We deliberately do NOT allow `Bash(git push:*)`, `Bash(git reset:*)`, `Bash(git rebase:*)`, `Bash(git clean:*)`, or `Bash(rm:*)` — Claude must request permission for those.

### 4.4 Hooks

**PreToolUse — pre-commit ruff check.** Matcher fires on `Bash` calls whose command starts with `git commit`. The hook runs `ruff check src/` from the project root. Non-zero exit blocks the commit. Hook command (PowerShell, since the dev machine is Windows 11):

```
powershell -NoProfile -Command "cd 'C:/Users/talha/Downloads/MarketSage-Analytics'; ruff check src/"
```

We use `powershell` rather than `bash` so the hook works on the user's Windows machine without WSL. The `-NoProfile` flag avoids loading the user profile (faster, more deterministic).

**PostToolUse — task summary.** Matcher fires on the `Stop` event (built-in event when a Claude turn ends). The hook prints the working tree status so the user always sees what changed:

```
powershell -NoProfile -Command "cd 'C:/Users/talha/Downloads/MarketSage-Analytics'; git status --short"
```

### 4.5 Environment variables

Two project-level env vars are injected for every Claude Code session:

- `PYTHONPATH=src` — fixes the most common gotcha (modules under `src/` not importable).
- `API_BASE_URL=http://localhost:8000` — the default backend URL the frontend uses.

### 4.6 Final JSON content

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(python -m:*)",
      "Bash(pytest:*)",
      "Bash(pip:*)",
      "Bash(pip install:*)",
      "Bash(ruff:*)",
      "Bash(uvicorn:*)",
      "Bash(gradio:*)",
      "Bash(git status)",
      "Bash(git status:*)",
      "Bash(git log)",
      "Bash(git log:*)",
      "Bash(git diff)",
      "Bash(git diff:*)",
      "Bash(git show:*)",
      "Bash(git branch:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git checkout:*)",
      "Bash(ls:*)",
      "Bash(pwd)",
      "Bash(cat:*)",
      "Bash(echo:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -Command \"if ($env:CLAUDE_TOOL_INPUT_command -like 'git commit*') { Set-Location 'C:/Users/talha/Downloads/MarketSage-Analytics'; ruff check src/ }\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -Command \"Set-Location 'C:/Users/talha/Downloads/MarketSage-Analytics'; git status --short\""
          }
        ]
      }
    ]
  },
  "env": {
    "PYTHONPATH": "src",
    "API_BASE_URL": "http://localhost:8000"
  }
}
```

---

## 5. Artifact 3 — Memory files

### 5.1 Location

`C:\Users\talha\.claude\projects\C--Users-talha-Downloads-MarketSage-Analytics\memory\`

### 5.2 File set

Five files, each a Markdown document with a short title and bullet-style content:

1. `MEMORY.md` — index with one-line summary of each other file
2. `project-snapshot.md` — what the project is, who owns it, current status
3. `developer-preferences.md` — Talha's preferences (terse responses, no AI attribution, evidence before assertions)
4. `gotchas.md` — known footguns (PYTHONPATH, mock LLM, yfinance/CoinGecko rate limits, Windows bash scripts)
5. `git-rules.md` — strict commit/PR rules

### 5.3 Per-file content sketches

**`MEMORY.md`** (the index):

```
# Memory Index — MarketSage Analytics

- project-snapshot.md  — What the project is and who owns it.
- developer-preferences.md  — Talha's working style and response preferences.
- gotchas.md  — Known footguns and how to avoid them.
- git-rules.md  — Strict commit, branch, and PR rules.
```

**`project-snapshot.md`** — Identity (multi-agent financial analysis, LangGraph + Groq), 8 agents named, key entry points (`main.py`, `run_frontend.py`), tech stack one-liner, owner Talha Umer, current state (production-ready MVP, no CI yet).

**`developer-preferences.md`** — Terse responses by default, no preamble, evidence-before-assertions, no AI co-author/attribution lines, prefer editing existing files, no new docs without ask, only commit when asked, ask before destructive ops.

**`gotchas.md`** — Five entries with symptom → cause → fix pattern matching the CLAUDE.md Debugging Guide, plus one entry on Windows-vs-bash (`run_frontend_with_viz.sh` won't run natively in PowerShell — use `python src/frontend/gradio_app_with_viz.py` instead).

**`git-rules.md`** — Author Talha Umer, no Claude/Anthropic attribution anywhere, imperative subject under 72 chars, never `--no-verify`, never force-push main, never amend pushed commits, stage explicit files only, don't commit without ask, branching conventions.

---

## 6. Artifact 4 — `docs/` scaffolding

### 6.1 Directories created

- `C:\Users\talha\Downloads\MarketSage-Analytics\docs\architecture\`
- `C:\Users\talha\Downloads\MarketSage-Analytics\docs\agents\`
- `C:\Users\talha\Downloads\MarketSage-Analytics\docs\api\`
- `C:\Users\talha\Downloads\MarketSage-Analytics\docs\superpowers\specs\`

### 6.2 Placeholder `README.md` per subdirectory

Each `README.md` is short (<20 lines): purpose of the directory, what kind of files belong here, naming convention, link back to the root `README.md`.

- `docs/architecture/README.md` — system design, sequence diagrams, data flow. File names like `2026-05-03-langgraph-workflow.md`.
- `docs/agents/README.md` — one file per agent named `<agent-name>.md` (e.g., `market-research.md`).
- `docs/api/README.md` — endpoint reference beyond Swagger; auth notes; example payloads.
- `docs/superpowers/specs/README.md` — brainstorm spec files using ISO date prefix `YYYY-MM-DD-<slug>.md`. The current spec satisfies the placeholder requirement, so this README documents the convention.

The existing `docs/README.md` is left in place — it already describes the directory's purpose at a higher level.

---

## 7. Self-Review (placeholders, contradictions, ambiguity)

Reviewed sections 1–6 with these questions:

- **Any placeholders left?** Hook command earlier draft used a generic `git commit` matcher without context detection; corrected to use `$env:CLAUDE_TOOL_INPUT_command` so the hook only fires on actual `git commit` invocations rather than every `Bash` call. The matcher is set to `Bash` (broad) but the inline conditional restricts the action.
- **Contradictions?** Brainstorm said "post-task hook" — Claude Code's event for that is `Stop` (fires when the agent finishes a turn). Spec uses `Stop` and explicitly notes this so the hook event name is unambiguous.
- **Bash vs PowerShell?** Hooks must run on Windows. All hook commands are PowerShell-based with `-NoProfile`. The CLAUDE.md uses `bash` only for the official `run_frontend_with_viz.sh` reference but lists Windows alternatives.
- **`run_frontend_with_viz.sh` on Windows?** Resolved in CLAUDE.md Development Workflows by giving the equivalent `python src/frontend/gradio_app_with_viz.py` invocation.
- **Memory file paths?** Confirmed the project memory directory `C--Users-talha-Downloads-MarketSage-Analytics` already exists in `C:\Users\talha\.claude\projects\` (per environment listing). Only the `memory/` subfolder needs to be created.
- **Permissions completeness?** Added `git checkout:*` and `git branch:*` (often needed for branch hygiene) but explicitly excluded `git push`, `git reset`, `git rebase`, `git clean`, and `rm`. Read-only utilities (`ls`, `pwd`, `cat`, `echo`) included to avoid unnecessary prompts.
- **Pre-commit ruff scope?** Limited to `src/` to avoid false positives on `tests/` or top-level scripts; if Talha later wants strict tests too, switch to `ruff check`.

No remaining ambiguity. Spec is implementation-ready.

---

## 8. Implementation Order

1. Spec document (this file).
2. `CLAUDE.md` at project root.
3. `.claude/settings.json`.
4. Memory files (5 files including `MEMORY.md`).
5. Docs scaffolding (4 README files; `docs/superpowers/specs/README.md` documents the convention).

Each artifact is independent and can be committed separately as approved.

---

## 9. Verification Checklist

After implementation:

- `CLAUDE.md` exists at project root, is < 250 lines, all 13 sections present.
- `.claude/settings.json` parses as valid JSON (`python -c "import json; json.load(open('.claude/settings.json'))"`).
- Memory directory contains all 5 files.
- All 4 docs directories exist with a `README.md`.
- No code under `src/` was modified.
- No Claude attribution anywhere in any artifact.

---

## 10. Out-of-Scope (deferred to follow-up)

- Per-agent docs in `docs/agents/` (8 files).
- Architecture diagrams in `docs/architecture/`.
- API reference content beyond Swagger.
- Pre-commit framework integration (we use a Claude hook, not the `pre-commit` Python tool).
- CI workflow for ruff/pytest.
