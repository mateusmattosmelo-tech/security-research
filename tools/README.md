# Tools

Small, self-contained scripts written while hunting. Each documents its usage at the top and
does one thing. Network tools say so in their docstring — run them only against targets you're
authorized to test, with any required research/identification header set.

| Tool | What it does | Network? |
|---|---|---|
| `ct_recon.py` | CT-log subdomain enumeration + DNS bucketing (public/internal/CNAME). | passive |
| `takeover_scan.py` | Check hosts for dangling-service (subdomain takeover) fingerprints. | yes |
| `js_endpoints.py` | Extract API paths/URLs from JS bundles. | no |
| `header_audit.py` | Report present/missing security headers for a URL. | yes |
| `cors_probe.py` | Detect reflected-Origin-with-credentials CORS misconfig. | yes |
| `oauth_redirect_probe.py` | Test redirect_uri validation on an OAuth authorize endpoint. | yes |
| `workflow_audit.py` | Flag GitHub Actions injection / pwn-request patterns (static). | no |

## Conventions
- Read-only by default; anything that touches the network says so.
- Findings from heuristic tools are triage leads, not proof — confirm by hand.
