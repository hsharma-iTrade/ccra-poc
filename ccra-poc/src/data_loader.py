"""Fixture loaders for invoices, customers, and pre-extracted payment data.

Everything in this module is deterministic: the same fixture files always
yield the same in-memory records. No wall-clock or random values are read.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Resolve fixture root relative to this file: src/ -> ccra-poc/ -> fixtures/
_FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "fixtures"


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Required fixture missing: {path}. Demo cannot run without this file."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_invoices() -> list[dict]:
    """Load the seeded invoice ledger (~20 invoices across 10 customers)."""
    return _read_json(_FIXTURES_ROOT / "invoices" / "invoices.json")


def load_customers() -> list[dict]:
    """Load the customer reference list (with mocked contact emails)."""
    return _read_json(_FIXTURES_ROOT / "invoices" / "customers.json")


def load_inbox_manifest() -> list[dict]:
    """Load the 10 inbox (email-forwarded) payment fixtures."""
    return _read_json(_FIXTURES_ROOT / "payments" / "inbox_manifest.json")


def load_upload_manifest() -> list[dict]:
    """Load the 3 upload payment fixtures."""
    return _read_json(_FIXTURES_ROOT / "payments" / "upload_manifest.json")


def load_extracted(artifact_ref: str) -> dict:
    """Load the pre-extracted JSON for a given artifact filename.

    The pre-extracted JSON sits next to its source artifact and shares its
    base filename (with a .json suffix). This is the POC's stand-in for a
    real OCR + parse pipeline (per PRD Q1).
    """
    base = artifact_ref.rsplit(".", 1)[0]
    return _read_json(_FIXTURES_ROOT / "extracted" / f"{base}.json")


def invoices_by_number(invoices: list[dict]) -> dict[str, dict]:
    """Build a lookup keyed by invoice_id for O(1) matching."""
    return {inv["invoice_id"]: inv for inv in invoices}


def customers_by_name(customers: list[dict]) -> dict[str, dict]:
    """Build a lookup keyed by customer_name (case-insensitive)."""
    return {c["customer_name"].lower(): c for c in customers}
