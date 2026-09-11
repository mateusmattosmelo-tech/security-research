# Authorization Testing (IDOR / BOLA / Privilege Escalation)

Broken authorization is consistently the highest-impact, highest-frequency class in modern
web and API targets. Authentication asks *"who are you?"*; authorization asks *"are you
allowed to touch this?"* — and it's the second question that most apps answer sloppily.

## The mental model

Every request that touches a resource has four variables:

1. **Actor** — the identity the session represents.
2. **Object** — the thing being read or written.
3. **Object reference** — how the object is named in the request (path param, body field, header).
4. **Permission** — the rule that should link actor → object.

An authorization bug exists when the permission check is missing, incomplete, or trusts a
value the actor controls. So the whole discipline reduces to: **find every place the object
reference comes from the client, then test whether the permission is actually enforced.**

## Object-level (IDOR / BOLA)

- Map every endpoint where an identifier appears in the request (`/users/123`, `?order_id=`,
  `{"accountId": ...}`, `X-Account-Id:` header).
- Capture two clean sessions in **separate accounts** (A = attacker, B = victim).
- Replay A's request substituting B's identifier. Three outcomes matter:
  - **200 with B's data** → confirmed IDOR. Capture proof of *real* cross-account data.
  - **403 / 404** → check whether it's a real check or just a differential (see below).
  - **200 with empty/own data** → the server re-derived the object from the session (good design).

### Proving it properly

A strong report shows **actual unauthorized access to a real resource of another account** —
not a generic error against a synthetic ID. Many programs explicitly exclude
"authorization findings based solely on error-message differentials." So:

- Use two **real** accounts you own, not made-up IDs.
- Show B's genuine data returned to A, side by side with A's own baseline.
- Include the negative control (A's identifier returns A's data) to prove the swap is what moved it.

## Function-level (privilege escalation)

- Enumerate the actions each role can perform (admin, owner, member, guest, anonymous).
- Take a privileged action's raw request and replay it from a lower-privileged session.
- Watch for **method-scoped** gaps: `GET /admin/x` blocked but `POST /admin/x` allowed, or a
  v1 route enforcing auth while its v2 alias doesn't.

## Where the subtle ones hide (unusual state)

The defect lives on the path the tester doesn't walk:

- A grant/device/token that **pre-exists** rather than being freshly created.
- An object **expired but not revoked**.
- A wizard **abandoned mid-flow**, leaving a half-authorized object.
- A role **acquired by accepting an invite/link** rather than assigned by an admin.
- The **owner_source read from a client field** instead of derived from the session.

## Checklist

- [ ] Two real accounts captured, in isolated sessions.
- [ ] Every client-supplied identifier catalogued.
- [ ] Horizontal swap tested (A → B's object).
- [ ] Vertical swap tested (low role → high-role action).
- [ ] Method/alias variants tried on each protected route.
- [ ] Proof shows real cross-account resource, with positive + negative controls.
