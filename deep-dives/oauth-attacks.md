# OAuth 2.0 Attacks — Deep Dive

OAuth's security rests on a few parameters moving between the client, the authorization server (AS),
and the user's browser. Most account-takeover-grade bugs are one of those parameters validated too
loosely. This is the mechanic level of the main chains, for authorized testing with your own
accounts.

## The flow, and where the code can leak

Authorization-code flow:

```
1. client -> browser -> AS /authorize?client_id&redirect_uri&response_type=code&scope&state&code_challenge
2. user authenticates & consents
3. AS -> browser -> redirect_uri?code=AUTH_CODE&state=...
4. client backend -> AS /token  (code + client_secret + code_verifier) -> access_token
```

The `code` in step 3 travels through the **browser** to `redirect_uri`. If an attacker can make
step 3 deliver the code to a URL they control, they exchange it (or it's exchanged for them) and
take over the account. So `redirect_uri` validation is the crown jewel.

## redirect_uri exploitation

The AS must exact-match `redirect_uri` against the registered set. Loose matching leaks the code:

- **Bypass patterns** (same as open redirect): `https://client.com.evil.com/cb`,
  `https://client.com@evil.com/cb`, `.../cb/../evil`, `.../cb?x=https://evil`, path-prefix matches,
  subdomain wildcards the client didn't intend.
- **Open redirect on the client** as the pivot: `redirect_uri` is a *legit* client URL that itself
  open-redirects (or has an XSS) — the code lands on the legit host, then bounces to the attacker,
  or is read by injected script. This is why an open redirect on an OAuth client is not "low."
- **`response_mode` / fragment tricks:** switching to a mode that puts the token in a fragment the
  attacker's script on the redirect page can read.

## `state` — CSRF on the flow

`state` binds the callback to the user's session. If it's missing or unchecked:

- **Login CSRF / account fixation:** the attacker starts a flow, captures *their* `code`, then
  tricks the victim's browser into completing the callback with the attacker's code — now the
  victim is logged into the attacker's account (or the attacker's identity is linked to the
  victim's account, depending on the app), enabling data capture or account linking abuse.

## PKCE issues

PKCE binds the `code` to a `code_verifier` only the initiator knows (`code_challenge = S256(verifier)`).

- **No PKCE on a public client:** a stolen code can be redeemed by anyone → code interception is
  game over.
- **`plain` downgrade:** if `code_challenge_method=plain` is accepted, `challenge == verifier`, so
  intercepting the challenge (it's in the front-channel request) lets you redeem the code.
- **PKCE not enforced at the token endpoint** even when advertised.

## Code substitution / injection

- **Code replay:** codes must be single-use and short-lived. If reusable, a captured code is
  reusable.
- **Cross-client code injection:** inject a code obtained for client A into client B's callback; if
  the token endpoint doesn't bind the code to the requesting `client_id` and `redirect_uri`, it
  issues a token — attacker logs into B as the victim.
- **Mix-up attacks:** with multiple AS/IdPs, the client must track which AS a code came from; if not,
  a malicious AS can get its code redeemed at the honest one.

## OpenID Connect specifics

- `id_token` signature must be verified, with `iss`, `aud`, and `nonce` all checked. `nonce` is the
  OIDC equivalent of `state` for the id_token; missing `nonce` enables replay.
- `alg:none` / confusion on the `id_token` — see [JWT attacks](jwt-attacks.md).

## Testing method

Register/use your own client and two of your own accounts. Probe `/authorize` redirect_uri with the
matrix in `tools/oauth_redirect_probe.py`; verify `state`/`nonce` enforcement; check the token
endpoint binds code↔client↔redirect_uri↔verifier. Demonstrate takeover only against your **own**
victim account, with the normal flow as the control.

## Reporting

Lead with the chain: the loose parameter, the step where the code/token diverts, and the account
takeover it yields — shown end-to-end against your own accounts. Name the exact gap (redirect_uri
prefix match, missing state, plain PKCE, unbound code) so the AS team fixes the right thing.
