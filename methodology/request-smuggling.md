# HTTP Request Smuggling

When a front-end (proxy/CDN/load balancer) and a back-end disagree about where one request ends
and the next begins, an attacker can smuggle a partial request that prefixes the *next* user's
request — poisoning their response, capturing their data, or bypassing front-end controls.

## The disagreement

Classic desync comes from `Content-Length` vs `Transfer-Encoding: chunked`:

- **CL.TE:** front-end uses `Content-Length`, back-end uses `Transfer-Encoding`.
- **TE.CL:** the reverse.
- **TE.TE:** both support TE but one can be tricked into ignoring it via an obfuscated header
  (`Transfer-Encoding : chunked`, duplicate TE, odd casing/whitespace).

Modern variants come from **HTTP/2 → HTTP/1.1 downgrade** at the edge: H2 request fields
(method, path, headers) that aren't validated get reinterpreted as part of an H1 request
(H2.CL, H2.TE, CRLF injection in H2 header values).

## Detecting it safely

- **Timing probes** are the safe first step: a crafted request that, if a desync exists, makes the
  back-end wait for bytes that never come → a measurable delay. This detects without poisoning
  another user.
- Confirm with a **self-contained** test where possible (your own follow-up request captures the
  smuggled prefix), rather than experiments that could hit real users.

## Impact

- **Capture another user's request** (their headers, cookies, body) by smuggling a prefix that
  makes their request append to yours.
- **Response queue poisoning** — users receive the wrong responses.
- **Bypass front-end security controls** (WAF, auth at the edge) by hiding a request from the
  front-end.
- Chain with **cache poisoning** for persistence.

## Testing discipline

This class can disrupt real traffic — that's why it's easy to get wrong. Prefer timing-based
detection, keep tests minimal, avoid poisoning shared caches or capturing real users' data, and
stop at proof-of-concept. Many programs want a careful, self-contained demonstration and dislike
anything that could affect other users — read the policy.

## Reporting

Show the desync primitive (the exact headers), the detection (timing or self-capture), and the
concrete impact demonstrated against your own follow-up request. Name the variant (CL.TE / TE.CL /
H2.CL …) and the two components that disagree. Emphasize what you did to avoid impacting others.
