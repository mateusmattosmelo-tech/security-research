# Lab notes — Authentication (PortSwigger Web Security Academy)

Notes on the [authentication labs](https://portswigger.net/web-security/authentication) —
approach over answers. Public practice labs; safe to write up.

## Credential-based weaknesses

- **Username enumeration:** a different error, a different response time, or a different status for
  a valid vs. invalid username lets you build a user list. (In real programs this is often
  out of scope — check the policy before leaning on it.)
- **Broken brute-force protection:** lockout that only counts on invalid *passwords*, resets on a
  valid username, is IP-based (rotate), or is bypassable by varying a header. Labs teach the
  logic gap; real programs usually exclude rate-limiting.

## Multi-factor (MFA) flaws

- **MFA broken logic:** the second factor is verified, but the session is already authenticated
  before it — skip straight to the post-login page.
- **Brute-forceable OTP:** no attempt limit on the 2FA code; or the code is tied to a value you
  control.
- **2FA bypass via response tampering** or verifying the code for a *different* user than the one
  you logged in as.

## "Stay logged in" / token flaws

- A remember-me cookie that's a predictable or weakly-signed derivation of the username/password
  (e.g. `base64(user:md5(password))`) — forge it for another user.

## Password reset

- **Reset token predictability / leakage** (in the response, in a URL, or reusable).
- **Host-header reset poisoning:** the reset link is built from the `Host`/`X-Forwarded-Host`
  header; set it to your server, trigger a reset for the victim, capture the token they'd click.
- **Reset without the token:** the reset endpoint trusts a `username` field over the token.

## The through-line

Authentication breaks when a step that proves identity is optional, guessable, or bound to the
wrong thing. Map the full flow (login → MFA → session → reset) and test each transition
independently. Related: [OAuth/OIDC](../methodology/oauth-oidc-testing.md),
[JWT verification](../methodology/auditing-jwt-verification.md).
