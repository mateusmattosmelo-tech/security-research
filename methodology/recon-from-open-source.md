# Recon from a Target's Open Source

When a company ships open source — SDKs, CLIs, Terraform providers, an MCP server, the product
itself — that code is a free, authoritative map of the backend. You don't have to guess the
API; the company's own client encodes it. This is read-only recon that touches none of the
target's infrastructure.

## What to pull and why

| Artifact | What it reveals |
|---|---|
| **Official SDK / API client** | Every management endpoint, its parameters, and the object model — often generated from the internal OpenAPI spec. |
| **CLI** | The high-value operations a human runs, plus auth flow and token handling. |
| **Terraform provider** | The full resource graph: what objects exist and how they reference each other (great for spotting the tenant/ownership boundary). |
| **The product repo itself** | For infra products, the trust boundaries in the architecture — which layers are described as *shared*. |
| **Framework plugins / examples** | Default configs, connection-string shapes, and the "happy path" the docs assume. |

## How to work it

1. **List the org's repos** by recent activity and stars — the maintained ones are the real map.
2. **Find the endpoint surface.** In the API client, the request builders enumerate paths and
   methods. Note which parameters carry an object identifier (candidate BOLA/tenant-scoping
   fields) vs. which are server-derived.
3. **Read the object model.** The Terraform provider or SDK types show how resources reference
   each other — that reference graph is where authorization has to hold.
4. **Note the trust boundaries.** For infra/platform products, the architecture doc names the
   shared layers; those are the cross-tenant candidates.
5. **Diff public vs. observed.** Endpoints in the client that the UI never calls are unlinked
   surface worth testing first.

## Discipline

- This is reconnaissance, not exploitation — reading public code sends no traffic to the target.
- Turn what you learn into a checklist of hypotheses, then test them **only** against
  in-scope, authorized assets, with the account and headers the program requires.
- New endpoints discovered later go back on the map; recon never really closes.
