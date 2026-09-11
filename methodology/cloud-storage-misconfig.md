# Cloud Storage Misconfiguration

Object stores (S3, GCS, Azure Blob, R2) are a recurring source of data exposure: a bucket set to
public, listable, or world-writable leaks or lets an attacker tamper with data — often with no
authentication at all.

## Find the buckets

- **From the app:** asset URLs in HTML/JS/CSS often point at the bucket
  (`https://bucket.s3.amazonaws.com/…`, `storage.googleapis.com/bucket/…`, `*.r2.dev`,
  `*.blob.core.windows.net`). Mobile apps and API responses reveal them too.
- **From names:** derive candidates from the org/product name and common suffixes
  (`-assets`, `-uploads`, `-backups`, `-static`, `-dev`, `-logs`). Keep guessing light and
  targeted — mass brute force is noisy and often out of scope.
- **From DNS/CT:** CNAMEs pointing at storage endpoints.

## What to check (read-only first)

- **Listing:** does `GET https://bucket.s3.amazonaws.com/` (or `?list-type=2`) return the object
  index? A listable bucket hands you every key.
- **Anonymous read:** can you fetch objects without credentials? Look for sensitive keys —
  backups, dumps, configs, user uploads, source.
- **ACL / policy:** `?acl` may reveal permissions.

## Higher-impact checks (do carefully)

- **Anonymous write:** can you `PUT` an object? World-writable = defacement, malware hosting, or
  overwriting assets the app serves (stored XSS / supply chain). Prove it by writing a **benign,
  clearly-marked** canary object and deleting it immediately — never overwrite real objects.
- **Predictable object URLs:** private-ish files at guessable keys (IDOR over storage).
- **Signed-URL flaws:** overly long expiry, or a signing scheme you can manipulate.

## Beyond buckets

- **Public snapshots/images/registries:** EBS snapshots, container images, or registries left
  public can carry secrets and code.
- **Dangling storage CNAME** → subdomain takeover (see that note).

## Testing discipline

Read-only by default. For write tests, use a benign canary and remove it at once; never read more
than needed to prove exposure, and mask any sensitive data you incidentally see. Respect the
program's rules on enumeration.

## Reporting

Show the bucket/endpoint, the exact request (list/read/write), and the response proving access —
plus a representative (masked) sensitive key for reads, or your canary for writes. State whether
it's read, list, or write, and the data class exposed. That triad decides severity.
