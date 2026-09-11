# HTTP Request Smuggling — Deep Dive

Smuggling exploits a front-end and back-end disagreeing on **message length** so that bytes you
send are interpreted by the back-end as the start of the *next* connection's request. This is the
byte-level layout of each variant and how to detect them without harming other users. Authorized
testing; prefer timing-based detection and self-contained proofs.

## Why it happens

HTTP/1.1 keeps connections alive and pipelines requests. Two ways to state body length —
`Content-Length` (CL) and `Transfer-Encoding: chunked` (TE) — and if the two servers pick
differently, the boundary between requests desyncs.

## CL.TE (front-end uses CL, back-end uses TE)

Front-end reads `Content-Length: 6`, forwards all 6 bytes. Back-end reads chunked, sees the `0`
terminator, and treats the rest as a new request:

```
POST / HTTP/1.1
Host: target
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Front-end forwards the whole thing (CL=6 covers `0\r\n\r\nG`). Back-end processes `0\r\n\r\n` as a
complete zero-length body, leaving `G` buffered — it prefixes the next request (`G` + someone's
`ET /... ` → `GET /...`).

## TE.CL (front-end uses TE, back-end uses CL)

Reverse. Front-end chunk-parses; back-end honors `Content-Length`:

```
POST / HTTP/1.1
Host: target
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Length: 15
...
0

```

Front-end sends the full chunked body; back-end reads only `Content-Length: 4` bytes (`5c\r\n`),
leaving the smuggled `GPOST ...` as the next request. (Exact byte counts must be computed for the
target — off-by-one kills it.)

## TE.TE (both do TE, one is tricked)

Both support TE, so **obfuscate** the header so only one honors it:

```
Transfer-Encoding: chunked
Transfer-Encoding: x
```
or `Transfer-Encoding : chunked` (space before colon), `Transfer-Encoding:\tchunked`, a smuggled
newline, duplicate headers, casing. Whichever server ignores the obfuscated TE falls back to CL →
you've created CL.TE or TE.CL.

## HTTP/2 desync (the modern surface)

At the edge, H2 is often downgraded to H1 for the back-end. H2 carries length implicitly, so if the
front-end doesn't sanitize on rewrite:

- **H2.CL:** you declare a `content-length` in the H2 request that the back-end (now H1) honors,
  desyncing.
- **H2.TE:** inject a `transfer-encoding: chunked` H2 header that survives downgrade.
- **CRLF injection in H2 header values/names:** H2 allows bytes H1 doesn't; a `\r\n` smuggled into
  a header value becomes real header/request separators after downgrade → request splitting.

## Detecting safely (do this first)

Timing-based, self-contained, no other users harmed:

- Send a CL.TE probe whose back-end interpretation leaves it **waiting** for bytes that never
  arrive → the response is delayed by the socket timeout. A normal request returns fast.
  ```
  POST / HTTP/1.1
  Transfer-Encoding: chunked
  Content-Length: 4

  1
  A
  X
  ```
  If the back-end is TE and waits for the next chunk → delay = CL.TE likely.
- Confirm with a self-capture where *your own* second request retrieves the smuggled prefix, rather
  than experiments that catch real users' requests.

## Impact

- **Capture another user's request** (headers, cookies, body) by smuggling a prefix that their
  request completes.
- **Response queue poisoning:** desync shifts the response↔request pairing so users get others'
  responses — persistent until the connection resets.
- **Bypass front-end controls** (WAF/auth at the edge) by hiding the real request from it.
- **Chain to web cache poisoning** for persistence and scale.

## Discipline

This class disrupts shared infrastructure — that's the risk. Prefer timing detection; keep tests
minimal; do not poison shared caches or harvest real users' data; stop at a self-contained PoC.
State in the report what you did to avoid impacting others. Name the variant and the two components
that disagree.
