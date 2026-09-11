# Lab notes — Cross-Site Scripting (PortSwigger Web Security Academy)

Notes on the [XSS labs](https://portswigger.net/web-security/cross-site-scripting) — approach over
answers. Public practice labs; safe to write up. Pairs with
[XSS in SPAs](../methodology/xss-in-spas.md).

## Find the context first

XSS is context-dependent — the same input is safe in one place and executable in another. Reflect
a unique marker and see **where** it lands:

- **HTML body:** `<h1>MARKER</h1>` renders → try `<script>` or an event-handler tag
  (`<img src=x onerror=alert(1)>`).
- **HTML attribute:** break out of the attribute (`"><svg onload=...>`), or use an event handler
  if you can't break out.
- **JavaScript string:** break out of the string/quote (`'-alert(1)-'`, `</script>`), mind the
  surrounding syntax.
- **URL / href:** `javascript:` URLs, or a source that becomes an attribute value.

## Reflected / stored / DOM

- **Reflected:** payload in the request, echoed in the immediate response. Deliver via a crafted
  link.
- **Stored:** payload persists (a comment, a profile field) and fires for other users — higher
  impact.
- **DOM-based:** the sink is client-side JS (`innerHTML`, `location`, `eval`). Trace source→sink
  in the script; the server may never see the payload (`#` fragment).

## Filter and WAF evasion

- Tag/attribute the filter forgot; case variation; alternative events (`onpointerover`,
  `onanimationstart`); SVG/MathML contexts; HTML-encoding and double-encoding; breaking a
  blocklist with a less-common vector. Labs each isolate one gap.

## CSP and exploitation

- Read the CSP first — it decides which payloads work. Bypasses: an allowlisted CDN hosting a
  JSONP/callable endpoint, `strict-dynamic` gaps, dangling markup to exfiltrate without script.
- The impact story is what the script does in the victim's session: steal the session cookie/token,
  perform actions as them, or exfiltrate data — show that, not just `alert(1)`.

## Reporting

Give the injectable input, the context, the working payload, and it executing in a victim
context. Stored > reflected > DOM for severity. A framework's default escaping doing its job is a
refutation, not a finding.
