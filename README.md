# Security Research

A working journal of my application & web security research — recon, methodology,
tooling, and write-ups. This repo documents the **whole path**, not just the findings:
the hypotheses that went nowhere are part of the craft.

## What's in here

| Folder | What it holds |
|---|---|
| [`methodology/`](methodology/) | How I approach a target — recon checklists, testing playbooks, notes I reuse. |
| [`tools/`](tools/) | Small scripts I write while hunting (recon helpers, parsers, PoC scaffolds). |
| [`targets/`](targets/) | Per-engagement journals — scope, recon output, hypotheses, what was tested. |
| [`writeups/`](writeups/) | Finished, sanitized write-ups of confirmed findings and CTF/lab solutions. |

## Ground rules I hold myself to

- **Only authorized targets.** Public/private bug bounty programs, CTFs, labs, or systems I own.
  Scope is checked against each program's policy before a single request goes out.
- **Coordinated disclosure.** Details of a real vulnerability in a third-party system are
  published only after it's fixed and disclosure is permitted. Until then, only sanitized
  methodology lives here.
- **No secrets, no PII.** Credentials, session tokens, and personal data never get committed
  (see [`.gitignore`](.gitignore)). Evidence is masked before it's written down.

## About me

Application security researcher focused on authentication, authorization, and business-logic
flaws. Reachable through the profile that owns this repo.

---
*This repository is a portfolio of authorized security research. Nothing here is a how-to for
attacking systems you don't have permission to test.*
