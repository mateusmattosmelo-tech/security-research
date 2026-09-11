# Subdomain Takeover

A subdomain takeover happens when a DNS record points at a service that no longer exists —
a deleted GitHub Pages site, a released cloud bucket, a torn-down PaaS app. The DNS record
still says "this hostname lives over there," but "over there" is now claimable by anyone.
Claim it, and you serve content on the target's own subdomain.

## Why it matters

A subdomain of the target is trusted by browsers and often by the target's own systems:

- **Phishing** with a genuinely legitimate hostname — no lookalike domain needed.
- **Cookie theft / fixation** if any cookie is scoped to `.example.com`.
- **OAuth / SSO abuse** if a redirect allowlist or trust boundary includes the subdomain
  or a wildcard.
- **Bypassing CSP / CORS** allowlists that name `*.example.com`.

That's why these are usually rated meaningfully, not informational — the impact rides on the
trust the parent domain already carries.

## How to find them

1. **Enumerate hostnames** (CT logs, passive DNS) — the same list you build for attack-surface
   mapping.
2. **Read the DNS answer**, don't just resolve it. A `CNAME` to a third-party service is the
   candidate. Follow the whole chain — a record can hop through several intermediates before it
   lands on the claimable service.
3. **Fingerprint the response.** Each service has a tell when the backing resource is gone:
   - GitHub Pages → `404 "There isn't a GitHub Pages site here"` / `"Site not found"`
   - S3 → `NoSuchBucket`
   - CloudFront → `NoSuchDistribution` / "The request could not be satisfied"
   - Cloud PaaS/Pages → a generic "project not found" / "nothing here yet"
   - A TLS handshake failure on a CNAME to a shared-cert service is itself a hint the custom
     domain was never claimed there.

## Confirming without causing harm

The proof-of-concept is inherently "claim the dangling resource," which is disruptive if done
carelessly. Do the minimum:

- Establish the dangling record with the DNS chain and the service's own "gone" fingerprint —
  that alone is often enough for triage.
- If a program wants live confirmation, claim it with a **harmless, clearly-marked** page (your
  research handle, a timestamp) and nothing else — never real-looking content, never credential
  capture. Release it immediately after.
- Watch for **provider domain-verification**: modern GitHub/Cloud providers let an org verify a
  domain so only they can bind its subdomains. If the parent is verified, the record is broken
  but not takeable — report it as a dangling record, not a confirmed takeover.

## Reporting

Lead with the DNS chain, the "gone" fingerprint, and the concrete trust the subdomain carries
(cookies, OAuth, CSP). State plainly whether you confirmed the claim or stopped at the dangling
record, and why. Don't overstate feasibility you didn't verify.
