# Security Research

A working journal of my application & web security research — recon, methodology, tooling, and
write-ups. This repo documents the **whole path**, not just the findings: the map I build, the
hypotheses I test, and the ones that go nowhere are all part of the craft.

## Methodology

Reusable playbooks, refined on real (authorized) engagements.

**Recon & mapping**
- [Recon playbook](methodology/recon-playbook.md)
- [Recon from a target's open source](methodology/recon-from-open-source.md)
- [Attack-surface mapping](methodology/attack-surface-mapping.md)
- [Building an API inventory for authz testing](methodology/api-inventory-for-authz.md)

**Auth & access**
- [Authorization testing (IDOR/BOLA/privesc)](methodology/authorization-testing.md)
- [OAuth 2.0 / OIDC testing](methodology/oauth-oidc-testing.md)
- [Auditing a JWT verification implementation](methodology/auditing-jwt-verification.md)
- [Multi-tenant isolation testing](methodology/multi-tenant-isolation.md)
- [Testing a hosted MCP server](methodology/mcp-server-security.md)

**Web / API / infra**
- [API security testing (REST & GraphQL)](methodology/api-security-testing.md)
- [GraphQL security testing](methodology/graphql-security-testing.md)
- [Business logic testing](methodology/business-logic.md)
- [Race conditions](methodology/race-conditions.md)
- [SSRF hunting](methodology/ssrf-hunting.md)
- [Subdomain takeover](methodology/subdomain-takeover.md)
- [Dependency confusion](methodology/dependency-confusion.md)
- [Auditing GitHub Actions workflows](methodology/github-actions-security.md)

**Craft**
- [Secure code review](methodology/secure-code-review.md)
- [Scope & disclosure hygiene](methodology/scope-and-disclosure-hygiene.md)
- [Writing a vulnerability report that doesn't get downgraded](methodology/writing-a-vulnerability-report.md)

## Tools

Small, self-contained scripts — see [`tools/`](tools/) for the full index.
`ct_recon` · `takeover_scan` · `js_endpoints` · `header_audit` · `cors_probe` ·
`oauth_redirect_probe` · `workflow_audit`

## Write-ups

Finished, sanitized write-ups of confirmed findings (post-disclosure) and CTF/lab solutions live
in [`writeups/`](writeups/).

## Ground rules

- **Only authorized targets** — bug bounty programs in scope, CTFs, labs, or systems I own.
- **Coordinated disclosure** — third-party vulnerability details are published only after they're
  fixed and disclosure is permitted; until then, only sanitized methodology.
- **No secrets, no PII** — credentials, tokens, and personal data never get committed
  (see [`.gitignore`](.gitignore)); evidence is masked before it's written down.

---
*A portfolio of authorized security research. Nothing here is a how-to for attacking systems you
don't have permission to test.*
