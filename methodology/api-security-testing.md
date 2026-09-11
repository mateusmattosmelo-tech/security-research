# API Security Testing (REST & GraphQL)

APIs are where the real attack surface lives today — the browser UI is just one client of
many, and the API often trusts its callers more than it should. This is my working method
for a control-plane / product API.

## 1. Build the API map before probing

- Collect the spec if it exists: OpenAPI/Swagger, GraphQL introspection, Postman collections,
  the JS bundle's client, mobile app decompilation.
- For every operation, record: path, method, auth required, parameters, and — critically —
  which parameters carry an **object identifier** vs. which are derived server-side.
- Note versioning: `/v1` and `/v2` of the same resource often diverge in what they enforce.

## 2. Authentication surface

- How is the caller identified? Session cookie, bearer token, API key, signed request?
- Where does the token come from and what's its scope? A token minted for one purpose
  (e.g. read) reused on a write endpoint is a common gap.
- Test the **absence** of auth on each endpoint, not just presence: does the same route answer
  anonymously? With an expired token? With another tenant's token?

## 3. Authorization surface

This is the highest-yield area — see [`authorization-testing.md`](authorization-testing.md).
For APIs specifically:

- **BOLA:** swap object IDs between two real accounts and confirm real cross-account data.
- **BFLA:** replay privileged operations from an under-privileged token.
- **Mass assignment:** add fields the client UI never sends (`"role":"admin"`, `"ownerId":...`,
  `"verified":true`) and see if the server honors them.
- **Tenant scoping:** on a multi-tenant platform, the tenant/project/org ID is the boundary —
  test whether it's enforced server-side or trusted from the request.

## 4. Input & injection

- Reflect on where user input reaches a query, a template, a shell, a downstream request.
- SSRF: any parameter that becomes a URL the server fetches (webhooks, import-from-URL,
  avatar fetch, callback registration).
- Injection: SQL/NoSQL where input hits a datastore; command injection where it hits a shell;
  SSTI where it hits a template.

## 5. GraphQL specifics

- Run introspection (if enabled) to get the full schema; if disabled, field-suggestion errors
  still leak names.
- Test each **mutation** for authz independently — the query side being locked down says nothing
  about the mutation side.
- Watch **aliasing and batching** for limits bypass, and arbitrary-document acceptance
  (does the gateway execute any document anonymously?).
- Check that nested resolvers re-check authorization; a parent object being authorized doesn't
  mean its children are.

## 6. Business logic

State machines, money movement, quota/limits, and multi-step flows — see
[`business-logic.md`](business-logic.md).

## Discipline

- Add the program's identifying research header to every request when one is required.
- Respect rate limits and never run enumeration/brute-force where the policy forbids it.
- Write every observation to the target journal, not memory. New endpoints go back on the map.
