# GraphQL Attacks — Deep Dive

One endpoint, a huge surface, and authorization pushed into resolvers. Beyond the overview, this
covers schema recovery when introspection is off, batching/alias abuse, and the authorization
patterns that actually break. Authorized testing with two accounts you own.

## Recover the schema when introspection is disabled

Introspection off ≠ schema hidden:

- **Field suggestions:** a typo'd field returns `Did you mean "email"?` — GraphQL leaks valid names
  through suggestion errors. Iterate to reconstruct types/fields.
- **`clairvoyance`**-style tooling automates this suggestion-based schema recovery.
- **Persisted-query / APQ leakage:** the client bundle contains the queries; hashes and documents
  reveal operations even without introspection.
- **Partial introspection:** some servers block `__schema` but allow `__type(name:)` — probe known
  type names directly.
- **Error verbosity:** type/coercion errors leak argument names and types.

## Authorization — where it actually breaks

- **Per-mutation authz:** the query side being locked says nothing about mutations. Test every
  mutation independently; teams often guard reads and forget writes.
- **Nested resolver authz:** `me { organization { members { email, ... } } }` — the parent is
  yours, but children may be re-resolved without a per-object check. Walk from an object you own to
  data you shouldn't see.
- **Node/global-id BOLA:** `node(id: "<base64 of Type:otherId>")` or `entity(id:)` — decode the
  global id, swap to another tenant's, re-encode. The id is often just base64(`Type:pk`).
- **Aliasing the same object with different ids** to bulk-test BOLA in one request:
  `a: user(id:1){email} b: user(id:2){email} ...`.
- **Mutation argument mass-assignment:** input objects that accept fields the UI never sends
  (`ownerId`, `role`, `isAdmin`).

## Batching & alias abuse

- **Rate-limit / brute-force bypass:** many servers rate-limit *requests*, not *operations*. One
  request with N aliased mutations = N attempts:
  ```graphql
  mutation { a: login(u:"x",p:"1"){t} b: login(u:"x",p:"2"){t} ... }
  ```
  Defeats per-request throttling on login/OTP/coupon endpoints — a real, high-value pattern.
- **Array batching:** `[{query:...},{query:...}]` where supported — same effect at the transport
  level.
- Combine with alias to enumerate/extract many objects in a single request (also evades per-request
  logging/alerting).

## Denial-of-service surface (usually out of scope — know it, don't fire it)

- **Deeply nested queries** through circular relationships (`a{b{a{b{...}}}}`) — quadratic/
  exponential resolution.
- **Wide aliasing / large `first:`** to force huge result sets.
- Most programs exclude query-complexity DoS; report the *absence* of depth/complexity limits as a
  hardening note at most, and don't actually degrade the service.

## Injection through resolvers

Resolver arguments reach the same sinks as REST: filter/`where` args → SQL/NoSQL injection;
sort/order fields → injection; a "search" arg → the datastore. Test them as injection points, not
just as data.

## CSRF & transport

- If the endpoint accepts `GET` for queries (and sometimes mutations) or
  `application/x-www-form-urlencoded` bodies, it can be CSRF-able (no preflight). Check whether
  mutations are reachable via GET / form-encoded.

## Method

Recover the schema (introspection or suggestions), inventory mutations and secret-returning
fields, then run BOLA with two accounts (alias-batched), test batching against any throttled
operation, and probe resolver args for injection. Prove real cross-account data, with controls.

## Reporting

Give the exact operation, the two-account contrast (or the batched brute that beat the limit), and
the concrete data/impact. Note whether the gap is per-field, systemic (a resolver pattern across
types = a class), or transport (batching/CSRF). Systemic beats instance.
