# SAML / SSO Security

SAML carries an identity assertion from an IdP to a service provider (SP) as signed XML. The bugs
are almost all about **signature validation** — if the SP mishandles the signature, an attacker
forges or tampers with the assertion and logs in as anyone.

## The core: how is the signature validated?

- **Is it validated at all?** Strip the `<Signature>` and resubmit — a stray SP will accept an
  unsigned assertion.
- **What is signed — assertion or response, and does the SP check the right one?** An SP that
  trusts a signed *response* but reads claims from an unsigned nested *assertion* (or vice-versa)
  is exploitable.
- **XML Signature Wrapping (XSW):** add a second, attacker-controlled assertion alongside the
  legitimately signed one so the signature verifies against the original while the app reads the
  injected one. The classic SAML break — several XSW variants exist; try each.
- **Canonicalization / comment injection:** `admin@x.com` vs `admin@x.com<!---->.evil` — some
  parsers drop text at comments, so the signed value and the read value differ.

## Other checks

- **Recipient / Audience / Destination:** does the SP enforce that the assertion was minted for
  *it*? A missing audience check enables assertion replay across SPs.
- **NotBefore / NotOnOrAfter:** are validity windows enforced? Replay of an old assertion.
- **InResponseTo:** bound to a real AuthnRequest, or accepted unsolicited (IdP-initiated) —
  unsolicited + weak audience = forgery surface.
- **IdP metadata / certificate:** can the attacker influence which cert validates the signature
  (a `KeyInfo` the SP trusts from the message itself)? It must use a pre-configured cert, never
  one supplied in the assertion.
- **XXE in the SAML parser:** the assertion is XML — the parser may be vulnerable to external
  entities.

## OIDC/OAuth SSO overlaps

If the SSO is OIDC rather than SAML, the equivalent checks are `id_token` signature/`iss`/`aud`,
`nonce`, and redirect_uri — see [OAuth 2.0 / OIDC testing](oauth-oidc-testing.md).

## Testing safely

Use your own IdP account and your own SP account. Forge/tamper against **your** identity first to
prove the validation gap without touching anyone else; only demonstrate impersonation with a
second account you also control.

## Reporting

Show the original vs. modified assertion, exactly which element you changed, and the login
succeeding as a different (attacker-owned) identity. Name the specific gap (no signature check,
XSW variant N, missing audience) — that's what the SP team fixes.
