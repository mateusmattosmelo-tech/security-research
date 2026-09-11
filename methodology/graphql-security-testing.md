# GraphQL Security Testing

GraphQL moves a lot of authorization decisions into resolvers, and a single endpoint hides a
large surface. The query side being locked down tells you nothing about the mutation side — each
field is its own trust decision.

## Map the schema

- **Introspection:** if `__schema` is enabled, pull the whole type/query/mutation graph.
- **If introspection is off:** field-suggestion errors ("Did you mean …?") still leak names;
  persisted-query hashes, the client bundle, and error messages fill in the rest.
- Note every **mutation** and every field that returns sensitive data or a secret.

## Authorization — the main event

- **Per-field authz:** test each mutation and sensitive query independently. A locked `viewer`
  query says nothing about `updateUser` or `adminStats`.
- **Nested resolver authz:** an authorized parent object can expose children that aren't
  re-checked — `me { organization { members { email } } }`. Walk the graph for objects reachable
  through a parent you legitimately own.
- **BOLA via node ids:** pass another tenant's object id to a `node(id:)` / `entity(id:)` field.

## GraphQL-specific abuse

- **Batching / aliasing** to bypass rate limits or brute-force protections:
  `q1: login(...) q2: login(...) …` in one request.
- **Query depth / complexity** as DoS — usually out of scope, and often a declared known issue;
  check the policy before spending time.
- **Mutation-through-query** and CSRF if the endpoint accepts `GET` or form-encoded bodies.
- **Injection in resolver arguments** — filters, sort/order fields, or raw-ish arguments that
  reach a datastore.

## Practical tips

- Test with two real accounts (A/B) exactly as for REST BOLA — prove real cross-account data,
  not an error differential.
- Watch responses for over-fetching: fields returned that the UI never requests but the resolver
  happily includes.
- Diff what the official client asks for vs. what the schema allows — the gap is unlinked surface.

## Reporting

Give the exact query/mutation, the two-account contrast, and the concrete data crossed. Note
whether introspection was on and whether the issue is per-field or systemic — a systemic
resolver-authz gap is a class, worth far more than one field.
