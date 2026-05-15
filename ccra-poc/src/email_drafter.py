"""Template-based follow-up email drafter.

Per PRD UC-005: produce a pre-composed email body based on the
exception classification. No outbound send - clipboard only.
"""

from __future__ import annotations

from decimal import Decimal


def _fmt(amount) -> str:
    if amount is None:
        return "$0.00"
    return f"${Decimal(str(amount)):,.2f}"


def draft_follow_up(
    classification: str,
    flags: list[str],
    payer_name: str,
    invoice_number: str,
    invoiced_amount,
    paid_amount,
    delta_amount,
    contact_email: str = "",
    check_number: str = "",
) -> dict:
    """Build a follow-up email draft. Returns dict with subject, to, body."""

    abs_delta = abs(Decimal(str(delta_amount or 0)))
    invoiced_str = _fmt(invoiced_amount)
    paid_str = _fmt(paid_amount)
    delta_str = _fmt(abs_delta)

    is_duplicate = "DUPLICATE" in (flags or [])
    is_payer_mismatch = "PAYER_MISMATCH" in (flags or [])

    if classification == "UNDERPAID":
        subject = f"Re: Payment for {invoice_number} - short by {delta_str}"
        body = (
            f"Hi {payer_name},\n\n"
            f"Thank you for your recent payment"
            f"{f' (check #{check_number})' if check_number else ''}. "
            f"We received {paid_str} applied to invoice {invoice_number}, "
            f"which has an outstanding balance of {invoiced_str}. "
            f"That leaves a short-pay of {delta_str}.\n\n"
            f"Could you please confirm whether this short-pay is intentional "
            f"(e.g., a claim or credit being applied) and, if so, let us know "
            f"the reason so we can update our records? If it was unintentional, "
            f"please send a follow-up payment for the difference at your "
            f"earliest convenience.\n\n"
            f"Thanks,\nAR Team"
        )
    elif classification == "OVERPAID":
        subject = f"Re: Overpayment on {invoice_number} - {delta_str} surplus"
        if is_duplicate:
            body = (
                f"Hi {payer_name},\n\n"
                f"We received a payment of {paid_str} referencing invoice "
                f"{invoice_number}, but our records show this invoice has "
                f"already been paid in full. The {paid_str} appears to be an "
                f"additional payment.\n\n"
                f"Could you please clarify whether this was intended for another "
                f"open invoice, or would you like us to issue a refund / apply "
                f"it as a credit on your account?\n\n"
                f"Thanks,\nAR Team"
            )
        else:
            body = (
                f"Hi {payer_name},\n\n"
                f"Thank you for your payment"
                f"{f' (check #{check_number})' if check_number else ''}. "
                f"We received {paid_str} applied to invoice {invoice_number} "
                f"(balance {invoiced_str}). This leaves an overpayment of "
                f"{delta_str}.\n\n"
                f"How would you like us to apply the surplus - as a credit on "
                f"your account, or against a specific other invoice? Please let "
                f"us know so we can post it correctly.\n\n"
                f"Thanks,\nAR Team"
            )
    elif classification == "UNMATCHED":
        subject = f"Payment received - invoice {invoice_number} not found"
        body = (
            f"Hi {payer_name},\n\n"
            f"We received a payment of {paid_str}"
            f"{f' (check #{check_number})' if check_number else ''} "
            f"referencing invoice number {invoice_number}, but we could not "
            f"locate an invoice with that number in our system.\n\n"
            f"Could you please confirm:\n"
            f"  - The correct invoice number(s) this payment is intended for, "
            f"or\n"
            f"  - A copy of the original invoice if you believe it was issued "
            f"by us\n\n"
            f"so we can apply the payment correctly?\n\n"
            f"Thanks,\nAR Team"
        )
    else:  # MATCHED with flags (typically PAYER_MISMATCH only)
        subject = f"Payment received for {invoice_number} - payer name clarification"
        body = (
            f"Hi {payer_name},\n\n"
            f"We received a payment of {paid_str} for invoice {invoice_number}. "
            f"The amount matches the invoice balance, but the payer name on the "
            f"payment did not match our customer of record for this invoice. "
            f"Could you confirm this payment was issued on behalf of the "
            f"invoiced customer so we can record it correctly?\n\n"
            f"Thanks,\nAR Team"
        )

    if is_payer_mismatch and classification != "MATCHED":
        body += (
            "\n\nNote: The payer name on the payment did not match our customer "
            "of record for this invoice - please confirm this payment is "
            "associated with the correct account."
        )

    return {
        "to": contact_email or "(no contact email on file)",
        "subject": subject,
        "body": body,
    }
