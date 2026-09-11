# Race Conditions — Deep Dive

A race condition is a **collision inside a time window**: between the moment the server checks a
condition and the moment it acts on it, a second request slips in and both act on the same
pre-check state. The result is doing-once-what-should-be-once. This covers the sub-states, the
single-packet attack that makes them reliable, and detection. Authorized testing on your own
resources; keep bursts small.

## The window (TOCTOU)

```
request 1: read balance (100) --------------- write balance (100 - 100 = 0)
request 2:        read balance (100) ------------------- write balance (100 - 100 = 0)
```

Two "withdraw 100" reads see 100 before either writes → both succeed → 200 withdrawn from 100.
Any **check-then-act without a lock or atomic update** is vulnerable: `if credits>0 {credits--}`,
"redeem once," "one vote," quota ceilings enforced with read-modify-write.

## Why sequential testing fails — and the single-packet attack

The window is often sub-millisecond, and network **jitter** between requests is larger than the
window, so sequential (even rapid) requests miss it. You must make requests arrive *together*:

- **HTTP/1.1 — last-byte sync:** send N requests but withhold the final byte of each; then release
  all final bytes at once so they complete simultaneously (Burp's "last-byte sync" / Turbo Intruder
  `gate`).
- **HTTP/2 — single-packet attack** (the reliable modern technique, PortSwigger): pack the last
  frames of ~20-30 requests into **one TCP packet**. They hit the server with essentially zero
  jitter, landing inside the window together. This turns flaky races into consistent ones.

The idea: eliminate network jitter so the only variance left is server-side scheduling — which is
inside the window you're targeting.

## Sub-states worth testing (beyond limit-overrun)

- **Limit overrun:** spend/redeem/withdraw past the ceiling (the balance/coupon/quota case above).
- **Multi-use of a single-use token:** password-reset token, gift card, invite — used twice in
  parallel before consumption commits.
- **State-machine desync:** fire two transitions at once (approve+cancel, submit+edit) to reach a
  state the machine forbids.
- **Time-of-check on uniqueness:** register two accounts with the same email/username in parallel
  before the uniqueness check commits → duplicate/confused accounts.
- **"Partial construction" windows:** an object that briefly belongs to no one / has default
  permissions before ownership is set — act in that window.
- **Rate-limit / anti-automation bypass** via the same collision (multiple attempts counted as one).

## Detecting and confirming

1. **Baseline (positive control):** one request → one effect (spend once → −1).
2. **Burst:** N parallel via single-packet / last-byte sync.
3. **Measure the over-effect:** how many of N succeeded vs. the ceiling; the balance below zero; the
   token accepted twice.
4. Races are **probabilistic** — repeat to show it's reproducible, and report the success rate and N.

## Discipline

Test on **your own** account/resources. Keep N small (tens, not thousands — a burst, not a flood;
a flood is DoS and out of scope). Don't leave the system in a broken state; reverse test effects
where possible.

## Reporting

Show the positive control, the parallel dispatch (name the technique — single-packet attack), and
the concrete over-effect (money/quota/duplicate/forbidden state) with the numbers (N sent, M
succeeded, ceiling). Tie it to impact. Fix: atomic operations / row locks / unique constraints /
idempotency keys — say which.
