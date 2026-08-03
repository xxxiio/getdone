"""Invoice calculation used by the rollout refactoring case."""

from __future__ import annotations


def _line_total(line: dict[str, float]) -> float:
    quantity = line["quantity"]
    unit_price = line["unit_price"]
    if quantity < 0:
        raise ValueError("quantity must be non-negative")
    if unit_price < 0:
        raise ValueError("unit_price must be non-negative")
    return quantity * unit_price


def _discount_rate(customer_tier: str) -> float:
    rates = {"standard": 0.0, "preferred": 0.05, "partner": 0.10}
    try:
        return rates[customer_tier]
    except KeyError as exc:
        raise ValueError(f"unknown customer tier: {customer_tier}") from exc


def _rounded_result(subtotal: float, discount_rate: float) -> dict[str, float]:
    discount = subtotal * discount_rate
    taxable = subtotal - discount
    tax = taxable * 0.20
    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "total": round(taxable + tax, 2),
    }


def calculate_invoice(lines: list[dict[str, float]], customer_tier: str) -> dict[str, float]:
    subtotal = sum(_line_total(line) for line in lines)
    return _rounded_result(subtotal, _discount_rate(customer_tier))
