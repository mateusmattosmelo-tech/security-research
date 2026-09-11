# Testing Multi-Tenant Isolation

On a SaaS or cloud platform, the single most valuable property is **tenant isolation**: one
customer must never be able to read, write, or influence another customer's data or compute.
When it breaks, severity is usually critical — cross-tenant access is the top of almost every
program's reward table.

This note is about *how to reason about* isolation on a data/compute platform, generically.

## Where the boundary lives

Isolation is enforced at several layers, and a platform is only as strong as its weakest one:

| Layer | The boundary object | How it breaks |
|---|---|---|
| **Control plane / API** | tenant / project / org ID in the request | ID trusted from client instead of derived from session |
| **Application** | row-level filters, ownership checks | missing `WHERE tenant_id = ?`, or it's client-supplied |
| **Database** | role/schema separation, row-level security | shared role, RLS disabled, superuser reachable |
| **Storage** | per-tenant keys / paths | shared key, path traversal, predictable object names |
| **Compute** | container / VM / namespace | escape to host, shared cache, side channels |
| **Secrets** | per-tenant credentials | a control-plane secret that grants cross-tenant access |

## A method for probing it

1. **Stand up two tenants you own** — Tenant A (attacker) and Tenant B (victim). Give B some
   distinctive, real data so a leak is unambiguous.
2. **Enumerate the boundary object** in every request: is it a project ID, a connection string,
   a branch name, an endpoint host, a bucket path? List every place it appears.
3. **Swap A → B** at each layer:
   - API: call A's session against B's project/resource ID.
   - Data: from inside A's own compute, try to reach B's data (another role's tables, another
     schema, a shared catalog).
   - Storage/secrets: does any identifier or credential A can see reference B?
4. **Prove real access.** A confirmed finding shows B's genuine data returned to A, with a
   positive control (A sees A's data) and negative control (a non-existent tenant errors
   cleanly). Error-message differentials alone are usually out of scope.

## Platform-specific angles worth remembering (generic, database-as-a-service)

- **Extensions / plugins:** allow-listed server-side extensions expand the SQL surface. An
  extension that reaches the filesystem, network, or another role changes the blast radius —
  reason about what each *shipped* extension can do within your own compute.
- **Roles & privileges:** the gap between "your own database's owner" and "full superuser" is
  where privilege-gain findings live — reaching another role's objects, or bypassing row/role
  permissions inside your own compute.
- **Shared infrastructure:** any layer described as "shared" (a shared storage service, a shared
  pager/cache) is a cross-tenant candidate — unauthorized read/write there affects other tenants.
- **Connection strings & endpoints:** these encode the boundary. Test whether one tenant's
  endpoint or credential can be pointed at another tenant's data.

## Reporting isolation bugs

- Lead with the boundary that broke and the two-tenant proof.
- State the exact layer and the exact object reference that wasn't enforced.
- Severity follows the reward table: cross-tenant data access / contamination is typically the
  critical band; an authorization bypass scoped to a single tenant is a tier below.
