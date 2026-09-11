# Lab notes — Access Control (PortSwigger Web Security Academy)

Notes on working the [access control labs](https://portswigger.net/web-security/access-control).
These are free, intentionally-vulnerable practice labs — writing them up is fair game and a good
way to show the method. Each note is the *approach*, not just the answer.

## Unprotected admin functionality

- The admin panel exists but isn't linked. Check `/robots.txt`, then guess (`/admin`,
  `/administrator-panel`). When the path is obfuscated, the front-end JS often contains it — read
  the bundle.
- **Lesson:** "hidden" is not "protected." Enumerate from the client's own code, not guesswork.

## IDOR — horizontal (another user's data)

- A parameter carries an object id (`?id=`, `/download?filename=`, an account number). Swap it for
  another user's value and see if the server re-checks ownership.
- The strongest proof uses two accounts you control: A's request returns B's real data.

## IDOR — via a leaked identifier

- Sometimes you can't guess the id, but the app leaks it elsewhere (a different response, an email
  field, an API that lists users). Chain: leak the id → use it on the vulnerable endpoint.
- **Lesson:** an information-disclosure bug is a *door* — the finding is what you do with the id.

## Privilege escalation via request tampering

- The role is trusted from a client-controlled place: a `roleid` in the request body, a cookie
  (`Admin=false`), a JWT claim, or a hidden field. Change it and see if the server honors it.
- **Mass assignment variant:** add a field the UI never sends (`"roleid":2`) to a profile update.

## Method / path bypasses

- An endpoint blocked for `GET` may be open for `POST` (or vice-versa); a URL-matching rule may be
  case-sensitive (`/ADMIN`) or defeated by a trailing slash / path segment.
- **Referer-based access control:** if access is gated on the `Referer` header, forge it.

## The through-line

Access control breaks when the server trusts the client for identity, role, or object ownership.
The method is always: find where that trust is placed, then vary exactly that one thing with two
accounts you own and a positive/negative control. See
[authorization testing](../methodology/authorization-testing.md) for the full playbook.
