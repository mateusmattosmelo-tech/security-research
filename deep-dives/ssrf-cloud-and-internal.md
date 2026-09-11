# SSRF to Cloud Metadata & Internal Services — Deep Dive

A confirmed SSRF is a network position, not a payload. Its worth is what that position reaches. The
top prize on cloud is the **instance metadata service (IMDS)** — a link-local endpoint that hands
out the workload's credentials. This is the mechanic level, for authorized testing.

## The metadata endpoints

All live at `169.254.169.254` (link-local), each cloud with its own shape:

**AWS — IMDSv1 (no header, if still enabled):**
```
GET http://169.254.169.254/latest/meta-data/iam/security-credentials/
GET http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
```
returns `AccessKeyId`, `SecretAccessKey`, `Token` — temporary creds you can use against the AWS API
(scope depends on the role).

**AWS — IMDSv2 (token-bound; the mitigation):** requires a PUT to get a token first, then a header:
```
PUT  http://169.254.169.254/latest/api/token   -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"
GET  http://169.254.169.254/latest/meta-data/... -H "X-aws-ec2-metadata-token: <token>"
```
IMDSv2 defeats *most* SSRF because the SSRF usually can't send a custom request header or a PUT.
So it matters whether your SSRF primitive controls the method and headers — a full-request SSRF
(e.g. via a proxy param, gopher, or a redirect that preserves method) can still reach it; a
"fetch this URL with GET" primitive usually can't.

**GCP** — requires a header, which is itself a mitigation:
```
GET http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
    -H "Metadata-Flavor: Google"
```
Also `.../instance/attributes/`, and (older) the `?recursive=true&alt=json` and legacy `v1beta1`
paths that didn't require the header.

**Azure:**
```
GET http://169.254.169.254/metadata/instance?api-version=2021-02-01 -H "Metadata: true"
GET .../metadata/identity/oauth2/token?resource=https://management.azure.com/ -H "Metadata: true"
```

## Reaching it when the input is filtered

The target's fetcher and its allow/blocklist rarely parse URLs identically. Byte-level tricks:

- **Alternate IP encodings of 169.254.169.254 / 127.0.0.1:** decimal (`2852039166`), octal
  (`0251.0376.0251.0376`), hex (`0xA9FEA9FE`), mixed, zero-compressed (`127.1`), IPv6-mapped
  (`[::ffff:169.254.169.254]`), and `[::1]` for localhost.
- **Parser confusion:** `http://expected-host@169.254.169.254/`, `http://169.254.169.254#@expected`,
  `http://169.254.169.254\t`, embedded credentials, or a URL where the app's regex and the HTTP
  client disagree about the authority.
- **Redirect chaining:** allowlist checks the *first* URL; you point it at your host, which 302s to
  `169.254.169.254`. Only works if the fetcher follows redirects and re-checks nothing.
- **DNS rebinding:** a name you control resolves to a public IP at check-time (passes the
  allowlist) and to `169.254.169.254` at fetch-time (TTL 0). Defeats "resolve then compare"
  when resolution happens twice.

## Non-HTTP escalation: gopher & friends

If the fetcher honors other schemes, `gopher://` lets you write **arbitrary bytes to a TCP port** —
turning SSRF into interaction with internal line-protocols:

- **Redis** (`gopher://127.0.0.1:6379/_` + CRLF-encoded commands): `SET` a webshell into a known
  path, or rewrite config, or add a cron via the RDB-write trick.
- **Internal HTTP APIs** that trust network position (admin endpoints, unauthenticated dashboards).
- SMTP, memcached, and other text protocols similarly.

`file://` (local file read), `dict://`, and `ftp://` are worth trying against a permissive client.

## Blind SSRF

No reflection → prove with an OOB listener. The **DNS lookup alone** often confirms the fetch even
when egress is filtered (the resolver still runs). Then escalate: time-based internal port scanning
(open vs. closed vs. filtered by response timing), and error-message oracles.

## Testing discipline

Read only what proves impact; if you retrieve credentials, **mask them** and don't use them beyond
the least call that shows scope (a read-only `sts:GetCallerIdentity` equivalent), only if the
program allows. Keep internal sweeps tiny. Use your own OOB domain.

## Reporting

Show the request that triggers the fetch, the metadata/creds response (masked) or the OOB callback,
and the concrete reach — "these temporary credentials, scoped to role X, which grant Y." The
severity is the blast radius of that network position, not the SSRF itself.
