# Tools

Small, self-contained scripts written while hunting. Each documents its usage at the top
and does exactly one thing. None sends traffic unless you point it at a URL explicitly.

| Tool | What it does |
|---|---|
| `js_endpoints.py` | Pull candidate API paths and URLs out of JS bundles (local files / stdin). |
| `header_audit.py` | Fetch a URL and report present/missing security headers. |

## Conventions

- Read-only by default; anything that touches the network says so in its docstring.
- Only run network tools against targets you're authorized to test, with any required
  research/identification header set.
