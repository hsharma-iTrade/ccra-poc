"""Internal account-manager escalation drafter.

Per PRD UC-005 (POC scope): when a payment exception is detected,
draft a brief INTERNAL escalation to the customer's Account Manager
(the iTN-internal salesperson who owns the relationship). The AM will
then phone the customer.

CCRA is NOT writing customer-facing copy - all drafts here are
internal escalations from the AR Team to the AM.
"""

from __future__ import annotations

from decimal import Decimal


def _fmt(amount) -> str:
    if amount is None:
        return "$0.00"
    return f"${Decimal(str(amount)):,.2f}"


def _first_name(full_name: str) -> str:
    if not full_name:
        return "there"
    return full_name.strip().split()[0]


def _classification_summary(
    classification: str,
    flags: list[str],
    invoice_number: str,
    invoiced_str: str,
    paid_str: str,
    delta_str: str,
    check_number: str,
) -> str:
    """One-line factual summary of what was detected."""
    chk = f" (check #{check_number})" if check_number else ""
    if classification == "UNDERPAID":
        return (
            f"Detected: UNDERPAID on invoice {invoice_number}. "
            f"Expected {invoiced_str}, received {paid_str}{chk} - "
            f"short by {delta_str}."
        )
    if classification == "OVERPAID":
        if "DUPLICATE" in (flags or []):
            return (
                f"Detected: OVERPAID / DUPLICATE on invoice {invoice_number}. "
                f"Invoice already paid in full; additional {paid_str}{chk} "
                f"received (surplus {delta_str})."
            )
        return (
            f"Detected: OVERPAID on invoice {invoice_number}. "
            f"Expected {invoiced_str}, received {paid_str}{chk} - "
            f"surplus of {delta_str}."
        )
    if classification == "UNMATCHED":
        return (
            f"Detected: UNMATCHED. Payment of {paid_str}{chk} references "
            f"invoice {invoice_number}, but no invoice with that number "
            f"was found in our system."
        )
    # MATCHED with flags (typically PAYER_MISMATCH only)
    return (
        f"Detected: PAYER_MISMATCH on invoice {invoice_number}. "
        f"Amount {paid_str}{chk} matches the invoice balance, but the "
        f"payer name on the payment did not match our customer of record."
    )


def draft_follow_up(
    classification: str,
    flags: list[str],
    payer_name: str,
    invoice_number: str,
    invoiced_amount,
    paid_amount,
    delta_amount,
    contact_email: str = "",  # kept for back-compat; not used in body
    check_number: str = "",
    customer_name: str = "",
    account_manager_name: str = "",
    account_manager_email: str = "",
) -> dict:
    """Build an INTERNAL escalation email to the Account Manager.

    Returns dict with: to, to_name, subject, body, customer_name.
    """

    abs_delta = abs(Decimal(str(delta_amount or 0)))
    invoiced_str = _fmt(invoiced_amount)
    paid_str = _fmt(paid_amount)
    delta_str = _fmt(abs_delta)

    # Display values
    cust = customer_name or payer_name or "(unknown customer)"
    am_name = account_manager_name or "(unassigned Account Manager)"
    am_email = account_manager_email or "(no AM email on file)"
    am_first = _first_name(account_manager_name)

    subject = f"Payment exception - {cust} - {invoice_number}"

    detected_line = _classification_summary(
        classification=classification,
        flags=flags or [],
        invoice_number=invoice_number,
        invoiced_str=invoiced_str,
        paid_str=paid_str,
        delta_str=delta_str,
        check_number=check_number,
    )

    # Build the factual summary block (one fact per line)
    facts = [
        f"  - Customer:           {cust}",
        f"  - Invoice #:          {invoice_number}",
        f"  - Amount expected:    {invoiced_str}",
        f"  - Amount paid:        {paid_str}",
        f"  - Delta:              {delta_str}",
        f"  - Classification:     {classification}",
    ]
    if flags:
        facts.append(f"  - Flags:              {', '.join(flags)}")
    if check_number:
        facts.append(f"  - Check / ref #:      {check_number}")
    if payer_name and customer_name and payer_name.strip().lower() != customer_name.strip().lower():
        facts.append(f"  - Payer name on remit: {payer_name}")

    facts_block = "\n".join(facts)

    body = (
        f"Hi {am_first},\n\n"
        f"{detected_line}\n\n"
        f"Summary:\n"
        f"{facts_block}\n\n"
        f"Could you reach out to {cust} to confirm and resolve? "
        f"Let me know if you need any additional context from the "
        f"remittance.\n\n"
        f"Thanks,\nAR Team"
    )

    return {
        "to": am_email,
        "to_name": am_name,
        "subject": subject,
        "body": body,
        "customer_name": cust,
    }
