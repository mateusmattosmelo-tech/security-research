# XS-Leaks (Cross-Site Leaks) — Deep Dive

XS-Leaks infer small pieces of a victim's cross-origin state by observing **side effects** the same-
origin policy doesn't hide: timing, error vs. success, frame counts, cache state, resource sizes.
Each leak is one bit ("is the victim an admin?", "does this search return results?", "is this the
logged-in user?"), and bits compound. Advanced but real; authorized testing.

## Why they work

SOP stops you *reading* a cross-origin response, but many observable behaviors depend on it:
whether a request errored, how long it took, whether it was cacheable, whether a page created
frames, whether an image loaded. An attacker page triggers a cross-origin request (with the
victim's cookies) and measures one of these oracles.

## The oracle families

- **Status/error oracles:** load the target URL as a `<script>`/`<img>`/`<link>`/`fetch(no-cors)`
  and use `onload`/`onerror` — success vs. 404/403 flips the event. Reveals existence/authorization
  ("does `/admin` return 200 for this victim?").
- **Timing oracles:** measure response time (a search that matches is slower; a heavy authorized
  page vs. a redirect). `performance` API, or event timing.
- **Frame-counting:** `window.frames.length` of a cross-origin window you opened/framed reveals how
  many iframes the page rendered — which can encode state (0 results vs N).
- **Cache probing:** request a resource, then time whether a subsequent load is cached — reveals the
  victim visited/loaded it.
- **`postMessage` broadcasts:** a target that `postMessage`s state to `*` leaks it to your window.
- **COOP/COEP & `window.opener`:** whether `window.opener` is nulled, or a popup's properties,
  leaks navigation/cross-origin-isolation state.
- **Content-length / range** and media-error oracles: response size or decode success as the bit.
- **CSP violation reports** and `error` events as oracles.
- **Cache-partition / storage / quota** side channels.

## Building an attack

1. Find a target endpoint whose response **differs by victim state** (admin vs not, has-item vs
   not, search-hit vs miss).
2. Pick an oracle that reflects that difference (status via onload/onerror, timing, frame count).
3. From an attacker page, trigger it with the victim's ambient cookies and read the oracle.
4. Repeat to extract multiple bits (binary-search a value, enumerate a set).

Example: `<img src="https://target/api/orders?q=SECRET" onerror=leak(0) onload=leak(1)>` — if the
authorized+matching response loads as an image-ish 200 and the miss 404s, each query is a bit about
the victim's data.

## Defenses (what makes it a refutation)

Modern headers close most XS-Leaks — note their presence:
- **`Cross-Origin-Opener-Policy` (COOP)** — severs `window.opener`, kills frame/window oracles.
- **`Cross-Origin-Resource-Policy` (CORP)** & **`Cross-Origin-Embedder-Policy` (COEP)** — block
  cross-origin embedding.
- **`SameSite` cookies** (Lax/Strict) — the request won't carry the victim's session cross-site, so
  the oracle reflects an anonymous response (no leak). This is the big one.
- **`X-Frame-Options`/`frame-ancestors`** — blocks framing-based oracles.
- **`Vary`/cache partitioning**, unpredictable responses.

If the target sets SameSite cookies + COOP/CORP, most of these don't apply — write it up as a
refutation.

## Testing discipline & reporting

XS-Leaks are subtle and probabilistic — prove reliably (repeat, show the oracle flips with the
victim's state, using your own victim account). Report the specific oracle, the state it leaks, a
working PoC page, and the concrete inference ("an attacker page determines whether the logged-in
victim is an admin / has ordered X"). Note which cross-origin-isolation headers are missing that
would close it.
