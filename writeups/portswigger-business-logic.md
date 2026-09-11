# Lab notes — Business Logic (PortSwigger Web Security Academy)

Notes on the [business logic labs](https://portswigger.net/web-security/logic-flaws) — approach
over answers. Public practice labs; safe to write up. Pairs with
[business logic methodology](../methodology/business-logic.md).

## The recurring theme

The app does exactly what it was coded to do — and the code trusts the client to play fair. Find
the assumption, break it.

## Client-side validation only

- A limit, price, or discount enforced only in the browser. Intercept the request and send the
  value the UI wouldn't let you (a negative quantity, a lower price, a huge number). The server
  accepts it because it never re-checked.

## Trusting client-supplied values

- A price, total, or currency sent in the request and used verbatim. Change the amount; change the
  quantity to negative to invert a total; buy an expensive item by tampering the product/price
  pairing.

## Broken/assumed workflow

- Steps assumed to happen in order. Skip a step (complete checkout without the payment step),
  repeat a one-time step (apply a coupon twice), or perform a later step directly without the
  earlier ones.

## Trusting extra input the flow didn't intend

- A parameter the UI never sends but the server honors (`role`, `isAdmin`, an email domain that
  grants access, an "email" field that changes which account is affected).

## Insufficient checks on inputs' relationships

- Two fields that must agree but aren't cross-checked (the account you pay *from* vs. the one you
  own; a discount code vs. eligibility). Mismatch them.

## How to work them

1. Map the intended flow end to end and note every value the client controls.
2. For each, ask: does the server re-validate this, or trust it? Then test exactly that.
3. Prove impact with the intended flow as a control, then the broken flow, then the concrete
   outcome (money, access, a state that shouldn't exist).

## Reporting

Show the intended request/response, the tampered one, and the concrete gain. Business logic bugs
are product-specific and rarely duplicated — a clear "with X I got Y" is the whole report.
