# Secrets Scanning

Leaked credentials are among the highest-impact, lowest-effort findings — a live key in a public
repo, a package, or a client bundle can be straight account or infrastructure access. The work is
knowing where to look and how to tell a real secret from a test fixture.

## Where secrets leak

- **Public repos & their git history.** The current tree is often clean while a key sits in an old
  commit — scan history, not just `HEAD`.
- **Published packages.** npm/PyPI tarballs sometimes include a `.env`, a config, or source maps
  the repo `.gitignore` would have caught. Download and scan the actual published artifact.
- **Client bundles & source maps.** Frontend JS ships to the browser; a `.map` can reveal original
  source, internal endpoints, and occasionally keys.
- **CI logs, Docker layers, and build artifacts.** Public workflow logs and image layers leak
  tokens.
- **Org-wide code search** for high-signal prefixes.

## High-signal patterns

`AKIA…` (AWS access key id), `ghp_/gho_/ghs_/ghr_` (GitHub tokens), `xox[baprs]-` (Slack),
`sk-…` (many API providers), `AIza…` (Google), `-----BEGIN … PRIVATE KEY-----`,
`eyJ…` (JWTs), plus provider-specific formats. But the prefix alone isn't a finding.

## Telling real from noise

Most raw hits are false positives — test fixtures, example values, fake data, docs. Before
reporting:

- **Filter the obvious noise:** paths/strings containing `example`, `test`, `dummy`, `sample`,
  `fixture`, `<`, `xxxx`, `redacted`, and unit-test files.
- **Check the context:** is it in a test vector, a sample DB, a scraped HTML file? Then it's noise.
- **Confirm it's live (carefully).** The only proof a key matters is that it works — but validate
  with the least-privileged, non-destructive call the provider offers (a "whoami"/token-info
  endpoint), never a state-changing one, and only if the program allows it. A revoked/expired key
  is not a finding.

## Handling responsibly

- **Never paste the full secret** in a report, screenshot, or repo — mask it (first 6 + last 4).
- Report fast: live keys are a race. Include exactly where it lives (repo + path + commit) and how
  you confirmed it's live, masked.
- Scanning your *own* portfolio before every push is the same discipline in reverse — a
  pre-commit secret check keeps you from becoming the case study.

## Tooling

Grep with the patterns above for a quick pass; dedicated scanners (git-history aware) for depth.
The judgment — real vs. fixture, live vs. dead — is yours, not the scanner's.
