"""CCRA POC - Cash Collection Reconciliation Assistant
Streamlit single-page demo per docs/refined-prd.md (POC scope).

Critical Path Journey:
  Inbox -> Use sample data -> Dashboard tiles -> click tile ->
  click row -> drilldown -> Draft email -> clipboard.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_loader import (
    customers_by_name,
    invoices_by_number,
    load_customers,
    load_extracted,
    load_inbox_manifest,
    load_invoices,
    load_upload_manifest,
)
from src.email_drafter import draft_follow_up
from src.matching_engine import match_payment, rollup_payment_status

# ----------------------------------------------------------------------------
# Page config + global CSS
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="CCRA - Cash Collection Reconciliation Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      /* Tile styling */
      .tile {
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }
      .tile-matched   { border-left: 6px solid #16a34a; }
      .tile-underpaid { border-left: 6px solid #ea580c; }
      .tile-overpaid  { border-left: 6px solid #2563eb; }
      .tile-unmatched { border-left: 6px solid #dc2626; }
      .tile-label { font-size: 13px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
      .tile-value { font-size: 36px; font-weight: 700; color: #111827; }
      .tile-sub { font-size: 12px; color: #9ca3af; margin-top: 4px; }

      .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 4px;
      }
      .b-matched   { background: #dcfce7; color: #166534; }
      .b-underpaid { background: #ffedd5; color: #9a3412; }
      .b-overpaid  { background: #dbeafe; color: #1e40af; }
      .b-unmatched { background: #fee2e2; color: #991b1b; }
      .b-flag      { background: #fef3c7; color: #92400e; }

      .artifact-preview {
        background: #f9fafb;
        border: 1px dashed #d1d5db;
        border-radius: 8px;
        padding: 16px;
        font-family: 'SF Mono', Menlo, monospace;
        font-size: 12px;
        color: #374151;
        white-space: pre-wrap;
      }

      .stButton > button {
        border-radius: 8px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Session state init
# ----------------------------------------------------------------------------

def _init_state():
    if "page" not in st.session_state:
        st.session_state.page = "inbox"  # 'inbox' | 'dashboard'
    if "payments" not in st.session_state:
        # list of dicts: {payment_id, source_channel, payer_name, ...,
        # remittance_lines, match_results, artifact_ref, ...}
        st.session_state.payments = []
    if "ingested_fixture_ids" not in st.session_state:
        st.session_state.ingested_fixture_ids = set()
    if "selected_classification" not in st.session_state:
        st.session_state.selected_classification = None  # filter for tile click
    if "selected_payment_id" not in st.session_state:
        st.session_state.selected_payment_id = None
    if "selected_line_index" not in st.session_state:
        st.session_state.selected_line_index = None
    if "show_draft" not in st.session_state:
        st.session_state.show_draft = False


_init_state()


# Cached data loaders so we re-use loaded fixtures across reruns.
@st.cache_data
def _cached_invoices():
    return load_invoices()


@st.cache_data
def _cached_customers():
    return load_customers()


@st.cache_data
def _cached_inbox():
    return load_inbox_manifest()


@st.cache_data
def _cached_upload():
    return load_upload_manifest()


INVOICES = _cached_invoices()
CUSTOMERS = _cached_customers()
INBOX_FIXTURES = _cached_inbox()
UPLOAD_FIXTURES = _cached_upload()
INVOICES_LOOKUP = invoices_by_number(INVOICES)
CUSTOMERS_LOOKUP = customers_by_name(CUSTOMERS)


# ----------------------------------------------------------------------------
# Ingest + match
# ----------------------------------------------------------------------------

def ingest_fixture(fixture: dict, source_label: str) -> None:
    """Ingest one fixture (inbox or upload), run matching, append to session."""
    fixture_id = fixture["fixture_id"]
    if fixture_id in st.session_state.ingested_fixture_ids:
        return  # idempotent per session

    artifact_ref = fixture.get("artifact_ref") or fixture.get("filename")
    extracted = load_extracted(artifact_ref)

    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    payment = {
        "payment_id": payment_id,
        "fixture_id": fixture_id,
        "source_channel": fixture.get("source_channel", source_label),
        "received_at": fixture.get("received_at", ""),
        "payer_name": extracted.get("payer_name", ""),
        "check_number": extracted.get("check_number", ""),
        "payment_date": extracted.get("payment_date", ""),
        "total_amount": Decimal(str(extracted.get("total_amount", 0))),
        "remittance_lines": extracted.get("remittance_lines", []),
        "extraction_status": extracted.get("extraction_status", "EXTRACTED"),
        "artifact_ref": artifact_ref,
        "fixture_meta": fixture,
    }
    # Run the matching engine
    payment["match_results"] = match_payment(payment, INVOICES_LOOKUP)
    payment["rollup_status"] = rollup_payment_status(payment["match_results"])

    st.session_state.payments.append(payment)
    st.session_state.ingested_fixture_ids.add(fixture_id)


def ingest_all_sample_data():
    """Use sample data: ingest all 10 inbox + 3 upload fixtures at once."""
    for fix in INBOX_FIXTURES:
        ingest_fixture(fix, "EMAIL")
    for fix in UPLOAD_FIXTURES:
        ingest_fixture(fix, "UPLOAD")


# ----------------------------------------------------------------------------
# Computed views
# ----------------------------------------------------------------------------

def all_match_rows() -> pd.DataFrame:
    """Flatten every Match Result across every Payment into one DataFrame.

    Each row = one Remittance Line + its Match Result + Payment context.
    """
    rows = []
    for payment in st.session_state.payments:
        for idx, mr in enumerate(payment["match_results"]):
            line = mr["line"]
            invoice_id = mr.get("invoice_id")
            inv = INVOICES_LOOKUP.get(invoice_id) if invoice_id else None
            invoiced = inv["open_balance"] if inv else None
            paid = float(line.get("line_amount", 0))
            delta = float(mr.get("delta_amount", 0))
            customer_name = (
                mr.get("customer_name_of_record")
                or payment["payer_name"]
                or "(unknown)"
            )
            rows.append(
                {
                    "payment_id": payment["payment_id"],
                    "line_index": idx,
                    "customer": customer_name,
                    "payer_name": payment["payer_name"],
                    "invoice_number": line.get("invoice_number", ""),
                    "classification": mr["classification"],
                    "flags": ", ".join(mr.get("flags") or []),
                    "invoiced": float(invoiced) if invoiced is not None else None,
                    "paid": paid,
                    "delta": delta,
                    "source": payment["source_channel"],
                    "received_at": payment["received_at"],
                    "check_number": payment["check_number"],
                }
            )
    return pd.DataFrame(rows)


def classification_counts(df: pd.DataFrame) -> dict[str, int]:
    base = {"MATCHED": 0, "UNDERPAID": 0, "OVERPAID": 0, "UNMATCHED": 0}
    if df.empty:
        return base
    for k, v in df["classification"].value_counts().to_dict().items():
        base[k] = int(v)
    return base


# ----------------------------------------------------------------------------
# UI: header / nav
# ----------------------------------------------------------------------------

def render_header():
    left, right = st.columns([5, 2])
    with left:
        st.markdown("### 💰 CCRA - Cash Collection Reconciliation Assistant")
        st.caption(
            "Hackathon POC | Forward remittances, auto-match, surface exceptions, "
            "draft follow-ups."
        )
    with right:
        cols = st.columns(2)
        with cols[0]:
            if st.button(
                "📥 Inbox",
                use_container_width=True,
                type="primary" if st.session_state.page == "inbox" else "secondary",
            ):
                st.session_state.page = "inbox"
                st.session_state.selected_payment_id = None
                st.session_state.show_draft = False
                st.rerun()
        with cols[1]:
            if st.button(
                "📊 Dashboard",
                use_container_width=True,
                type="primary" if st.session_state.page == "dashboard" else "secondary",
            ):
                st.session_state.page = "dashboard"
                st.rerun()
    st.divider()


# ----------------------------------------------------------------------------
# UI: Inbox page
# ----------------------------------------------------------------------------

def render_inbox():
    st.markdown("## Payment Inbox")
    st.caption(
        "Forwarded remittance emails on the left, file uploads on the right. "
        "Click an item to ingest, or load the full demo set with one click."
    )

    # Primary demo button + counters
    top_left, top_right = st.columns([3, 2])
    with top_left:
        if st.button(
            "✨ Use sample data (ingest all 13 fixtures)",
            type="primary",
            use_container_width=True,
        ):
            ingest_all_sample_data()
            st.session_state.page = "dashboard"
            st.rerun()
    with top_right:
        n_ingested = len(st.session_state.payments)
        n_total = len(INBOX_FIXTURES) + len(UPLOAD_FIXTURES)
        st.metric("Ingested so far", f"{n_ingested} / {n_total}")

    st.divider()

    col_inbox, col_upload = st.columns([2, 1])

    # ----- Forwarded inbox -----
    with col_inbox:
        st.markdown("#### 📧 Forwarded Inbox (10 emails)")
        st.caption("Simulated email-forwarded remittance artifacts.")
        for fix in INBOX_FIXTURES:
            already = fix["fixture_id"] in st.session_state.ingested_fixture_ids
            with st.container(border=True):
                a, b = st.columns([4, 1])
                with a:
                    badge = "✅" if already else "•"
                    st.markdown(
                        f"**{badge} {fix['subject']}**  \n"
                        f"_{fix['from_email']}_  \n"
                        f"<span style='color:#6b7280;font-size:12px;'>"
                        f"{fix['received_at']} | {fix['source_channel']} | "
                        f"{fix['artifact_ref']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<span style='color:#374151;font-size:13px;'>"
                        f"{fix['preview_snippet']}</span>",
                        unsafe_allow_html=True,
                    )
                with b:
                    if st.button(
                        "Ingest",
                        key=f"ing_{fix['fixture_id']}",
                        disabled=already,
                        use_container_width=True,
                    ):
                        ingest_fixture(fix, "EMAIL")
                        st.rerun()

    # ----- Upload -----
    with col_upload:
        st.markdown("#### 📎 File Upload (3 fixtures)")
        st.caption("Drag-and-drop or pick from sample uploads.")

        st.file_uploader(
            "Drop a check image or PDF (POC: fixture lookup by filename)",
            type=["pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help=(
                "Per Q1, the POC bypasses live OCR. Drop a file with one of the "
                "sample filenames below or click 'Ingest' to use the fixture."
            ),
        )

        for fix in UPLOAD_FIXTURES:
            already = fix["fixture_id"] in st.session_state.ingested_fixture_ids
            with st.container(border=True):
                badge = "✅" if already else "•"
                st.markdown(
                    f"**{badge} {fix['display_label']}**  \n"
                    f"<span style='color:#6b7280;font-size:12px;'>"
                    f"{fix['filename']}</span>  \n"
                    f"<span style='color:#374151;font-size:13px;'>"
                    f"{fix['preview_snippet']}</span>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Ingest",
                    key=f"up_{fix['fixture_id']}",
                    disabled=already,
                    use_container_width=True,
                ):
                    ingest_fixture(fix, "UPLOAD")
                    st.rerun()


# ----------------------------------------------------------------------------
# UI: Dashboard page
# ----------------------------------------------------------------------------

def render_dashboard():
    st.markdown("## Exceptions Dashboard")

    if not st.session_state.payments:
        st.info(
            "No payments ingested yet. Open the **Inbox** and click "
            "**'Use sample data'** to load the demo set, or ingest individual "
            "fixtures."
        )
        return

    df = all_match_rows()
    counts = classification_counts(df)

    # Tiles
    c1, c2, c3, c4 = st.columns(4)
    tile_specs = [
        (c1, "MATCHED",   "tile-matched",   "Matched",   counts["MATCHED"]),
        (c2, "UNDERPAID", "tile-underpaid", "Underpaid", counts["UNDERPAID"]),
        (c3, "OVERPAID",  "tile-overpaid",  "Overpaid",  counts["OVERPAID"]),
        (c4, "UNMATCHED", "tile-unmatched", "Unmatched", counts["UNMATCHED"]),
    ]
    for col, code, klass, label, count in tile_specs:
        with col:
            active = st.session_state.selected_classification == code
            st.markdown(
                f"""
                <div class='tile {klass}' style='{"border: 2px solid #111827;" if active else ""}'>
                    <div class='tile-label'>{label}</div>
                    <div class='tile-value'>{count}</div>
                    <div class='tile-sub'>remittance lines</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            label_text = f"Showing: {label}" if active else f"Filter: {label}"
            if st.button(label_text, key=f"tile_{code}", use_container_width=True):
                st.session_state.selected_classification = (
                    None if active else code
                )
                st.session_state.selected_payment_id = None
                st.session_state.show_draft = False
                st.rerun()

    st.divider()

    # Filter row + clear
    filt_col, clear_col = st.columns([5, 1])
    with filt_col:
        text_filter = st.text_input(
            "Filter by customer or invoice number",
            value="",
            placeholder="Type to filter rows...",
        )
    with clear_col:
        st.write("")
        if st.button("Clear filters", use_container_width=True):
            st.session_state.selected_classification = None
            st.rerun()

    # Apply filters
    fdf = df.copy()
    if st.session_state.selected_classification:
        fdf = fdf[fdf["classification"] == st.session_state.selected_classification]
    if text_filter:
        tf = text_filter.lower()
        fdf = fdf[
            fdf["customer"].str.lower().str.contains(tf, na=False)
            | fdf["invoice_number"].str.lower().str.contains(tf, na=False)
        ]

    st.caption(f"{len(fdf)} of {len(df)} remittance lines shown")

    # Row list
    if fdf.empty:
        st.warning("No remittance lines in this category. Try clearing the filter.")
    else:
        for _, row in fdf.iterrows():
            with st.container(border=True):
                cols = st.columns([2, 1.3, 1, 1, 1, 0.8, 1, 0.8])
                cols[0].markdown(f"**{row['customer']}**")
                cols[1].markdown(f"`{row['invoice_number']}`")
                cols[2].markdown(
                    f"{'$' + format(row['invoiced'], ',.2f') if row['invoiced'] is not None else '—'}"
                )
                cols[3].markdown(f"${row['paid']:,.2f}")
                delta = row["delta"]
                if delta == 0:
                    cols[4].markdown("**$0.00**")
                else:
                    color = "#ea580c" if delta < 0 else "#2563eb"
                    cols[4].markdown(
                        f"<span style='color:{color};font-weight:600;'>"
                        f"{'-' if delta < 0 else '+'}${abs(delta):,.2f}</span>",
                        unsafe_allow_html=True,
                    )
                cols[5].markdown(f"<span style='font-size:11px;'>{row['source']}</span>", unsafe_allow_html=True)

                badges_html = f"<span class='badge b-{row['classification'].lower()}'>{row['classification']}</span>"
                if row["flags"]:
                    for flag in row["flags"].split(", "):
                        badges_html += f"<span class='badge b-flag'>{flag}</span>"
                cols[6].markdown(badges_html, unsafe_allow_html=True)

                if cols[7].button(
                    "Open",
                    key=f"open_{row['payment_id']}_{row['line_index']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_payment_id = row["payment_id"]
                    st.session_state.selected_line_index = int(row["line_index"])
                    st.session_state.show_draft = False
                    st.rerun()

    # Drill-down panel
    if st.session_state.selected_payment_id:
        render_drilldown()


# ----------------------------------------------------------------------------
# UI: Drilldown side panel + email draft
# ----------------------------------------------------------------------------

def _find_payment(payment_id: str) -> dict | None:
    for p in st.session_state.payments:
        if p["payment_id"] == payment_id:
            return p
    return None


def render_drilldown():
    pid = st.session_state.selected_payment_id
    payment = _find_payment(pid)
    if not payment:
        return

    st.divider()
    title_col, close_col = st.columns([6, 1])
    with title_col:
        st.markdown(f"### 🔍 Drill-down: {payment['payer_name']} - Check #{payment['check_number']}")
    with close_col:
        if st.button("Close ✕", use_container_width=True):
            st.session_state.selected_payment_id = None
            st.session_state.show_draft = False
            st.rerun()

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Payment context")
        st.markdown(
            f"""
            - **Payer name:** {payment['payer_name']}
            - **Check / reference #:** `{payment['check_number']}`
            - **Total amount:** ${float(payment['total_amount']):,.2f}
            - **Payment date:** {payment['payment_date']}
            - **Source channel:** {payment['source_channel']}
            - **Received at:** {payment['received_at']}
            - **Extraction status:** `{payment['extraction_status']}`
            - **Rollup status:** _{payment['rollup_status']}_
            """
        )

        st.markdown("#### Remittance lines (all)")
        for idx, mr in enumerate(payment["match_results"]):
            line = mr["line"]
            is_selected = idx == (st.session_state.selected_line_index or 0)
            border_color = "#111827" if is_selected else "#e5e7eb"
            inv_open = mr.get("open_balance_at_match")
            delta = mr.get("delta_amount") or Decimal("0")

            badges = f"<span class='badge b-{mr['classification'].lower()}'>{mr['classification']}</span>"
            for flag in mr.get("flags") or []:
                badges += f"<span class='badge b-flag'>{flag}</span>"

            line_html = f"""
            <div style='border:2px solid {border_color};border-radius:8px;padding:10px;margin-bottom:8px;'>
                <div><b>Invoice:</b> <code>{line.get('invoice_number','')}</code> {badges}</div>
                <div><b>Line amount:</b> ${float(line.get('line_amount',0)):,.2f} &nbsp;|&nbsp;
                     <b>Open balance:</b> {'$' + format(float(inv_open),',.2f') if inv_open is not None else '—'} &nbsp;|&nbsp;
                     <b>Delta:</b> ${float(delta):,.2f}</div>
                <div style='color:#6b7280;font-size:12px;'>{line.get('description','')}</div>
            </div>
            """
            st.markdown(line_html, unsafe_allow_html=True)

            if st.button(
                f"📨 Draft follow-up for {line.get('invoice_number','')}",
                key=f"draft_{pid}_{idx}",
                disabled=mr["classification"] == "MATCHED" and not mr.get("flags"),
                use_container_width=True,
            ):
                st.session_state.selected_line_index = idx
                st.session_state.show_draft = True
                st.rerun()

    with right:
        st.markdown("#### Source artifact preview")
        # Try to render real artifact if present, else show text preview
        artifact_path = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "artifacts"
            / payment["artifact_ref"]
        )
        if artifact_path.exists():
            if artifact_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                st.image(str(artifact_path), use_container_width=True)
            else:
                st.info(f"Artifact at: `{artifact_path.name}`")
        # Always show extraction text preview (POC stand-in for real OCR view)
        fixture_meta = payment.get("fixture_meta", {})
        preview = f"""[POC artifact preview - text rendering of pre-extracted data]

Source file: {payment['artifact_ref']}
Channel:     {payment['source_channel']}
Scenario:    {fixture_meta.get('scenario_note', '(no note)')}

PAYER:   {payment['payer_name']}
CHECK#:  {payment['check_number']}
DATE:    {payment['payment_date']}
TOTAL:   ${float(payment['total_amount']):,.2f}

REMITTANCE LINES:
"""
        for line in payment["remittance_lines"]:
            preview += (
                f"  - {line.get('invoice_number',''):20s}  "
                f"${float(line.get('line_amount',0)):>12,.2f}  "
                f"{line.get('description','')}\n"
            )
        st.markdown(
            f"<div class='artifact-preview'>{preview}</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.show_draft:
        render_email_draft(payment)


def render_email_draft(payment: dict):
    idx = st.session_state.selected_line_index or 0
    if idx >= len(payment["match_results"]):
        return
    mr = payment["match_results"][idx]
    line = mr["line"]

    invoiced = mr.get("open_balance_at_match") or Decimal("0")
    paid = Decimal(str(line.get("line_amount", 0)))
    delta = Decimal(str(mr.get("delta_amount", 0)))

    customer_name = mr.get("customer_name_of_record") or payment["payer_name"]
    customer_record = CUSTOMERS_LOOKUP.get((customer_name or "").lower(), {})
    contact_email = customer_record.get("contact_email", "")

    draft = draft_follow_up(
        classification=mr["classification"],
        flags=mr.get("flags") or [],
        payer_name=customer_name,
        invoice_number=line.get("invoice_number", ""),
        invoiced_amount=invoiced,
        paid_amount=paid,
        delta_amount=delta,
        contact_email=contact_email,
        check_number=payment.get("check_number", ""),
    )

    st.divider()
    st.markdown("### ✉️ Follow-up email draft")
    st.caption("Pre-composed by CCRA based on the exception type. POC: copy-to-clipboard only.")

    st.text_input("To:", value=draft["to"], key="draft_to", disabled=True)
    st.text_input("Subject:", value=draft["subject"], key="draft_subject", disabled=True)
    st.text_area("Body:", value=draft["body"], height=300, key="draft_body")

    full_text = f"To: {draft['to']}\nSubject: {draft['subject']}\n\n{draft['body']}"

    cols = st.columns([2, 2, 1])
    with cols[0]:
        # Streamlit can't directly drive the system clipboard from Python;
        # the canonical POC pattern is a hidden JS button via st.components.
        copy_html = f"""
        <button onclick="navigator.clipboard.writeText({full_text!r}).then(
            () => {{
                const el = document.getElementById('copy-toast');
                if (el) {{ el.innerText = '✅ Copied to clipboard'; el.style.display='inline'; }}
            }},
            () => {{
                const el = document.getElementById('copy-toast');
                if (el) {{ el.innerText = '⚠️ Clipboard blocked - use the textarea above'; el.style.display='inline'; }}
            }}
        )" style="padding:8px 16px;border-radius:8px;border:1px solid #2563eb;background:#2563eb;color:white;font-weight:600;cursor:pointer;width:100%;">
            📋 Copy to clipboard
        </button>
        <span id='copy-toast' style='display:none;margin-left:12px;color:#166534;font-weight:600;'></span>
        """
        st.components.v1.html(copy_html, height=50)
    with cols[1]:
        st.download_button(
            "⬇️ Download as .txt",
            data=full_text,
            file_name=f"draft_{line.get('invoice_number','draft')}.txt",
            use_container_width=True,
        )
    with cols[2]:
        if st.button("Close draft", use_container_width=True):
            st.session_state.show_draft = False
            st.rerun()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    render_header()
    if st.session_state.page == "inbox":
        render_inbox()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
