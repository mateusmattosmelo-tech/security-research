# Security Research

A working journal of my application & web security research — recon, methodology, tooling, and
write-ups. This repo documents the **whole path**, not just the findings: the map I build, the
hypotheses I test, and the ones that go nowhere are all part of the craft.

## Methodology

Reusable playbooks, refined on real (authorized) engagements.

**Recon & mapping**
- [Recon playbook](methodology/recon-playbook.md)
- [Recon from a target's open source](methodology/recon-from-open-source.md)
- [Mobile app recon (APK/IPA)](methodology/mobile-app-recon.md)
- [Attack-surface mapping](methodology/attack-surface-mapping.md)
- [Building an API inventory for authz testing](methodology/api-inventory-for-authz.md)

**Auth & access**
- [Authorization testing (IDOR/BOLA/privesc)](methodology/authorization-testing.md)
- [OAuth 2.0 / OIDC testing](methodology/oauth-oidc-testing.md)
- [Auditing a JWT verification implementation](methodology/auditing-jwt-verification.md)
- [Multi-tenant isolation testing](methodology/multi-tenant-isolation.md)
- [Testing a hosted MCP server](methodology/mcp-server-security.md)
- [LLM application security](methodology/llm-application-security.md)
- [SAML / SSO security](methodology/saml-sso-security.md)

**Web / API / infra**
- [API security testing (REST & GraphQL)](methodology/api-security-testing.md)
- [GraphQL security testing](methodology/graphql-security-testing.md)
- [Business logic testing](methodology/business-logic.md)
- [Race conditions](methodology/race-conditions.md)
- [SSRF hunting](methodology/ssrf-hunting.md)
- [Subdomain takeover](methodology/subdomain-takeover.md)
- [Web cache poisoning & host-header](methodology/cache-poisoning-and-host-header.md)
- [File upload testing](methodology/file-upload-testing.md)
- [XSS in single-page apps](methodology/xss-in-spas.md)
- [WebSocket security](methodology/websocket-security.md)
- [Prototype pollution](methodology/prototype-pollution.md)
- [Insecure deserialization](methodology/insecure-deserialization.md)
- [XXE (XML external entities)](methodology/xxe.md)
- [HTTP request smuggling](methodology/request-smuggling.md)
- [CSRF & clickjacking](methodology/csrf-and-clickjacking.md)
- [Open redirect](methodology/open-redirect.md)
- [CRLF / header injection](methodology/crlf-injection.md)
- [Cloud storage misconfiguration](methodology/cloud-storage-misconfig.md)
- [Dependency confusion](methodology/dependency-confusion.md)
- [Auditing GitHub Actions workflows](methodology/github-actions-security.md)
- [CI/CD & supply-chain security](methodology/cicd-supply-chain.md)

**Craft**
- [Secure code review](methodology/secure-code-review.md)
- [Secrets scanning](methodology/secrets-scanning.md)
- [Enumeration within scope](methodology/enumeration-within-scope.md)
- [Scope & disclosure hygiene](methodology/scope-and-disclosure-hygiene.md)
- [Writing a vulnerability report that doesn't get downgraded](methodology/writing-a-vulnerability-report.md)

## Deep dives

Byte-level, mechanic-first treatments — see [`deep-dives/`](deep-dives/).
`jwt-attacks` · `ssrf-cloud-and-internal` · `oauth-attacks` · `sql-injection` · `xss-advanced` · `request-smuggling` · `prototype-pollution-rce` · `ssti` · `deserialization-gadgets` · `command-injection` · `iam-privesc` · `access-control-and-idor` · `race-conditions` · `prompt-injection` · `nosql-injection` · `saml-xsw` · `graphql-attacks` · `account-takeover-chains` · `mobile-attacks` · `web-cache-deception` · `path-traversal-lfi` · `cors-and-postmessage` · `payment-business-logic` · `websocket-attacks` · `xs-leaks` · `dns-rebinding` · `git-exposure-and-secrets` · `http-parameter-pollution`

## Tools

Small, self-contained scripts — see [`tools/`](tools/) for the full index.
`ct_recon` · `takeover_scan` · `js_endpoints` · `header_audit` · `cors_probe` ·
`oauth_redirect_probe` · `workflow_audit` · `jwt_decode` · `wellknown_scan` · `openapi_diff` · `jwt_none_forge` · `authz_matrix` · `report_pack` · `csp_analyze`

## Write-ups

Finished, sanitized write-ups of confirmed findings (post-disclosure) and CTF/lab solutions live
in [`writeups/`](writeups/).

See also [references & reading](references.md).

## Ground rules

- **Only authorized targets** — bug bounty programs in scope, CTFs, labs, or systems I own.
- **Coordinated disclosure** — third-party vulnerability details are published only after they're
  fixed and disclosure is permitted; until then, only sanitized methodology.
- **No secrets, no PII** — credentials, tokens, and personal data never get committed
  (see [`.gitignore`](.gitignore)); evidence is masked before it's written down.

---
*A portfolio of authorized security research. Nothing here is a how-to for attacking systems you
don't have permission to test.*
