"""Exact-cents matching engine for the CCRA POC.

Per PRD UC-003: every Remittance Line is classified into exactly one of
MATCHED / UNDERPAID / OVERPAID / UNMATCHED, with independent DUPLICATE
and PAYER_MISMATCH flags. Tolerance is exact-cents (no fuzz, per Q3).

The engine is pure: it takes inputs and returns deterministic outputs.
No I/O, no clocks, no randomness.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def _to_decimal(value: Any) -> Decimal:
    """Coerce JSON numeric values to Decimal for exact-cents arithmetic."""
    return Decimal(str(value))


def classify_remittance_line(
    line: dict,
    invoices_lookup: dict[str, dict],
    payer_name: str,
) -> dict:
    """Classify one Remittance Line and return its Match Result.

    Returns a dict with: classification, flags (list), delta_amount,
    invoice_id (None when UNMATCHED), open_balance_at_match.
    """
    invoice_number = line.get("invoice_number", "").strip()
    line_amount = _to_decimal(line.get("line_amount", 0))
    invoice = invoices_lookup.get(invoice_number)

    flags: list[str] = []

    # Case 1: invoice not in ledger
    if invoice is None:
        return {
            "classification": "UNMATCHED",
            "flags": flags,
            "delta_amount": line_amount,  # full amount is "extra" against nothing
            "invoice_id": None,
            "open_balance_at_match": None,
            "customer_name_of_record": None,
        }

    open_balance = _to_decimal(invoice["open_balance"])
    customer_of_record = invoice["customer_name"]

    # Payer mismatch is an independent flag
    if payer_name and payer_name.strip().lower() != customer_of_record.strip().lower():
        flags.append("PAYER_MISMATCH")

    # Case 2: invoice already fully paid -> DUPLICATE flag + classification
    if open_balance == Decimal("0"):
        flags.append("DUPLICATE")
        # Treat the comparison as overpayment-against-zero for delta
        delta = line_amount - open_balance
        if line_amount > 0:
            classification = "OVERPAID"
        else:
            classification = "MATCHED"
        return {
            "classification": classification,
            "flags": flags,
            "delta_amount": delta,
            "invoice_id": invoice["invoice_id"],
            "open_balance_at_match": open_balance,
            "customer_name_of_record": customer_of_record,
        }

    # Case 3: invoice has open balance; compare amounts (exact-cents)
    delta = line_amount - open_balance
    if delta == Decimal("0"):
        classification = "MATCHED"
    elif delta < Decimal("0"):
        classification = "UNDERPAID"
    else:
        classification = "OVERPAID"

    return {
        "classification": classification,
        "flags": flags,
        "delta_amount": delta,
        "invoice_id": invoice["invoice_id"],
        "open_balance_at_match": open_balance,
        "customer_name_of_record": customer_of_record,
    }


def match_payment(payment: dict, invoices_lookup: dict[str, dict]) -> list[dict]:
    """Run the matching engine across every Remittance Line in a Payment.

    Returns a list of Match Result dicts, one per Remittance Line, in the
    same order as the input lines.
    """
    payer_name = payment.get("payer_name", "")
    results = []
    for line in payment.get("remittance_lines", []):
        result = classify_remittance_line(line, invoices_lookup, payer_name)
        # Attach the original line for downstream display
        result["line"] = line
        results.append(result)
    return results


def rollup_payment_status(match_results: list[dict]) -> str:
    """Produce a human-readable summary status for an entire Payment.

    Examples: "3 lines: 2 matched, 1 underpaid"; "1 line: unmatched".
    """
    if not match_results:
        return "0 lines"

    counts: dict[str, int] = {}
    for r in match_results:
        c = r["classification"].lower()
        counts[c] = counts.get(c, 0) + 1

    n = len(match_results)
    word = "line" if n == 1 else "lines"
    parts = [f"{count} {name}" for name, count in sorted(counts.items())]
    return f"{n} {word}: " + ", ".join(parts)
