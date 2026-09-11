# Insecure Deserialization

When an app deserializes attacker-controlled bytes into live objects, the deserializer can be
steered into constructing objects and invoking methods the attacker chooses — often reaching
remote code execution. The impact ceiling is high, so it's worth spotting the formats and sinks.

## Spot the format

Recognizable markers of a serialized blob crossing a trust boundary (cookie, hidden field, API
body, cache, message queue):

- **Java:** base64 starting `rO0` (or hex `ac ed 00 05`). `readObject` on user data.
- **Python:** `pickle` / `cPickle`, `PyYAML` `yaml.load` (unsafe), `jsonpickle`, `shelve`.
- **PHP:** `unserialize()` on user input; strings like `O:8:"stdClass":…`. Phar wrappers.
- **.NET:** `BinaryFormatter`, `LosFormatter`, `ObjectStateFormatter`, `Json.NET` with
  `TypeNameHandling`, `__VIEWSTATE`.
- **Ruby:** `Marshal.load`, unsafe YAML.
- **Node:** `node-serialize`, unsafe use of `eval`-based deserializers.

## Where it hides

Session cookies, view state, "remember me" tokens, cache entries, inter-service messages, import
features, and any parameter that round-trips an object. The dangerous ones are where the app
**deserializes before authenticating**, or trusts an internal channel that isn't as internal as
assumed.

## Testing

- Identify the format, then try a **benign** gadget first: a payload that causes a detectable,
  harmless effect (a delay via a sleep gadget, a DNS/HTTP callback to your listener) — never a
  destructive command. The callback proves execution without touching data.
- Gadget chains are library-dependent (ysoserial for Java/.NET, known PHP/Python chains). Match
  the gadget to the libraries actually present.
- Blind cases: rely on out-of-band (DNS/HTTP) confirmation, like SSRF.

## Reporting

Show the serialized input location, the format, and the out-of-band proof of code execution (the
callback, the timed delay) — with a benign payload. State the gadget/library chain and that you
avoided any destructive action. This class is high severity; the proof needs to be unambiguous
and clean.
