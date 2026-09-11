# Lab notes — SQL Injection (PortSwigger Web Security Academy)

Notes on the [SQL injection labs](https://portswigger.net/web-security/sql-injection) — approach
over answers. Public practice labs; safe to write up.

## Confirm and locate

- Break the query with a single quote and watch for an error or behavior change. Test every input
  that could reach a query: URL params, body fields, headers (`User-Agent`, `Referer`), cookies.
- Confirm boolean control: `' AND 1=1--` vs `' AND 1=2--` producing different responses.

## In-band (results reflected)

- **UNION-based:** find the column count (`ORDER BY n` until it errors, or `UNION SELECT NULL,…`),
  find which columns render, then select data (`username, password` from the users table). On
  Oracle remember `FROM dual`.
- **Enumerate the schema:** `information_schema.tables` / `.columns` (or the DB-specific catalog)
  to find table and column names before dumping.

## Blind

- **Boolean-based:** no data returned, but the page differs on true/false. Extract data one
  character at a time with `SUBSTRING(...)=...` conditions.
- **Time-based:** no visible difference at all — use a conditional delay
  (`'; IF(condition) WAITFOR DELAY '0:0:5'--`, `pg_sleep`, `SLEEP()`) and measure response time.
- **Out-of-band (OAST):** when blind and un-timed, trigger a DNS/HTTP callback to a listener you
  control (e.g. via a stacked query or a DB-specific function) — the lookup proves execution and
  can carry exfiltrated data.

## Practical notes

- Fingerprint the DBMS first (error strings, version functions, comment syntax) — the payloads
  differ per engine.
- Filters/WAF: comments, case variation, and encoding help, but the real fix the labs teach is
  that **parameterized queries** kill the class — that's the recommended fix in every report.

## Reporting

Show the injectable parameter, the payload, and the data returned (or the timing/OOB proof for
blind). Prove it against a benign target value first; never dump more than needed. Full method in
[API security testing](../methodology/api-security-testing.md).
