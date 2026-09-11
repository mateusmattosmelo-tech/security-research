# Secure Code Review

When the target is open source — or ships an SDK, a CLI, or a client bundle — the source is a
map of where the bugs are. Reading it is account-free and often points straight at the sink you'd
otherwise fuzz for blindly. Source tells you *where*; a report still needs it *reproduced* against
the running system.

## Start where trust crosses a boundary

Don't read top to bottom. Jump to the places where untrusted input meets a powerful operation:

- **Auth & session:** token/signature verification, session derivation, "who am I" logic.
- **Authorization:** where the code decides whether the caller may touch an object — and whether
  the object id comes from the request or the session.
- **Sinks:** query builders (SQLi), template rendering (SSTI), command execution, deserialization,
  file paths (traversal), outbound URL fetches (SSRF).
- **Tenant boundary:** on a multi-tenant product, every place a tenant/org id is trusted.

## Questions to hold in mind

- **Does the signature cover what's parsed?** (JWT and similar — verify vs. read the same bytes.)
- **Is the algorithm/key pinned, or attacker-influenced?**
- **Is there a fallback path that skips the check?** "If no key configured, trust this header."
  Then ask *who can trigger the fallback* and *who can set the header*.
- **Fail open or fail closed?** What does the error path return — a default identity, or a deny?
- **Are identifiers validated and parameterized**, or concatenated / trusted from the client?
- **Third-party components:** a bug in a library only counts if you can show it's exploitable in
  *this* implementation (many programs exclude generic CVE-in-a-dep reports).

## Turn reading into leads, then proof

Each smell becomes a hypothesis with an address (`file:line`). But a code-level finding is a
**lead** until it's demonstrated end to end against an in-scope, authorized target — the forged
token accepted, the injected value executed, the wrong tenant's row returned. Say clearly which
part you proved and which is still inference from the code; don't ship a code smell as a confirmed
exploit.

## Practical mechanics

- Clone shallow / sparse to read just the component you care about.
- Grep for the dangerous primitives first (`format!`/string-built SQL, `eval`, `exec`,
  `pickle`/`Marshal`, `fetch(`, `redirect(`), then read outward from the hits.
- Read the tests — they document intended behavior and sometimes the edge cases the authors
  worried about (a hint at where it's fragile).
