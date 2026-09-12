# Web Cache Deception — Deep Dive

Cache poisoning makes the cache store *your* malicious response for everyone. Cache **deception**
is the inverse: trick the cache into storing a *victim's private* response under a URL the attacker
can then fetch. The victim visits a crafted link, their authenticated response gets cached, and the
attacker reads it. This is the mechanic level; test with two of your own accounts.

## The disagreement it exploits

Two systems look at the same URL differently:

- The **origin** does *path-based routing*: `/account/profile/foo.css` still routes to the profile
  handler (extra path ignored, or matched by a prefix route) and returns the victim's private data.
- The **cache** does *extension/rule-based caching*: it sees `.css` (or `/static/`, or an image
  extension) and caches the response as if it were a static asset — ignoring `Cache-Control`, or
  because a CDN rule force-caches by extension.

Result: a private, authenticated response gets stored in a shared cache under a path the attacker
chose.

## The attack

1. Attacker crafts a URL that (a) the origin serves as the victim's private page, and (b) the cache
   treats as cacheable:
   ```
   https://target/account/profile/attacker.css
   https://target/settings/anything.js
   https://target/api/me/x.jpg
   ```
2. Victim (authenticated) is lured to open it. Origin returns their profile/settings/PII; the cache
   stores it keyed on that URL.
3. Attacker (unauthenticated) requests the **same URL** → the cache serves the victim's cached
   private response.

## Path-confusion variants (why modern CDNs still fall)

The trick is making origin and cache disagree on where the path "ends." Delimiters the two parse
differently:

- **Extension append:** `/profile.css` — origin ignores, cache caches by `.css`.
- **Path parameter / matrix:** `/profile;foo.css`, `/profile%2f..%2fx.css`.
- **Encoded delimiters:** `/profile%00.css`, `/profile%0a.css`, `/profile%23.css` (`#`),
  `/profile%3f.css` (`?`) — origin decodes/stops at one; cache keys on the raw string.
- **Static-directory prefix:** `/static/..%2faccount%2fprofile` — cache sees `/static/` (force-cache
  rule), origin traversal resolves to the private page.

Each CDN/origin pair parses these differently; the research is finding the delimiter where they
diverge (PortSwigger's cache-deception work catalogs the classes).

## Detecting

- Request the crafted URL **authenticated**, then again **unauthenticated / from another session**;
  if the second gets the first's private data → deception confirmed.
- Watch cache indicators: `X-Cache: HIT`, `Age`, `CF-Cache-Status: HIT`, `cf-cache-status`.
- Confirm the origin actually returns private data for the crafted path (not a 404/redirect).

## Testing discipline

This caches **another user's** data by design, so keep the blast radius tiny: use your **own** two
accounts (victim + attacker), craft a URL unlikely to be hit by real users, and if you can, purge
the cache entry after. Don't cache strangers' data. Note in the report what you did to avoid
impacting real users.

## Reporting

Show the crafted URL, the origin returning private data for it (authenticated), the cache headers
proving it stored (`MISS`→`HIT`), and the attacker session retrieving the victim's data. Name the
delimiter/rule that made origin and cache disagree. Fix: cache by `Content-Type` not extension,
honor `Cache-Control`, don't cache authenticated responses, and normalize paths consistently.
