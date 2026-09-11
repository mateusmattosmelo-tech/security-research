# File Upload Testing

Upload features hand the server attacker-controlled bytes and often a filename and content-type.
The bugs come from what the server does with them: where it stores them, how it serves them back,
and whether it trusts the metadata the client sent.

## The questions that matter

1. **What does the server validate — and how?** Extension, content-type header, magic bytes, or
   nothing? Client-declared content-type is attacker-controlled; only server-side content
   inspection counts.
2. **Where does the file land, and how is it served back?** Same origin as the app, or an isolated
   storage host? Served with the right content-type and `Content-Disposition`, or sniffable?
3. **Is the stored name predictable or attacker-controlled?** Path traversal in the filename,
   overwrite of another user's/object's file, guessable URLs.

## What to try

- **Extension / type bypass:** double extensions (`x.php.png`), null bytes, case tricks, allowed
  extension with malicious content, mismatched magic bytes vs. declared type.
- **Stored XSS:** upload an SVG (XML → script), an HTML file, or a file served with a sniffable
  content-type on the app origin. If it renders in the victim's session, that's stored XSS.
- **Path traversal / overwrite:** `../` in the filename or a client-supplied storage path;
  overwriting a sibling object or another tenant's file.
- **XXE / parser bugs:** uploads parsed server-side (SVG, DOCX/XLSX, XML, image metadata) may hit
  an XML or image library — XXE, SSRF via external entities, decompression bombs.
- **SSRF via "import from URL":** the upload-by-URL variant is an SSRF sink (see the SSRF note).
- **Content-type confusion:** does the download endpoint let you control the served content-type?

## Isolation is the real defense

The safest designs serve user content from a separate, sandboxed origin with a forced
`Content-Type` and `Content-Disposition: attachment`. If uploads are served from the app's own
origin and can render, half the classes above become reachable — note that architecture as the
root cause.

## Reporting

Show the upload request (the bytes, the filename, the declared type), the URL it's served at, and
the response headers proving how it's served. For stored XSS, show it executing in a victim
context; for traversal/overwrite, show the cross-object effect with a control. Keep test files
benign and clean them up.
