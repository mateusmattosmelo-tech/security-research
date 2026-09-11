# Race Conditions

A race condition is a check-then-act gap: the server validates a condition, then acts on it, and
between the two a second request slips in. The result is doing something once that should only be
possible once — redeeming a coupon twice, overdrawing a balance, exceeding a quota, using a
one-time token more than once.

## Where they live

Any operation that (a) checks a limit or state and (b) mutates it, without holding a lock or using
an atomic/transactional update:

- "Spend one credit / use one invite / redeem one code."
- Balance transfers and withdrawals (double-spend).
- Quota and rate ceilings enforced with read-modify-write.
- One-time tokens: password resets, email confirmations, single-use links.
- "Apply once" actions: a discount, a vote, a follow, a claim.

## How to test

- Fire **N identical requests in parallel** at the exact same instant. The goal is to have
  several land inside the check-then-act window together.
- Use HTTP/2 **single-packet** delivery, or a tool that releases queued requests simultaneously,
  to shrink the timing jitter. Sequential requests won't reproduce it.
- Compare the outcome to the intended one: did more than the allowed number succeed?

## Proving it cleanly

- Establish the intended behavior first (positive control: one request, one effect).
- Then show the parallel burst producing the extra effect — the doubled credit, the second
  redemption, the balance that went below zero.
- Quantify: how many of N succeeded, and what the ceiling was supposed to be.

## Impact and reporting

Tie it to a concrete outcome — money, quota, or an authorization state that shouldn't be
reachable twice. Show the request, the parallel dispatch, and the before/after state with a
positive control. Note that these are inherently probabilistic: say how many attempts it took and
that the effect is repeatable.

Keep it non-destructive: test on your own account/resources, and don't hammer a shared system —
a handful of well-timed bursts, not a flood (which crosses into DoS and is usually out of scope).
