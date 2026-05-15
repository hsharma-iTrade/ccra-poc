<div align="center">
  <img src="assets/oms-icon.svg" width="48" alt="CCRA logo" />
  <h1>CCRA — Cash Collection Reconciliation Assistant</h1>
  <p><strong>Open-source AR exception triage tool built with Python + Streamlit</strong></p>
  <p>
    <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" />
    <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
    <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
    <img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" />
  </p>
</div>

---


## What is CCRA?

Accounts-receivable teams receive checks and ACH remittances from lockboxes, forwarded emails, and scanned paper mail. Today, clerks manually cross-reference every payment against an invoice ledger — a tedious process where most payments are fine and only a small fraction need attention.

**CCRA automates the triage:**

- Ingest payment fixtures (simulated email forwards, file uploads, camera captures)
- Auto-match each remittance line against an invoice ledger (exact-cents matching)
- Surface a clean exceptions dashboard: **Matched / Underpaid / Overpaid / Unmatched**
- Drill into any exception: see the source artifact (PDF), payment context, and a pre-drafted internal escalation email addressed to the account manager who owns that customer

> **Built as a 1-hour hackathon POC.** Not production-hardened, but intentionally structured so production-grade components (real OCR, live IMAP ingestion, ERP integration) can be dropped in module by module.

---

## Live demo

👉 **[Try it on Streamlit Cloud](https://itrade-ccra-demo.streamlit.app/)** _(replace with your deployed URL)_

**Demo flow (60 seconds):**

1. **Inbox** → click **"Use sample data"** — ingests 13 pre-extracted payment fixtures
2. **Dashboard** → tiles update: Matched 12 / Underpaid 2 / Overpaid 2 / Unmatched 1
3. Click the **Underpaid** tab → filtered row list
4. Click **Open** on any row → drilldown: payment context + source PDF + remittance lines
5. Click **Draft account-manager escalation** → internal email pre-composed, copy to clipboard

---

## Architecture

```
ccra-poc/
├── app.py                      # Streamlit entry — all UI pages + routing
├── requirements.txt
├── runtime.txt                 # pins Python 3.10 for Streamlit Cloud
├── assets/
│   └── oms-icon.svg            # brand icon
├── fixtures/
│   ├── invoices/
│   │   ├── invoices.json       # 22-invoice seed ledger across 10 customers
│   │   └── customers.json      # customer → account manager mapping
│   ├── payments/
│   │   ├── inbox_manifest.json # 10 "forwarded email" fixture references
│   │   └── upload_manifest.json# 3 "uploaded file" fixture references
│   ├── extracted/              # pre-extracted JSON files (one per payment fixture)
│   └── artifacts/
│       └── pdf/                # source PDFs wired to specific invoices
└── src/
    ├── data_loader.py          # loads + caches fixture JSON
    ├── matching_engine.py      # pure function: (payments, invoices) → match results
    └── email_drafter.py        # classification-keyed internal escalation templates
```

### Core modules

| Module | Responsibility |
|--------|---------------|
| `src/matching_engine.py` | Deterministic exact-cents classifier. Pure function — no Streamlit dependencies. Easy to unit test and swap for a fuzzy/tolerance-based matcher. |
| `src/data_loader.py` | Loads invoices, customers, and fixture manifests. Replace with ERP API calls here. |
| `src/email_drafter.py` | Produces a draft internal escalation per classification. Swap templates or plug in an LLM here. |
| `app.py` | All UI: brand strip, inbox, dashboard with tab-strip filter, drilldown, email panel. One file for hackathon speed — split into `ui/` modules for production. |

---

## Getting started

### Prerequisites

- Python 3.10+
- No database, no API keys, no external services required

### Run locally

```bash
# 1. Clone
git clone https://github.com/hsharma-iTrade/ccra-poc.git
cd ccra-poc

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies (just two)
pip install -r requirements.txt

# 4. Run
streamlit run app.py
# → open http://localhost:8501
```

### Stop the server

```bash
# Option A — Ctrl+C in the terminal where Streamlit is running

# Option B — kill by port (if running in background)
kill $(lsof -ti :8501)          # macOS / Linux
# Windows: netstat -ano | findstr :8501 → taskkill /PID <pid> /F
```

---

## Deploy to Streamlit Cloud (free, 5 minutes)

1. Fork this repo on GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pick your fork, branch `main`, main file `app.py`
4. Click **Deploy** — first build takes ~2 min
5. Share the public URL with your team or customers

No secrets or environment variables needed for the POC fixture mode.

---

## Adding your own fixtures

All fixture data lives in `fixtures/`. No code changes required to add payments.

### Add a new payment fixture

1. Create a JSON file in `fixtures/extracted/` following this schema:

```json
{
  "fixture_id": "email_my_customer_20260601",
  "display_label": "My Customer Co — ACH 2026-06-01",
  "source_channel": "ACH_EMAIL",
  "payer_name": "My Customer Co",
  "check_number": "ACH-20260601-01",
  "payment_date": "2026-06-01",
  "total_amount": 5000.00,
  "remittance_lines": [
    { "invoice_number": "INV-2026-0001", "line_amount": 3000.00 },
    { "invoice_number": "INV-2026-0002", "line_amount": 2000.00 }
  ],
  "artifact_ref": "email_my_customer_20260601.txt",
  "scenario_note": "Multi-invoice ACH — fully matched"
}
```

2. Add an entry to `fixtures/payments/inbox_manifest.json` (or `upload_manifest.json`)
3. The matching engine will auto-classify against `fixtures/invoices/invoices.json`

### Add a source PDF

Map an invoice number to a PDF so the drilldown shows the real document:

```python
# In app.py, find INVOICE_PDF_MAP and add:
INVOICE_PDF_MAP = {
    "INV-2026-0020": "fixtures/artifacts/pdf/remittance_check_sample.pdf",
    "INV-YOUR-INV":  "fixtures/artifacts/pdf/your_check.pdf",   # ← add here
}
```

---

## Roadmap / good first issues

Contributions welcome — especially from developers who want to see this become a real product.

| # | Feature | Effort | Notes |
|---|---------|--------|-------|
| 🟢 | **Add more fixture scenarios** | XS | Multi-invoice partial pay, foreign currency, duplicate ACH |
| 🟢 | **Unit tests for matching engine** | S | `src/matching_engine.py` is a pure function — easy to cover |
| 🟡 | **Tolerance-based matching** | S | Match within ±$0.01 for rounding differences; configurable threshold |
| 🟡 | **Real IMAP ingestion** (Gmail / Outlook) | M | `imaplib` + App Password; poll on button click |
| 🟡 | **OCR extraction** (AWS Textract / Google Document AI) | M | Replace pre-extracted JSON with real PDF → JSON pipeline |
| 🟡 | **Export exceptions to CSV** | S | `st.download_button` on the dashboard |
| 🔴 | **ERP integration** (NetSuite / QuickBooks API) | L | Replace `fixtures/invoices/` with live API calls in `src/data_loader.py` |
| 🔴 | **Multi-tenant auth** | L | Streamlit + Auth0 / Supabase |
| 🔴 | **Webhook inbound email** (AWS SES / SendGrid) | L | Real-time push instead of poll |

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make your changes + add tests if touching `src/`
4. Open a pull request — describe what you changed and why
5. No CLA, no contributor agreement — just MIT

**Code style:** `black` + `ruff` (not enforced by CI yet — PRs to add that welcome!)

---

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| UI | [Streamlit](https://streamlit.io) 1.32+ | Fastest path from Python logic to interactive web UI |
| Matching engine | Pure Python + `decimal` | Exact-cents arithmetic; zero external dependencies |
| Data | JSON flat files | No DB setup — easy to fork and run locally |
| Deploy | Streamlit Community Cloud | Free tier, GitHub-connected, no config |

---

## License

MIT — do whatever you want with it. A star ⭐ is appreciated if you find it useful.

---

## Background

Built as a hackathon POC at [iTradeNetwork](https://www.itradenetwork.com) to demonstrate the AR reconciliation use case for fresh produce supply chains. The matching engine and exception-triage pattern are domain-agnostic — applicable to any business that receives payments against invoices.

Product requirements: [`docs/refined-prd.md`](../docs/refined-prd.md)
