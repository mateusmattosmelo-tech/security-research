# Building an API Inventory for Authorization Testing

Before testing authorization on an API, inventory it. A spec-driven inventory turns "poke at
whatever I see in the browser" into "here are the 60 operations that take an object id, ranked by
what leaks if the check is missing." It's also work you can do entirely offline, before touching
the target.

## Where the inventory comes from

- **OpenAPI / Swagger** — the authoritative list of paths, methods, parameters, and response
  shapes. Often shipped inside the official SDK (`v2.json`, `openapi.yaml`) even when the live
  `/openapi.json` needs auth.
- **Official client / CLI** — request builders enumerate the same surface, plus the auth flow.
- **GraphQL introspection** — schema of types, queries, and mutations.

## What to extract per operation

| Field | Why |
|---|---|
| method + path | the operation |
| object identifiers in the path/body (`{project_id}`, `{user_id}`, `{key_id}`) | BOLA candidates — the boundary the server must enforce |
| what it returns | ranks impact if the check fails |
| what it mutates | write-side authorization, often weaker than read |
| the tenant/org container in the path | the isolation boundary |

## Rank by blast radius, not by path order

Two categories jump the queue:

1. **Operations that return a secret** — a password reveal, a connection string, an API key, a
   token, a signed URL. A missing check here is straight credential disclosure — usually the top
   of the reward table.
2. **Operations that grant or change access** — permission grants, role changes, key creation,
   sharing. A missing check here is privilege escalation.

Everything under a `{tenant_id}` / `{org_id}` / `{project_id}` is a cross-tenant candidate: the
question is always "does the server re-derive this container from my session, or trust it from my
request?"

## Turn the inventory into a test matrix

With two accounts you own (A = attacker, B = victim):

- For each object-id operation, call it as **A** against **B's** identifier.
- Confirmed finding = A receives or changes B's real resource, with a positive control (A→A's
  own object returns A's data) and a negative control (a non-existent id errors cleanly).
- Error-message differentials alone usually don't count — demonstrate the real resource.

## Why do this before you have access

Even with no account yet, the inventory is finished work: the moment you can authenticate, the
test matrix runs immediately instead of starting from zero. And the ranking tells you exactly
which handful of the dozens of endpoints to hit first.
