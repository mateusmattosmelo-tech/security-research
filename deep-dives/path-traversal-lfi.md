# Path Traversal & File Inclusion — Deep Dive

If user input reaches a filesystem path, `../` sequences (or their many encodings) can escape the
intended directory to read — or sometimes write/execute — arbitrary files. This covers the
traversal encodings, LFI-to-RCE escalations, and the sinks. Authorized testing; read only what
proves it.

## The sinks

Any parameter that becomes a path: file download (`?file=`), image/avatar loaders, template/include
paths, log viewers, "export"/"report" filenames, ZIP/archive extraction (Zip Slip), and
Android content-provider `openFile`. Also indirect: an uploaded filename used later as a path.

## Traversal encodings (defeating naive filters)

A filter that strips `../` once, or blocks the literal, falls to:

- **Basic:** `../../../../etc/passwd`, Windows `..\..\..\windows\win.ini`.
- **URL / double-URL:** `%2e%2e%2f`, `%252e%252e%252f` (server decodes twice).
- **Overlong UTF-8 / unicode:** `%c0%ae%c0%ae%c0%af`, `%uff0e`.
- **Nested/stripped:** `....//`, `..././`, `..;/` (path-param), so a single-pass `../`-removal
  leaves a valid `../`.
- **Mixed separators / backslash** on Windows; **null byte** `%00` on legacy stacks to truncate an
  appended extension (`../../etc/passwd%00.png`).
- **Absolute path** where the app concatenates but also honors an absolute (`/etc/passwd`).
- **Leading-slash / prefix bypass:** if the app prepends a base dir, `....//` or an absolute may
  escape; if it appends an extension, null byte or a path that already ends correctly.

## What to read first (proof + escalation)

- **Proof:** `/etc/passwd`, `/etc/hostname`, `C:\windows\win.ini` (benign, unambiguous).
- **App source / config:** the app's own files (`../config.php`, `.env`, `application.properties`,
  `web.config`) — often leaks DB creds, API keys, secrets.
- **Process/runtime:** `/proc/self/environ` (env vars incl. secrets), `/proc/self/cmdline`,
  `/proc/self/cwd/…`, cloud creds files (`~/.aws/credentials`), SSH keys.

## LFI → RCE escalations

Local file **inclusion** (the file is executed/interpreted, not just read) escalates:

- **PHP wrappers:** `php://filter/convert.base64-encode/resource=index.php` to read source;
  `php://filter/.../resource=` chains and `data://`/`expect://` for execution where enabled.
- **Log poisoning:** inject PHP/code into a log (User-Agent, a failed login) then include the log
  file → the injected code runs.
- **Session/upload include:** include your uploaded file or a PHP session file you seeded.
- **`/proc/self/environ` include** (older setups) with a payload in an env-reflected header.
- **Zip Slip:** an archive entry named `../../../../var/www/shell.php` that the extractor writes
  outside the target dir → write/RCE.

## Detecting blind

If content isn't reflected, use differential/OOB: a valid vs. traversal path returning different
sizes/status, or (on Windows/UNC or via a wrapper) a path that triggers an OOB fetch to your
listener.

## Testing discipline

Read the **minimum** that proves it (`/etc/hostname`, the first lines of a config with secrets
masked). Don't exfiltrate user data or keys wholesale; mask anything sensitive in evidence. For
write/RCE, use a benign marker and clean up.

## Reporting

Show the parameter, the exact (encoded) payload, and the file contents proving traversal (masked) —
plus, for LFI→RCE, the execution proof (wrapper output, poisoned-log callback). Name the encoding
that bypassed the filter and the fix: canonicalize then verify the resolved path stays within an
allowlisted base dir (not blocklist `../`).
