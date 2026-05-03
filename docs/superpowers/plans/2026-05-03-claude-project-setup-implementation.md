# Claude Code Project Setup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the four pre-written Claude Code setup artifacts (CLAUDE.md, .claude/settings.json, memory files, docs scaffolding) and land them as four atomic commits authored by Talha Umer.

**Architecture:** Pre-flight verification → four sequential commits (spec doc, CLAUDE.md, settings.json, docs scaffolding) → hook smoke tests → final verification. Memory files live outside the repo at `~/.claude/projects/.../memory/` and are NOT committed.

**Tech Stack:** Python 3.8+ (validation only), git, PowerShell (Windows 11), ruff 0.13.2 (pre-commit hook).

---

## Spec Reference

Source spec: `C:\Users\talha\Downloads\MarketSage-Analytics\docs\superpowers\specs\2026-05-03-claude-project-setup-design.md`

## File Inventory

**Already written (no further authoring required — only verification + commits):**

| Artifact | Path | Status |
|----------|------|--------|
| Spec doc | `docs/superpowers/specs/2026-05-03-claude-project-setup-design.md` | Written, untracked |
| Spec README | `docs/superpowers/specs/README.md` | Written, untracked |
| CLAUDE.md | `CLAUDE.md` | Written, untracked |
| Settings | `.claude/settings.json` | Written, untracked |
| Architecture docs scaffold | `docs/architecture/README.md` | Written, untracked |
| Agents docs scaffold | `docs/agents/README.md` | Written, untracked |
| API docs scaffold | `docs/api/README.md` | Written, untracked |
| Memory index | `~/.claude/projects/C--Users-talha-Downloads-MarketSage-Analytics/memory/MEMORY.md` | Written, NOT committed (outside repo) |
| Memory: project snapshot | `~/.claude/.../memory/project-snapshot.md` | Written, NOT committed |
| Memory: developer prefs | `~/.claude/.../memory/developer-preferences.md` | Written, NOT committed |
| Memory: gotchas | `~/.claude/.../memory/gotchas.md` | Written, NOT committed |
| Memory: git rules | `~/.claude/.../memory/git-rules.md` | Written, NOT committed |
| Plans dir | `docs/superpowers/plans/` | Created during plan write |

## Commit Plan

| # | Commit | Files staged |
|---|--------|--------------|
| 1 | Add Claude project setup design spec | `docs/superpowers/specs/2026-05-03-claude-project-setup-design.md`, `docs/superpowers/specs/README.md` |
| 2 | Add CLAUDE.md project guidance | `CLAUDE.md` |
| 3 | Add Claude Code permissions, hooks, and env | `.claude/settings.json` |
| 4 | Scaffold docs subdirectories with READMEs | `docs/architecture/README.md`, `docs/agents/README.md`, `docs/api/README.md` |

Memory files at `~/.claude/projects/.../memory/` are user-level config and are NOT in any commit.

## Strict Rules (read before every task)

- Author identity: Talha Umer (`talhaumer`). Never use `--author=...`.
- Zero AI attribution in commit messages, bodies, or any artifact: no `Co-Authored-By: Claude`, no "Generated with Claude Code", no robot-emoji footer.
- Imperative subject under 72 characters.
- Stage files explicitly by name. Never `git add -A` / `git add .`.
- Never `--no-verify`. Never force-push main.
- Always use HEREDOC for commit messages so formatting is preserved (PowerShell here-string `@'...'@`).
- **Do not commit unless the user explicitly asks.** This plan describes the steps; an executing agent should still pause for the user's explicit go-ahead before each `git commit`.

---

## Task 1: Pre-flight verification

**Files:** none modified — read-only checks.

- [ ] **Step 1: Confirm working directory and git state**

Run:
```powershell
Set-Location 'C:\Users\talha\Downloads\MarketSage-Analytics'
git status --short
git log --oneline -3
```

Expected output (untracked files may vary slightly in order):
```
?? .claude/
?? CLAUDE.md
?? docs/agents/
?? docs/api/
?? docs/architecture/
?? docs/superpowers/
bb80771 Improve README with accurate tech stack and project details
b2bd21a Initial commit
```

If `git status` shows tracked-file modifications under `src/`, **stop** and surface to user — this plan only adds new files.

- [ ] **Step 2: Verify each artifact exists with non-zero size**

Run:
```powershell
$paths = @(
    'CLAUDE.md',
    '.claude/settings.json',
    'docs/superpowers/specs/2026-05-03-claude-project-setup-design.md',
    'docs/superpowers/specs/README.md',
    'docs/architecture/README.md',
    'docs/agents/README.md',
    'docs/api/README.md'
)
foreach ($p in $paths) {
    if (Test-Path $p) { '{0,7} bytes  {1}' -f (Get-Item $p).Length, $p }
    else { 'MISSING        {0}' -f $p }
}
```

Expected: every path prints a `<bytes>  <path>` line, no `MISSING`. Sizes should be: CLAUDE.md ~14000, settings.json ~1400, spec ~17000, READMEs 700–1100.

- [ ] **Step 3: Validate `.claude/settings.json` parses**

Run:
```powershell
python -c "import json; d = json.load(open('.claude/settings.json')); assert set(d.keys()) >= {'permissions', 'hooks', 'env'}; print('OK', list(d.keys()))"
```

Expected: `OK ['$schema', 'permissions', 'hooks', 'env']`

If this errors, fix the JSON before proceeding (do not commit broken JSON).

- [ ] **Step 4: Verify env vars and hook keys are present**

Run:
```powershell
python -c @'
import json
d = json.load(open('.claude/settings.json'))
assert d['env'].get('PYTHONPATH') == 'src', 'PYTHONPATH wrong'
assert d['env'].get('API_BASE_URL') == 'http://localhost:8000', 'API_BASE_URL wrong'
assert any(h.get('matcher') == 'Bash' for h in d['hooks']['PreToolUse']), 'PreToolUse Bash matcher missing'
assert 'Stop' in d['hooks'], 'Stop hook missing'
perms = d['permissions']['allow']
required = ['Bash(python:*)', 'Bash(pytest:*)', 'Bash(ruff:*)', 'Bash(git commit:*)', 'Bash(git status)']
for r in required:
    assert r in perms, f'missing permission: {r}'
forbidden = ['Bash(git push:*)', 'Bash(git reset:*)', 'Bash(rm:*)']
for f in forbidden:
    assert f not in perms, f'forbidden permission present: {f}'
print('settings.json structural checks PASS')
'@
```

Expected: `settings.json structural checks PASS`

- [ ] **Step 5: Scan for AI attribution strings in all artifacts**

Run:
```powershell
$paths = @(
    'CLAUDE.md',
    '.claude/settings.json',
    'docs/superpowers/specs/2026-05-03-claude-project-setup-design.md',
    'docs/superpowers/specs/README.md',
    'docs/architecture/README.md',
    'docs/agents/README.md',
    'docs/api/README.md'
)
$forbidden = 'Co-Authored-By:|Generated with \[Claude Code\]|Generated with Claude Code|noreply@anthropic'
$hits = Select-String -Path $paths -Pattern $forbidden
if ($hits) { $hits | Format-List; throw 'FORBIDDEN attribution found' } else { 'no forbidden attribution found' }
```

Expected: `no forbidden attribution found`

(The string "Claude Code" appears legitimately in CLAUDE.md as the consumer of the file and in spec/memory references. We block only the *attribution* phrasings: `Co-Authored-By:`, `Generated with [Claude Code]`, `noreply@anthropic`.)

- [ ] **Step 6: Confirm git author identity**

Run:
```powershell
git config user.name
git config user.email
```

Expected: `Talha Umer` and an email matching Talha (e.g., `talhaumer721@gmail.com` or a configured GitHub no-reply). If the name is anything else, **stop** and surface to user — do not run `git config` to fix; the user must approve any identity change.

- [ ] **Step 7: Confirm memory files exist outside the repo**

Run:
```powershell
$mem = "$env:USERPROFILE\.claude\projects\C--Users-talha-Downloads-MarketSage-Analytics\memory"
$files = @('MEMORY.md', 'project-snapshot.md', 'developer-preferences.md', 'gotchas.md', 'git-rules.md')
foreach ($f in $files) {
    $p = Join-Path $mem $f
    if (Test-Path $p) { 'OK   {0}' -f $p } else { 'MISS {0}' -f $p }
}
```

Expected: 5 `OK` lines. If any are missing, surface to user — do not auto-create (memory files were authored in the previous session and any miss indicates drift).

- [ ] **Step 8: Pause for user go-ahead**

Surface to the user: "Pre-flight checks pass. Ready to commit 4 artifacts in 4 sequential commits authored by Talha Umer. Proceed?"

Do NOT proceed to Task 2 without explicit `yes`/`proceed`/`go`.

---

## Task 2: Commit 1 — Add design spec

**Files:**
- Stage: `docs/superpowers/specs/2026-05-03-claude-project-setup-design.md`
- Stage: `docs/superpowers/specs/README.md`

- [ ] **Step 1: Stage exactly the two spec files**

Run:
```powershell
git add docs/superpowers/specs/2026-05-03-claude-project-setup-design.md docs/superpowers/specs/README.md
git status --short
```

Expected (other untracked entries should remain `??`):
```
A  docs/superpowers/specs/2026-05-03-claude-project-setup-design.md
A  docs/superpowers/specs/README.md
?? .claude/
?? CLAUDE.md
?? docs/agents/
?? docs/api/
?? docs/architecture/
?? docs/superpowers/plans/
```

If anything else is staged (`A` rows you didn't expect), run `git reset HEAD <file>` for the extras and re-check.

- [ ] **Step 2: Show the staged diff for sanity check**

Run:
```powershell
git diff --cached --stat
```

Expected: 2 files changed, ~16000+ insertions(+).

- [ ] **Step 3: Commit with HEREDOC message**

Run:
```powershell
git commit -m @'
Add Claude project setup design spec

Captures the four-artifact design: CLAUDE.md, .claude/settings.json,
user-level memory files, and docs scaffolding. Includes per-section
content, hook commands, and verification checklist.
'@
```

Expected: commit succeeds, ruff hook does NOT run (this commit touches only docs).

If the Stop hook prints `git status --short` afterward, that's expected.

- [ ] **Step 4: Verify the commit**

Run:
```powershell
git log -1 --pretty='format:%H%n%an <%ae>%n%s%n%n%b'
```

Expected:
- Subject is `Add Claude project setup design spec`
- Author is `Talha Umer <...>`
- Body contains no `Co-Authored-By:` and no `Generated with`
- Subject length ≤ 72 chars

- [ ] **Step 5: Pause for user go-ahead before next commit**

Surface: "Commit 1 of 4 done: spec doc landed. Proceed with commit 2 (CLAUDE.md)?"

---

## Task 3: Commit 2 — Add CLAUDE.md

**Files:**
- Stage: `CLAUDE.md`

- [ ] **Step 1: Final scan of CLAUDE.md for AI attribution strings**

Run:
```powershell
Select-String -Path CLAUDE.md -Pattern 'Co-Authored-By:|Generated with \[Claude Code\]|Generated with Claude Code|noreply@anthropic'
```

Expected: no output (no matches).

The strings "Claude" and "Claude Code" do appear in CLAUDE.md (it's the file's intended audience). That is allowed — only the attribution phrases above are forbidden.

- [ ] **Step 2: Stage the file**

Run:
```powershell
git add CLAUDE.md
git status --short
```

Expected: `A  CLAUDE.md` plus the existing `??` entries for `.claude/`, `docs/agents/`, `docs/api/`, `docs/architecture/`, `docs/superpowers/plans/`.

- [ ] **Step 3: Commit**

Run:
```powershell
git commit -m @'
Add CLAUDE.md with project guidance

Documents agent architecture, LangGraph workflow, dev workflows,
debugging guide, env vars, coding rules, and strict git rules so
Claude Code sessions start with full context.
'@
```

Expected: commit succeeds. If the ruff pre-commit hook runs (it shouldn't — matcher checks for `git commit*` in the input command and runs `ruff check src/`), it passes because no `src/` files changed.

- [ ] **Step 4: Verify**

Run:
```powershell
git log -1 --pretty='format:%H%n%an%n%s'
```

Expected: subject `Add CLAUDE.md with project guidance`, author `Talha Umer`.

- [ ] **Step 5: Pause for user go-ahead**

Surface: "Commit 2 of 4 done: CLAUDE.md landed. Proceed with commit 3 (.claude/settings.json)?"

---

## Task 4: Commit 3 — Add `.claude/settings.json`

**Files:**
- Stage: `.claude/settings.json`

**Pre-condition note:** The `.claude/` directory also contains a `worktrees/` subdirectory from past Claude Code sessions. We must stage **only** the `settings.json`, not the worktrees.

- [ ] **Step 1: Confirm `.gitignore` behavior for `.claude/worktrees`**

Run:
```powershell
git check-ignore -v .claude/worktrees/gifted-jackson-df69bf 2>$null
git status --short .claude/
```

Two possibilities:
- If `git check-ignore` returns a path, worktrees are already ignored — good.
- If `git status` shows worktree paths as `??`, we still avoid them by staging only the specific file in Step 2.

Either way, Step 2 stages only the one file.

- [ ] **Step 2: Stage the single file by exact path**

Run:
```powershell
git add .claude/settings.json
git status --short
```

Expected: exactly one new entry `A  .claude/settings.json`. The `.claude/worktrees/` paths must NOT appear as `A`. If they do, run `git reset HEAD .claude/worktrees` and re-check.

- [ ] **Step 3: Re-validate JSON one more time before committing**

Run:
```powershell
python -c "import json; json.load(open('.claude/settings.json')); print('JSON OK')"
```

Expected: `JSON OK`.

- [ ] **Step 4: Commit**

Run:
```powershell
git commit -m @'
Add Claude Code permissions, hooks, and env

Allowlists python/pytest/pip/ruff/uvicorn/gradio plus read-only and
staging git commands. PreToolUse hook runs ruff check on commits.
Stop hook prints git status. Sets PYTHONPATH=src and API_BASE_URL.
'@
```

Expected: commit succeeds.

- [ ] **Step 5: Smoke test the pre-commit ruff hook**

The hook runs `ruff check src/` only when the input command starts with `git commit`. Manually trigger ruff to confirm it works against the codebase:

Run:
```powershell
ruff check src/
```

If ruff exits 0: hook will not block future commits.

If ruff exits non-zero: **surface the lint output to the user** and ask whether to fix, ignore (lower severity), or update the hook scope. **Do NOT auto-fix.** Talha's developer preferences require evidence-before-action and explicit approval before code changes.

Record outcome in your reply: `ruff check src/ → exit 0` or paste the violations.

- [ ] **Step 6: Verify commit author and message**

Run:
```powershell
git log -1 --pretty='format:%an%n%s%n%n%b'
```

Expected: author `Talha Umer`, subject `Add Claude Code permissions, hooks, and env`, no `Co-Authored-By` or "Generated with" lines.

- [ ] **Step 7: Pause for user go-ahead**

Surface: "Commit 3 of 4 done: settings.json landed and ruff hook tested. Proceed with commit 4 (docs scaffolding)?"

---

## Task 5: Commit 4 — Scaffold docs subdirectories

**Files:**
- Stage: `docs/architecture/README.md`
- Stage: `docs/agents/README.md`
- Stage: `docs/api/README.md`

**Note:** `docs/superpowers/specs/README.md` was already committed in commit 1. `docs/superpowers/plans/` contains this plan document and is intentionally LEFT UNCOMMITTED here — committing the plan is a follow-up decision for the user.

- [ ] **Step 1: Stage the three READMEs by exact path**

Run:
```powershell
git add docs/architecture/README.md docs/agents/README.md docs/api/README.md
git status --short
```

Expected: 3 new `A` entries plus the lingering untracked `?? docs/superpowers/plans/`.

- [ ] **Step 2: Commit**

Run:
```powershell
git commit -m @'
Scaffold docs subdirectories with READMEs

Adds placeholder READMEs for architecture, agents, and api docs
with naming conventions and links back to CLAUDE.md.
'@
```

Expected: commit succeeds.

- [ ] **Step 3: Verify**

Run:
```powershell
git log -1 --pretty='format:%an%n%s'
```

Expected: author `Talha Umer`, subject `Scaffold docs subdirectories with READMEs`.

- [ ] **Step 4: Pause for user go-ahead before final verification**

Surface: "Commit 4 of 4 done. Ready to run the final verification suite?"

---

## Task 6: Final verification

**Files:** none modified — read-only checks.

- [ ] **Step 1: Verify exactly 4 new commits all by Talha Umer**

Run:
```powershell
git log --pretty='format:%h %an :: %s' -6
```

Expected (top to bottom = newest to oldest):
```
<hash> Talha Umer :: Scaffold docs subdirectories with READMEs
<hash> Talha Umer :: Add Claude Code permissions, hooks, and env
<hash> Talha Umer :: Add CLAUDE.md with project guidance
<hash> Talha Umer :: Add Claude project setup design spec
bb80771 <prior author> :: Improve README with accurate tech stack and project details
b2bd21a <prior author> :: Initial commit
```

If any of the 4 new commits has an author other than `Talha Umer`, surface to user immediately.

- [ ] **Step 2: Verify subject line lengths ≤ 72**

Run:
```powershell
git log -4 --pretty='format:%s' | ForEach-Object { '{0,3}  {1}' -f $_.Length, $_ }
```

Expected: every line shows length ≤ 72.

- [ ] **Step 3: Verify no AI attribution in any of the 4 commit messages**

Run:
```powershell
$matches = git log -4 --pretty='format:%B' | Select-String -Pattern 'Co-Authored-By:|Generated with \[Claude Code\]|Generated with Claude Code|noreply@anthropic'
if ($matches) { $matches; throw 'FORBIDDEN attribution found in commit history' } else { 'commit history clean' }
```

Expected: `commit history clean`.

- [ ] **Step 4: Re-validate `.claude/settings.json`**

Run:
```powershell
python -c "import json; json.load(open('.claude/settings.json')); print('settings.json valid')"
```

Expected: `settings.json valid`.

- [ ] **Step 5: Confirm CLAUDE.md mentions of Claude Code are intentional, not attribution**

Run:
```powershell
Select-String -Path CLAUDE.md -Pattern 'Claude|Anthropic|Co-Authored' | Select-Object LineNumber, Line | Format-Table -Wrap
```

Expected: the only matches should be:
- The `# CLAUDE.md` heading (line 1)
- "Guidance for Claude Code when working in the **MarketSage Analytics** repository." (line 3)
- The Git Rules section listing forbidden tokens (`Claude`, `Anthropic`, `Co-Authored-By: Claude`)
- The `.claude/settings.json` references

NO line should look like `Co-Authored-By: Claude <noreply@...>` or `Generated with [Claude Code]`. Eyeball the table for unexpected matches and surface them if found.

- [ ] **Step 6: Confirm working tree state**

Run:
```powershell
git status --short
```

Expected: only `?? docs/superpowers/plans/` should remain (the plan file itself was created during planning and is intentionally outside the 4 commits).

If anything else is uncommitted (e.g., a `.claude/worktrees/` entry, a stray `.gradio/` cache, or modified `src/`), surface to user.

- [ ] **Step 7: Document Stop hook smoke test (deferred)**

The `Stop` hook in `.claude/settings.json` runs `git status --short` at the end of each Claude turn. It only takes effect on **the next Claude Code session start** because Claude reads `settings.json` at session start, not mid-session.

In your reply to the user, include this line:
> "Stop hook is configured but won't activate until the next Claude Code session start. To verify in the next session: end any turn and confirm a `git status --short` line appears in the post-turn output."

Do NOT attempt to mid-session reload settings.

- [ ] **Step 8: Final summary to user**

Report:
- 4 commits landed, all authored by Talha Umer, all subjects ≤ 72 chars, no AI attribution.
- `ruff check src/` outcome from Task 4 Step 5.
- Memory files exist at `~/.claude/projects/.../memory/` (5 files, not committed by design).
- Stop hook deferred verification note (above).
- Working tree clean except for `docs/superpowers/plans/` (this plan file itself).
- Optional follow-up: ask user whether to commit `docs/superpowers/plans/2026-05-03-claude-project-setup-implementation.md` as a 5th commit, e.g., subject `Add Claude project setup implementation plan`.

---

## Failure modes and recovery

| Symptom | Recovery |
|---------|----------|
| `git commit` fails because of pre-commit ruff hook | Read the ruff output, surface to user, do NOT `--no-verify`. If user approves, fix the lint and try again with a NEW commit (do not amend). |
| Wrong file accidentally staged | `git reset HEAD <file>` to unstage. Re-run `git add <correct-files>` and re-verify with `git status --short`. |
| Wrong commit author detected after the fact | Surface to user immediately. Do NOT run `git rebase` or `git commit --amend --author=...` without explicit approval. |
| `.claude/settings.json` JSON broken | Stop. Read the file, identify the syntax error, ask user before fixing — the spec content is the source of truth. |
| Memory file missing in pre-flight | Re-author the missing file from the spec section 5.3 sketch. Ask user to confirm. |
| User says "stop" or doesn't approve a commit | Stop immediately. Leave staged files staged so the user can inspect; do not unstage without ask. |

---

## Self-Review

**1. Spec coverage** — Walked the spec sections:
- Section 3 (CLAUDE.md): Task 3 commits it; Task 1 Step 5 + Task 6 Step 5 verify no AI attribution.
- Section 4 (settings.json): Task 4 commits it; Task 1 Steps 3–4 + Task 6 Step 4 validate JSON; Task 4 Step 5 smoke-tests the ruff hook; Task 6 Step 7 documents the Stop-hook deferred test.
- Section 5 (memory files): Task 1 Step 7 verifies they exist; commit plan explicitly excludes them. No spec requirement to commit them.
- Section 6 (docs scaffolding): Task 5 commits the three subdirectory READMEs; Task 2 commits the specs README alongside the spec. Existing root `docs/README.md` is intentionally left unchanged (matches spec section 6.2).
- Section 9 (verification checklist): Task 6 covers every item — JSON validity, file existence is implicit (we just committed them), no AI attribution in artifacts (Task 1 Step 5) and in commits (Task 6 Step 3), no `src/` modifications (Task 1 Step 1 + Task 6 Step 6).

No gaps.

**2. Placeholder scan** — No "TBD", "TODO", "implement later", "similar to Task N", "add appropriate error handling", or undefined symbols. Every shell command shows the actual command and its expected output.

**3. Type / path / command consistency** — Cross-checked file paths between tasks: `docs/superpowers/specs/2026-05-03-claude-project-setup-design.md` is consistent in spec reference, Task 1 Step 2, Task 1 Step 5, and Task 2 Step 1. The CLAUDE.md path, settings.json path, and memory directory path are all spelled identically across tasks. The four commit subjects are quoted verbatim in the commit step and in Task 6 Step 1 expected output.

**4. Strict-rule compliance** — Every commit step uses HEREDOC, stages files explicitly by name, never uses `--no-verify`, and pauses for user approval. The plan never asks an executor to bypass the user's "don't commit unless asked" rule — every commit task starts with a "pause for user go-ahead" gate.

Plan is complete and ready to execute.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-03-claude-project-setup-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
