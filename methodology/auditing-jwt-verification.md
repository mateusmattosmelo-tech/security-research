# Auditing a JWT Verification Implementation

JWTs concentrate a lot of trust in a small amount of code: get the verification wrong and every
identity the token asserts becomes forgeable. When I have the source (open-source project, a
leaked bundle, a library), the verification routine is one of the highest-yield things to read.
Here's the checklist I run against it.

## 1. Is the algorithm pinned?

The classic JWT break is **algorithm confusion**:

- **`alg: none`** accepted → unsigned tokens pass.
- **`RS256` → `HS256`** confusion → the public key gets used as an HMAC secret, so anyone with
  the public key forges tokens.
- **`kid` tricks** → path traversal or SQL injection through the key-id header selecting an
  attacker-influenced key.

The safe pattern is to **ignore the token's `alg` header entirely** and verify with a single,
pinned algorithm and key. If the code branches on the header's `alg`, read that branch hard.

## 2. Does the signature cover what you parse?

Confirm the bytes handed to the signature check are the same bytes the claims are parsed from.
Off-by-one splitting (`header.payload.signature`) or verifying one region while reading claims
from another is a real bug class. Watch how the code splits on `.` — signature over
`header.payload`, claims from `payload`.

## 3. Are the time and identity claims enforced?

- **`exp`** — is it required, or optional? An optional `exp` means a token that never expires.
- **`nbf` / `iat`** — checked with a sane clock-skew leeway (30–120s), not zero, not unbounded.
- **`aud` / `iss`** — validated against the expected audience/issuer, or blindly trusted?
- **replay** — is there a `jti` / nonce / monotonic check, and is it actually enforced on every
  path (including cache hits)?

## 4. What happens on the failure and fallback paths?

This is where the subtle ones live. Look for:

- A **fallback mode** that skips verification — e.g. "if no key is configured, read the claims
  from an unauthenticated parameter." Ask precisely **who can trigger that mode** and **who can
  set that parameter**. If the caller controls both, verification is optional in practice.
- **Caching** that returns a prior result without re-checking time/replay.
- Errors that **fail open** (return a default identity) instead of failing closed.

## 5. Where does the verified identity go?

A correct verification is worthless if the caller then reads identity from an unverified place.
Trace the output: does the authorization logic consume the *verified* claims, or a
sibling parameter that anything can set?

## Reporting what you find in code

A code-level finding is a **hypothesis** until it's demonstrated against the running system.
Source tells you *where* the flaw is; a report needs the flaw *reproduced* against an in-scope,
authorized target — the forged token accepted, the wrong identity returned. State clearly which
part you proved and which part is still inference from the code; don't present a code smell as a
confirmed exploit.
