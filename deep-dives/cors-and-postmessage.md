# Cross-Origin Data Theft: CORS & postMessage — Deep Dive

Two different mechanisms, same goal: read data across an origin boundary that the browser is
supposed to enforce. CORS misconfig lets a malicious site read authenticated API responses;
postMessage flaws let a malicious frame/opener exchange data with the target window. Authorized
testing.

## CORS — the exploitable misconfigurations

The same-origin policy blocks cross-origin reads *unless* the server opts in with
`Access-Control-Allow-Origin` (ACAO). The dangerous configs:

1. **Reflected origin + credentials:** server echoes the request `Origin` into ACAO **and** sets
   `Access-Control-Allow-Credentials: true`. Any site reads the victim's authenticated responses:
   ```
   Origin: https://evil.com  ->  ACAO: https://evil.com  +  ACAC: true
   ```
   PoC: `fetch('https://target/api/me',{credentials:'include'}).then(r=>r.text()).then(exfil)`.
2. **Weak allowlist regex:** matches `target.com.evil.com`, `eviltarget.com`, or treats a substring
   as the whole host. Register/host the matching origin.
3. **`null` origin accepted + credentials:** `ACAO: null` is granted, and `null` is reachable from a
   sandboxed iframe (`<iframe sandbox="allow-scripts" srcdoc="...">`) or a `data:`/redirect origin —
   so the attacker sends `Origin: null` and reads the response.
4. **Trusting any subdomain** (`*.target.com`) when one subdomain has an XSS/takeover → pivot.
5. **`ACAO: *`** — note this **cannot** be combined with credentials by browsers, so it only leaks
   data that needs no auth; still a finding if that data is sensitive.

Test with `tools/cors_probe.py`; confirm with a real cross-origin `fetch` that returns the victim's
data.

## postMessage — the exploitable patterns

`window.postMessage` sends data between windows/frames across origins. Two sides break:

### Vulnerable receiver
A `message` handler that doesn't validate `event.origin` and sinks the data:
```js
window.addEventListener('message', e => {
  document.getElementById('x').innerHTML = e.data;   // DOM XSS from any window
});
```
- **No origin check + dangerous sink** (`innerHTML`, `eval`, `location`, a JS bridge) → XSS/redirect
  from any page that can get a handle to this window (open it as a popup, or if it's framed).
- **No origin check + trusted action** (the message drives an authenticated action or reveals data)
  → CSRF/data theft.

### Leaky sender
Code that `postMessage`s sensitive data with `targetOrigin: '*'`:
```js
otherWindow.postMessage(secretToken, '*');   // any origin in that window receives it
```
An attacker who controls (or frames/opens) the receiving window reads the token. `'*'` targetOrigin
on anything sensitive is a leak.

## Exploiting postMessage in practice

- **Framing:** if the target frames the attacker (or vice-versa), you have a window handle. Embed the
  target in your page (if `X-Frame-Options`/`frame-ancestors` allow) or open it as a popup you keep a
  reference to, then `postMessage` to it / listen for its messages.
- **Origin-check bypasses:** a receiver that checks `event.origin.indexOf('target.com') > -1` →
  `https://target.com.evil.com`; `endsWith('target.com')` → `eviltarget.com`; a check against
  `event.source` instead of `event.origin`.

## Method

- CORS: enumerate API endpoints returning sensitive data; probe ACAO/ACAC reflection and the
  `null`/regex variants; confirm with a cross-origin credentialed `fetch`.
- postMessage: grep the bundle for `addEventListener('message'` and `postMessage(`; trace receiver
  origin checks and sinks, and sender `targetOrigin` values; build a PoC page that frames/opens the
  target and exchanges the message.

## Reporting

- CORS: show the request Origin, the reflected ACAO+ACAC, and a working cross-origin PoC returning
  the victim's data. Name the exact misconfig (reflection, null, regex).
- postMessage: show the handler (`file:line` in the bundle), the missing/weak origin check, the
  sink or the leaked secret, and a PoC page demonstrating theft/execution against your own session.
