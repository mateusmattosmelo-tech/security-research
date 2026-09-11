# Dependency Confusion

Dependency confusion is a supply-chain bug: if a project depends on an **internal** package name
that isn't claimed on the **public** registry, an attacker publishes a malicious package under
that name and the build may pull the attacker's version. It's found entirely from public
artifacts.

## How to look

1. **Collect the package names a target references.** Read `package.json`, `requirements.txt`,
   `pyproject.toml`, `go.mod`, `pom.xml` in the org's public repos, CI configs, and Dockerfiles.
2. **Separate internal from public.** Internal names are the ones that look private, are pinned to
   versions you can't find publicly, or point at a private registry in `.npmrc` / `pip.conf`.
3. **Check the public registry for each.** For npm: `GET https://registry.npmjs.org/<name>`.
   For PyPI: `GET https://pypi.org/pypi/<name>/json`.
   - **404 on the public registry** for a name the build installs = candidate.
   - **200** = already claimed (by the org or someone else) = not squattable by you.

## The scope caveat that saves you a false alarm

**Scoped npm packages (`@org/name`) are protected by scope ownership.** If the org owns the
`@org` scope (i.e. it has published at least one public `@org/...` package), nobody else can
publish `@org/anything`. So an unpublished `@org/internal-thing` is *not* a dependency-confusion
target — the scope blocks the squat. Only **unscoped** internal names, or scopes the org doesn't
own, are actually claimable.

The same logic applies to any registry with namespace/ownership controls — check who owns the
namespace before calling it exploitable.

## Confirming responsibly

Do **not** publish a package that executes code on install to prove this — that runs on real
build machines. If a program wants confirmation, publish a benign package that only phones home
a harmless canary (or none at all), coordinate first, and remove it immediately. Usually the
dangling name + registry 404 + the reference in the build is enough for triage.

## Reporting

State the exact internal name, where the build references it, and the registry 404 that shows
it's unclaimed. Call out the namespace-ownership status explicitly — it's the difference between
a real finding and a non-issue.
