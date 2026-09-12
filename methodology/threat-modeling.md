# Threat Modeling for Offensive Recon

Threat modeling is usually framed as a defensive exercise, but it's just as useful offensively:
it's a structured way to decide *where the bugs probably are* before you spend hours testing. A
good model turns "poke at everything" into "these five trust boundaries are where this product
most likely fails."

## The four questions (Shostack)

1. **What are we building?** Draw the data-flow: components, data stores, external entities, and the
   requests between them.
2. **What can go wrong?** Enumerate threats per element and per flow.
3. **What are we going to do about it?** (Defender's job — but knowing the expected control tells
   you what to test *for the absence of*.)
4. **Did we do a good job?** (Iterate.)

For a hunter, questions 1 and 2 are the map.

## Draw the data-flow and mark the trust boundaries

The bugs cluster on **trust boundaries** — every line where data crosses from less-trusted to
more-trusted:

- Browser/app → API (authn/authz, input validation).
- API → datastore (injection, tenant scoping).
- Service → service (does the internal call re-authorize, or trust the caller?).
- Tenant → tenant (the isolation boundary on a multi-tenant product).
- User content → renderer (XSS), → parser (XXE/deserialization), → template (SSTI).
- App → third party / outbound fetch (SSRF), → build/deploy (supply chain).

Draw them; each boundary is a testing target.

## STRIDE as a checklist per element

For each component/flow, walk STRIDE — it maps cleanly to bug classes:

| STRIDE | Question | Classes to test |
|---|---|---|
| **S**poofing | Can I be someone else? | auth bypass, JWT/OAuth/SAML, session |
| **T**ampering | Can I change data in transit/at rest? | IDOR/mass-assignment, param tampering, integrity |
| **R**epudiation | Can I act without a trace? | logging gaps (usually low) |
| **I**nfo disclosure | Can I read what I shouldn't? | BOLA, path traversal, verbose errors, secrets |
| **D**oS | Can I degrade it? | (often out of scope — note, don't fire) |
| **E**levation | Can I gain privilege? | privesc, IDOR-to-admin, RCE chains |

## Rank by impact × reachability

Not all boundaries are equal. Prioritize where a break is **critical** (cross-tenant, auth, money,
RCE) *and* **reachable** with the access you have (account-free? one account? two?). The reward
table of the program tells you where the money is; the model tells you where the flaws are; test the
overlap first.

## Turn the model into a plan

Output a ranked list of hypotheses tied to boundaries:
- "The `/api/v2/{project_id}/...` boundary trusts `project_id` from the request → test cross-tenant
  BOLA (needs two accounts)."
- "The outbound webhook fetch → test SSRF (account-free-ish)."
- "The template render of the invite name → test SSTI."

Then attack the highest impact × reachability first, and let recon feed new boundaries back into
the model as you find them (recon never closes).

## Why this makes you faster and more credible

A hunter who can articulate *why* they tested where they did — "this is the tenant boundary, and it
trusts a client value" — writes better reports and finds systemic (class) bugs instead of one-off
instances. It's the difference between luck and method.
