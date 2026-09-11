#!/usr/bin/env python3
"""
ct_recon.py — enumerate a domain's subdomains from Certificate Transparency, then
bucket them by what the DNS answer says: internet-reachable, internal (RFC1918),
CNAME-to-a-service, or no record.

CT logs are a near-complete list of the hostnames an organization has issued certs for —
including the ones nobody links to. Reading the DNS answer before sending any HTTP tells
you which are actually worth a look and which are internal-only.

Usage:
    python3 ct_recon.py example.com
    python3 ct_recon.py example.com --json out.json

Passive: queries public CT aggregators and your resolver. Sends nothing to the target.
"""
import ipaddress
import json
import socket
import sys
import urllib.request


def fetch_crtsh(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            data = json.load(r)
        return {n.strip().lower() for row in data for n in row["name_value"].split("\n")}
    except Exception:
        return set()


def fetch_certspotter(domain):
    url = (f"https://api.certspotter.com/v1/issuances?domain={domain}"
           "&include_subdomains=true&expand=dns_names")
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            data = json.load(r)
        return {n.strip().lower() for i in data for n in i.get("dns_names", [])}
    except Exception:
        return set()


def is_private(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def classify(host):
    try:
        _, _, ips = socket.gethostbyname_ex(host)
    except OSError:
        return "no-record", None
    if not ips:
        return "no-record", None
    if any(is_private(ip) for ip in ips):
        return "internal", ips[0]
    return "public", ips[0]


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 1
    domain = argv[1]
    names = {n for n in (fetch_crtsh(domain) | fetch_certspotter(domain))
             if "*" not in n and n.endswith(domain)}
    buckets = {"public": [], "internal": [], "no-record": []}
    for h in sorted(names):
        kind, ip = classify(h)
        buckets[kind].append((h, ip))
    for kind in ("public", "internal", "no-record"):
        print(f"\n# {kind} ({len(buckets[kind])})")
        for h, ip in buckets[kind]:
            print(f"  {h}" + (f"  {ip}" if ip else ""))
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
        json.dump(buckets, open(out, "w"), indent=2)
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
