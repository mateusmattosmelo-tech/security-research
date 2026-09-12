# Payment & E-commerce Business Logic — Deep Dive

Checkout, pricing, and refund flows are where business-logic bugs turn directly into money. The
server often trusts the client for values it should recompute, or fails to make multi-step,
money-moving operations atomic. This maps the concrete patterns; test on your own orders/account
with the smallest amounts, and never against real transactions you don't own.

## Trust-the-client value tampering

The recurring root cause: a price/total/quantity/currency is sent by the client and used verbatim.

- **Price tampering:** the `price`/`amount`/`total` is in the request (cart, checkout, or a hidden
  field) and honored → set it to `1`, `0.01`, or `0`. The server should recompute from the product
  id server-side.
- **Negative quantity / amount:** `quantity=-1` or a negative line item → inverts the total, or
  credits your balance. Negative refunds, negative gift-card top-ups.
- **Currency swap:** pay in a weaker currency while the value is treated as the stronger
  (`amount=100&currency=IDR` charged as if USD), or a currency the processor rounds to zero.
- **Rounding / precision:** sub-cent amounts, many tiny line items, or a currency with more decimals
  than the processor handles → rounding in your favor.
- **Product/price mismatch:** buy an expensive item but reference a cheap item's price
  (`item=expensive&price_id=cheap`).

## Coupon, credit & referral abuse

- **Coupon stacking / reuse:** apply the same single-use coupon twice (sequential, or via a race —
  see below), or stack multiple that should be mutually exclusive.
- **Coupon on ineligible items**, or a percentage coupon on a value you inflate then deflate.
- **Referral/credit self-dealing:** refer yourself, or exploit that credit is granted before the
  referred action is validated.
- **Gift card / store credit:** apply, then cancel the order but keep the credit; or a race between
  redeem and refund.

## Broken / skippable workflow

- **Skip payment:** complete the post-payment step (order confirmation) without the payment step —
  replay the "success" callback, or navigate straight to the fulfillment endpoint.
- **Tamper the payment-gateway callback:** if the app trusts a client-delivered
  `status=success`/signature it doesn't verify, forge it. (Check whether the webhook signature is
  validated server-side.)
- **Reorder steps:** apply discount after tax calc, change cart after price lock, edit the order
  between authorization and capture.

## Refund & cancellation logic

- **Refund > paid:** refund an amount greater than charged, or refund to a different instrument.
- **Cancel-after-fulfillment:** get the digital good / service, then cancel for a refund.
- **Double refund:** two parallel refund requests on one order (race).

## Races on money (the amplifier)

Many of the above become reliable via the [race-condition single-packet attack](race-conditions.md):
redeem one coupon N times, withdraw/transfer the same balance twice, apply store credit
concurrently, submit two refunds. Fire ~20 parallel and measure the over-effect.

## Testing discipline (money is sensitive)

- Use **your own** account and the **smallest** amounts; prefer test/sandbox modes if the program
  provides them.
- Prove the flaw with a single minimal transaction, then stop — don't repeatedly extract value.
- Reverse/cancel your test transactions where possible, and say so in the report.

## Reporting

Show the intended request/response (control), the tampered one, and the concrete financial outcome
(paid less/nothing, credited yourself, refunded more, coupon reused N times). Quantify. Name the
root cause (client-trusted value, unverified callback, non-atomic operation) and the fix
(recompute server-side, verify webhook signatures, atomic/idempotent money operations).
