# Attack-Surface Mapping

Before testing anything, you need the full list of what's actually reachable. Most of the
interesting exposure isn't the main app — it's the forgotten dev instance, the internal tool
that leaked onto the public internet, the preview environment that never got locked down.
This is how I build that list, entirely from passive and read-only signals.

## 1. Enumerate names (passive)

- **Certificate Transparency** (crt.sh and friends): every TLS cert a company issues is logged,
  so CT is a near-complete list of hostnames — including the ones nobody links to.
- Passive DNS, `subfinder`/`amass`, and the target's own open-source repos (Terraform, k8s
  manifests, CI configs) round it out.

## 2. Separate reachable from internal (DNS only)

Resolve each name and read the answer before sending any HTTP:

- **RFC1918 addresses** (`10.x`, `172.16–31.x`, `192.168.x`) → internal, not reachable from
  the internet. Note them for the map, but don't probe.
- **`*.internal.*` naming** is a strong hint the operator considers it private.
- **CNAMEs to a SaaS** (managed Grafana, a status-page vendor, an object store) → that surface
  belongs to the vendor, not your target; auth and bugs live on their side.
- **Public A records on the target's own ranges** → these are the candidates worth a look.

## 3. Check exposure without exploiting

For each reachable candidate, a single unauthenticated GET tells you most of what you need:

- **What is it?** `Server` header, redirect chain, page title, favicon hash. A `gunicorn`
  redirecting to `/login/` with a recognizable title is a fingerprint.
- **Is it gated?** Does it sit behind an access proxy (a Zero-Trust login), or is it a direct
  origin? An internal tool on a direct origin while the rest of the estate is behind an access
  proxy is itself a finding — inconsistent surface.
- **What version?** Many apps expose `/version`, `/health`, a `version_info.json`, or a build
  hash in static asset names — all readable unauthenticated. Version tells you which known
  issues could apply.
- **Is access actually enforced?** Confirm the data views redirect to login and the API returns
  401. Check whether self-registration is open (a GET of the register form — never submit it).

## 4. Where to stop

Exposure recon ends at "this exists, this is its version, this is how it's gated." The moment a
check would require guessing a credential, forging a session, or triggering a known exploit,
you've crossed from mapping into exploitation — and that needs an in-scope, authorized target,
the account/headers the program requires, and a good-faith, non-destructive approach. Write the
candidate down, then decide deliberately how far the program's rules let you take it.

## Severity honesty

An exposed internal tool that still enforces auth is usually **low/informational** on its own —
a surface-reduction recommendation, not a breach. It becomes high-impact only when it also
allows unauthorized access (open registration, an unrestricted OAuth, anonymous data, a known
unauth CVE on the running version). Report the exposure for what it is; don't inflate it.
