from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from invoice import calculate_invoice


class InvoiceTests(unittest.TestCase):
    def test_partner_invoice(self) -> None:
        result = calculate_invoice(
            [{"quantity": 2, "unit_price": 10.0}, {"quantity": 1, "unit_price": 5.0}],
            "partner",
        )
        self.assertEqual(
            {"subtotal": 25.0, "discount": 2.5, "tax": 4.5, "total": 27.0},
            result,
        )

    def test_rejects_invalid_line(self) -> None:
        with self.assertRaisesRegex(ValueError, "quantity"):
            calculate_invoice([{"quantity": -1, "unit_price": 5.0}], "standard")

    def test_rejects_unknown_tier(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown customer tier"):
            calculate_invoice([], "unknown")


if __name__ == "__main__":
    unittest.main()
