# Prototype Pollution to RCE — Deep Dive

Prototype pollution writes onto `Object.prototype`, so every object inherits the injected property.
Alone it's a curiosity; its power is the **gadget** — existing code that reads a property from a
plain object and does something dangerous with it. This traces the mechanics and the real gadget
chains, client and server. Authorized testing; confirm impact out-of-band and on your own
resources.

## The write

Vulnerable merge/set/clone that walks a key path without blocking `__proto__` / `constructor` /
`prototype`:

```js
// merge(target, source) with source = JSON.parse(userInput)
{"__proto__":{"polluted":"x"}}
{"constructor":{"prototype":{"polluted":"x"}}}   // when __proto__ is stripped
```

After the merge, `({}).polluted === "x"` — every object now has `polluted` unless it defines its
own. Common vulnerable operations: recursive `merge`/`extend`/`defaultsDeep`, `_.set(obj, path,
val)` with a user path, query-string parsers that build nested objects (`?a[__proto__][x]=1`),
`Object.assign` deep variants.

## Client-side chains (→ DOM XSS)

Pollute a property a library later reads as configuration:

- A template/sanitizer option that becomes `innerHTML` when a config flag is truthy.
- A script loader that reads `src`/`baseURL` from an options object → inject a script URL.
- jQuery historically: polluting an option consumed by `$.extend`-driven behavior.
- Combined with **DOM clobbering** when you only have HTML injection: clobber to seed the property,
  gadget to execute.

The chain: pollution source (URL/JSON) → polluted prop → framework gadget that sinks it → XSS under
whatever CSP allows.

## Server-side chains (→ RCE)

On Node, the deadly gadgets are in how child processes and require/exec resolve options:

- **`child_process.spawn/exec` options:** polluting `shell`, `NODE_OPTIONS`, or env-related
  properties can turn a benign spawn into attacker-controlled command execution. E.g. polluting a
  property that becomes `options.shell` or injecting `NODE_OPTIONS=--require /proc/self/...`.
- **Template engines:** polluting internal options (e.g. EJS/Pug/Handlebars compile options like
  `outputFunctionName`, `escapeFunction`, `compileDebug`/`client`) has yielded RCE by injecting
  code into the compiled template function.
- **`require`/module resolution** and config-driven `eval`-like paths.

The exact gadget depends on the Node version and the libraries loaded — the research is in matching
a *reachable* pollution to a gadget that's actually present in the target's dependency tree.

## Finding the pair

1. **Find the sink (pollution):** send `__proto__`/`constructor.prototype` payloads to JSON bodies,
   query strings (`a[__proto__][b]=c`), and any merge/config endpoint; detect with a harmless
   property and a reflected behavior change, or a status/latency tell for blind.
2. **Find the gadget:** read the dependency tree and known gadget databases; look for spawn/exec,
   template compilation, and option-object reads downstream of the pollution.
3. **Chain:** pollute the exact property the gadget reads.

## Confirming safely

- Prove the write with a benign property first.
- For RCE, use a **non-destructive** gadget: a DNS/HTTP callback to your listener (proves
  execution), a timing delay, or writing a marked file you remove — never a destructive command.
- Blind server-side: rely on OOB, like SSRF/deserialization.

## Reporting

Show the pollution request, the property, the gadget (`file`/package + the code that reads it), and
the end effect (XSS execution, or the OOB callback / marked artifact proving RCE) with a control
showing normal behavior without the polluted key. Note the Node/library versions — the gadget is
version-specific. Fix: block `__proto__`/`constructor`/`prototype` keys, use `Map`/null-proto
objects, and `Object.freeze(Object.prototype)` where feasible.
