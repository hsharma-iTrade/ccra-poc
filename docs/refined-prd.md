# Refined PRD: Cash Collection Reconciliation Assistant (CCRA)

## 1. Basic Information

| Field             | Value                                                            |
| :---------------- | :--------------------------------------------------------------- |
| Project Name      | Cash Collection Reconciliation Assistant (CCRA)                  |
| Internal Codename | ccra-poc                                                         |
| Priority          | High (Hackathon POC — customer-facing demo)                      |
| Target Release    | Hackathon Demo (1-hour POC scaffold + demo flow)                 |
| Pipeline Mode     | Greenfield (POC scope — PRD → Architecture → Plan → Code)        |
| Document Type     | Refined PRD (MVP-scoped)                                         |
| Source Material   | `interview_transcript.txt`, `voice_recording_transcript`, `docs/initial-prd.md` |
| MVP Sprint Window | Single 1-hour build sprint (POC scaffold + curated demo flow)    |

### Create Table

| Created By      | Name      | Date       |
| :-------------- | :-------- | :--------- |
| Harvey AI (PRD) | Harvey AI | 2026-05-15 |
| User (Operator) | hsharma   | 2026-05-15 |

### Sign-Off Table

| Role             | Approver Name | Status   | Sign-Off Date |
| :--------------- | :------------ | :------- | :------------ |
| PM               | hsharma       | Approved | 2026-05-15    |
| Engineering Lead | hsharma       | Approved | 2026-05-15    |
| Design           | hsharma       | Approved | 2026-05-15    |

> Note: Hackathon POC — single-operator demo. All three role sign-offs are recorded by the same user (hsharma) under Harvey's single-user convention for hackathon mode. In a production engagement these three roles would be filled by three distinct approvers from the customer org.

---

## 2. Executive Summary

The Cash Collection Reconciliation Assistant (CCRA) is a hackathon Proof-of-Concept that eliminates the most painful step in a food distributor's Accounts Receivable workflow: manually matching incoming customer payments (checks, ACH remittances, lockbox PDFs) against open invoices. The MVP demo ingests pre-extracted payment artifacts via email-forward and file-upload, runs an exact-cents matching engine against a seeded invoice ledger of ~100 sample invoices, and renders an **Exceptions Dashboard** that splits the day's payments into Matched / Underpaid / Overpaid / Unmatched buckets so AR clerks can focus only on the ~20% that need a follow-up call. Target users are the AR Clerk (primary), AR Manager, and Account Manager at a mid-market food distributor whose AR team scaling is bottlenecked by hand-keying every check stub. Expected business impact for the demo customer: directional validation that this approach can cut AR reconciliation time materially (~80% reduction stated in the customer interview) and unlock sub-linear AR headcount scaling — leading to a credible upsell from existing OMS/IR products.

---

## 3. Problem Statement

Food-distributor AR teams operate a structurally manual reconciliation workflow that breaks at scale:

1. **Payment artifacts arrive through fragmented, mostly non-electronic channels** — mailed paper checks with stubs, lockbox PDF scans, ACH remittance emails (PDF or inline body), and occasional bank notifications. There is no single ingest point. *Source: `interview_transcript.txt`*
2. **Every artifact is hand-keyed.** Stubs list one-or-many invoice numbers and amounts that must sum to the check total; clerks transcribe every line into the ERP one-by-one.
3. **The ERP holds invoices but cannot see incoming payments until a clerk types them in.** Invoices flow OMS → ERP, but payment matching stops there. The clerk cannot know whether a $1,000 invoice was paid in full, paid at $950, or paid at $800 until the check is opened and processed. *Source: `interview_transcript.txt` lines 1–14*
4. **Short-pays trigger a chase loop with no context.** Once a payment doesn't match, the clerk hands it off to the account manager who must re-investigate every claim from scratch (e.g., *"they're not paying for the broccoli"*, *"they're not paying for the temperature quarter"*). This is the highest-value work, buried under the 80% of routine matches.
5. **The team cannot scale linearly with revenue growth.** Customer stated: *"it has been very hard to add people in that team as we grow because it's a lot of manual checking."* *Source: `voice_recording_transcript` lines 4–6*

**The core problem CCRA solves:** AR clerks cannot answer, at a glance, *"100 checks came in today — which 20 need my attention, and exactly which customer + invoice + amount for each?"* Today, producing that view is a multi-hour aggregation task. The MVP demo proves the path from raw payment artifact → classified exception list in under 30 seconds.

---

## 4. KPIs & Business Justification

### KPIs

| KPI                                              | Baseline (Today)                   | Target (Post-POC, illustrative) | Notes                                                                |
| :----------------------------------------------- | :--------------------------------- | :------------------------------ | :------------------------------------------------------------------- |
| Time per 100 checks to produce exception list    | Hours (manual aggregation)         | Minutes                         | ~80% reduction stated by customer in interview                       |
| % of checks needing human review                 | 100% (every check hand-keyed)      | ~20% (only exceptions)          | The 80% that match cleanly are auto-applied                          |
| Time to first follow-up call on a short-pay      | Hours-to-days (after manual sweep) | Same-day                        | Exceptions surface immediately after ingest                          |
| Cash-application accuracy                        | Human transcription error rate     | Higher (auto-extract + match)   | Removes hand-keying step                                             |
| AR headcount scalability                         | Linear with payment volume         | Sub-linear                      | Scaling pain explicitly called out by customer                       |
| Demo "direction-validation" outcome (POC-specific) | N/A                              | Customer says "yes, this is the direction" | Single binary KPI for hackathon success                        |

### Business Justification

- **Why now:** Customer is actively struggling to scale the AR team with revenue growth; only ~25% of revenue flows through their own OMS, with the remainder coming through procurement partners (Kroger, retail chains, food-service distributors), each with different invoice formats. Manual reconciliation is the hard bottleneck. *Source: `interview_transcript.txt`*
- **Strategic fit:** Customer already operates an Invoice Register (IR) system and an OMS. CCRA is a natural payment-capture + matching extension and a credible upsell.
- **Demo value:** A working POC that ingests a forwarded remittance email + a scanned check, matches both against sample invoices, and renders an exceptions dashboard tells a compelling, tangible time-savings story in a 1-hour hackathon demo.

---

## 5. Success Criteria

For the **hackathon POC MVP**, success is defined as **all** of the following:

1. **Customer direction confirmation:** The customer (interview participant) watches the demo and confirms *"Yes — this is the direction we want; if this worked at full scale, it would cut our AR reconciliation time materially."*
2. **End-to-end demo runs in under 5 minutes** with no operator intervention beyond clicking through the Critical Path Journey:
   - Load sample payment artifacts (forwarded remittance email PDF + scanned check image, both pre-extracted per Q1 decision).
   - Run extraction + matching against the seeded invoice ledger.
   - Render the Exceptions Dashboard with the four classification tiles.
   - Drill into one underpayment row → view payment context + artifact thumbnail.
   - Open the "Draft follow-up" panel and copy the pre-composed email body.
3. **All four classification outcomes appear in the demo:** at least one `MATCHED`, one `UNDERPAID`, one `OVERPAID`, one `UNMATCHED`, and **at least one multi-invoice check** (per Q7).
4. **Three Sign-Off roles Approved** on this refined PRD (recorded in §1).

**Explicitly out of scope for "success":** production-grade extraction accuracy, full ERP integration, multi-tenant security, scale beyond ~100 invoices and ~30 payments, accessibility conformance, mobile-native UI, outbound email send.

---

## 6. Users & Personas

> Note: The customer org's published persona master list was not provided. Personas below are provisional, derived from the interview transcript, and flagged for confirmation by the customer's product team (per Q5 resolution: use provisional personas for the demo).

| Persona             | Role                        | Goals                                                                              | Pain Points (Today)                                                                              |
| :------------------ | :-------------------------- | :--------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| **AR Clerk (primary)** | Processes incoming payments | Apply every payment to the right invoice quickly; flag short-pays for follow-up | Hand-keys every stub; aggregates across email, lockbox, paper, ACH; no consolidated view; cannot answer "which checks need my attention today?" in under an hour |
| **AR Manager**      | Owns AR team performance    | Scale reconciliation throughput without linear headcount growth                    | Cannot hire fast enough; team time is consumed by routine matching, not real exceptions          |
| **Account Manager** | Owns customer relationship  | Resolve short-pays with customers; recover claim amounts                           | Receives short-pays with no context; must re-investigate every claim from scratch                |
| **ERP / OMS Admin** (system actor) | Keeps invoice data flowing | Maintain a reliable invoice feed into CCRA from OMS / IR / data warehouse | Currently no payment-side visibility loops back to ERP; manual cash application introduces lag |

**Primary user for the MVP demo:** AR Clerk. The Exceptions Dashboard and drill-down flow are designed against the AR Clerk's mental model: *"100 checks came in — 80 matched, 15 underpaid, 5 overpaid; show me the 20 with the customer + invoice + delta."*

*Provisional personas — flag for addition to the customer's master persona list during a production engagement.*

---

## 7. Scope

### Critical Path Journey (MVP)

The single user journey the MVP must prove end-to-end:

> **Forward remittance email (or upload check image) → System extracts payment data → Auto-match against invoice ledger → AR Clerk views Exceptions Dashboard → Drills into an exception row → Opens the pre-composed follow-up email draft → Copies it to clipboard.**

Everything in the MVP scope below exists to support this single path. Everything outside it is deferred.

### In Scope (MVP — 1-hour POC Build)

1. **Two ingest channels:**
   - **Email forwarding** — a forwarding inbox concept; for POC build, simulated via local fixture-based ingestion of pre-extracted JSON tied to sample email PDFs (per Q1).
   - **File upload** — drag-and-drop / file-picker for PDF + image artifacts in the POC UI. Upload triggers fixture-based extraction (per Q1); a "Use sample data" toggle bypasses any live OCR.
2. **Invoice ledger seed** — a CSV/JSON fixture of ~100 sample invoices representing the consolidated invoice view that would normally come from the customer's data warehouse / ERP. Includes a mix of customers and open balances.
3. **Matching engine with exact-cents tolerance** (per Q3) producing four mutually-exclusive classifications per Remittance Line: `MATCHED`, `UNDERPAID`, `OVERPAID`, `UNMATCHED`. Plus two non-mutually-exclusive flags: `DUPLICATE` (invoice already fully paid) and `PAYER_MISMATCH` (warn-only per Q4).
4. **Exceptions Dashboard** with four summary tiles (Matched / Underpaid / Overpaid / Unmatched counts) and a filterable, sortable row list (Customer · Invoice # · Invoiced · Paid · Delta · Source · Received).
5. **Drill-down side panel** — clicking a row shows the full Payment context (all Remittance Lines on that check, per-line match status) plus a thumbnail/preview of the source artifact.
6. **Follow-up email draft preview** — "Draft follow-up" button opens a side panel with a pre-composed body (payer name, invoice number(s), invoiced vs paid amounts, delta). "Copy to clipboard" only — no live send (per Q6).
7. **Multi-invoice check demo case** (per Q7) — at least one fixture demonstrates a single check settling multiple invoices, with at least one of those lines triggering an exception.
8. **Determinism guarantee** — same fixtures + same invoice ledger always produce identical match results across runs.

### Out of Scope (Deferred — Phase 2 or later)

| Item                                                                            | Rationale for Deferral                                                                          |
| :------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------- |
| AP three-way matching (paper invoice → pending payable → release)               | Customer confirmed this is a "flip" of the AR flow — valuable but explicitly out of POC scope (Q2) |
| Post-recall recovery / chargeback reconciliation (multi-party, multi-year)      | Complex multi-party workflow (grower-shipper → distributor → retailer); explicitly deferred     |
| Direct lockbox API ingestion                                                    | Email-forwarded lockbox PDFs cover the POC; native lockbox APIs are a later integration         |
| Direct bank ACH feed (BAI/CAMT, bank APIs)                                      | Email ACH notifications are sufficient for demo                                                  |
| Live ERP write-back (auto cash application)                                     | POC reads invoices from seed; doesn't post payments back                                         |
| Multi-tenant auth, SSO, role-based access                                       | Single demo user / no auth for POC                                                              |
| Production extraction accuracy (>99%)                                           | POC uses pre-extracted JSON tied to curated samples (Q1)                                         |
| Live OCR pipeline (Tesseract / cloud OCR)                                       | Pre-extracted JSON for demo reliability; live OCR may be added if time permits (Q1)              |
| Outbound email send (Gmail / Outlook draft integration)                         | POC shows clipboard-copy only (Q6)                                                              |
| Procurement-partner invoice ingestion (Kroger, retail chains, food-service)     | POC assumes seed CSV represents the consolidated view; multi-source ingestion is Phase 2 (Q8)    |
| Configurable match tolerance (e.g., $0.01 fuzz)                                 | POC is exact-match only (Q3); configurable tolerance is a Phase 2 enhancement                    |
| `PAYER_MISMATCH` blocking behavior, resolution workflows, audit log UI          | Warn-only flag for POC (Q4); resolution UI deferred                                              |
| Real-time invoice feed from ERP/OMS/IR                                          | POC uses static seed; live feeds are Phase 2                                                    |
| Mobile-native ingestion app                                                     | Browser file-upload (with `<input capture>`) is sufficient for POC                              |
| Accessibility / WCAG conformance, internationalization, multi-language          | Best-effort keyboard nav only for POC                                                            |

---

## 8. Use Cases

> 5 MVP use cases, all required for the Critical Path Journey. Two Phase-2 use cases retained for traceability.

### Phasing Summary

| ID     | Use Case                                            | Phase   | Critical Path? |
| :----- | :-------------------------------------------------- | :------ | :------------- |
| UC-001 | Ingest payment artifacts via forwarded email        | MVP     | Yes            |
| UC-002 | Ingest payment artifacts via image/file upload      | MVP     | Yes            |
| UC-003 | Auto-match payments against open invoices           | MVP     | Yes            |
| UC-004 | View Exceptions Dashboard and drill into details    | MVP     | Yes            |
| UC-005 | Preview follow-up email draft for an exception      | MVP     | Yes            |
| UC-006 | AP three-way invoice matching                       | Phase 2 | —              |
| UC-007 | Recall-recovery reconciliation                      | Phase 2 | —              |

---

### UC-001 — Ingest Payment Artifacts via Forwarded Email

- **Actors:** AR Clerk (primary); Email Ingest Service (system).
- **Trigger:** AR Clerk forwards a remittance email (ACH notification, lockbox PDF, scanned-check email) to the dedicated CCRA inbox concept (e.g., `check-processing@<customer>.com`). For POC build: simulated by loading a pre-curated email-fixture record.
- **Steps:**
  1. Email-fixture record is selected/loaded into CCRA.
  2. System parses email body + attachments (PDF, image).
  3. System extracts (from pre-extracted JSON tied to the fixture, per Q1): payer name/ID, payment date, check/reference number, total amount, list of (invoice number, amount) Remittance Lines.
  4. System persists a Payment record + one Remittance Line per stub line.
  5. System hands off to UC-003 (matching engine).
- **Alt / Edge Flows:**
  - Email has no extractable payment data → Payment marked `extraction_status=FAILED`, surfaced in dashboard as "needs manual review."
  - Email contains multiple PDFs → each PDF processed as a separate Payment.
  - PDF text unreadable (low-quality scan) → for POC, the pre-extracted JSON path bypasses this; flagged `extraction_status=PARTIAL` if a fixture deliberately simulates this case.
- **Business Rules:**
  - One forwarded email = one or more Payment records (depending on attachment count).
  - Re-ingestion of the same artifact (same `check_number` + `total_amount` + `payer_name`) flags `DUPLICATE_ARTIFACT` (per §11).
- **Acceptance Criteria:**
  - Given a forwarded email fixture with a remittance PDF, when the system processes it, then a Payment record is created with at minimum: `payer_name`, `total_amount`, and ≥1 Remittance Line.
  - Given a multi-invoice stub, the system creates exactly one Remittance Line per invoice referenced on the stub, and the sum of Remittance Line amounts equals the Payment `total_amount` (else the Payment is flagged as reconciliation-discrepant).

---

### UC-002 — Ingest Payment Artifacts via Image/File Upload

- **Actors:** AR Clerk (primary); Upload UI; Extraction Service (system).
- **Trigger:** AR Clerk opens the POC UI and drags/selects one or more check or stub artifacts (image or PDF) into the upload zone.
- **Steps:**
  1. User uploads file(s) via the UI.
  2. System runs extraction on each artifact — for POC, extraction is a fixture lookup keyed by filename → pre-extracted JSON (per Q1).
  3. System produces Payment + Remittance Line records identical in shape to UC-001.
  4. Hands off to UC-003.
- **Alt / Edge Flows:**
  - File is not an image or PDF → reject with user-facing error; no Payment created.
  - File has no matching fixture in the POC seed → flag `INVALID_ARTIFACT` and surface in dashboard.
  - "Use sample data" toggle → bypasses upload, loads the full demo fixture batch in one click.
- **Business Rules:**
  - User may upload 1–N files in a single action.
  - Mobile-camera capture uses the same upload endpoint via `<input type="file" capture>`.
- **Acceptance Criteria:**
  - Given a check-image upload that matches a known fixture, when processed, then a Payment record with `payer_name`, `total_amount`, and `check_number` is created.
  - Given 5 files uploaded simultaneously, 5 Payment records are created (or rejected with explicit reasons per artifact).

---

### UC-003 — Auto-Match Payments Against Open Invoices

- **Actors:** Matching Engine (system).
- **Trigger:** A Payment record with ≥1 Remittance Line is persisted by UC-001 or UC-002.
- **Steps:**
  1. For each Remittance Line, look up `invoice_number` in the Invoice Ledger.
  2. If invoice not found → classify line `UNMATCHED`.
  3. If invoice found and `open_balance == 0` → classify line `DUPLICATE` (invoice already fully paid).
  4. If invoice found and `open_balance > 0`:
     - `line_amount == open_balance` → `MATCHED`
     - `line_amount < open_balance` → `UNDERPAID`
     - `line_amount > open_balance` → `OVERPAID`
  5. If the Payment's `payer_name` does not match the invoice's `customer_name` → also set `PAYER_MISMATCH` flag (warn-only, does not change the primary classification).
  6. Compute `delta_amount = line_amount − open_balance` (signed).
  7. Persist one Match Result per Remittance Line.
- **Alt / Edge Flows:**
  - One check covers multiple invoices → each Remittance Line is evaluated independently; the Payment as a whole shows a rolled-up status (e.g., "3 lines: 2 matched, 1 underpaid").
  - Remittance Line with negative or zero amount → reject the line (§11) and flag the Payment `extraction_status=PARTIAL`.
- **Business Rules:**
  - **Matching tolerance is exact-cents for POC** (per Q3 decision). Configurable tolerance is Phase 2.
  - The four primary classifications (`MATCHED`, `UNDERPAID`, `OVERPAID`, `UNMATCHED`) are mutually exclusive.
  - `DUPLICATE` and `PAYER_MISMATCH` are independent flags; either may coexist with any primary classification (e.g., an `UNMATCHED` payment from an unknown payer is `UNMATCHED + PAYER_MISMATCH`).
  - A single check may settle 1–N invoices.
- **Validation Rules:**
  - `invoice_number` must be a non-empty string.
  - `line_amount` must be a non-zero positive decimal.
- **Calculation Logic:**
  - `delta_amount = line_amount − open_balance` (negative = underpayment, positive = overpayment, zero = matched).
- **Acceptance Criteria:**
  - Every Remittance Line has exactly one Match Result with exactly one primary classification.
  - Re-running the matching engine on the same Payment + Invoice Ledger yields byte-identical Match Results (determinism per §12).

---

### UC-004 — View Exceptions Dashboard and Drill Into Details

- **Actors:** AR Clerk (primary); AR Manager.
- **Trigger:** User opens the CCRA dashboard URL (root of the POC app).
- **Steps:**
  1. Dashboard loads with four summary tiles: **Matched count**, **Underpaid count**, **Overpaid count**, **Unmatched count**. Counts roll up across all Remittance Lines in the current session.
  2. User clicks a tile (e.g., "Underpaid").
  3. Row list below filters to that classification. Columns: **Customer · Invoice # · Invoiced Amount · Paid Amount · Delta · Source (email/upload) · Received Date**.
  4. User clicks a row → side panel opens with full Payment context (the entire check + all its Remittance Lines, each showing its individual match status) + thumbnail/preview of the source artifact when available.
  5. User can return to dashboard view without losing dashboard filter state.
- **Alt / Edge Flows:**
  - No payments ingested yet → dashboard shows zero tiles and an empty-state message: "No payments ingested yet. Forward an email or upload a file to begin."
  - All payments matched cleanly (zero exceptions) → dashboard shows the matched count and an "All clear" state on the three exception tiles.
  - Row list is empty when filtered → "No exceptions in this category" message.
- **Business Rules:**
  - Summary count for a classification = number of Remittance Lines with that primary classification.
  - `DUPLICATE` and `PAYER_MISMATCH` flags are displayed as badges in the row list and side panel but do not alter the tile counts.
- **State Transitions:** Match Result lifecycle: `created` → (POC stops here; `RESOLVED` state is Phase 2). The dashboard is read-only — no resolve/dismiss actions in MVP.
- **Acceptance Criteria:**
  - Summary tile counts sum to the total Remittance Lines ingested.
  - Drill-down row displays customer name, invoice number, delta amount that exactly match the underlying Match Result and source artifact.
  - Dashboard renders in <2 seconds for the POC scale (~30 payments, ~100 Remittance Lines).

---

### UC-005 — Preview Follow-Up Email Draft for an Exception

- **Actors:** AR Clerk (primary).
- **Trigger:** From a drill-down row (UC-004), user clicks "Draft follow-up."
- **Steps:**
  1. System opens a side panel with a pre-composed email body:
     - **To:** payer's `contact_email` (mocked in the Customer fixture for POC).
     - **Subject:** references the invoice number(s) (e.g., "Re: Payment for INV-2026-0042 — short by $50.00").
     - **Body:** payer name, invoice number(s), invoiced vs paid amounts, delta, polite ask to clarify.
  2. User clicks "Copy to clipboard" → full body is copied (per Q6: clipboard-copy only, no live send).
- **Alt / Edge Flows:**
  - For `OVERPAID` exceptions, the draft acknowledges the overpayment and asks how to apply the surplus.
  - For `UNMATCHED`, the draft asks the payer to confirm which invoice(s) the payment was intended for.
  - For `DUPLICATE`, the draft notes that the referenced invoice appears to be already paid and asks the payer to clarify.
- **Business Rules:**
  - Draft is generated from a small set of templates keyed on classification.
  - No outbound email is ever sent by the POC.
- **Acceptance Criteria:**
  - Draft body includes payer name, invoice number(s), invoiced amount, paid amount, delta — all values matching the underlying Match Result.
  - "Copy to clipboard" succeeds in modern browsers; user sees a toast/confirmation.

---

## 9. Data, Entities & Information

### Core Entities (MVP)

#### Invoice (read-only seed data for POC)

| Field          | Type    | Required | Notes                                                    |
| :------------- | :------ | :------- | :------------------------------------------------------- |
| invoice_id     | string  | yes      | Primary key; e.g., `INV-2026-0001`                       |
| customer_id    | string  | yes      | FK → Customer                                            |
| customer_name  | string  | yes      | Denormalized for POC display                             |
| invoice_date   | date    | yes      |                                                          |
| due_date       | date    | yes      |                                                          |
| total_amount   | decimal | yes      | Invoice face value                                       |
| open_balance   | decimal | yes      | Remaining balance; static in POC (no write-back)         |
| status         | enum    | yes      | `OPEN`, `PAID`, `PARTIALLY_PAID`                         |
| description    | string  | no       | Line-item summary (e.g., "produce — broccoli, lettuce")  |
| source_system  | string  | no       | Originating upstream system (ERP, OMS, IR); POC: `SEED` |

#### Payment (created from ingested artifact)

| Field             | Type      | Required | Notes                                                          |
| :---------------- | :-------- | :------- | :------------------------------------------------------------- |
| payment_id        | string    | yes      | Generated                                                      |
| source_channel    | enum      | yes      | `EMAIL`, `UPLOAD`, `LOCKBOX_EMAIL`, `ACH_EMAIL`                |
| received_at       | timestamp | yes      | When CCRA ingested the artifact                                |
| payer_name        | string    | yes      | Extracted from check/stub/remittance                           |
| check_number      | string    | no       | Reference number for non-check payments                        |
| payment_date      | date      | no       |                                                                |
| total_amount      | decimal   | yes      | Full amount on the check / remittance                          |
| raw_artifact_ref  | string    | no       | Path to stored PDF/image (POC: fixture filename)                |
| extraction_status | enum      | yes      | `EXTRACTED`, `PARTIAL`, `FAILED`                               |

#### Remittance Line (one per invoice referenced on a stub)

| Field          | Type    | Required | Notes                                                  |
| :------------- | :------ | :------- | :----------------------------------------------------- |
| line_id        | string  | yes      | Generated                                              |
| payment_id     | string  | yes      | FK → Payment                                           |
| invoice_number | string  | yes      | As written on the stub (may not match a known invoice) |
| line_amount    | decimal | yes      | Amount applied to that invoice                         |
| description    | string  | no       |                                                        |

#### Match Result (one per Remittance Line)

| Field           | Type      | Required | Notes                                                                                  |
| :-------------- | :-------- | :------- | :------------------------------------------------------------------------------------- |
| match_id        | string    | yes      | Generated                                                                              |
| line_id         | string    | yes      | FK → Remittance Line (1:1)                                                             |
| invoice_id      | string    | no       | FK → Invoice (null when `UNMATCHED`)                                                   |
| classification  | enum      | yes      | Primary: `MATCHED`, `UNDERPAID`, `OVERPAID`, `UNMATCHED`. Mutually exclusive.          |
| flags           | enum-list | no       | Independent flags: `DUPLICATE`, `PAYER_MISMATCH`. Zero or more may apply.              |
| delta_amount    | decimal   | yes      | `line_amount − open_balance` (negative = under, positive = over, zero = matched)       |
| created_at      | timestamp | yes      |                                                                                        |

#### Customer (lightweight reference)

| Field         | Type   | Required | Notes                                  |
| :------------ | :----- | :------- | :------------------------------------- |
| customer_id   | string | yes      |                                        |
| customer_name | string | yes      |                                        |
| contact_email | string | no       | Used for draft follow-up emails (mocked) |

### Relationships

- `Customer 1—N Invoice` (each invoice belongs to one customer).
- `Payment 1—N Remittance Line` (each check has one or more stub lines).
- `Remittance Line 1—1 Match Result` (every line gets exactly one match result).
- `Match Result 0..1—1 Invoice` (a match result references an invoice except when `UNMATCHED`).

### Privacy & Sensitivity

- Customer payment data is **financially sensitive PII** in production.
- **POC uses 100% synthetic data** — no real customer payment artifacts are ingested.
- **Production (Phase 2) requirements** (not implemented in POC): encryption at rest for stored artifacts, PII handling per the customer org's data policy, immutable audit log of every Match Result, role-based access control, retention policies.

### Data Volume (POC)

- **Invoices:** ~100 seed rows.
- **Payments:** ~20–30 per demo run.
- **Remittance Lines:** ~30–80 per demo run (some checks single-invoice, some multi-invoice).
- **Match Results:** 1:1 with Remittance Lines.
- All data fits comfortably in memory; no DB tuning required.

---

## 10. Integrations

### POC (In Scope)

| System                  | Direction | Mechanism                                                | Notes                                                                              |
| :---------------------- | :-------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| Email inbox concept     | Inbound   | Fixture-based — pre-extracted JSON tied to email-fixture filenames | Simulates forwarded remittance emails; no live IMAP for POC                  |
| File upload UI          | Inbound   | Browser multipart upload (drag-drop / file-picker)       | Mobile-camera flow via `<input type="file" capture>` uses the same endpoint        |
| Invoice ledger seed     | Inbound   | Static CSV or JSON fixture loaded at app start           | Represents the customer's consolidated invoice list from ERP/OMS/IR/data warehouse |
| Clipboard               | Outbound  | Browser Clipboard API                                    | "Copy follow-up email to clipboard" — sole outbound channel in POC                 |

### Future / Deferred (Phase 2)

| System                                                                          | Direction                   | Mechanism                          | Notes                                                                       |
| :------------------------------------------------------------------------------ | :-------------------------- | :--------------------------------- | :-------------------------------------------------------------------------- |
| Customer ERP / OMS                                                              | Inbound (invoices)          | API / scheduled extract            | Real consolidated invoice feed                                              |
| Customer ERP                                                                    | Outbound (cash application) | API write-back                     | Auto-apply matched payments to ERP                                          |
| Lockbox provider                                                                | Inbound                     | Lockbox API or SFTP                | Native lockbox feed                                                         |
| Bank ACH feeds                                                                  | Inbound                     | Bank API or BAI/CAMT files         | Direct ACH notifications                                                    |
| Outlook / Gmail (drafts)                                                        | Outbound                    | Graph API / Gmail API              | Place drafts directly in the user's outbox (per Q6, deferred)               |
| Procurement partners (Kroger, retail chains, food-service distributors)         | Inbound                     | Partner-specific feeds             | Multi-source invoice consolidation (per Q8, deferred)                       |
| Live OCR pipeline (Tesseract / cloud OCR)                                       | Internal                    | Library or cloud service           | Production-grade extraction; POC uses pre-extracted JSON per Q1             |

---

## 11. Error Handling & Edge Cases

| Condition                                                          | Behavior                                                                                                  |
| :----------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| Email arrives with no recognizable payment data                    | Payment record created with `extraction_status=FAILED`; surfaced in dashboard as "needs manual review"    |
| PDF/image extraction yields low confidence (POC: simulated)        | `extraction_status=PARTIAL`; flagged in dashboard                                                          |
| Invoice number on stub does not exist in ledger                    | Match Result `classification=UNMATCHED`                                                                    |
| Invoice exists but `open_balance == 0` (already fully paid)        | Match Result `classification=MATCHED|UNDERPAID|OVERPAID` per amount + `flags=[DUPLICATE]`                  |
| Payer on check ≠ customer-of-record on invoice                     | Match Result keeps its primary classification + `flags=[PAYER_MISMATCH]` (warn only per Q4)                |
| Stub line amounts do not sum to check `total_amount`               | Payment flagged `extraction_status=PARTIAL`; dashboard row shows "reconciliation discrepancy" badge        |
| Same Payment ingested twice (same `check_number` + `total_amount` + `payer_name`) | Second ingestion rejected as `DUPLICATE_ARTIFACT`; no new Payment created                          |
| Upload file is not an image or PDF                                 | Reject with user-facing error message; no Payment created                                                  |
| Upload filename has no matching POC fixture                        | Flag artifact `INVALID_ARTIFACT`; surface in dashboard with explanation                                    |
| Remittance Line has negative or zero amount                        | Reject the line; flag Payment `extraction_status=PARTIAL`                                                  |
| Empty session (no payments ingested yet)                           | Dashboard renders empty-state message with ingestion CTA                                                   |
| Browser Clipboard API unavailable / blocked                        | Show inline fallback: pre-composed text in a selectable textarea with "Select all" affordance              |
| Demo machine offline / file system unreachable for fixtures        | App fails fast at startup with a clear error pointing to the missing fixture path                          |

---

## 12. Non-Functional Expectations

> Calibrated for a 1-hour hackathon POC. Production targets would be re-set during a production engagement.

| Category         | POC Expectation                                                                                                                |
| :--------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| Performance      | Demo flow completes end-to-end (ingest → match → dashboard render) in < 30 seconds for the full fixture batch (~30 artifacts)  |
| Scalability      | POC handles ~100 invoices and ~30 payments fully in memory; no DB tuning, no pagination required                               |
| Availability     | Single-instance local dev server; no HA, no failover                                                                            |
| Security         | No real PII; no authentication; local-only deployment; demo machine considered trusted                                          |
| Accessibility    | Best-effort keyboard navigation on dashboard and side panels; full WCAG conformance deferred                                   |
| Platform Support | Modern desktop browser (Chrome / Edge / Safari latest). Mobile-camera upload supported via `<input type="file" capture>`        |
| **Determinism**  | Given the same fixture set + same invoice ledger, matching results are byte-identical across runs (critical for demo reliability) |
| **Reproducibility** | Demo runs identically on any operator's machine given the same fixture directory checked into the repo                       |
| Observability    | Console logging sufficient for POC; structured logs deferred                                                                    |
| Localization     | English only; i18n deferred                                                                                                     |
| Data retention   | All POC data is in-memory / fixture-based; nothing is persisted across app restarts                                            |

---

## 13. UI/UX Requirements

### Key Screens

1. **Inbox / Upload Screen** (secondary)
   - Drop zone for files (PDF / images) with a file-picker fallback.
   - "Use sample data" button — loads the full demo fixture batch in one click (primary demo path).
   - List of recently-ingested artifacts with `extraction_status` badges (`EXTRACTED` / `PARTIAL` / `FAILED`).

2. **Exceptions Dashboard** (primary demo screen — landing page)
   - **Four summary tiles** at the top: **Matched (count)** · **Underpaid (count)** · **Overpaid (count)** · **Unmatched (count)**.
   - Clicking a tile filters the row list below by primary classification.
   - **Row list columns:** Customer · Invoice # · Invoiced · Paid · Delta · Source (email/upload) · Received Date.
   - Sort by any column; simple text filter on Customer / Invoice #.
   - `DUPLICATE` and `PAYER_MISMATCH` flags shown as inline badges on affected rows.

3. **Drill-Down Side Panel**
   - Opens on row click (no full page reload).
   - Shows the full Payment header (payer, check number, total amount, received date, source channel).
   - Lists all Remittance Lines on that Payment, each with its per-line match status.
   - Thumbnail/preview of the source artifact (PDF first-page render or image) when available.
   - **"Draft follow-up" button** → opens email draft panel.

4. **Email Draft Panel**
   - Pre-composed body with payer name, invoice number(s), invoiced/paid/delta amounts, classification-specific wording.
   - "Copy to clipboard" button + toast confirmation on success.
   - "Close" returns focus to the drill-down panel.

### Interaction Patterns

- Single-page app feel: dashboard ↔ drill-down ↔ email draft all happen in the same view, no full page reloads.
- **Dashboard is the landing screen** — exception counts are the first thing the user sees, consistent with the customer's stated mental model: *"he wants to see 100 checks came in, 80 matched, 15 underpaid, 5 overpaid."* *Source: `interview_transcript.txt`*
- Empty state, loading state, and error state are explicit (not silent).
- Keyboard navigation works for tile selection, row navigation, and panel close (best-effort).

### Visual / Style Direction (POC)

- Lightweight, clean, demo-friendly aesthetic — clarity over polish.
- Theme: light only for POC (system/dark deferred).
- Responsive: desktop-first; layout should not break on tablet/mobile, but a mobile-optimized experience is out of scope.

### Design Assets

```
Design Assets: None provided — UI will be planned during the build phase by the UX Design agent.
  figma_file_url: "None"
  figma_screens: []
  screenshots: "None"
  wireframes: "None"
  notes: "Customer did not provide any visual references in the interview or voice recording. UX Design will plan a minimal, demo-friendly layout for the 1-hour POC build."
```

> **Note for Architect:** Tech stack, framework, component library, and design system choices are deferred to Architect mode. This PRD specifies only the UI/UX requirements (screens, interactions, layout, content), not the implementation technology.

---

## 14. Constraints, Dependencies & Risks

### Constraints

- **Time-boxed:** 1-hour hackathon POC build. Scope must remain on the Critical Path Journey; everything else is deferred.
- **Synthetic data only:** Customer's real invoice/payment data is not available. POC uses curated fixtures.
- **Local-only deployment:** No cloud deployment, no production hosting, no shared environment.
- **No real OCR for the demo path:** Pre-extracted JSON tied to fixture filenames (per Q1). Live OCR may be attempted only as a stretch if time permits.
- **Single demo operator:** No auth, no multi-user state, no concurrency considerations.

### Dependencies

| Dependency                                                                                                                | Owner | Status     |
| :------------------------------------------------------------------------------------------------------------------------ | :---- | :--------- |
| Synthetic invoice ledger fixture (CSV/JSON, ~100 sample invoices across multiple customers, mix of open balances)         | Team  | To create  |
| Synthetic payment artifacts (3–5+ sample PDFs/images covering MATCHED, UNDERPAID, OVERPAID, UNMATCHED, multi-invoice cases) | Team  | To create  |
| Pre-extracted JSON files keyed by fixture filename (per Q1)                                                               | Team  | To create  |
| Customer / payer contact emails (mocked in Customer fixture for draft-email content)                                       | Team  | To create  |

### Risks

| Risk                                                                                  | Likelihood | Impact | Mitigation                                                                                                                                |
| :------------------------------------------------------------------------------------ | :--------- | :----- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| Live OCR accuracy too low for live demo                                                | High       | High   | Pre-extracted JSON is the primary demo path (per Q1). Live OCR is a stretch goal only.                                                     |
| Demo fixtures don't represent customer's real artifacts well                           | Medium     | Medium | Build fixtures directly from interview patterns: multi-invoice stubs, multiple channels, the four classifications, payer mismatch case.    |
| Customer expects production polish in POC                                              | Medium     | Medium | Frame demo explicitly as direction-validation, not a production system. State this in the demo opening.                                    |
| Scope creep into AP matching or recall recovery                                        | Low        | High   | Both explicitly listed Out of Scope in §7. Decline mid-build requests; capture as Phase 2.                                                 |
| Clipboard API blocked in browser context (rare)                                        | Low        | Low    | Fallback: pre-composed text in a selectable textarea (§11).                                                                                |
| 1-hour build window slips because of fixture creation                                   | Medium     | High   | Time-box fixture creation to the first 15 minutes; have a fallback hard-coded JSON if creation overruns.                                   |
| Customer asks for procurement-partner multi-source ingestion live                       | Medium     | Medium | Acknowledge as a strong Phase-2 candidate (Q8); show that the single-ledger seed model is a placeholder for the consolidated feed.         |
| Determinism breaks (e.g., timestamp-driven ordering causes different demo runs)        | Low        | High   | All ordering keys use deterministic, content-derived ids; `received_at` set from fixture metadata, not wall-clock.                          |

---

## 15. Open Questions

All 8 open questions from `docs/initial-prd.md` §15 have been **resolved** for the POC by accepting the recommended defaults. They are retained here as decisions-of-record with Phase-2 follow-ups.

| #   | Question                                                                                                          | POC Decision (accepted)                                                | Phase 2 Follow-Up                                                   |
| :-- | :---------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------- | :------------------------------------------------------------------ |
| Q1  | Extraction: real OCR or pre-extracted JSON?                                                                       | **Pre-extracted JSON** keyed by fixture filename                       | Add live OCR pipeline (Tesseract or cloud OCR)                      |
| Q2  | AP three-way matching as secondary demo?                                                                          | **Strictly Phase 2** — not in POC                                      | Mirror AR flow for AP three-way matching                            |
| Q3  | Match tolerance — exact-cents or small variance?                                                                  | **Exact-cents only**                                                   | Configurable tolerance (per-customer or global threshold)           |
| Q4  | `PAYER_MISMATCH`: block or warn?                                                                                  | **Warn-only flag** (non-blocking)                                      | Resolution workflow + audit log                                     |
| Q5  | Use customer's master persona list?                                                                               | **Use provisional personas** (§6); flag for confirmation                | Map to customer's master persona library                            |
| Q6  | Follow-up emails — Gmail/Outlook draft integration or clipboard-only?                                             | **Clipboard-only**                                                     | Graph API / Gmail API draft integration                             |
| Q7  | Multi-invoice-per-check demo case?                                                                                | **Yes** — at least one multi-invoice fixture in the demo               | Production-volume multi-invoice handling at scale                   |
| Q8  | Checks for non-ERP-originated invoices (Kroger, retail chains)?                                                   | **POC assumes seed CSV represents the consolidated view**              | Multi-source invoice ingestion from procurement partners            |

**No unresolved open questions remain for MVP scope.** Any new questions raised during architecture, ux design, plan, or build phases should be captured in those phases' artifacts, not back-ported to this PRD.

---

## 16. Appendix

### Domain Glossary

| Term                            | Definition                                                                                                                                | Example / Notes                                                                |
| :------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| AR (Accounts Receivable)        | Function of collecting money owed to the company by its customers.                                                                        | Primary domain of this POC.                                                    |
| AP (Accounts Payable)           | Function of paying money owed by the company to its suppliers.                                                                            | Out of scope; customer's future "flip" use case.                               |
| Invoice                         | A bill issued to a customer for goods/services. Has an open balance until fully paid.                                                     | Originates in OMS / ERP / IR.                                                  |
| Open Invoice                    | An invoice with non-zero `open_balance` — not yet fully paid.                                                                              |                                                                                |
| Check                           | A paper or electronic payment instrument from a customer, usually accompanied by a **stub** that itemizes which invoices it pays.         | May settle one or many invoices.                                               |
| Check Stub                      | The document accompanying a check listing invoice numbers + amounts. Line amounts sum to the check `total_amount`.                         |                                                                                |
| Remittance                      | A payer's notification specifying which invoices a payment settles and the amount per invoice. Often arrives via email for ACH payments.   |                                                                                |
| Remittance Line                 | One (invoice_number, amount) entry from a stub or remittance. The atomic unit the matching engine operates on.                            | One Payment has 1–N Remittance Lines.                                          |
| Lockbox                         | Bank-operated service that receives mailed checks on the company's behalf and provides scanned images + remittance data.                  | One of the ingest channels.                                                    |
| ACH (Automated Clearing House)  | Electronic funds-transfer system between banks. ACH payments arrive with an email remittance notification.                                |                                                                                |
| Payment                         | An ingested check / ACH / lockbox artifact with a `total_amount` and 1–N Remittance Lines.                                                | CCRA core entity (see §9).                                                     |
| Match Result                    | The outcome of comparing a Remittance Line to its target Invoice — primary classification + flags + delta.                                | CCRA core entity (see §9).                                                     |
| Short-Pay                       | A payment less than the invoice's open balance.                                                                                            | Synonymous with `UNDERPAID`.                                                   |
| Over-Pay                        | A payment more than the invoice's open balance.                                                                                            | Synonymous with `OVERPAID`.                                                    |
| Unmatched                       | A Remittance Line whose `invoice_number` does not exist in the Invoice Ledger.                                                            |                                                                                |
| Duplicate                       | A Remittance Line referencing an invoice whose `open_balance` is already zero (already fully paid).                                       | Independent flag in MVP, not a primary classification.                         |
| Payer Mismatch                  | The `payer_name` on a check does not equal the `customer_name` of record on the referenced invoice.                                       | Warn-only flag (Q4).                                                           |
| Match / Reconciliation          | The act of associating a Remittance Line with an Invoice and determining if amounts agree. **Core action of CCRA.**                       |                                                                                |
| Exception                       | A Remittance Line whose Match Result is not a clean `MATCHED` — i.e., `UNDERPAID`, `OVERPAID`, `UNMATCHED`, or any line with `DUPLICATE` / `PAYER_MISMATCH` flags. | The 20% the AR Clerk needs to handle.                              |
| Claim                           | A formal customer-side dispute about an invoice, typically triggered after a short-pay.                                                   | *"They're not paying for the broccoli..."* — interview.                        |
| Cash Application                | Recording a payment against an invoice in the ERP, reducing its open balance.                                                              | POC stops short of writing back to ERP.                                        |
| OMS                             | Order Management System — originates orders + invoices for ~25% of the customer's revenue.                                                | Per interview.                                                                 |
| IR System                       | Invoice Register — the customer's existing internal system for tracking invoices.                                                          | Per interview: *"we have the invoice rate IR system."*                         |
| ERP                             | Enterprise Resource Planning — system of record for financials including AR.                                                              |                                                                                |
| Three-Way Matching              | (AP only — out of scope) Matching a paper invoice to a pending payable + a receipt before releasing payment.                              | Phase 2.                                                                       |
| Critical Path Journey           | (POC) Ingest → Extract → Match → Exceptions Dashboard → Drill-Down → Draft Follow-Up.                                                     | See §7.                                                                        |
| Exceptions Dashboard            | The CCRA primary screen — four classification tiles + filterable row list of exceptions.                                                  | See §8 UC-004, §13.                                                            |

### References

- `interview_transcript.txt` — customer interview, primary requirements source. Origin of all use cases, entities, the four-classification mental model, and the 80/20 exception framing.
- `voice_recording_transcript` — supplementary context. Reinforces AR-team scaling pain (lines 4–6), introduces the mobile-camera scan pattern (lines 22–24), and mentions AP and recall-recovery as adjacent but explicitly-deferred use cases (lines 9–10, 31–46).
- `docs/initial-prd.md` — initial PRD that this refined PRD supersedes for build-phase work. Initial PRD remains the historical record of unrefined scope and unresolved open questions.
- **Architecture-level content from source documents:** None detected. Both transcripts describe user needs, business pain, and workflow only; no design patterns, tech choices, or architectural prescriptions are present. Architect mode will design the architecture from the requirements in this PRD.

---

**PRD Complete — Ready for architect mode (architecture) and ux design (when UI).**
