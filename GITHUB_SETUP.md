# GitHub Manual Setup

`gh` CLI was not available in this environment, so the project is in manual
GitHub mode. This is not a project failure; use the commands below on a
machine with `gh` installed and authenticated.

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
