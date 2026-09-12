# SAML XML Signature Wrapping — Deep Dive

SAML asserts identity as signed XML. The signature protects *an* element; the app reads identity
from *some* element. When those two aren't guaranteed to be the same element, an attacker keeps a
validly-signed element to pass the signature check while injecting a second, unsigned element that
the app actually reads. That's XML Signature Wrapping (XSW). This is the mechanic level; test only
against your own IdP/SP accounts.

## The two references that must agree

- **What is signed:** the `<ds:Signature>` contains a `<ds:Reference URI="#_id">` pointing at the
  element it covers, plus a digest of that element.
- **What is consumed:** the SP's code selects an element (often "the Assertion") and reads
  `Subject/NameID`, `AttributeStatement`, `Conditions`.

XSW exploits a gap between **signature verification** (does *a* valid signature over *some*
referenced element exist?) and **assertion processing** (which element does the business logic
read?). If verification and processing resolve the element differently — by id, by position, by
first-match, by XPath — you win.

## The wrapping variants (XSW1–XSW8)

The families, by where the malicious (evil) assertion goes relative to the signed (original) one
and where the signature ends up:

- **XSW1/2 (signature over the Response):** add a forged Response/Assertion as a sibling; the
  original signed element is kept (sometimes moved into an `<Object>` or as a sibling) so the
  signature still validates, while the processor reads the forged one.
- **XSW3/4 (signature over the Assertion):** inject an evil Assertion as a sibling of, or wrapping,
  the original signed Assertion. Processor picks the evil one; verifier still finds the original.
- **XSW5/6:** the signature's `Reference` still points at the original, but the original is embedded
  inside the evil assertion (or moved), so digest matches while the read element is attacker's.
- **XSW7/8:** hide the original signed assertion inside an `<Extensions>` or an `<Object>` element
  (elements the schema allows but the processor ignores for identity), leaving the evil assertion
  as the one processed.

The common trick across all: give the evil assertion a **different (or absent) `ID`**, or place it
where the processor's element selection (getElementsByTagName first-match, XPath, id-lookup that
returns the wrong node) picks it, while the signature library re-finds the original by its
`Reference URI`.

## How to test methodically

1. Capture a **valid** signed SAML response for your own account (from a real IdP login).
2. For each XSW variant, build the modified XML: duplicate the assertion, change the copy's `NameID`
   to the victim identity (a second account you own), set/remove `ID`s per the variant, and place
   the original signed element where verification still finds it.
3. Submit to the SP's ACS endpoint and observe: does it log you in as the injected identity?
   (SAML Raider / a script automate all eight.)
4. The one that works reveals exactly how the SP's verification and processing disagree.

## Adjacent SAML bugs to try alongside

- **No signature check at all:** strip `<Signature>` → accepted? (Some SPs verify only if present.)
- **Comment/canonicalization injection:** `NameID` = `admin@corp.com<!---->.evil` — a parser that
  truncates at the comment during read but not during digest lets you change the effective NameID.
- **Missing `Recipient`/`Audience`/`Destination`** → assertion replay across SPs.
- **`NotOnOrAfter` not enforced** → replay old assertions.
- **`KeyInfo` trusted from the message** → supply your own cert (the SP must pin the IdP cert).
- **XXE in the SAML parser** (it's XML — see the XXE deep-dive).

## Reporting

Show the original vs. wrapped XML with the exact structural change (which variant, where the evil
assertion sits, the id juggling), the SP accepting it, and login as a *different* identity you
control. Name the root cause: verification and processing selecting different elements. Fix:
verify and read the **same** element (schema-hardened, id-uniqueness-enforced parsing), pin the
IdP certificate, and enforce audience/recipient/timing.
