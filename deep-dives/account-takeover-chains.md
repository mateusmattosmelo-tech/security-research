# Account Takeover Chains — Deep Dive

Account takeover (ATO) is rarely one bug. It's usually a chain: a "low" issue that's worthless
alone becomes critical when it feeds the next step. Thinking in chains is what separates a $100
report from a $5,000 one. This maps the common chains and the pivot points. Authorized testing,
your own accounts as victim.

## The pivots that turn low → ATO

### Password reset poisoning (Host header → token capture)
The reset email link is built from a request header the app trusts:
```
POST /forgot-password    Host: attacker.com        (or X-Forwarded-Host: attacker.com)
```
The victim receives a link to `attacker.com/reset?token=...`; if they click, the token hits your
server. Chain: header injection (low) + a victim who clicks (or an email-preview fetcher that
auto-visits) → full ATO. Amplify with a `dangling-markup`/side-channel if no click.

### Open redirect / XSS on an OAuth client → code/token theft
An open redirect or XSS on a page that is (or shares origin with) an OAuth `redirect_uri` exfiltrates
the authorization `code`/token → attacker exchanges it → ATO. This is why an open redirect on an
auth-adjacent host isn't "informational." (See [OAuth attacks](oauth-attacks.md).)

### IDOR on email/phone change → ATO
An IDOR or missing-authz on "update email" (or a mass-assignment `email`/`ownerId` field) lets you
set the victim's email to yours, then reset the password. Read-IDOR to leak the victim's id +
write-IDOR to change their recovery = takeover.

### Response manipulation on MFA / reset
The MFA-verify or reset endpoint returns `{"success":false}` but the client gates on it —
flip it, or the endpoint verifies the code for the wrong user, or the 2FA step is skippable because
the session is already authenticated before it.

### Predictable / leaked reset token
Token is sequential, time-seeded, reused, returned in a response body, or reflected — derive/replay
it. UUIDv1 reset tokens are time+MAC predictable within a window.

### Pre-account / account linking
"Login with Google" that links to an existing local account **by email without verification** →
register locally with the victim's email (unverified), then OAuth-login as them, or vice-versa.
`state`-less OAuth enables login-CSRF account linking.

### JWT / session forging
`alg:none`, algorithm confusion, weak HMAC secret, or a session id that's a signed-but-forgeable
value → mint the victim's session directly. (See [JWT attacks](jwt-attacks.md).)

### Cache poisoning → session/CSRF-token theft, or serving your script
Poison a cached response with your content or capture another user's response containing their
tokens (see [request smuggling](request-smuggling.md) / cache poisoning).

## Chaining discipline

- **Map each primitive's output to the next's input.** An info-disclosure that leaks a user id is
  the *key* to an IDOR that changes that user's email. Always ask: what does this unlock?
- A finding that only *reveals* something (id, endpoint, token format, email) is a **door** — walk
  through it before you close the report as "information disclosure."

## Proving an ATO safely

- Use **two accounts you own**: A (attacker) takes over B (victim).
- Demonstrate the full chain end to end, then show you can authenticate as B (a B-only resource,
  B's profile) — the minimum that proves control.
- Don't touch real users. For the "victim clicks" step, you are the victim.

## Reporting

Lead with the outcome (full ATO) and lay out the chain as numbered steps, each with its proof,
ending in "authenticated as victim B." Give each link's severity honestly, but the report's rating
is the chain's impact. A clean ATO chain is among the highest-paid reports — the write-up quality
is what makes the chain legible to the triager.
