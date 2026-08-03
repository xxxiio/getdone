"""Invoice calculation used by the rollout refactoring case."""

from __future__ import annotations


def calculate_invoice(lines: list[dict[str, float]], customer_tier: str) -> dict[str, float]:
    subtotal = 0.0
    for line in lines:
        quantity = line["quantity"]
        unit_price = line["unit_price"]
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        if unit_price < 0:
            raise ValueError("unit_price must be non-negative")
        subtotal += quantity * unit_price

    if customer_tier == "standard":
        discount_rate = 0.0
    elif customer_tier == "preferred":
        discount_rate = 0.05
    elif customer_tier == "partner":
        discount_rate = 0.10
    else:
        raise ValueError(f"unknown customer tier: {customer_tier}")

    discount = subtotal * discount_rate
    taxable = subtotal - discount
    tax = taxable * 0.20
    total = taxable + tax
    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
    }
