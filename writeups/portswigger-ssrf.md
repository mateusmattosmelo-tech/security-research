# Lab notes — SSRF (PortSwigger Web Security Academy)

Notes on the [SSRF labs](https://portswigger.net/web-security/ssrf) — approach over answers.
Public practice labs; safe to write up. Pairs with the
[SSRF hunting](../methodology/ssrf-hunting.md) methodology.

## Basic SSRF against the local server

- A parameter takes a URL (a stock-check "fetch from internal API", an admin URL). Point it at
  `http://localhost/admin` (or `127.0.0.1`) and reach functionality meant to be internal-only.
- Escalate: hit an internal-only admin action (delete a user) by having the server request it.

## SSRF against other back-end systems

- The parameter can reach an internal IP range. Sweep `http://192.168.0.X/admin` (small, targeted
  — not a flood) to find the internal host, then act on it.

## Defeating filters

- **Blocklist bypass:** alternate encodings of `127.0.0.1` (decimal `2130706433`, `0`, IPv6
  `[::1]`, `127.1`), or `http://localhost.` tricks.
- **Allowlist bypass:** put the allowed host in the userinfo (`https://allowed@evil`), use `@`,
  `#`, or a URL that the parser and the fetcher disagree on; or an open redirect on an allowed host
  that bounces to the internal target.
- **DNS rebinding** where the check and the fetch resolve the name at different times.

## Blind SSRF

- No response reflected — confirm with an out-of-band listener (Burp Collaborator or your own
  canary domain). The DNS lookup alone proves the fetch. Then probe for internal effects.

## Cloud metadata (the high-impact escalation)

- Point the SSRF at the metadata endpoint (`169.254.169.254`) to read instance credentials /
  config. On clouds requiring a token/header (IMDSv2), chain the token request first. Those
  temporary creds are often the real prize — cross-service or cross-tenant access.

## Reporting

Show the request that triggers the fetch and the evidence it happened (internal response, or the
OOB callback). Tie it to concrete impact — what the server-side position reached. Keep internal
sweeps small and non-destructive.
