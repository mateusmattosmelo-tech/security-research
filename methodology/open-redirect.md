# Open Redirect

An open redirect is an endpoint that sends the browser to a URL taken from a parameter without
validating it. On its own it's usually low severity, but it's a reliable **building block** —
it steals OAuth codes, defeats redirect_uri allowlists, and lends credibility to phishing from a
legitimate domain.

## Find the redirectors

- Parameters named `redirect`, `url`, `next`, `return`, `returnUrl`, `returnTo`, `dest`,
  `destination`, `continue`, `r`, `u`, `goto`, `callback`, `back`, `success_url`.
- Login/logout flows, SSO callbacks, "you must sign in, then we'll send you back" flows, email
  link trackers, and link shorteners.

## Test it

Point the parameter at an external host and see where you land (watch the `Location` header):

- Plain: `?next=https://attacker.example.com`
- Protocol-relative: `?next=//attacker.example.com`
- Backslash / mixed: `?next=/\attacker.example.com`, `https:/\attacker.example.com`
- Allowlist bypasses when it checks for a prefix/substring:
  `?next=https://trusted.com.attacker.example.com`,
  `?next=https://attacker.example.com/trusted.com`,
  `?next=https://attacker.example.com#trusted.com`,
  userinfo: `?next=https://trusted.com@attacker.example.com`
- `javascript:` scheme where the value becomes an `href` (that's XSS, not just redirect).

## Where it matters most

- **OAuth/OIDC:** an open redirect on a page that's an allowed `redirect_uri` (or shares its
  origin) can exfiltrate the authorization `code`/token — turning a low bug into account takeover.
  This is the escalation to always check (see [OAuth/OIDC](oauth-oidc-testing.md)).
- **Chained SSRF / filter bypass:** an allowlisted host that open-redirects lets an SSRF reach the
  real internal target.

## Reporting

Show the request and the `Location` (or landing) pointing at your external host. State the
severity honestly: standalone it's usually low/informational, but if you can chain it to token
theft or SSRF, lead with that chain and demonstrate it. A redirect confined to same-origin paths
is not a finding.
