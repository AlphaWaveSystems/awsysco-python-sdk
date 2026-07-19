<!-- HARNESS:START
     version=0.34.0
     schema=1
     agent=awsysco-python-sdk
     updated=2026-07-19T12:15:55Z
     DO NOT EDIT THIS BLOCK — regenerate with: harness-ctl update /Users/patrickbertsch/dev/awsysco-python-sdk
-->

# Harness — This Project

**Agent `awsysco-python-sdk`** · tier `mid` · privacy `local_preferred`

Full harness configuration, budget, escalation rules, available tools, and — critically —
how to actually connect to it, all live in **`AGENTS.md`**. Read that file, not this one,
for anything harness-related.

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
