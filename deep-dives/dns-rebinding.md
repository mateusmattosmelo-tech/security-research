# DNS Rebinding — Deep Dive

DNS rebinding turns a victim's browser into a proxy onto their private network. The attacker's
domain first resolves to a public IP (to pass same-origin and load the script), then "rebinds" to
an internal IP (`127.0.0.1`, `192.168.x`, a router, an internal service) — and because the *host*
name hasn't changed, the browser treats requests to the internal IP as same-origin. Authorized
testing (your own network/services, or a program that includes this).

## Why it defeats SOP

Same-origin is keyed on **(scheme, host, port)** — the *hostname*, not the resolved IP. If
`attacker.com` resolves to `1.2.3.4` when the page loads, then to `127.0.0.1` on the next request,
the browser still thinks it's talking to `attacker.com` (same origin) — so the attacker's JS can
read the response from `127.0.0.1`. It's a way to reach services that trust "localhost / internal
network" without any CORS.

## The mechanics

1. Attacker controls a domain with a DNS server that answers with a **very low TTL** (0–1s).
2. Victim loads `http://attacker.com/` → resolves to the attacker's **public** server → serves the
   rebinding JS.
3. The JS loops requesting `http://attacker.com:<port>/...`. The attacker's DNS now answers with the
   **internal** target IP (rebind). The browser, cache expired, re-resolves to the internal IP.
4. JS reads the internal service's responses (same-origin) and exfiltrates them.

Reliability tricks: two A records (public + private) so the browser fails over to the internal one
when the public is dropped/firewalled; forcing cache expiry; targeting services on known ports.

## What it reaches

- **Services that bind to `127.0.0.1`/`0.0.0.0` with no auth**, trusting the network position:
  local admin panels, dev servers, databases with HTTP interfaces, IoT/router admin, Kubernetes
  kubelet, cloud agent endpoints, Electron/desktop-app local servers, and even **cloud metadata**
  from a browser on a cloud host.
- Anything whose only defense is "only reachable from localhost / the LAN."

## The defenses (and thus what's a refutation)

A service is safe from rebinding if it does any of:
- **Validates the `Host` header** against an allowlist (rebinding keeps the attacker host in `Host`,
  so a strict check rejects it) — the primary defense.
- Requires **authentication** / a non-guessable token, not just network position.
- Uses **HTTPS** with a cert the attacker host can't satisfy.
- **DNS-rebinding protection** at the resolver (rejecting public names that resolve to private IPs).

Check the target's `Host` validation first — a service that echoes/acts regardless of `Host` is the
candidate.

## Testing

Stand up a rebinding setup you control (a low-TTL DNS + the loader page) — public tooling exists
(e.g. rebinding services/frameworks). Point it at **your own** internal service and show the browser
reading its response cross-context. Confirm the `Host` header the internal service receives (it'll
be your attacker domain — proving the SOP bypass, and testing whether the service checks it).

## Reporting

Show the rebinding setup, the internal service reached, and the data read from it via the victim's
browser — plus the `Host` header the service accepted. Name the missing defense (no `Host`
validation / auth). Impact = whatever the internal service exposes to "the local network." Keep it
to services/networks you're authorized to test.
