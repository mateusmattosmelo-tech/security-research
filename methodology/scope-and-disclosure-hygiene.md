# Scope & Disclosure Hygiene

The fastest way to lose a bounty — or a program invite, or legal safe harbor — isn't a weak bug.
It's testing out of scope, leaking data, or disclosing something you weren't allowed to. This is
the discipline I hold myself to on every engagement.

## Before the first request

- **Read the whole policy.** Write down in-scope assets, out-of-scope assets, and the exact rules:
  rate-limit limits, prohibited techniques (automated scanning, DoS, brute force, social
  engineering), which environments to use (staging vs prod), and whether real user data can be
  touched.
- **Note the required identifiers.** Many programs want a specific header (e.g. an
  `X-HackerOne-Research: <handle>` / `X-Bug-Bounty` header) or a test account created with a
  specific email domain so they can tell your traffic from an attacker's. Set it on every request.
- **Prefer the staging asset** when the program provides one. Only touch production when the
  policy allows it, and notify first if it asks you to.

## While testing

- **Use accounts you own.** Cross-account tests use two of *your* accounts, never a real user's.
- **Don't destroy or exfiltrate.** Prove access with the minimum — a single record, your own
  data, a canary — not a bulk dump. "Good-faith effort to avoid privacy violations" is a rule,
  not a suggestion.
- **Respect the excluded classes.** If rate-limiting, enumeration, or missing headers are out of
  scope, don't spend cycles there — and don't report them.
- **Stay inside the fence.** An interesting host that's out of scope is out of scope. "Open scope"
  clauses reward *owned* assets by impact, but the environment/notify rules still apply.

## Disclosure

- **Coordinated by default.** A private program's details — including resolved bugs — stay private
  unless the program consents in writing. Assume no public disclosure without permission.
- **A portfolio is sanitized methodology, not leaked findings.** The technique is publishable; the
  target-specific vuln is not, until it's fixed and disclosure is allowed.
- **Never publish secrets, PII, credentials, or session tokens** — in a report, a screenshot, a
  video frame, or a repo.

## Why this is a competitive advantage

Triagers reward researchers who make their life easy and safe: clear scope adherence, declared
test IPs, masked secrets, reproducible steps. Programs re-invite the people they trust. Hygiene
isn't overhead — it's what turns a finding into a paid, repeatable relationship.
