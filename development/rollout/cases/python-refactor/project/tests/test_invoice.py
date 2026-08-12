from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from invoice import calculate_invoice


def test_partner_invoice() -> None:
    result = calculate_invoice(
        [{"quantity": 2, "unit_price": 10.0}, {"quantity": 1, "unit_price": 5.0}],
        "partner",
    )
    assert result == {"subtotal": 25.0, "discount": 2.5, "tax": 4.5, "total": 27.0}


def test_rejects_invalid_line() -> None:
    with pytest.raises(ValueError, match="quantity"):
        calculate_invoice([{"quantity": -1, "unit_price": 5.0}], "standard")


def test_rejects_unknown_tier() -> None:
    with pytest.raises(ValueError, match="unknown customer tier"):
        calculate_invoice([], "unknown")
