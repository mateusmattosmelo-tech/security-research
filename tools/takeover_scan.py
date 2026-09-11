#!/usr/bin/env python3
"""
takeover_scan.py — check a list of hosts for dangling-service (subdomain takeover)
fingerprints.

A subdomain that CNAMEs to a service where the backing resource is gone can be claimed by
anyone. Each service has a tell in its response when the resource is missing. This reads the
CNAME chain and the HTTP body and flags the known "it's gone" signatures.

Usage:
    python3 takeover_scan.py hosts.txt
    echo sub.example.com | python3 takeover_scan.py -

A dangling record is a *candidate*, not a confirmed takeover — modern providers may block the
claim via domain verification. Confirm deliberately and never with harmful content.
"""
import subprocess
import sys
import urllib.request

# service -> substring that means "the backing resource is gone"
FINGERPRINTS = {
    "GitHub Pages": ["there isn't a github pages site here", "site not found · github pages"],
    "AWS S3": ["nosuchbucket", "the specified bucket does not exist"],
    "CloudFront": ["nosuchdistribution", "the request could not be satisfied"],
    "Heroku": ["no such app", "herokucdn.com/error-pages/no-such-app.html"],
    "Fastly": ["fastly error: unknown domain"],
    "Cloud PaaS/Pages": ["project not found", "nothing is here yet", "deploy your"],
    "Netlify": ["not found - request id"],
    "Shopify": ["sorry, this shop is currently unavailable"],
}


def cname_chain(host):
    try:
        out = subprocess.run(["dig", "+short", host, "CNAME"],
                             capture_output=True, text=True, timeout=10)
        return [c.rstrip(".") for c in out.stdout.split() if c]
    except Exception:
        return []


def body(host):
    for scheme in ("https", "http"):
        try:
            req = urllib.request.Request(f"{scheme}://{host}/",
                                         headers={"User-Agent": "takeover-scan/1.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                return r.read(8192).decode("utf-8", "ignore").lower()
        except urllib.error.HTTPError as e:
            try:
                return e.read(8192).decode("utf-8", "ignore").lower()
            except Exception:
                return ""
        except Exception:
            continue
    return ""


def scan(host):
    cn = cname_chain(host)
    b = body(host)
    for service, sigs in FINGERPRINTS.items():
        if any(s in b for s in sigs):
            return host, cn, service
    return host, cn, None


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    src = sys.stdin if argv[1] == "-" else open(argv[1])
    hosts = [l.strip() for l in src if l.strip()]
    for h in hosts:
        host, cn, service = scan(h)
        chain = " -> ".join(cn) if cn else "(no CNAME)"
        flag = f"  *** DANGLING: {service} ***" if service else ""
        print(f"{host}  {chain}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
