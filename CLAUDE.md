<!-- HARNESS:START
     version=0.32.0
     schema=1
     agent=awsysco-python-sdk
     updated=2026-07-18T02:25:54Z
     DO NOT EDIT THIS BLOCK — regenerate with: harness-ctl update /Users/patrickbertsch/dev/awsysco-python-sdk
-->

# Harness — Active Constraints

**This file is the entry point for every task in this project — always start here.**

**Agent:** `awsysco-python-sdk` · trust: `worker` · model: `mid`
**Budget:** 40 steps · 80000 tokens · $3.00 per session
**Privacy:** local_preferred — local models preferred; cloud only on low confidence
**Memory namespace:** `awsysco-python-sdk-worker`


## Must escalate (blocks until human approves)

- `create_pr`

- `deploy`

- `spend`



## Available tools
See `harness/TOOLS.md` for full reference with parameter schemas.

- `web_search` — search the web via Brave/Google
- `web_fetch` — fetch and extract URL content
- `file_ops` — read/write files within the project root
- `memory_store` / `memory_search` — per-session key-value memory

## Project overrides (harness.yaml)

*(no harness.yaml found — using manifest defaults)*


<!-- HARNESS:END -->

---


# Harness — AwsyscoPythonSdk

**Agent:** `awsysco-python-sdk` · trust: `worker` · model: `mid`
**Project root:** `~/dev/awsysco-python-sdk`
**Remote:** `https://github.com/AlphaWaveSystems/awsysco-python-sdk`
**Stack:** `Python`

## Startup

Before working:
1. Read this file
2. `cd ~/dev/awsysco-python-sdk`
3. Run verification: `pytest && ruff check .`
4. Check `git status` and `git log --oneline -10`

## Working rules

- Branch names: `feat/awsysco-python-sdk`, `fix/awsysco-python-sdk`, `chore/awsysco-python-sdk`
- Always work in a git worktree: `git worktree add .worktrees/<branch> -b <branch>`
- Stage specific files only — never `git add .`
- Commit format: `type: description` (feat/fix/chore/refactor/docs)
- PRs required for all merges — no direct commits to main/master
- Run verification before every commit

## Verification

```bash
pytest && ruff check .
```

## Definition of done

- [ ] Implementation complete and verified
- [ ] Tests pass
- [ ] PR created (or commit staged if no remote)
- [ ] No regressions in adjacent features

## Guardrails

Bounded autonomy. Escalate deploys and spend to Zeus.
