# Access Control & IDOR — Deep Dive

Broken access control is the #1 web risk because there are so many places to get it wrong. Beyond
"swap the id," this covers how to defeat the defenses teams add — unpredictable ids, encrypted ids,
signed ids — and the structural gaps (mass assignment, method/version drift, state-based). For
authorized testing with two accounts you own.

## The identifier is the battleground

The object reference is where authz is enforced or trusted. Defenses and their attacks:

### Sequential / small ids
Trivial: enumerate. The finding is the missing ownership check, not the id shape.

### "Unpredictable" ids (UUID/GUID, random)
Unpredictability is not authorization — but it raises the bar to *obtaining* the id. So the game is
**leaking** it, then using it:

- **Where ids leak:** other API responses (a list endpoint, a search, a `included`/`_embedded`
  block over-returning), URLs, emails/notifications, `Location` headers, referrer, timestamps in
  the object, GraphQL `node` connections, export/CSV features, error messages.
- **Weak "random":** UUIDv1 is time+MAC based (predictable within a window); `Math.random()`,
  incrementing-with-jitter, or timestamp-seeded ids can be forecast. Collect several, model the
  entropy.
- Once leaked/predicted → the vulnerable endpoint that doesn't re-check ownership hands over the
  object. **An id you can obtain is not a security control** — that's the report framing.

### Encrypted / hashed ids (oracle attacks)
Apps sometimes ship `id = base64(AES(...))` or `hash(id)` thinking opacity = safety:

- **Hash of a small space:** `sha256(zipcode)` / `md5(email)` / `sha1(userid)` is reversible by
  brute over the space — compute the hash of *your own* value to prove the oracle, then reverse
  others offline. (A real case: a "hashed" postal code recovered in ~1s against the space.)
- **ECB / no integrity:** block-level cut-and-paste, or flipping since there's no MAC.
- **Padding oracle:** if the app decrypts the id and its error/behavior differs on bad padding, you
  can decrypt/encrypt arbitrary ids (CBC padding oracle) — turning an opaque id into a forgeable
  one.

### Signed ids (HMAC/JWT-wrapped)
- If the id is signed but the **signature isn't verified** on the read path, tamper freely.
- If HMAC with a weak/leaked secret → forge (see [JWT attacks](jwt-attacks.md) for the crypto).
- Signature covers the id but not the *action/scope* → reuse a valid signed id in a context it
  wasn't meant for.

## Structural gaps (independent of the id)

- **Mass assignment / over-posting:** add fields the UI never sends to a create/update —
  `"ownerId":<victim>`, `"role":"admin"`, `"verified":true`, `"tenantId":<other>`. The server binds
  them because it trusts the object shape.
- **Method & version drift:** `GET /admin/x` blocked, `POST` allowed; v1 enforces authz, the v2
  alias doesn't; a `HEAD` or `OPTIONS` leaks. GraphQL mutation unguarded while the query is locked.
- **Sub-resource / nested authz:** parent authorized, child re-fetched by client id without a
  re-check (`/orgs/mine/members/{id}` where `{id}` isn't scoped to the org).
- **State-based:** access on an object that's *expired but not revoked*, a *pre-existing* grant, an
  invite/role acquired by accepting a link, a wizard abandoned mid-flow.

## Proving it to survive triage

Programs discount authz reports that show only an **error differential against synthetic ids**. The
strong proof:

1. Two **real** accounts you own (A attacker, B victim); give B distinctive real data.
2. A's request returns/alters **B's real resource** — show the data.
3. **Positive control:** A→A's own object returns A's data. **Negative control:** a non-existent id
   errors cleanly. Varying only the id is what proves the swap moved it.

## Reporting

Lead with the real cross-account resource A obtained. Name the exact reference and where authz was
missing (endpoint, method, sub-resource, mass-assigned field), and — if you defeated a defense —
how (leaked the UUID here, reversed the hash in Ns, forged the signature with the leaked key). If
it's a **class** (a whole route family / any object type), say so; a class beats an instance by
orders of magnitude.
