# Git Exposure & Secrets in History — Deep Dive

Two adjacent, high-yield, account-free classes: an **exposed `.git` directory** on a web server
(reconstruct the whole source) and **secrets buried in git history** (a key committed then
"removed" still lives in an old commit). Both are pure recon; the payoff is source and credentials.

## Exposed `.git/` on the web root

If the deploy copied `.git/` into the served directory, the repository is downloadable even when
directory listing is off — because the file layout is predictable.

- **Detect:** `GET /.git/HEAD` → `ref: refs/heads/main` (200) is the tell. Also `/.git/config`,
  `/.git/logs/HEAD`, `/.git/index`.
- **Reconstruct:** from `HEAD`/`refs` you get the tip commit; `git` objects live at
  `/.git/objects/<2>/<38>` (zlib-compressed). Tools (`git-dumper`) walk refs → commits → trees →
  blobs and rebuild the full working tree, including deleted files and history.
- **Payoff:** full server-side source (find other vulns from code), plus any secrets ever committed.

Related exposures to check the same way: `/.svn/`, `/.hg/`, `/.bzr/`, `.DS_Store` (leaks filenames),
and backup files (`.bak`, `~`, `.swp`, `index.php.save`).

## Secrets in git history (public repos too)

The current tree being clean means nothing — `git log -p`, or scanning every blob, surfaces what
was committed then removed:

- **Where:** an accidental `.env`, a config with DB creds, a private key, a token hardcoded during
  debugging, a CI secret, a customer file. Removed in a later commit but present in the object that
  the earlier commit points to.
- **Scan history, not HEAD:** clone with full history and run a history-aware scanner
  (`trufflehog`, `gitleaks`) across all commits and branches; or `git log -p -S<pattern>` to find
  when a secret was added/removed.
- **Deleted branches / dangling objects:** force-pushes and deleted branches can leave objects
  reachable via the reflog or via GitHub's commit API even after they're "gone" from the branch.
- **Forks & GitHub events:** a secret pushed to a private repo then forked/mirrored, or captured in
  the public events API, can persist elsewhere.

## Telling a live secret from noise

Most raw regex hits are fixtures/examples. Before reporting (see also the
[secrets-scanning methodology](../methodology/secrets-scanning.md)):
- Filter `example|test|dummy|sample|fixture|<...>|redacted` and test/spec paths.
- Judge context: a scraped HTML file, a sample DB, or a unit-test vector is noise.
- **Confirm live** with the least-privileged, non-destructive call the provider offers (a
  token-info / `whoami`), only if the program allows — a revoked key isn't a finding.

## Handling responsibly

- Report **fast** — live keys are a race.
- **Never paste the full secret** anywhere; mask (first 6 + last 4). Give the exact location: repo,
  path, and **commit hash**, plus how you confirmed it live (masked).
- For an exposed `.git`, you don't need to dump everything — `/.git/config` + a couple of objects
  proving reconstruction is enough for triage.

## Reporting

`.git` exposure: show `/.git/HEAD` returning a ref and a reconstructed file (or the config), and the
impact (full source / a secret found in it). History secret: the commit hash, path, masked secret,
and the live-confirmation. Fix: strip VCS dirs from deploys; rotate exposed secrets and purge them
from history (rotation is the real fix — history rewrite alone doesn't un-leak).
