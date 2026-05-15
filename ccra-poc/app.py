"""CCRA POC - Cash Collection Reconciliation Assistant
Streamlit single-page demo per docs/refined-prd.md (POC scope).

Critical Path Journey:
  Inbox -> Use sample data -> Dashboard tiles -> click tile ->
  click row -> drilldown -> Draft AM escalation -> clipboard.

UI is branded for iTradeNetwork AR Operations:
navy + accent green + gold + warm cream palette, Playfair Display serif
headlines.
"""

from __future__ import annotations

import random
import re
import uuid
from datetime import datetime
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
# Page config + global CSS  (iTradeNetwork branding)
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="CCRA - Cash Collection Reconciliation Assistant",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Palette (iTradeNetwork)
NAVY = "#1B3A5F"
GREEN = "#4F6B3A"
GOLD = "#C4A04A"
CREAM = "#F7F4ED"
TEXT = "#1A1A1A"
BORDER = "#D9D2C2"
RED = "#B33A3A"


st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

      /* ---- Page chrome ---- */
      .stApp {{
        background: {CREAM};
        color: {TEXT};
      }}
      .block-container {{
        padding-top: 0.5rem !important;
      }}
      body, .stMarkdown, .stCaption, p, span, div, label, input, textarea {{
        font-family: 'Inter', 'Source Sans Pro', sans-serif;
      }}
      /* Serif headlines */
      h1, h2, h3,
      .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
      [data-testid="stHeader"] h1,
      [data-testid="stHeader"] h2,
      [data-testid="stHeader"] h3,
      .ccra-serif {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: {NAVY};
        letter-spacing: 0.2px;
      }}

      /* ---- Brand header strip ---- */
      .brand-strip {{
        background: {NAVY};
        color: {CREAM};
        padding: 14px 22px;
        margin: 0 -1rem 18px -1rem;
        border-bottom: 3px solid {GOLD};
        display: flex;
        align-items: center;
        gap: 22px;
      }}
      .brand-strip .brand-oms {{
        display: flex;
        align-items: center;
        gap: 8px;
        background: {CREAM};
        padding: 6px 12px;
        border-radius: 4px;
        flex: 0 0 auto;
      }}
      .brand-strip .brand-oms svg {{
        display: block;
        height: 26px;
        width: auto;
      }}
      .brand-strip .brand-oms-word {{
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: {NAVY};
        letter-spacing: 1px;
        line-height: 1;
      }}
      .brand-strip .brand-divider {{
        width: 1px;
        align-self: stretch;
        background: rgba(247,244,237,0.25);
        margin: 4px 0;
        flex: 0 0 auto;
      }}
      .brand-strip .brand-center {{
        flex: 1 1 auto;
      }}
      .brand-strip .brand-title {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 20px;
        font-weight: 700;
        color: {CREAM};
        letter-spacing: 0.4px;
      }}
      .brand-strip .brand-sub {{
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: #E8DEC2;
        text-transform: uppercase;
        letter-spacing: 1.2px;
      }}

      /* ---- Tiles ---- */
      .tile {{
        padding: 22px 22px 18px 22px;
        border-radius: 6px;
        border: 1px solid {BORDER};
        background: #FFFFFF;
        box-shadow: 0 1px 3px rgba(27,58,95,0.06);
      }}
      .tile-matched   {{ border-top: 6px solid {GREEN};  }}
      .tile-underpaid {{ border-top: 6px solid {RED};    }}
      .tile-overpaid  {{ border-top: 6px solid {GOLD};   }}
      .tile-unmatched {{ border-top: 6px solid {RED};    }}
      .tile-info      {{ border-top: 6px solid {NAVY};   }}
      .tile-label {{
        font-size: 11px;
        color: #6F6655;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 600;
      }}
      .tile-value {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 44px;
        font-weight: 700;
        color: {NAVY};
        line-height: 1.0;
        margin-top: 6px;
      }}
      .tile-sub {{
        font-size: 12px;
        color: #8A8270;
        margin-top: 6px;
      }}
      .tile-matched   .tile-value {{ color: {GREEN}; }}
      .tile-overpaid  .tile-value {{ color: {GOLD};  }}
      .tile-underpaid .tile-value {{ color: {RED};   }}
      .tile-unmatched .tile-value {{ color: {RED};   }}
      .tile {{
        position: relative;
        cursor: pointer;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
      }}
      .tile:hover {{
        box-shadow: 0 4px 10px rgba(27,58,95,0.15);
        transform: translateY(-1px);
      }}
      .tile-active {{
        box-shadow: 0 0 0 2px {NAVY}, 0 4px 12px rgba(27,58,95,0.18) !important;
        transform: translateY(-1px);
      }}
      .tile-active-chip {{
        position: absolute;
        top: 12px;
        right: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 700;
        color: {CREAM};
        background: {NAVY};
        padding: 3px 9px;
        border-radius: 11px;
        letter-spacing: 0.6px;
        text-transform: uppercase;
      }}
      .tile-active-chip::before {{
        content: '● ';
        color: {GOLD};
        margin-right: 2px;
      }}

      /* ---- Tile filter button (Strategy B) ----
         Each tile lives inside st.container(key="tile-XXX") which renders
         <div class="st-key-tile-XXX">. Below the tile markdown we render a
         visible st.button styled to look like part of the card. Clicking
         the button toggles the filter. This is bulletproof — no DOM
         overlay tricks, no z-index issues, no Streamlit version drift.
      */
      div.st-key-tile-MATCHED,
      div.st-key-tile-UNDERPAID,
      div.st-key-tile-OVERPAID,
      div.st-key-tile-UNMATCHED {{
        position: relative;
      }}
      /* Pull the button up so it sits flush under the tile (no gap). */
      div.st-key-tile-MATCHED div[data-testid="stButton"],
      div.st-key-tile-UNDERPAID div[data-testid="stButton"],
      div.st-key-tile-OVERPAID div[data-testid="stButton"],
      div.st-key-tile-UNMATCHED div[data-testid="stButton"] {{
        margin-top: -1px !important;
      }}
      /* Style the filter button to read as the footer of the tile card. */
      div.st-key-tile-MATCHED div[data-testid="stButton"] > button,
      div.st-key-tile-UNDERPAID div[data-testid="stButton"] > button,
      div.st-key-tile-OVERPAID div[data-testid="stButton"] > button,
      div.st-key-tile-UNMATCHED div[data-testid="stButton"] > button {{
        width: 100%;
        background: #FFFFFF;
        color: {NAVY};
        border: 1px solid {BORDER};
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 10px 12px !important;
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        cursor: pointer;
        box-shadow: 0 1px 3px rgba(27,58,95,0.06);
        transition: background 0.12s ease, color 0.12s ease;
      }}
      div.st-key-tile-MATCHED div[data-testid="stButton"] > button:hover,
      div.st-key-tile-UNDERPAID div[data-testid="stButton"] > button:hover,
      div.st-key-tile-OVERPAID div[data-testid="stButton"] > button:hover,
      div.st-key-tile-UNMATCHED div[data-testid="stButton"] > button:hover {{
        background: {CREAM};
        color: {NAVY};
        border-color: {NAVY};
      }}
      div.st-key-tile-MATCHED div[data-testid="stButton"] > button:focus,
      div.st-key-tile-UNDERPAID div[data-testid="stButton"] > button:focus,
      div.st-key-tile-OVERPAID div[data-testid="stButton"] > button:focus,
      div.st-key-tile-UNMATCHED div[data-testid="stButton"] > button:focus {{
        outline: none !important;
        box-shadow: 0 0 0 2px {NAVY} !important;
      }}
      /* Active state — solid navy footer with cream text. */
      div.st-key-tile-MATCHED.tile-wrap-active div[data-testid="stButton"] > button,
      div.st-key-tile-UNDERPAID.tile-wrap-active div[data-testid="stButton"] > button,
      div.st-key-tile-OVERPAID.tile-wrap-active div[data-testid="stButton"] > button,
      div.st-key-tile-UNMATCHED.tile-wrap-active div[data-testid="stButton"] > button {{
        background: {NAVY};
        color: {CREAM};
        border-color: {NAVY};
      }}
      /* Tile body must NOT have rounded bottom corners — the button is the footer. */
      .tile-has-button {{
        border-radius: 6px 6px 0 0 !important;
        box-shadow: none !important;
      }}

      /* ---- Badges ---- */
      .badge {{
        display: inline-block;
        padding: 3px 9px;
        border-radius: 11px;
        font-size: 10px;
        font-weight: 700;
        margin-right: 4px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        border: 1px solid transparent;
      }}
      .b-matched   {{ background: #E6EFDD; color: {GREEN}; border-color: #C8D8B5; }}
      .b-underpaid {{ background: #F4DCDC; color: {RED};   border-color: #E3B9B9; }}
      .b-overpaid  {{ background: #F5E9C9; color: #7A6320; border-color: #E4D29A; }}
      .b-unmatched {{ background: #F4DCDC; color: {RED};   border-color: #E3B9B9; }}
      .b-flag      {{ background: #FBF1D5; color: #7A6320; border-color: {GOLD}; }}

      /* ---- Artifact preview ---- */
      .artifact-preview {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 14px 16px;
        font-family: 'SF Mono', Menlo, monospace;
        font-size: 12px;
        color: #2E2A20;
        white-space: pre-wrap;
      }}

      /* ---- Drilldown header ---- */
      .drill-header {{
        background: {NAVY};
        color: {CREAM};
        padding: 12px 18px;
        border-radius: 6px 6px 0 0;
        margin-top: 8px;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 18px;
        font-weight: 600;
        border-bottom: 2px solid {GOLD};
      }}
      .drill-body {{
        background: {CREAM};
        border: 1px solid {BORDER};
        border-top: none;
        padding: 16px;
        border-radius: 0 0 6px 6px;
      }}

      /* ---- AM "To:" header on email panel ---- */
      .am-to-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-left: 6px solid {NAVY};
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 12px;
      }}
      .am-to-label {{
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: {NAVY};
      }}
      .am-to-name {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 20px;
        font-weight: 600;
        color: {NAVY};
        margin-top: 2px;
      }}
      .am-to-email {{
        font-family: 'SF Mono', Menlo, monospace;
        font-size: 13px;
        color: #4A4A4A;
        margin-top: 2px;
      }}
      .am-to-note {{
        font-size: 11px;
        color: #6F6655;
        margin-top: 8px;
        font-style: italic;
      }}

      /* ---- Buttons ---- */
      .stButton > button {{
        border-radius: 4px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 0.3px;
      }}
      .stButton > button[kind="primary"] {{
        background: {NAVY};
        color: {CREAM};
        border: 1px solid {NAVY};
      }}
      .stButton > button[kind="primary"]:hover {{
        background: #122A45;
        border-color: #122A45;
        color: {CREAM};
      }}
      .stButton > button[kind="secondary"] {{
        background: #FFFFFF;
        color: {NAVY};
        border: 1px solid {BORDER};
      }}
      .stButton > button[kind="secondary"]:hover {{
        border-color: {NAVY};
        color: {NAVY};
      }}
      .stDownloadButton > button {{
        background: {GREEN};
        color: {CREAM};
        border: 1px solid {GREEN};
        border-radius: 4px;
        font-weight: 600;
      }}
      .stDownloadButton > button:hover {{
        background: #3F5A2D;
        border-color: #3F5A2D;
        color: {CREAM};
      }}

      /* ---- Inputs ---- */
      .stTextInput input, .stTextArea textarea {{
        background: #FFFFFF;
        border-radius: 4px;
        border: 1px solid {BORDER};
        color: {TEXT};
      }}
      .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {NAVY};
        box-shadow: 0 0 0 1px {NAVY};
      }}

      /* ---- Divider ---- */
      hr {{ border-color: {BORDER} !important; }}

      /* ---- st.container border ---- */
      div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        border-color: {BORDER} !important;
        background: #FFFFFF;
      }}

      /* ---- Metric ---- */
      [data-testid="stMetricValue"] {{
        font-family: 'Playfair Display', Georgia, serif;
        color: {NAVY};
      }}
      [data-testid="stMetricLabel"] {{
        color: #6F6655;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 11px !important;
      }}

      /* ---- Compact "+" upload popover button ---- */
      div[data-testid="stPopover"] > div > button {{
        background: {NAVY} !important;
        color: {CREAM} !important;
        border: 1px solid {NAVY} !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 3px rgba(27,58,95,0.18);
      }}
      div[data-testid="stPopover"] > div > button:hover {{
        background: #122A45 !important;
        border-color: {GOLD} !important;
        color: {CREAM} !important;
      }}
      div[data-testid="stPopover"] > div > button p {{
        font-size: 18px !important;
        font-weight: 700 !important;
        margin: 0 !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Brand header strip (rendered once at top of every page)
# ----------------------------------------------------------------------------

# Inline iTradeNetwork OMS swirl icon. Read from assets/ once at import.
# Fill color is already #F1AA48 (Tradewinds gold) inside the SVG file.
_OMS_ICON_PATH = Path(__file__).parent / "assets" / "oms-icon.svg"
try:
    _OMS_ICON_SVG = _OMS_ICON_PATH.read_text(encoding="utf-8").strip()
except OSError:
    _OMS_ICON_SVG = ""  # graceful degradation — wordmark only


def render_brand_strip():
    st.markdown(
        f"""
        <div class='brand-strip'>
            <div class='brand-oms' title='iTradeNetwork OMS'>
                {_OMS_ICON_SVG}
                <span class='brand-oms-word'>CCRA</span>
            </div>
            <div class='brand-divider'></div>
            <div class='brand-center'>
                <div class='brand-title'>Cash Collection Reconciliation</div>
                <div class='brand-sub'>iTradeNetwork &middot; AR Operations</div>
            </div>
        </div>
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
        st.session_state.payments = []
    if "ingested_fixture_ids" not in st.session_state:
        st.session_state.ingested_fixture_ids = set()
    if "selected_classification" not in st.session_state:
        st.session_state.selected_classification = None
    if "selected_payment_id" not in st.session_state:
        st.session_state.selected_payment_id = None
    if "selected_line_index" not in st.session_state:
        st.session_state.selected_line_index = None
    if "show_draft" not in st.session_state:
        st.session_state.show_draft = False
    if "user_uploaded_artifacts" not in st.session_state:
        # List[dict] of user-supplied uploads (PDF or camera capture).
        # Each item: {artifact_name, source, size_kb, uploaded_at, ingested}
        st.session_state.user_uploaded_artifacts = []
    if "last_processed_pdf_name" not in st.session_state:
        # Tracks last processed st.file_uploader filename to dedupe reruns.
        st.session_state.last_processed_pdf_name = None
    if "last_processed_camera_id" not in st.session_state:
        # Tracks last processed st.camera_input file_id to dedupe reruns.
        st.session_state.last_processed_camera_id = None


_init_state()


# ----------------------------------------------------------------------------
# User-upload helpers (Fix 2)
# ----------------------------------------------------------------------------

# Max user-uploaded artifacts to keep in the demo list (FIFO drop oldest).
USER_UPLOAD_CAP = 20

# Characters considered safe in a displayed filename.
_FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9._\- ]+")


def _sanitize_filename(name: str) -> str:
    """Strip dangerous characters from a filename for safe display."""
    if not name:
        return "unnamed"
    cleaned = _FILENAME_SAFE_RE.sub("_", name).strip()
    return cleaned or "unnamed"


def _unique_filename(name: str) -> str:
    """Return name, or name (2)/(3)/... if it already exists in the upload list."""
    existing = {item["artifact_name"] for item in st.session_state.user_uploaded_artifacts}
    if name not in existing:
        return name
    stem, dot, ext = name.rpartition(".")
    if not dot:
        stem, ext = name, ""
    n = 2
    while True:
        candidate = f"{stem} ({n}).{ext}" if ext else f"{stem} ({n})"
        if candidate not in existing:
            return candidate
        n += 1


def _register_user_upload(artifact_name: str, source: str, size_bytes: int) -> None:
    """Append a user-uploaded artifact record to session state, FIFO-capped."""
    record = {
        "artifact_name": _unique_filename(_sanitize_filename(artifact_name)),
        "source": source,  # 'upload' | 'camera'
        "size_kb": max(1, int(round(size_bytes / 1024))),
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "ingested": False,
    }
    st.session_state.user_uploaded_artifacts.append(record)
    # FIFO cap
    overflow = len(st.session_state.user_uploaded_artifacts) - USER_UPLOAD_CAP
    if overflow > 0:
        st.session_state.user_uploaded_artifacts = (
            st.session_state.user_uploaded_artifacts[overflow:]
        )


def ingest_user_upload(record: dict) -> None:
    """Demo-only: ingest a random built-in upload fixture under the user-supplied name.

    No real OCR/scraping; pick a random payment fixture from upload_manifest.json,
    clone it with a synthetic fixture_id (so it won't collide with existing ingests),
    overlay the user's artifact_name, and run normal ingest_fixture().
    """
    if record.get("ingested"):
        return
    if not UPLOAD_FIXTURES:
        return
    base = random.choice(UPLOAD_FIXTURES)
    synthetic = dict(base)  # shallow copy
    synthetic["fixture_id"] = f"USERUP-{uuid.uuid4().hex[:8].upper()}"
    synthetic["filename"] = record["artifact_name"]
    synthetic["artifact_ref"] = base.get("artifact_ref") or base.get("filename")
    synthetic["display_label"] = record["artifact_name"]
    synthetic["source_channel"] = "UPLOAD"
    ingest_fixture(synthetic, "UPLOAD")
    record["ingested"] = True


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
    render_brand_strip()
    left, right = st.columns([5, 2])
    with left:
        st.markdown(
            # "<h2 class='ccra-serif' style='margin-bottom:2px;'>CCRA</h2>"
            "<div style='color:#6F6655;font-size:13px;'>"
            "Forward remittances &middot; auto-match &middot; surface exceptions &middot; "
            "draft AM escalations."
            "</div>",
            unsafe_allow_html=True,
        )
    with right:
        cols = st.columns(2)
        with cols[0]:
            if st.button(
                "Inbox",
                use_container_width=True,
                type="primary" if st.session_state.page == "inbox" else "secondary",
            ):
                st.session_state.page = "inbox"
                st.session_state.selected_payment_id = None
                st.session_state.show_draft = False
                st.rerun()
        with cols[1]:
            if st.button(
                "Dashboard",
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
    st.markdown("<h2 class='ccra-serif'>Payment Inbox</h2>", unsafe_allow_html=True)
    st.caption(
        "Forwarded remittance emails on the left, file uploads on the right. "
        "Click an item to ingest, or load the full demo set with one click."
    )

    top_left, top_right = st.columns([3, 2])
    with top_left:
        if st.button(
            "Use sample data  (ingest all 13 fixtures)",
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

    with col_inbox:
        st.markdown("<h4 class='ccra-serif'>Forwarded Inbox  &middot;  10 emails</h4>", unsafe_allow_html=True)
        st.caption("Simulated email-forwarded remittance artifacts.")
        for fix in INBOX_FIXTURES:
            already = fix["fixture_id"] in st.session_state.ingested_fixture_ids
            with st.container(border=True):
                a, b = st.columns([4, 1])
                with a:
                    badge = "&#10003;" if already else "&middot;"
                    st.markdown(
                        f"<div style='color:{NAVY};font-weight:600;'>{badge} {fix['subject']}</div>"
                        f"<div style='color:#6F6655;font-size:12px;'>"
                        f"{fix['from_email']} &middot; {fix['received_at']} &middot; "
                        f"{fix['source_channel']} &middot; {fix['artifact_ref']}</div>"
                        f"<div style='color:#2E2A20;font-size:13px;margin-top:4px;'>"
                        f"{fix['preview_snippet']}</div>",
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

    with col_upload:
        n_user_uploads = len(st.session_state.user_uploaded_artifacts)
        total_fixtures = len(UPLOAD_FIXTURES) + n_user_uploads
        hdr_left, hdr_right = st.columns([5, 1])
        with hdr_left:
            st.markdown(
                f"<h4 class='ccra-serif' style='margin-bottom:0;'>"
                f"File Upload  &middot;  {total_fixtures} fixtures</h4>",
                unsafe_allow_html=True,
            )
        with hdr_right:
            with st.popover("+", use_container_width=False, help="Upload a PDF or take a photo"):
                st.markdown(
                    "<div style='font-family:Playfair Display,Georgia,serif;color:#1B3A5F;"
                    "font-size:16px;font-weight:600;margin-bottom:6px;'>Add an artifact</div>",
                    unsafe_allow_html=True,
                )

                # --- Option 1: Upload PDF ---
                st.markdown(
                    "<div style='color:#1B3A5F;font-weight:600;font-size:13px;margin-top:4px;"
                    "margin-bottom:2px;'>1. Upload PDF</div>",
                    unsafe_allow_html=True,
                )
                pdf_file = st.file_uploader(
                    "Upload PDF",
                    type=["pdf"],
                    accept_multiple_files=False,
                    label_visibility="collapsed",
                    key="upload_pdf",
                    help="Drop a remittance or check PDF from your device.",
                )
                if pdf_file is not None and pdf_file.name != st.session_state.last_processed_pdf_name:
                    _register_user_upload(pdf_file.name, "upload", getattr(pdf_file, "size", 0) or 0)
                    st.session_state.last_processed_pdf_name = pdf_file.name
                    st.rerun()

                st.markdown(
                    "<div style='height:8px;'></div>"
                    "<div style='color:#1B3A5F;font-weight:600;font-size:13px;margin-bottom:2px;'>"
                    "2. Take photo of check / remittance</div>",
                    unsafe_allow_html=True,
                )
                cam_file = st.camera_input(
                    "Take photo of check / remittance",
                    label_visibility="collapsed",
                    key="upload_camera",
                    help="Opens your device camera (rear camera on mobile).",
                )
                if cam_file is not None and getattr(cam_file, "file_id", None) != st.session_state.last_processed_camera_id:
                    synth_name = f"camera_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    _register_user_upload(synth_name, "camera", getattr(cam_file, "size", 0) or 0)
                    st.session_state.last_processed_camera_id = getattr(cam_file, "file_id", synth_name)
                    st.rerun()

        st.caption("Pick from sample uploads below, or use the + button to add a PDF or photo.")

        # --- Built-in upload fixtures ---
        for fix in UPLOAD_FIXTURES:
            already = fix["fixture_id"] in st.session_state.ingested_fixture_ids
            with st.container(border=True):
                badge = "&#10003;" if already else "&middot;"
                st.markdown(
                    f"<div style='color:{NAVY};font-weight:600;'>{badge} {fix['display_label']}</div>"
                    f"<div style='color:#6F6655;font-size:12px;'>{fix['filename']}</div>"
                    f"<div style='color:#2E2A20;font-size:13px;margin-top:4px;'>"
                    f"{fix['preview_snippet']}</div>",
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

        # --- User-uploaded artifacts (PDF + camera) ---
        for idx, rec in enumerate(st.session_state.user_uploaded_artifacts):
            ingested = rec.get("ingested", False)
            source_badge = "📎 Uploaded" if rec["source"] == "upload" else "📷 Photo"
            row_badge = "&#10003;" if ingested else "&middot;"
            with st.container(border=True):
                st.markdown(
                    f"<div style='color:{NAVY};font-weight:600;'>"
                    f"{row_badge} {source_badge} &middot; {rec['artifact_name']}</div>"
                    f"<div style='color:#6F6655;font-size:12px;'>"
                    f"{rec['size_kb']} KB &middot; {rec['uploaded_at']}</div>"
                    f"<div style='color:#2E2A20;font-size:13px;margin-top:4px;'>"
                    f"User-supplied artifact (demo: ingest will use a sample fixture).</div>",
                    unsafe_allow_html=True,
                )
                btn_label = "✓ Ingested" if ingested else "Ingest"
                if st.button(
                    btn_label,
                    key=f"userup_{idx}_{rec['artifact_name']}",
                    disabled=ingested,
                    use_container_width=True,
                ):
                    ingest_user_upload(rec)
                    st.rerun()


# ----------------------------------------------------------------------------
# UI: Dashboard page
# ----------------------------------------------------------------------------

def render_dashboard():
    st.markdown("<h2 class='ccra-serif'>Exceptions Dashboard</h2>", unsafe_allow_html=True)

    if not st.session_state.payments:
        st.info(
            "No payments ingested yet. Open the **Inbox** and click "
            "**'Use sample data'** to load the demo set, or ingest individual "
            "fixtures."
        )
        return

    df = all_match_rows()
    counts = classification_counts(df)

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
            tile_classes = (
                f"tile tile-has-button {klass}"
                f"{' tile-active' if active else ''}"
            )
            active_chip = (
                "<div class='tile-active-chip'>Active</div>" if active else ""
            )
            # Each tile lives inside st.container(key=f"tile-{code}") which
            # renders <div class="st-key-tile-CODE">. We render the tile
            # markup, then a visible st.button below it styled (via CSS) to
            # look like the footer of the card. When active, we also inject
            # a tiny <style> that adds .tile-wrap-active to this container
            # so the footer button switches to the navy "active" treatment.
            with st.container(key=f"tile-{code}"):
                # NOTE: HTML must be flush-left (no leading indent on lines).
                # Streamlit's markdown parser treats lines indented 4+ spaces
                # as a code block and ESCAPES the HTML inside, even with
                # unsafe_allow_html=True. Keep this string left-aligned.
                tile_html = (
                    f"<div class='{tile_classes}'>"
                    f"{active_chip}"
                    f"<div class='tile-label'>{label}</div>"
                    f"<div class='tile-value'>{count}</div>"
                    f"<div class='tile-sub'>remittance lines</div>"
                    f"</div>"
                )
                st.markdown(tile_html, unsafe_allow_html=True)
                # Active-state styling for THIS tile's button — scoped CSS
                # injected only when this tile is the selected filter.
                if active:
                    active_css = (
                        f"<style>"
                        f"div.st-key-tile-{code} "
                        f"div[data-testid='stButton'] > button {{"
                        f" background: {NAVY} !important;"
                        f" color: {CREAM} !important;"
                        f" border-color: {NAVY} !important;"
                        f" }}"
                        f"</style>"
                    )
                    st.markdown(active_css, unsafe_allow_html=True)
                btn_label = (
                    f"✓ Active — click to clear" if active
                    else f"Filter by {label}"
                )
                if st.button(
                    btn_label,
                    key=f"tile_btn_{code}",
                    use_container_width=True,
                ):
                    st.session_state.selected_classification = (
                        None if active else code
                    )
                    st.session_state.selected_payment_id = None
                    st.session_state.show_draft = False
                    st.rerun()

    st.divider()

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

    if fdf.empty:
        st.warning("No remittance lines in this category. Try clearing the filter.")
    else:
        for _, row in fdf.iterrows():
            with st.container(border=True):
                cols = st.columns([2, 1.3, 1, 1, 1, 0.8, 1, 0.8])
                cols[0].markdown(f"<div style='color:{NAVY};font-weight:600;'>{row['customer']}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"`{row['invoice_number']}`")
                cols[2].markdown(
                    f"{'$' + format(row['invoiced'], ',.2f') if row['invoiced'] is not None else '—'}"
                )
                cols[3].markdown(f"${row['paid']:,.2f}")
                delta = row["delta"]
                if delta == 0:
                    cols[4].markdown("**$0.00**")
                else:
                    color = RED if delta < 0 else GOLD
                    cols[4].markdown(
                        f"<span style='color:{color};font-weight:700;'>"
                        f"{'-' if delta < 0 else '+'}${abs(delta):,.2f}</span>",
                        unsafe_allow_html=True,
                    )
                cols[5].markdown(f"<span style='font-size:11px;color:#6F6655;'>{row['source']}</span>", unsafe_allow_html=True)

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


def _lookup_customer_record(payment: dict, mr: dict) -> dict:
    """Best-effort customer lookup, prefers customer-of-record over payer_name."""
    candidates = [
        mr.get("customer_name_of_record"),
        payment.get("payer_name"),
    ]
    for cand in candidates:
        if not cand:
            continue
        rec = CUSTOMERS_LOOKUP.get(cand.strip().lower())
        if rec:
            return rec
    return {}


def render_drilldown():
    pid = st.session_state.selected_payment_id
    payment = _find_payment(pid)
    if not payment:
        return

    st.divider()
    title_col, close_col = st.columns([6, 1])
    with title_col:
        st.markdown(
            f"<div class='drill-header'>Drill-down &middot; "
            f"{payment['payer_name']} &middot; Check #{payment['check_number']}</div>",
            unsafe_allow_html=True,
        )
    with close_col:
        if st.button("Close", use_container_width=True):
            st.session_state.selected_payment_id = None
            st.session_state.show_draft = False
            st.rerun()

    left, right = st.columns([3, 2])

    with left:
        st.markdown("<h4 class='ccra-serif'>Payment context</h4>", unsafe_allow_html=True)
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

        st.markdown("<h4 class='ccra-serif'>Remittance lines</h4>", unsafe_allow_html=True)
        for idx, mr in enumerate(payment["match_results"]):
            line = mr["line"]
            is_selected = idx == (st.session_state.selected_line_index or 0)
            border_color = NAVY if is_selected else BORDER
            inv_open = mr.get("open_balance_at_match")
            delta = mr.get("delta_amount") or Decimal("0")

            badges = f"<span class='badge b-{mr['classification'].lower()}'>{mr['classification']}</span>"
            for flag in mr.get("flags") or []:
                badges += f"<span class='badge b-flag'>{flag}</span>"

            # Lookup AM for this line so we can show the AM name on the line card
            cust_rec = _lookup_customer_record(payment, mr)
            am_name = cust_rec.get("account_manager_name", "")
            am_line = (
                f"<div style='color:#6F6655;font-size:11px;margin-top:6px;'>"
                f"<b>AM:</b> {am_name}</div>"
            ) if am_name else ""

            line_html = f"""
            <div style='border:2px solid {border_color};border-radius:6px;padding:12px;margin-bottom:10px;background:#FFFFFF;'>
                <div><b style='color:{NAVY};'>Invoice:</b> <code>{line.get('invoice_number','')}</code> &nbsp; {badges}</div>
                <div style='margin-top:4px;'><b>Line amount:</b> ${float(line.get('line_amount',0)):,.2f} &nbsp;|&nbsp;
                     <b>Open balance:</b> {'$' + format(float(inv_open),',.2f') if inv_open is not None else '—'} &nbsp;|&nbsp;
                     <b>Delta:</b> ${float(delta):,.2f}</div>
                <div style='color:#6F6655;font-size:12px;margin-top:4px;'>{line.get('description','')}</div>
                {am_line}
            </div>
            """
            st.markdown(line_html, unsafe_allow_html=True)

            # Button label makes the internal-escalation intent obvious
            btn_label = (
                f"Draft account-manager escalation for {line.get('invoice_number','')}"
            )
            if st.button(
                btn_label,
                key=f"draft_{pid}_{idx}",
                disabled=mr["classification"] == "MATCHED" and not mr.get("flags"),
                use_container_width=True,
            ):
                st.session_state.selected_line_index = idx
                st.session_state.show_draft = True
                st.rerun()

    with right:
        st.markdown("<h4 class='ccra-serif'>Source artifact preview</h4>", unsafe_allow_html=True)
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
    customer_record = _lookup_customer_record(payment, mr)
    am_name = customer_record.get("account_manager_name", "")
    am_email = customer_record.get("account_manager_email", "")

    draft = draft_follow_up(
        classification=mr["classification"],
        flags=mr.get("flags") or [],
        payer_name=payment.get("payer_name", ""),
        invoice_number=line.get("invoice_number", ""),
        invoiced_amount=invoiced,
        paid_amount=paid,
        delta_amount=delta,
        contact_email=customer_record.get("contact_email", ""),
        check_number=payment.get("check_number", ""),
        customer_name=customer_name,
        account_manager_name=am_name,
        account_manager_email=am_email,
    )

    st.divider()
    st.markdown(
        "<h3 class='ccra-serif'>Account-manager escalation &middot; internal email</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Pre-composed by CCRA. This goes to the customer's iTN Account "
        "Manager - NOT to the customer. The AM will phone the customer to "
        "resolve."
    )

    # Prominent "To: Account Manager" card
    st.markdown(
        f"""
        <div class='am-to-card'>
            <div class='am-to-label'>To &middot; Account Manager (internal)</div>
            <div class='am-to-name'>{draft['to_name']}</div>
            <div class='am-to-email'>&lt;{draft['to']}&gt;</div>
            <div class='am-to-note'>
                Owns the relationship with <b>{draft['customer_name']}</b>.
                This is an internal escalation - not customer-facing copy.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.text_input("Subject:", value=draft["subject"], key="draft_subject", disabled=True)
    st.text_area("Body:", value=draft["body"], height=320, key="draft_body")

    full_text = (
        f"To: {draft['to_name']} <{draft['to']}>\n"
        f"Subject: {draft['subject']}\n\n"
        f"{draft['body']}"
    )

    cols = st.columns([2, 2, 1])
    with cols[0]:
        copy_html = f"""
        <button onclick="navigator.clipboard.writeText({full_text!r}).then(
            () => {{
                const el = document.getElementById('copy-toast');
                if (el) {{ el.innerText = 'Copied to clipboard'; el.style.display='inline'; }}
            }},
            () => {{
                const el = document.getElementById('copy-toast');
                if (el) {{ el.innerText = 'Clipboard blocked - use the textarea above'; el.style.display='inline'; }}
            }}
        )" style="padding:8px 16px;border-radius:4px;border:1px solid {NAVY};background:{NAVY};color:{CREAM};font-weight:600;cursor:pointer;width:100%;font-family:'Inter',sans-serif;letter-spacing:0.3px;">
            Copy to clipboard
        </button>
        <span id='copy-toast' style='display:none;margin-left:12px;color:{GREEN};font-weight:600;'></span>
        """
        st.components.v1.html(copy_html, height=50)
    with cols[1]:
        st.download_button(
            "Download as .txt",
            data=full_text,
            file_name=f"escalation_{line.get('invoice_number','draft')}.txt",
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
