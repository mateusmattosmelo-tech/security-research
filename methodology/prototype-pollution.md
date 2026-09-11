# Prototype Pollution

A JavaScript-specific class: if code merges attacker-controlled keys into an object without
guarding `__proto__` / `constructor` / `prototype`, the attacker writes onto `Object.prototype` —
and every object in the app inherits the injected property. On its own it's odd; chained to a
"gadget" that reads that property, it becomes DoS, privilege escalation, XSS, or RCE.

## Client-side

- **Sources:** URL query/hash parsed into an object, `JSON.parse` of user data, deep-merge of
  config, `location`-driven state.
- **Sinks/gadgets:** a later code path that reads a property and uses it in a dangerous way — an
  option that becomes `innerHTML`, a template config, a script `src`. Pollution + gadget = DOM XSS.
- **Test:** `?__proto__[test]=polluted` (and `constructor[prototype][test]`), then check
  `Object.prototype.test` in the console. Many libraries have known gadget chains.

## Server-side (Node)

- **Sources:** `Object.assign`/lodash `merge`/`defaultsDeep`/`set` on request JSON, query parsers,
  form parsers.
- **Impact:** pollute a property the app later reads for an auth/branching decision
  (`isAdmin`, `role`), or a property a downstream library uses (`shell`, `NODE_OPTIONS`-style
  gadgets, template engine internals) — can reach privilege escalation or RCE.
- **Test:** send `{"__proto__":{"polluted":true}}` (or `constructor.prototype`) to a JSON endpoint
  and look for a behavior change downstream; blind cases need a gadget you can observe.

## Confirming it's real

Pollution alone is often low-impact — the finding's weight is the **gadget** it reaches. Show:
1. the merge/assign that accepts `__proto__` (the source), and
2. the concrete downstream effect (auth bypass, XSS execution, a crash, or command execution),
   not just that `Object.prototype` got a new key.

## Reporting

Give the request that pollutes, the property, and the gadget that turns it into impact — with a
control showing the app behaves normally without the polluted key. Name the vulnerable
merge/parse and, if client-side, the `file:line` in the bundle.
