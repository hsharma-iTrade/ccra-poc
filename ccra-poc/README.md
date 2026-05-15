# CCRA POC - Cash Collection Reconciliation Assistant

A 1-hour hackathon Proof-of-Concept that ingests payment artifacts (forwarded remittance emails, uploaded check images/PDFs), auto-matches them against a seeded invoice ledger, and surfaces an **Exceptions Dashboard** so AR clerks can focus only on the ~20% of payments that need a follow-up call.

Source of truth: [`docs/refined-prd.md`](../docs/refined-prd.md).

---

## What the demo proves

> "100 checks came in today - which 20 need my attention, and exactly which customer + invoice + amount for each?"

The POC answers that question in under 30 seconds for a curated fixture batch of 13 payments against a 22-invoice ledger.

The Critical Path Journey:

> **Inbox -> Use sample data -> Dashboard tiles -> click a tile -> click a row -> drill-down -> Draft follow-up -> Copy to clipboard**

All four classifications (`MATCHED`, `UNDERPAID`, `OVERPAID`, `UNMATCHED`) and both independent flags (`DUPLICATE`, `PAYER_MISMATCH`) appear in the fixture set, including at least one multi-invoice check.

---

## Tech stack

- **Python 3.10+** (any 3.10 / 3.11 / 3.12 / 3.13 works locally; Streamlit Community Cloud uses 3.10 per `runtime.txt`)
- **Streamlit** - single-page reactive UI
- **pandas** - tabular row list + filtering
- **decimal.Decimal** - exact-cents arithmetic (per PRD Q3)

No databases, no external services, no auth. Everything is fixture-driven and deterministic.

---

## Project structure

```
ccra-poc/
├── app.py                                # Streamlit entry point - run this
├── requirements.txt                      # Python dependencies
├── runtime.txt                           # Python version pin (Streamlit Cloud)
├── README.md                             # this file
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data_loader.py                    # fixture loaders + lookup builders
│   ├── matching_engine.py                # exact-cents classification logic
│   └── email_drafter.py                  # template-based follow-up drafter
└── fixtures/
    ├── invoices/
    │   ├── invoices.json                 # 22 seeded invoices, 10 customers
    │   └── customers.json                # customer reference + contact emails
    ├── payments/
    │   ├── inbox_manifest.json           # 10 forwarded-email fixtures
    │   └── upload_manifest.json          # 3 file-upload fixtures
    ├── extracted/                        # pre-extracted JSON per artifact (Q1)
    │   ├── bass_pro_check_44521.json
    │   ├── kroger_ach_2026051501.json
    │   └── ... (13 total, one per fixture)
    └── artifacts/                        # optional: drop real PDFs/images here
        └── README.txt
```

---

## Run locally

### 1. One-time setup

```bash
cd ccra-poc
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch the app

```bash
streamlit run app.py
```

Streamlit will open a browser to `http://localhost:8501` (or the next free port; the terminal output is authoritative).

### 3. Demo walkthrough (Critical Path)

1. App opens on the **Inbox** page showing 10 forwarded emails on the left and 3 sample uploads on the right.
2. Click **"Use sample data"** to ingest all 13 fixtures in one click (recommended for the demo).
3. The app jumps to the **Dashboard** showing four count tiles (Matched / Underpaid / Overpaid / Unmatched).
4. Click any tile to filter the row list below.
5. Click **Open** on any row to expand the drill-down panel with full Payment context + remittance lines + artifact preview.
6. Click **Draft follow-up** on an exception row to open the pre-composed email panel.
7. Click **Copy to clipboard** to copy the email body (browser confirms with a toast).

---

## Demo fixture scenario coverage

| Fixture                              | Classification mix                                      |
| ------------------------------------ | ------------------------------------------------------- |
| INBOX-001 (Bass Pro Foods)           | 2 MATCHED (multi-invoice)                               |
| INBOX-002 (Kroger ACH)               | 1 MATCHED                                               |
| INBOX-003 (Whole Foods lockbox)      | 1 UNDERPAID (-$50)                                      |
| INBOX-004 (Sysco - multi)            | 3-line check: 2 MATCHED + 1 (delta varies per ledger)   |
| INBOX-005 (US Foods ACH)             | 1 OVERPAID (+$100)                                      |
| INBOX-006 (Restaurant Depot)         | 1 MATCHED                                               |
| INBOX-007 (PFG - multi)              | 2 MATCHED (multi-invoice)                               |
| INBOX-008 (Mystery sender)           | 1 UNMATCHED                                             |
| INBOX-009 (Compass ACH)              | 1 OVERPAID + DUPLICATE (invoice already paid)           |
| INBOX-010 (TJ East LLC)              | 1 MATCHED + PAYER_MISMATCH (payer name differs)         |
| UPLOAD-001 (Kroger upload)           | 1 MATCHED                                               |
| UPLOAD-002 (Aramark upload)          | 1 UNDERPAID (-$125)                                     |
| UPLOAD-003 (Compass upload)          | 1 MATCHED                                               |

Every classification and flag appears at least once; INBOX-001, INBOX-004, and INBOX-007 are multi-invoice checks (PRD Q7).

---

## Determinism

Per PRD §12: the same fixtures + the same invoice ledger always produce byte-identical match results. There are no clocks read at match time, no random ids in the matching engine, no order-dependent lookups. You can run the demo end-to-end repeatedly without drift.

---

## Deploy to Streamlit Community Cloud (public URL)

Streamlit Community Cloud gives you a free public URL so the customer can view the demo on their laptop without any local install.

### Step 1 - Push the repo to GitHub

```bash
cd ccra-poc           # or the parent workspace, depending on how you want
                      # the repo to look on GitHub
git init
git add .
git commit -m "Initial CCRA POC scaffold"
git branch -M main

# Create an empty repo on github.com first (e.g. ccra-poc), then:
git remote add origin https://github.com/<your-username>/ccra-poc.git
git push -u origin main
```

### Step 2 - Connect the repo at share.streamlit.io

1. Open [https://share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Pick the repository (`<your-username>/ccra-poc`), branch `main`.
4. **Main file path:** `app.py`
5. **Python version:** Streamlit Cloud reads `runtime.txt` and uses **Python 3.10**. No manual selection needed.
6. Click **Deploy**.

### Step 3 - Share the public URL

Streamlit auto-assigns a URL like `https://<your-username>-ccra-poc-app-xxxxx.streamlit.app`. Send that link to the customer - the demo runs entirely in their browser, no install required.

### Notes

- Fixture data is committed to the repo, so the deployed app uses the exact same demo set as the local run. Determinism holds.
- The first deploy can take 2-3 minutes (Streamlit Cloud builds the venv). Subsequent rebuilds on `git push` are faster.
- `requirements.txt` is the only dependency manifest Streamlit Cloud reads. Keep it minimal.

---

## Out of scope (per PRD §7)

- Live OCR pipeline (pre-extracted JSON only, per Q1)
- Real ERP write-back
- Multi-tenant auth / SSO
- Outbound email send (clipboard only, per Q6)
- Production extraction accuracy
- Configurable match tolerance (exact-cents only, per Q3)
- Procurement-partner multi-source invoice ingestion (deferred to Phase 2)

---

## Troubleshooting

| Symptom                                              | Fix                                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'streamlit'`   | Activate the venv (`source .venv/bin/activate`) and re-run `pip install -r requirements.txt` |
| Port 8501 already in use                             | Streamlit will pick the next free port; check the terminal for the actual URL         |
| `FileNotFoundError: Required fixture missing`        | You moved or deleted a fixture file; restore from git                                 |
| Clipboard button blocked by browser                  | Use the Body textarea (it's editable + selectable) as the fallback per PRD §11        |
| Streamlit Cloud build fails on Python 3.10           | Verify `runtime.txt` contains exactly `python-3.10` (one line, no trailing whitespace) |
