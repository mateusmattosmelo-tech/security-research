# WebSocket Security

WebSockets keep a long-lived, bidirectional channel open after an HTTP handshake. They're often
tested less than REST, and two things get overlooked: the handshake's origin check, and the fact
that per-message authorization frequently isn't enforced.

## The handshake

- **Cross-Site WebSocket Hijacking (CSWSH):** if the server authenticates the connection with
  cookies and does **not** validate the `Origin` header on the handshake, any website can open a
  socket in a logged-in victim's browser and read/drive it — CSRF for WebSockets. Test: replay the
  handshake with a foreign `Origin` and see if it connects and stays authenticated.
- **Auth on the handshake vs. per message:** where is identity established? A token in the query
  string leaks into logs; a cookie invites CSWSH; a token in the first message is better but only
  if every later message is still authorized.

## Per-message authorization

- Once connected, does each message re-check what the user may do? A socket authorized for user A
  that accepts `{"action":"read","account":"B"}` is BOLA over the socket.
- Can you subscribe to channels/topics that belong to other users/tenants? Topic-based pub/sub is
  a common place tenant scoping is forgotten.
- Are messages that mutate state authorized the same way the REST equivalents are, or is the
  socket a softer path to the same actions?

## Other angles

- **Injection through messages:** message payloads reach the same sinks as HTTP (SQL, templates,
  command) — test them.
- **No rate limit / resource limits** on messages (often out of scope as DoS — check policy).
- **Message format confusion:** JSON vs. binary, type juggling in the message router.

## Testing mechanics

Capture the handshake and frames with a proxy that supports WebSockets; replay and edit frames.
For CSWSH, a tiny HTML page that opens the socket from a different origin and logs what it
receives is the cleanest proof.

## Reporting

For CSWSH: show the handshake accepted with a foreign Origin and the victim data received by an
attacker-origin page. For per-message authz: show the socket authorized as A returning/altering
B's resource, with a control. Name whether the gap is the handshake origin check or per-message
authorization.
