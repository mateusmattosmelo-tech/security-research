# Web Cache Poisoning & Host-Header Attacks

When a cache sits in front of an app, anything the app reflects but the cache ignores in its key
can be poisoned: you send a request with a malicious unkeyed input, the cache stores the response,
and every later visitor gets your version.

## The mechanic

1. **Find an unkeyed input that changes the response.** The cache key is usually method + host +
   path + query. Inputs *not* in the key but reflected in the response are the lever: `Host`,
   `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Forwarded-For`, other `X-Forwarded-*`, custom
   headers the app reads.
2. **Confirm it's cached.** Look at `Cache-Control`, `Age`, `X-Cache: HIT/MISS`, `CF-Cache-Status`.
   A response that goes from MISS to HIT with your injected value stuck in it is poisoning.
3. **Make it harmful.** Reflected value in a `<script src>`, a redirect `Location`, an absolute
   link, an open-redirect param, or a cached error page.

## Host-header specifics (even without a cache)

Apps that trust the `Host` (or `X-Forwarded-Host`) header build URLs from it:

- **Password-reset poisoning** — the reset link email uses the attacker's host; victim clicks,
  token leaks.
- **Open redirect / SSRF** via routing that trusts the header.
- **Cache-key confusion** when the app and the cache disagree on which host header matters.

## Testing safely

- Vary **one** header at a time and watch whether it reflects and whether it caches.
- Poison a **benign, unique** marker first (a canary querystring you control) to prove the
  mechanism before anything impactful — and pick a path/param unlikely to affect real users, or
  test on a value only you request.
- Cache poisoning affects *other users* by nature, so keep the payload harmless and the blast
  radius tiny; document that you avoided impacting real traffic.

## Cache deception (the inverse)

Trick the cache into storing a **private** page under a path it thinks is static:
`/(account)/profile/nonexistent.css`. If the app serves the profile but the cache keys on the
`.css` extension and stores it, the next visitor to that URL gets the victim's private data.

## Reporting

Show the request with the unkeyed input, the `MISS`→`HIT` transition proving it cached, and the
concrete harm (poisoned script/redirect, or the private data served to another request). Note the
cache headers that prove persistence. Rate-limit and pure cache-header findings are often out of
scope — check the policy.
