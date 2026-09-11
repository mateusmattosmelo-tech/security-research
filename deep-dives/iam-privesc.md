# Cloud IAM Privilege Escalation — Deep Dive

Once you hold cloud credentials (from an SSRF-to-metadata read, a leaked key, an over-scoped CI
token), the question is what they can do — and whether a limited identity can escalate to a
powerful one. These are the well-documented escalation primitives (AWS/GCP), for authorized
testing; enumerate read-only first and never touch resources outside your engagement.

## First: know who you are, quietly

```
aws sts get-caller-identity            # who am I (read-only, safe)
aws iam get-account-authorization-details   # if allowed, the full policy graph
gcloud auth list; gcloud config list
```

Enumerate your own permissions before acting. Tools like Pacu (AWS) / ScoutSuite / cloudsplaining
map effective permissions; the manual path is reading attached policies. Prefer read/describe/list
calls — they're low-risk and reveal the escalation surface.

## AWS escalation primitives (the classic set)

Rhino Security documented ~20+ paths; the recurring shapes:

- **`iam:CreateAccessKey` on another user** → mint keys for a more privileged user.
- **`iam:CreatePolicyVersion` / `SetDefaultPolicyVersion`** → rewrite a policy you can edit to
  grant `*`.
- **`iam:AttachUserPolicy`/`PutUserPolicy`/`AttachRolePolicy`** → attach `AdministratorAccess`.
- **`iam:PassRole` + a compute service** (`ec2:RunInstances`, `lambda:CreateFunction`+`Invoke`,
  `glue`, `cloudformation`, `codebuild`, `sagemaker`, `datapipeline`) → run code *as* a role more
  powerful than you, then use its creds. `PassRole`+`RunInstances`+SSRF-the-new-box is the textbook
  chain.
- **`iam:UpdateAssumeRolePolicy`** → let yourself assume a privileged role.
- **`sts:AssumeRole`** on a role whose trust policy is too broad.
- **`lambda:UpdateFunctionCode`** on a function that runs with a privileged role.

Each is "an edit permission on IAM/compute that indirectly grants more than the caller has."

## GCP escalation primitives

- **`iam.serviceAccounts.getAccessToken` / `actAs`** on a more privileged service account → get its
  token.
- **`iam.serviceAccountKeys.create`** → persistent key for a privileged SA.
- **`iam.serviceAccounts.implicitDelegation`**, **`setIamPolicy`** on a resource → grant yourself.
- **Deploy-as-SA:** create a Cloud Function / Cloud Run / GCE instance running as a privileged SA
  and read its token from that instance's metadata (SSRF-to-metadata again, now from your box).
- **`iam.roles.update`** on a custom role you're bound to → add permissions.

## The metadata pivot (ties back to SSRF)

On a compromised instance, the metadata service hands out the attached role/SA token. So the chain
is often: SSRF → metadata → role creds → (this doc) enumerate → escalate → broader access. And in
reverse: an escalation that lets you *deploy* compute lets you read a better token from the new
box's metadata.

## Lateral & data reach (post-escalation)

With a powerful identity: assume roles across accounts (org trust), read secrets
(`secretsmanager`/`ssm`/Secret Manager), snapshot/read storage across the account, and in worst
cases cross the **tenant boundary** if the identity spans tenants. On a bug-bounty target,
demonstrating cross-tenant access is the critical-tier finding — but stop at the minimum proof.

## Testing discipline (this one matters a lot)

- **Read-only by default.** `get-caller-identity`, `list*`, `describe*`, `getIamPolicy` are safe.
  Do not create/modify/delete real resources.
- If proving an escalation requires a write, use the **smallest, reversible** action, on a resource
  you created for the test, and clean up — and only if the program allows. Prefer describing the
  path (permission X exists, which per the known primitive grants Y) over performing destructive
  moves.
- **Mask credentials** everywhere. Never exfiltrate real data; a `get-caller-identity` of a role
  you shouldn't reach is often proof enough of cross-boundary access.

## Reporting

Show the starting identity (how you got it, masked), the enumerated permission that enables the
primitive, and the escalation demonstrated with the least-invasive proof — the assumed role's
`get-caller-identity`, not a data dump. Name the exact primitive and the fix (remove the dangerous
permission, tighten the trust policy / `PassRole` scope, enforce IMDSv2, least-privilege the role).
