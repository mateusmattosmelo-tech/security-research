# HTTP Parameter Pollution — Deep Dive

Send the same parameter twice and different components of the stack pick different values. That
disagreement — between a WAF and the app, a proxy and the origin, or two frameworks — bypasses
filters, defeats validation, and tampers with server-built requests. Small, but a reliable
bypass primitive. Authorized testing.

## The root: no standard for duplicate params

`?role=user&role=admin` is legal, and each layer resolves it differently:

| Stack | `?a=1&a=2` yields |
|---|---|
| PHP / Apache | last (`2`) |
| ASP.NET / IIS | both, comma-joined (`1,2`) |
| Express / Node | array `[1,2]` |
| Python (Flask/Django) | first (`1`) |
| Go net/http | first (`Get`), or all via `Query()[...]` |
| JSP / Tomcat | first (`1`) |

So a **WAF** that inspects the first value and an **app** that reads the last (or vice-versa) see
different inputs.

## What it buys you

- **WAF / validation bypass:** put a benign value where the filter looks and the payload where the
  app reads. `?q=safe&q=' OR 1=1--` — WAF sees `safe`, PHP app uses the injection. Same for XSS,
  path, command payloads split across duplicates.
- **Authorization / logic tampering:** duplicate a field the app trusts — `role=user&role=admin`,
  `amount=100&amount=1`, `userId=me&userId=victim` — where the consuming layer picks the attacker's
  copy.
- **Server-side HPP:** the app builds a downstream request/URL from your input and you inject an
  extra param into *that* — e.g. a value that becomes `...&api_key=...&yourparam` lets you append
  `&admin=true` to the internal call, or split a redirect/OAuth `redirect_uri`.
- **Array/type confusion:** where a framework turns `a[]=x&a[]=y` or `a=x&a=y` into an array, code
  expecting a string mishandles it (feeds into NoSQL operator injection, mass assignment, or
  crashes → info leak).

## Method

1. For a parameter with server-side effect (a filter, an authz field, a value used downstream),
   send it **twice** with different values and observe which the app honored (response reflects it,
   or the effect changes).
2. Map the precedence: does the app take first or last? Then place your payload in the honored slot
   and the decoy in the inspected slot.
3. Test both query-string and body (`application/x-www-form-urlencoded`) pollution, and mixed
   (query vs body) — the app may prefer one source over the other.

## Combine it

HPP is a *bypass amplifier* — pair it with the class you're actually exploiting: SQLi/XSS past a
WAF, an authz field the app reads from the "wrong" copy, or splitting an OAuth `redirect_uri` /
open-redirect target.

## Reporting

Show the polluted request, which value each relevant layer used (the WAF/proxy vs. the app), and the
concrete bypass/tamper it achieved. Name the precedence mismatch. Fix: canonicalize parameters
(reject or explicitly define duplicate handling) consistently across every layer, and validate on
the same value the app consumes.
