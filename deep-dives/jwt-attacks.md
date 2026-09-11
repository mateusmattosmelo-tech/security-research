# JWT Attacks — Deep Dive

A JWT is `base64url(header) . base64url(payload) . base64url(signature)`. The header's `alg` tells
the verifier how the signature was made. Almost every JWT break is the verifier trusting the token
about how to verify the token. This goes through each class at the mechanic level. Everything here
is for **authorized testing** — forge tokens for your own account against a system you may test.

## 1. `alg: none`

The spec defines an "unsecured" JWS with `alg:none` and an **empty** signature segment. A verifier
that honors it accepts unsigned tokens.

```
header  = {"alg":"none","typ":"JWT"}
token   = base64url(header) "." base64url(payload) "."      # note the trailing dot, empty sig
```

Variants that slip past naive blocklists: `None`, `NONE`, `nOnE` (the check must be
case-insensitive). Libraries that "fixed" this still sometimes accept `none` when the verifier is
called **without** an explicit allowed-algorithms list. The bug is really "verify() defaults to
trusting `alg`."

## 2. RS256 → HS256 algorithm confusion

The high-value one. Asymmetric `RS256` verifies with the **public** key; symmetric `HS256` verifies
with a **shared secret** via HMAC. The public key is, by definition, public.

If the server calls a generic `verify(token, key)` where `key` is the RSA **public** key, and the
attacker sets `alg:HS256`, some libraries then compute `HMAC-SHA256(publicKeyBytes, header.payload)`
— and the attacker can compute *exactly that*, because they have the public key. So:

1. Obtain the server's RSA public key (JWKS endpoint `/.well-known/jwks.json`, a TLS cert, the
   OIDC config, or recover it from two tokens).
2. Take the **exact byte representation** the server uses (usually the PEM/SPKI string — trailing
   newline included; getting the bytes wrong is the #1 reason PoCs fail).
3. Forge: header `{"alg":"HS256"}`, your payload, signature = `HMAC-SHA256(pubkey_pem, signing_input)`.

```python
import hmac, hashlib, base64, json
def b(x): return base64.urlsafe_b64encode(x).rstrip(b'=')
pub = open('pub.pem','rb').read()                    # the exact bytes the server holds
h = b(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
p = b(json.dumps({"sub":"victim","role":"admin"}).encode())
si = h + b'.' + p
sig = b(hmac.new(pub, si, hashlib.sha256).digest())
print((si + b'.' + sig).decode())
```

The fix — and what makes this a refutation when present — is the verifier **pinning the algorithm**
(`verify(token, key, algorithms=['RS256'])`) so `alg` from the token is never consulted.

## 3. `jwk` header injection (self-signed key)

The JOSE header can embed a public key in a `jwk` field. A verifier that trusts the token's own
embedded key verifies the attacker's signature against the attacker's key:

```
header = {"alg":"RS256","jwk":{"kty":"RSA","n":"<attacker n>","e":"AQAB"}}
```

You generate a keypair, embed the public half in `jwk`, and sign with your private half. The server
must instead use a **pre-configured** key, never one carried in the message.

## 4. `jku` / `x5u` — SSRF + key hijack

`jku`/`x5u` point at a URL the verifier fetches to get the key set. Two bugs:

- If the URL is unvalidated → **SSRF** (point it internally) and, worse, key hijack: host your own
  JWKS so the server fetches *your* key and validates *your* signature.
- Allowlist bypasses are the OAuth `redirect_uri` game again: `https://trusted/../..@evil`, open
  redirect on the trusted host, etc.

## 5. `kid` injection

`kid` (key id) selects which key to use and is often used to build a filesystem path or a DB query:

- **Path traversal:** `"kid":"../../../../dev/null"` → verifier reads an empty/known file as the
  key; sign with the matching (empty) key. `/proc/sys/...` or a predictable static file works too.
- **SQL injection:** `"kid":"x' UNION SELECT 'known-secret'-- -"` → the query returns an
  attacker-known key; sign with it.
- **Command injection** where `kid` reaches a shell.

## 6. Weak HMAC secret

If `HS256` with a guessable secret (`secret`, `changeme`, a leaked value), crack it offline:

```
hashcat -a 0 -m 16500 token.txt wordlist.txt
```

No traffic to the target — you brute the signature against a wordlist locally, then mint tokens.

## 7. CVE-2022-21449 — "psychic signatures"

Java 15–18's ECDSA verification accepted `r=0,s=0` as valid for ES256/384/512. A signature of two
zero values verified against *any* key. If the target ran a vulnerable JVM, a token with an
all-zero signature under `ES256` was accepted unconditionally.

## 8. Validation-order & claim bugs

- Signature verified but `exp`/`nbf`/`aud`/`iss` not enforced → replay, cross-audience reuse.
- `alg` allowed list includes both symmetric and asymmetric → confusion re-enabled.
- Parsing the payload from a different region than the signature covers (see the
  [verification-code audit](../methodology/auditing-jwt-verification.md)).
- Caching a validated result keyed only on the token string, skipping re-checks of time/replay.

## Testing method

`tools/jwt_decode.py` reads the token and flags the openings; `tools/jwt_none_forge.py` builds the
`alg:none` variants. For confusion, get the **exact** public-key bytes and compute the HMAC as
above. Prove impersonation against **your own** second account, with the original (valid) token as
the control, before anything else.
