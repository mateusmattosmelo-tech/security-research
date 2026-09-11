#!/usr/bin/env python3
"""
report_pack.py — turn an evidence directory into a report skeleton + attachment manifest.

Given a folder of evidence (screenshots, request/response logs), it emits a report template in the
common HackerOne field order and a manifest listing every attachment, so nothing in the folder is
uncited and no cited attachment is missing. It fills nothing in for you — the bytes and the claims
are yours to write.

Usage:
    python3 report_pack.py evidence/my-finding/ > report-skeleton.md

Reads local files only; sends no traffic.
"""
import os
import sys

FIELD_ORDER = [
    ("Title", "<where + what + consequence, <=80 chars, no severity prefix>"),
    ("Asset", "<exact in-scope asset from the policy>"),
    ("Weakness", "<CWE / class, e.g. Improper Authorization>"),
    ("Severity", "<the rating, with the metric that carries it on one line>"),
]

BODY = """
## Summary
<2-4 sentences: what, where, and what an attacker gains. Lead with the fact that carries severity.>

## Steps To Reproduce
1. <prerequisite block before step 1: accounts, headers>
2. <command in a code block; each step ends with the real observed result>

## Proof of Concept
<the decisive request/response or oracle contrast; reference attachments by name>

## Recommended Fix
- <specific, 1-3 items>

## Supporting Material/References
{supporting}

## Customer Impact
<direct harm to the user, measured>

## Business Impact
<direct harm to the business, measured; potential impact marked as extension>
"""


def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print(__doc__.strip())
        return 1
    d = argv[1]
    files = sorted(f for f in os.listdir(d)
                   if os.path.isfile(os.path.join(d, f)) and not f.startswith("."))
    print("<!-- report skeleton — fill every <...>; every attachment below must be cited -->\n")
    for name, hint in FIELD_ORDER:
        print(f"**{name}:** {hint}")
    supporting = "\n".join(f"  * {f} — <what it proves>" for f in files) or "  * <none yet>"
    print(BODY.format(supporting=supporting))
    print("\n---\n# Attachment manifest")
    if not files:
        print("(no files in the evidence directory yet)")
    for f in files:
        size = os.path.getsize(os.path.join(d, f))
        print(f"  {f}  ({size} bytes)")
    print("\nChecklist: each attachment cited in the body? each claim backed by an attachment? "
          "secrets masked? positive + negative control present?")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
