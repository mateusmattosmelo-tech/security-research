# Business Logic Testing

Business-logic flaws are the bugs a scanner never finds: the app does exactly what it was
coded to do, and what it was coded to do is wrong. They're also where the interesting money
is, because they're specific to the product and rarely duplicated.

## The core question

For every multi-step flow, ask: **what does the server assume that the client controls?**
The vulnerability is almost always a step, an order, a value, or a state the server trusts
the client to respect.

## Patterns to test

- **Skipped steps.** Complete a flow, then replay a late step without the early ones. Does a
  checkout finalize without payment? Does an upgrade apply without confirmation?
- **Reordered steps.** Run steps out of sequence. State machines that only validate the
  *current* transition, not the whole history, break here.
- **Replayed steps.** Repeat a one-time action (redeem, transfer, apply-once). Idempotency is
  often assumed, not enforced.
- **Value tampering.** Negative quantities, negative prices, zero, huge numbers, another
  currency, another user's coupon. Does the server re-validate or trust the client's math?
- **Parallel requests (race).** Fire the same "spend one credit" request N times at once.
  Check-then-act without a lock lets you spend the same thing twice.
- **State reuse.** A token/grant/object from an abandoned or expired flow, reused where the
  server expects a fresh one.

## Multi-tenant / quota angles

- Limits and quotas: is the ceiling enforced server-side, or just hidden in the UI?
- Ownership of intermediate objects: a half-created resource that briefly belongs to no one,
  or to the wrong tenant.

## Proving it

Show the intended flow (positive control), then the broken flow, then the concrete impact:
money moved, a limit exceeded, a resource obtained that shouldn't exist. Tie it to a real
outcome, not a theoretical one — that's what moves severity.
