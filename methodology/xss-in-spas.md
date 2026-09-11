# XSS in Single-Page Apps

Modern frameworks (React, Vue, Angular, Svelte) escape output by default, so classic reflected
XSS is rarer — but the sinks moved. In an SPA, XSS lives where the framework's escaping is
bypassed, where the app sinks data into the DOM manually, and in the client-side routing/state.

## Where it hides

- **Dangerous escape hatches:** `dangerouslySetInnerHTML` (React), `v-html` (Vue),
  `[innerHTML]` / bypassing `DomSanitizer` (Angular), `{@html}` (Svelte). Grep the bundle for
  these and trace what flows in.
- **DOM XSS sinks:** `innerHTML`, `outerHTML`, `document.write`, `eval`, `Function`,
  `setTimeout(string)`, `location`/`href` assignment, `insertAdjacentHTML`, jQuery `.html()`.
- **Sources:** `location.hash`/`search`, `postMessage` data, `window.name`, URL params fed into
  client routing, server JSON reflected without encoding.
- **`javascript:` URLs** in href/src bound from user data; `src`/`srcdoc` on iframes.
- **Sanitizer gaps:** an allowlist that misses an attribute or a mutation-XSS (mXSS) vector; an
  outdated DOMPurify.
- **Client-side template / expression injection** where a framework evaluates a string.

## How to work it

1. Read the bundle (see `js_endpoints.py` for pulling it apart) and grep for the sinks above.
2. Trace each sink backward to a source the attacker controls (URL, postMessage, stored data).
3. Try a marker payload appropriate to the context (HTML, attribute, JS string, URL) and confirm
   execution in a real browser, not just reflection.

## postMessage & CSP

- **postMessage:** a handler that doesn't check `event.origin`, or writes the message into a sink,
  is XSS/data-theft from any window. Check both the sender's `targetOrigin` and the receiver's
  origin validation.
- **CSP:** a strong `script-src` (nonce/strict-dynamic, no `unsafe-inline`, no `unsafe-eval`)
  blunts many payloads. Read the CSP first — it tells you which vectors are even worth trying and
  is itself part of the impact story.

## Reporting

Show the source, the sink (`file:line` in the bundle if you have it), the payload, and it
executing in a victim's session. Stored > reflected > DOM for impact; tie it to what the script
can do with the victim's session (token theft, actions on their behalf). A framework's default
escaping working correctly is a refutation, not a finding.
