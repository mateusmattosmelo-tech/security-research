# SSRF Hunting

Server-Side Request Forgery is the server making an HTTP (or other-protocol) request to a
destination the attacker chooses. On cloud infrastructure it's often high impact — reaching the
metadata service, internal services, or other tenants.

## Find the sinks

Any feature where the server fetches a URL is a candidate. Look for parameters that become a
request:

- Webhooks and callback URLs (register a webhook, "test connection").
- Import-from-URL, "fetch avatar from URL", link unfurling/preview, PDF/screenshot generators.
- Integrations that take an endpoint: SSO metadata URLs, `jwks_uri` / `logo_uri` in OAuth DCR,
  OpenID `sector_identifier_uri`.
- Anything that takes a hostname, an image URL, or an XML/SVG with external entities.

## What to point them at

- **Cloud metadata:** `http://169.254.169.254/…` (AWS/GCP/Azure variants), the GCP metadata
  header requirement, IMDSv2 token flow.
- **Internal ranges:** `127.0.0.1`, `10.x`, `169.254.x`, `.internal` names, `localhost` and its
  encodings.
- **Protocol/parse tricks:** `http://attacker@internal/`, redirect from an attacker host to an
  internal one, DNS rebinding, decimal/hex/IPv6 encodings of internal IPs.

## Confirm out-of-band

Blind SSRF is common — the response isn't reflected. You need an **OOB listener** (a collaborator
server / DNS canary you control) to see the callback. Point the sink at a unique subdomain of
your listener and watch for the hit; the DNS lookup alone often proves the fetch even when the
HTTP is filtered.

Until you see that callback, an SSRF is a **lead, not a finding** — say so plainly. "The endpoint
accepts a URL parameter" is not proof the server fetches it.

## Escalate

A confirmed SSRF is a door, not the end:

- Read cloud metadata → temporary credentials → cross-service or cross-tenant access.
- Reach an internal admin/API that trusts the network position.
- Turn blind into non-blind via error messages, timing, or a gopher/redis gadget where allowed.

## Reporting

Show the request that triggers the fetch and the out-of-band evidence that it happened
(the callback log, the DNS hit, or the metadata response returned). Tie it to concrete impact —
what the server-side position let you reach — not just "it made a request."
