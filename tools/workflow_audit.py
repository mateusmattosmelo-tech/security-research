#!/usr/bin/env python3
"""
workflow_audit.py — flag risky patterns in GitHub Actions workflow files.

Two classic bug classes:
  1. Script injection — untrusted event data (PR title, branch name, issue body) interpolated
     directly into a `run:` block as ${{ ... }}, giving an attacker shell execution.
  2. Pwn request — a `pull_request_target` / `workflow_run` workflow (which runs with secrets and
     a write token) that checks out and executes the PR's untrusted code.

This is a static heuristic to triage which workflows to read closely — not a proof of exploit.

Usage:
    python3 workflow_audit.py path/to/.github/workflows/
    python3 workflow_audit.py file.yml
"""
import os
import re
import sys

# event fields an attacker controls, when interpolated into run: => injection
TAINTED = re.compile(
    r"\$\{\{\s*github\.event\.(pull_request\.(title|body|head\.ref|head\.label)"
    r"|issue\.(title|body)|comment\.body|review\.body|"
    r"head_commit\.message|pages\.\*\.page_name)\s*\}\}"
)
PRIV_TRIGGER = re.compile(r"^\s*(pull_request_target|workflow_run)\s*:", re.M)
CHECKOUT_PR = re.compile(r"ref:\s*\$\{\{\s*github\.event\.pull_request\.head", re.M)


def audit(path, text):
    findings = []
    priv = bool(PRIV_TRIGGER.search(text))
    # injection: any tainted event field interpolated into the workflow. Strongest inside a
    # run: block (shell execution); flagged everywhere because it's attacker-controlled input.
    lines = text.splitlines()
    run_lines = set()
    in_run = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r"\s*-?\s*run:\s*", line):
            in_run = True
        elif re.match(r"\s*[\w-]+:\s*", line) and not stripped.startswith("-"):
            in_run = False
        if in_run:
            run_lines.add(i)
    for i, line in enumerate(lines, 1):
        if TAINTED.search(line):
            kind = "script-injection" if i in run_lines else "tainted-expression"
            findings.append((i, kind, line.strip()[:80]))
    if priv and CHECKOUT_PR.search(text):
        findings.append((0, "pwn-request",
                         "privileged trigger checks out PR head code"))
    elif priv:
        findings.append((0, "privileged-trigger",
                         "pull_request_target/workflow_run — verify it never runs PR code"))
    return findings


def walk(target):
    if os.path.isfile(target):
        yield target
    else:
        for root, _, files in os.walk(target):
            for f in files:
                if f.endswith((".yml", ".yaml")):
                    yield os.path.join(root, f)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 1
    any_found = False
    for path in walk(argv[1]):
        text = open(path, errors="ignore").read()
        for line, kind, detail in audit(path, text):
            any_found = True
            loc = f"{path}:{line}" if line else path
            print(f"[{kind}] {loc}\n    {detail}")
    if not any_found:
        print("no risky patterns matched (still read privileged workflows by hand)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
