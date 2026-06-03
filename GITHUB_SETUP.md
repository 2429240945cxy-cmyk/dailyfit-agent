# GitHub Manual Setup

`gh` CLI was not available in this environment, so the project is in manual
GitHub mode. This is not a project failure; use the commands below on a
machine with `gh` installed and authenticated.

## Current v6 Upload Status

Checked on 2026-06-03:

- Local branch: `main`
- GitHub CLI: not available on PATH in this environment
- Git remote: not configured
- `.env` is ignored by git
- Sensitive token scan: passed

Use one of the two upload paths below. Do not add `.env`.

## Recommended Upload Path With `gh`

Install GitHub CLI on Windows:

```powershell
winget install --id GitHub.cli
# or:
# choco install gh
```

Authenticate and upload the current project:

```powershell
cd G:\健身agent
gh auth login
gh auth status

rtk git status --short
rtk python backend/scripts/scan_sensitive_tokens.py
rtk git branch -M main

gh repo create dailyfit-agent --public --source=. --remote=origin --push
```

If the repo already exists on GitHub, bind it manually and push:

```powershell
cd G:\健身agent
rtk git remote add origin https://github.com/<YOUR_USERNAME>/dailyfit-agent.git
rtk git push -u origin main
```

Create a tracking issue for the uploaded v6 version:

```powershell
gh issue create `
  --title "Publish DailyFit Agent v6 live benchmark portfolio" `
  --body "Upload the v6 portfolio project with Aliyun live mode, real-data nutrition tools, Guardian, memory retrieval, web UI, benchmark JSON, no-secret scan, and v5-to-v6 metric comparison."
```

Optional branch/PR flow after the initial push:

```powershell
rtk git checkout -b codex/github-upload-final-check
rtk python backend/scripts/scan_sensitive_tokens.py
rtk python backend/scripts/verify_readme_numbers.py
rtk git push -u origin codex/github-upload-final-check

gh pr create `
  --title "Finalize DailyFit Agent v6 GitHub portfolio" `
  --body "Validates README metrics, no-secret scan, benchmark artifacts, web smoke, and v5-to-v6 result archive."
```

## Manual Upload Path Without `gh`

If you do not want to install `gh`:

1. Open GitHub in the browser and create a new public repository named `dailyfit-agent`.
2. Do not initialize it with README, license, or `.gitignore`.
3. Run:

```powershell
cd G:\健身agent
rtk git status --short
rtk python backend/scripts/scan_sensitive_tokens.py
rtk git branch -M main
rtk git remote add origin https://github.com/<YOUR_USERNAME>/dailyfit-agent.git
rtk git push -u origin main
```

If `origin` already exists:

```powershell
rtk git remote set-url origin https://github.com/<YOUR_USERNAME>/dailyfit-agent.git
rtk git push -u origin main
```

## Install And Authenticate

```bash
gh auth login
gh auth status
```

## Create Repository And Push

```bash
git init
git branch -M main
git add .
git commit -m "feat: dailyfit agent v1-live implementation"
gh repo create dailyfit-agent --public --source=. --remote=origin --push
```

## Create Milestone

```bash
gh api repos/:owner/dailyfit-agent/milestones -f title="v1-live-real-data"
```

## Create Phase Issues

```bash
gh issue create --title "Phase 0 - skeleton" --body "Create project skeleton, pyproject, README, env example, gitignore." --milestone "v1-live-real-data"
gh issue create --title "Phase 1 - schemas/storage/audit" --body "Implement Pydantic schemas, SQLite init, and JSON audit logging." --milestone "v1-live-real-data"
gh issue create --title "Phase 2 - Aliyun LLM provider" --body "Implement DashScope OpenAI-compatible chat, judge, embedding, cache, usage, budget, smoke tests." --milestone "v1-live-real-data"
gh issue create --title "Phase 3 - real nutrition/exercise data sources" --body "Implement OFF, USDA FDC, HPB cache, local fallback, and free-exercise-db loader." --milestone "v1-live-real-data"
gh issue create --title "Phase 4 - Guardian + memory retrieval" --body "Implement Guardian policy and BM25/lexical/embedding memory retrieval." --milestone "v1-live-real-data"
gh issue create --title "Phase 5 - LangGraph + FastAPI" --body "Implement graph workflow and API routes." --milestone "v1-live-real-data"
gh issue create --title "Phase 6 - web UI" --body "Implement static web UI served by FastAPI." --milestone "v1-live-real-data"
gh issue create --title "Phase 7 - real benchmark datasets" --body "Build nutrition, guardian, memory, and E2E v2 datasets with documented sources." --milestone "v1-live-real-data"
gh issue create --title "Phase 8 - benchmark + README verification" --body "Run benchmarks, write results, verify README numbers." --milestone "v1-live-real-data"
gh issue create --title "Phase 9 - self-audit loop" --body "Implement regression self-audit and GitHub issue loop." --milestone "v1-live-real-data"
gh issue create --title "Phase 10 - final docs and release" --body "Finish docs, release notes, and GitHub release." --milestone "v1-live-real-data"
```

## Branch, PR, And Merge Pattern

```bash
git checkout -b issue-1-phase-skeleton
# implement and test
pytest backend/tests/ -v
python backend/scripts/scan_sensitive_tokens.py
git add .
git commit -m "feat: phase 0 - skeleton closes #1"
git push -u origin issue-1-phase-skeleton
gh pr create --title "Phase 0: skeleton" --body "Closes #1"
```

Only merge when local tests pass:

```bash
gh pr merge --merge --delete-branch
git checkout main
git pull
```

## Release

```bash
git checkout main
git pull
git tag v1.0.0-live-real-data
git push origin v1.0.0-live-real-data
gh release create v1.0.0-live-real-data --title "DailyFit Agent v1.0.0 - Aliyun Live + Real Data + Web UI" --notes-file docs/release-notes-v1.md
```

## Live Finalization Manual Flow

Use this after installing and authenticating `gh`:

```bash
gh auth login
gh auth status

gh repo create dailyfit-agent --public --source=. --remote=origin --push
# If the repo already exists and no remote is configured:
# git remote add origin https://github.com/<YOUR_USERNAME>/dailyfit-agent.git
# git push -u origin main

gh issue create \
  --title "Validate Aliyun live mode and real-data benchmarks" \
  --body "Track live DashScope smoke, live benchmark execution, README metric verification, and no-secret audit."

git checkout -b issue-live-finalization
git add .
git reset .env
git commit -m "chore: finalize aliyun live mode and real-data benchmark reporting"
git push -u origin issue-live-finalization

gh pr create \
  --title "Finalize Aliyun live mode and benchmark reporting" \
  --body "Closes #<issue-number>. Validates DashScope live smoke, live benchmark outputs, README verification, web smoke, and no-secret scan."
```

## Judge Fix And Chat UI Manual Flow

`gh` was still not available during the 2026-05-15 continuation work. After
installing and authenticating `gh`, publish the live judge parsing fix, memory
dedupe fix, live benchmark refresh, and chat-style web UI with:

```bash
gh auth login
gh auth status

gh repo create dailyfit-agent --public --source=. --remote=origin --push
# If the repo already exists and no remote is configured:
# rtk git remote add origin https://github.com/<YOUR_USERNAME>/dailyfit-agent.git
# rtk git push -u origin main

gh issue create \
  --title "Harden E2E judge parsing and improve chat web UX" \
  --body "Fix tolerant judge JSON parsing, avoid vision judge model assumptions, dedupe memory hits, refresh live benchmark reporting, and make the web UI behave like a direct chat surface."

rtk git checkout -b issue-e2e-judge-web-ux
rtk git add .
rtk git reset .env
rtk git commit -m "fix: harden e2e judge and improve chat web ux"
rtk git push -u origin issue-e2e-judge-web-ux

gh pr create \
  --title "Harden E2E judge parsing and chat web UX" \
  --body "Closes #<issue-number>. Validates DashScope live smoke, full E2E judge parsing, web chat flow, README metric verification, self-audit dry-run, and no-secret scan."
```
