# NoSQL Injection — Deep Dive

NoSQL datastores (MongoDB, and query layers over Redis/Elasticsearch/CouchDB) don't use SQL, but
untrusted input reaching a query still lets an attacker change its logic — via operator injection,
type juggling, or server-side JavaScript. MongoDB is the common case. Authorized testing; prove on
your own data.

## Operator injection

Mongo queries are documents (`{username: X, password: Y}`). If the app builds the query from JSON
and the attacker controls the *value*, they can substitute a **query operator** object:

```json
{"username":"admin","password":{"$ne":"x"}}       // password not equal to "x" -> matches
{"username":{"$gt":""},"password":{"$gt":""}}     // both greater than "" -> first user
{"username":"admin","password":{"$regex":"^a"}}   // regex -> blind, char-by-char extraction
```

- `$ne`, `$gt`, `$gte` turn an equality check into "any" → **auth bypass**.
- `$regex` gives a **blind oracle**: anchor and extend (`^a`, `^ab`, …) to extract the password one
  character at a time from the true/false response, exactly like blind SQLi.
- `$in`/`$nin` with arrays, `$exists` to probe fields.

In URL-encoded bodies, the operator is injected via bracket notation the parser turns into nested
objects: `username[$ne]=x&password[$ne]=x`.

## Type juggling / parameter pollution

- Sending `password[$ne]=` (an object) where the app expected a string changes semantics — the
  bug is the app not enforcing the type before querying.
- Array vs string confusion, and language-specific coercion (PHP/Express body parsers building
  objects from `a[b]=c`).

## Server-side JavaScript injection (the RCE path)

Where the app uses `$where`, `mapReduce`, `$accumulator`/`$function` (aggregation), or
`group` with a JS predicate, and concatenates input into the JS string, you get JS execution in the
DB context:

```
'; return true; var x='       // in a $where string -> always true
$where: "this.name == '" + userInput + "'"     // break out, inject JS
```

`$where`/JS is disabled by default on modern Mongo and often unavailable — but where present it's
data exfiltration (read other docs via the JS) up to sabotage, and historically DoS via infinite
loops.

## Blind extraction (regex oracle)

No data reflected but behavior differs on match:

```
password[$regex]=^a        -> login "works"/different response  => first char is 'a'
password[$regex]=^ad       -> ...
```

Automate: for each position, try the charset until the response flips; also `$regex` with length
probes (`^.{n}$`) to learn length first.

## Beyond Mongo

- **Elasticsearch:** query-string injection, script fields (Painless) where scripting is enabled.
- **CouchDB:** design-doc / view injection.
- **Redis:** command injection via unescaped input reaching a command (and gopher-SSRF, see the
  SSRF deep-dive).

## Testing & reporting

Confirm with a benign oracle on **your own** account (`$ne` login bypass to *your* account, or a
`$regex` extraction of a value you already know, to prove the primitive). Extract only enough to
prove it. Report the injectable parameter, the operator/JS payload, and the proof (auth bypass,
extracted-then-verified value, or JS execution). Fix: validate types, reject query-operator objects
in user values, disable server-side JS, use parameterized/ODM queries.
