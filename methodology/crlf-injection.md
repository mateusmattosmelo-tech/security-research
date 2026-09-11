# CRLF / HTTP Header Injection

If user input reaches an HTTP response header (or a request the server builds) without stripping
carriage-return/line-feed (`\r\n`), an attacker can inject new headers or split the message. It's
the header-level cousin of injection: the delimiter is `%0d%0a`.

## Where it reaches headers

- **Redirects:** a `Location` built from a user-controlled parameter.
- **Set-Cookie:** a cookie value or name reflected from input.
- **Custom/reflected headers:** anything the app copies from input into a response header, or into
  a request it makes downstream (proxying, logging).

## What injection buys you

- **Header injection:** add `Set-Cookie` (session fixation), CORS headers, or security-header
  overrides.
- **Response splitting:** inject `\r\n\r\n` plus a full second response body → cache poisoning or
  reflected content the browser renders (can escalate to XSS if the injected body is HTML and the
  cache stores it).
- **Log injection / smuggling** on the downstream side where the server builds a request from
  input.

## Testing

- Put `%0d%0a` (and `%0a`, `%23%0d%0a`, double-encoded `%250d%250a`, unicode variants) into
  parameters that end up in a header. Watch the raw response headers for your injected line.
- A safe first probe injects a benign marker header (`X-Canary: 1`) and checks it appears in the
  response — proof of the primitive before anything impactful.

## Modern reality

Most mature HTTP stacks strip CR/LF from header values, so this is often refuted — but custom
frameworks, older servers, and hand-built downstream requests still fall to it. In HTTP/2, header
values can't contain raw CRLF, but an edge that **downgrades** H2→H1 may reintroduce the split
(overlaps with request smuggling).

## Reporting

Show the parameter, the encoded payload, and the raw response with your injected header/line
present. Escalate to the concrete impact (a planted cookie, a split response the cache served) and
report that, not just header reflection. Bare reflection with the stack stripping CRLF is a
refutation.
