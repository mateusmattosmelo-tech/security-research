# Recon Playbook

My default first pass on a new web/API target. The goal of recon isn't to find the bug —
it's to build a map complete enough that the bug has nowhere to hide.

## 0. Scope first, always

Before any request leaves my machine:

- Read the program policy end to end. Write down: in-scope domains/apps, out-of-scope,
  allowed test accounts, rate-limit rules, prohibited techniques (automated scanning,
  DoS, social engineering), and whether PII/prod data can be touched.
- Note the payout table and which vuln classes are eligible — it steers where to spend time.

## 1. Surface discovery (passive → active)

- **Subdomains:** certificate transparency (crt.sh), passive DNS, `subfinder`, `amass`.
- **Historical URLs:** Wayback (`waybackurls`), `gau` — old endpoints that still answer.
- **JS bundles:** pull and beautify every script; grep for API paths, feature flags,
  internal hostnames, and accidental keys.
- **Code footprint:** GitHub org + dorks, npm/PyPI packages, exposed `.git`, source maps.
- **Mobile:** if there's an app, the APK/IPA is a spec of the backend — decompile and read.

## 2. Map roles & state

- Enumerate the roles the product has (anon, free user, paid, admin, co-owner, invited guest).
- For each role, capture a clean authenticated session in its own browser profile.
- The interesting bugs live in the **unusual state**: a session refused but still valid, a
  pre-existing grant/device, an expired-but-not-revoked object, an abandoned wizard.

## 3. Classify the attack surface

For every operation observed, record in a table: endpoint, method, role required,
identifier source (client vs. session), and side effect (read / write / money / auth).
The rows where an identifier comes **from the client** and the object isn't owner-derived
are where IDOR/BOLA hides.

## 4. Derive test classes

From the map, derive the classes worth testing per endpoint — authz, business logic,
injection, SSRF, race conditions — and only then start probing. Probing before the map is
complete is searching in the dark.

## Rules I've paid to learn

- New surface never stops arriving. A subdomain found on request #500 goes back on the map
  and re-triggers class derivation.
- Depth must not block breadth. See an anomaly → write it down, keep covering, come back.
- Everything gets written to a file, not kept in my head — that's what lets the map grow.
