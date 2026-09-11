# CI/CD & Supply-Chain Security

The build pipeline is a high-value target: it holds deploy credentials, signs artifacts, and pushes
code straight to production. A weakness here isn't one app — it's everything the pipeline ships.
Much of it is auditable from public repos and package registries.

## Pipeline configuration (mostly public)

- **Untrusted code with secrets** — the pwn-request / injection classes; see
  [GitHub Actions security](github-actions-security.md).
- **Third-party actions/steps not pinned** — an action referenced by a mutable tag (`@v3`) or
  branch instead of a commit SHA can be swapped under you. Look for unpinned third-party actions,
  especially ones handling secrets.
- **Over-broad tokens** — `permissions:` set to write everywhere, long-lived PATs in secrets,
  cloud creds where OIDC would do.
- **Self-hosted runners** on public repos — a fork PR can run on your infrastructure.

## Artifact & dependency integrity

- **Dependency confusion** (unclaimed internal names) — see that note.
- **Typosquats / hijacked deps** — a dependency whose maintainer account or namespace lapsed.
- **Lockfile discipline** — are dependencies pinned and hash-verified, or floating?
- **Build provenance** — are released artifacts signed / attested (SLSA, sigstore), or could a
  tampered artifact pass as genuine?

## Cloud trust from CI

- **OIDC → cloud role assumption:** the `sub`/audience conditions on the trust policy must be
  tight. A wildcard or a too-broad `repo:org/*` condition lets a different workflow (or a fork)
  assume the deploy role. This is a recurring high-impact misconfig.

## Repo & release controls

- **Branch protection / required reviews** on the deploy branch; can a single actor push to it?
- **Environment protection rules** on production deploys.
- **Release/tag integrity** — who can cut a release that ships?

## How to work it (account-free first)

1. Read `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, and build configs in public repos.
2. Note triggers, secret usage, token scope, action pinning, and runner type.
3. Check dependency manifests against the registries (confusion / squats).
4. For each risk, trace it to concrete impact: whose secret, which environment, what gets shipped.

## Reporting

Show the exact config (`file:line`), the trust it misplaces, and what an attacker who abuses it
gains — a secret, a deploy, a poisoned artifact. Pipeline findings are often critical because the
blast radius is "everything this pipeline touches" — make that radius explicit.
