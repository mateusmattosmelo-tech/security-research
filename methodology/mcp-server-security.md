# Testing a Hosted MCP Server

Model Context Protocol (MCP) servers are a fast-growing, under-tested surface: a hosted MCP
server exposes tools that act on a user's behalf against a backend, gated by OAuth. That makes
it a concentrated target — the OAuth layer guards tools that can read and write real resources.
Here's how I approach one, using only its public, unauthenticated surface.

## 1. Read the advertised metadata

A spec-compliant server publishes discovery documents you can fetch with no token:

- `/.well-known/oauth-authorization-server` — issuer, `authorization_endpoint`, `token_endpoint`,
  `registration_endpoint`, `revocation_endpoint`, supported grants, PKCE methods, scopes.
- `/.well-known/oauth-protected-resource` — the resource and its authorization servers.

These tell you the whole auth shape before you send a single authenticated request. Note the
**scopes** — they reveal how much a token is worth (read vs write across which resource classes).

## 2. Dynamic client registration (DCR)

MCP commonly allows **anonymous** DCR (`token_endpoint_auth_method: none`). Registering a client
is the intended flow, not a bug — but it opens testing:

- Register a client with a redirect URI you control, then probe the authorize endpoint.
- Check whether DCR **validates or fetches** any client-supplied URL (`jwks_uri`, `logo_uri`).
  A server that fetches those is an SSRF candidate — confirm only with an out-of-band listener,
  and treat it as a lead until you see the callback.
- Be a good guest: **revoke** the client you created when you're done.

## 3. The redirect_uri check is the crown jewel

If the authorize endpoint accepts a redirect URI that isn't the client's registered one, an
attacker steals the authorization code and, with it, the victim's tokens. Test it exactly like
any OAuth server:

- Baseline: the registered URI → proceeds.
- Then every mismatch variant: a different host, an attacker subdomain
  (`registered.attacker.com`), a `@attacker.com` userinfo trick, a path append, a traversal, an
  appended `?next=`, a different path on the same host.
- Each should be rejected outright (an error, never a redirect to the supplied URI). Strict
  exact-match is the correct behavior; anything looser is a token-theft finding.

## 4. Everything behind the token

The tools themselves (`/sse`, `/mcp`, the JSON-RPC surface) require a bearer token — reaching
them means completing the OAuth flow with a real account. That's where the high-impact bugs live
(tool authorization, SSRF through tool parameters, injection into downstream calls), but it's
authenticated testing: only go there with an account you own and within the program's scope.

## 5. Don't forget PKCE and grant hygiene

- Is PKCE required, and only `S256` (not `plain`)?
- Which grants are enabled? An unexpected `implicit` or `password` grant is a smell.
- Does the token endpoint accept `none` auth for confidential operations it shouldn't?

## Reporting

Discovery metadata and a strict redirect_uri check are usually clean — write them up as the
refutations they are. A loose redirect_uri, an SSRF-on-DCR you confirmed out-of-band, or a tool
reachable without proper scope are the ones worth a report — and each needs the concrete request
and response that proves it, not just the shape of the endpoint.
