# Enumeration Within Scope (Without Tripping the Exclusions)

Most programs exclude "unauthenticated user enumeration, brute force, and DoS," and rate-limiting
reports are usually out of scope too. That doesn't mean you can't enumerate — it means you
enumerate *carefully*, and you know when an enumeration primitive is itself the finding versus
just noise. Getting this wrong gets your IP blocked, your account banned, and your report closed.

## Read the boundary first

- What does the policy forbid: automated scanning? account-creation-by-script? a request-rate cap?
  A specific enumeration class? Write it down before sending anything.
- Note any required identification header and test account rules — traffic that's identifiable as
  research is treated very differently from traffic that looks like an attack.

## Enumerate like a careful human, not a scanner

- **Passive first.** CT logs, public DNS, the app's own JS/API, sitemaps, the OpenAPI spec, mobile
  bundles — most of the map is available without hammering anything.
- **Targeted, not brute.** Guess a handful of high-probability paths/buckets/subdomains from names
  you already have, not a 100k wordlist. Depth from knowledge beats breadth from noise.
- **Throttle and cap.** Low concurrency, human-scale delays, small counts. You're confirming a
  hypothesis, not scanning.
- **Stop at proof.** Once one request proves the primitive, you don't need a thousand more.

## When enumeration IS the finding

An enumeration *oracle* can be a real bug even where "enumeration" is excluded — the exclusion is
about noisy scanning, not about a design flaw that leaks existence/data. The line: does the
endpoint reveal, to an unauthenticated caller, whether a **specific real** account/object/resource
exists or its private attribute? A response differential against **synthetic** ids is usually out
of scope; a differential that discloses a **real** person's registration, or an object belonging to
another account, can be in scope. Prove it against your own data / a resource you own, with a
positive and negative control — not against strangers, and not at volume.

## What to avoid entirely

- Credential brute force / stuffing, password spraying.
- Scripted account creation or loan/order submission where the policy forbids it.
- Anything that degrades service. A rate-limit *bypass* that enables one of the above is still
  abuse — report the bypass's impact, don't perform the abuse.

## Reporting

If the enumeration itself is the finding, lead with the real-resource disclosure and the
controls that prove it's not a synthetic-id differential. Keep the volume in your evidence tiny —
a couple of requests, your own data — precisely because restraint is what keeps it in scope.
