# OAuth 2.0 / OIDC Testing

OAuth and OIDC concentrate authentication into a handful of endpoints and a handful of
parameters. Most real bugs are not exotic crypto — they're a validation that's too loose or a
step that's optional when it shouldn't be. This is the checklist I run.

## Map the provider first

Fetch the discovery document (no auth needed):

- `/.well-known/openid-configuration` (OIDC) or `/.well-known/oauth-authorization-server`.
- Read off: `authorization_endpoint`, `token_endpoint`, `registration_endpoint`,
  `grant_types_supported`, `response_types_supported`, `code_challenge_methods_supported`,
  `scopes_supported`.

Smells worth noting immediately:

- `implicit` or `token` response types enabled (tokens in the URL fragment, easy to leak).
- `password` grant enabled (resource-owner password — credential-stuffing surface).
- `plain` in `code_challenge_methods` (weak PKCE).

## redirect_uri validation — the highest-value test

A loose redirect_uri check leaks the authorization code/token to an attacker. Test exact-match
enforcement with every bypass variant; only the registered URI should proceed, everything else
should error **without redirecting**:

- a different host entirely
- attacker subdomain suffix: `https://registered.example.com.attacker.com/cb`
- userinfo trick: `https://registered.example.com@attacker.com/cb`
- path append / traversal: `.../cb/../evil`, `.../cb/extra`
- different path on the same host
- appended open param: `.../cb?next=https://attacker.com`
- backslash and encoding tricks

(`tools/oauth_redirect_probe.py` runs this matrix.)

## PKCE and state

- Is PKCE **required** for public clients, and only `S256`? Missing PKCE on a public client
  allows authorization-code interception.
- Is `state` bound to the user session and checked on return? Missing/unchecked `state` is CSRF
  on the OAuth flow (login CSRF, account linking).

## Token handling

- Does the `token_endpoint` bind the code to the same client and the same redirect_uri that
  requested it? Code substitution across clients is a bug.
- For OIDC, is the `id_token` signature verified, the `iss`/`aud` checked, the `nonce` matched?
- Are authorization codes single-use and short-lived?

## Dynamic client registration (if enabled)

- Is anonymous DCR allowed? It's common and often intended, but it opens testing.
- Does the server **fetch** any client-supplied URL (`jwks_uri`, `logo_uri`, `sector_identifier_uri`)?
  If so, that's an SSRF candidate — confirm out-of-band.

## What usually isn't a bug (don't over-report)

- A well-configured provider that exact-matches redirect_uri, requires S256 PKCE, and checks
  state is doing it right — write those up as refutations, not findings.
- Rate-limiting and account-enumeration on auth endpoints are out of scope on many programs;
  check the policy before touching them.
