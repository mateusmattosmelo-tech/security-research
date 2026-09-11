# CSRF & Clickjacking

Both abuse the fact that a browser attaches a victim's ambient authority (cookies, session) to
requests the victim didn't intend. CSRF forges the request; clickjacking tricks the victim into
making it themselves.

## CSRF

A state-changing request that relies only on the session cookie, with no unpredictable token, can
be triggered from an attacker's page.

**Test:**
- Take a state-changing request (change email, transfer, add member). Does it require a CSRF token
  / custom header, or just the cookie?
- If there's a token, is it actually validated? Try: removing it, using another user's token,
  using an empty token, swapping `POST`→`GET`, changing the content-type to one that doesn't
  require preflight (`text/plain`, `application/x-www-form-urlencoded`).
- **SameSite:** modern cookies default to `SameSite=Lax`, which blocks cross-site `POST` CSRF for
  those cookies — but check: is the cookie `SameSite=None`? Is the dangerous action reachable via
  a top-level `GET` (which Lax still allows)? Is there a token *and* the cookie relies on it?

**Impact:** the forged action performed as the victim — account takeover if it changes email/
password, etc. Show a working HTML PoC that fires the request from a foreign origin.

## Clickjacking

If a sensitive page can be framed, an attacker overlays it under a decoy so the victim's click
lands on a real (invisible) button — "confirm", "delete", "authorize".

**Test:**
- Can the page be framed? Check for `X-Frame-Options: DENY/SAMEORIGIN` **and** a CSP
  `frame-ancestors` directive (CSP supersedes XFO). Missing both = frameable.
- Is there a sensitive one-click action on a frameable page (OAuth consent, delete, transfer)?
  Frameable alone is usually low; frameable + a damaging single click is the finding.

**PoC:** an HTML page that iframes the target, made transparent and positioned so the victim's
click hits the sensitive control.

## Reporting

- CSRF: the request, proof the token is absent/unvalidated, and a working cross-origin PoC that
  performs the action as the victim. Note the SameSite state — it decides exploitability.
- Clickjacking: the missing `frame-ancestors`/XFO, plus a framing PoC targeting a specific
  damaging action (not just "the site can be framed"). Bare missing-header reports are often
  out of scope.
