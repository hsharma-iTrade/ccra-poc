# Initial PRD: Cash Collection Reconciliation Assistant (CCRA)

## 1. Basic Information

| Field            | Value                                                            |
| :--------------- | :--------------------------------------------------------------- |
| Project Name     | Cash Collection Reconciliation Assistant (CCRA)                  |
| Internal Codename| ccra-poc                                                         |
| Priority         | High (Hackathon POC — customer-facing demo)                      |
| Target Release   | Hackathon Demo (1-hour POC scaffold + demo flow)                 |
| Pipeline Mode    | Greenfield (POC scope — PRD + POC scaffold only)                 |
| Document Type    | Initial PRD                                                      |
| Source Material  | `interview_transcript.txt`, `voice_recording_transcript`         |

### Create Table

| Created By        | Name                  | Date        |
| :---------------- | :-------------------- | :---------- |
| Harvey AI (PRD)   | Harvey AI             | 2026-05-15  |
| User (Operator)   | hsharma               | 2026-05-15  |

### Sign-Off Table

| Role             | Approver Name | Status   | Sign-Off Date |
| :--------------- | :------------ | :------- | :------------ |
| PM               | —             | Pending  | —             |
| Engineering Lead | —             | Pending  | —             |
| Design           | —             | Pending  | —             |

> Note: This is a hackathon POC. Sign-off captures customer direction agreement, not production release approval.

---

## 2. Executive Summary

The Cash Collection Reconciliation Assistant (CCRA) is a Proof-of-Concept that automates the most painful step in a food distributor's Accounts Receivable workflow: matching incoming customer payments (checks, ACH remittances, lockbox scans) against open invoices and surfacing the exceptions that require human follow-up. Today, AR clerks manually compile payment data from PDFs, scanned check stubs, and remittance emails, then key it into the ERP and chase short-pays one-by-one. CCRA ingests payment artifacts from a single forwarding inbox (and optional mobile scan), extracts payer + invoice + amount data, cross-matches it against the consolidated invoice list from the ERP / data warehouse, and presents a focused **Exceptions Dashboard** showing only the underpaid, overpaid, and unmatched payments — typically the 20% that need attention out of every 100 checks. The expected business impact for the demo customer is an ~80% reduction in AR reconciliation time and a dramatic improvement in cash-application accuracy, with AR clerks spending their time on real exceptions instead of routine matching. *Source: `interview_transcript.txt`*

---

## 3. Problem Statement

Food-distributor AR teams lose significant time on a structurally manual workflow:

1. **Payment artifacts arrive through multiple, mostly non-electronic channels** — mailed paper checks (with stubs), lockbox PDF scans, ACH remittance emails (PDF or inline body), and occasionally bank notifications. *Source: `interview_transcript.txt`*
2. **Each artifact must be hand-keyed.** Stubs list one-or-many invoice numbers and amounts that sum to the check total; the clerk must transcribe every line and apply it against the corresponding open invoice in the ERP.
3. **The ERP is the source of truth for invoices, but it has no visibility into actual payment receipt** — invoices flow from the OMS to the ERP, but payment matching stops there. The clerk cannot know whether a $1,000 invoice was paid in full, paid at $950, or paid at $800 until the check is physically opened and processed. *Source: `interview_transcript.txt` line 1–14*
4. **Short-pays trigger an account-manager chase loop.** Once a payment doesn't match the invoice, the AR clerk hands it off to the account manager, who has to investigate (e.g., "they're not paying for the broccoli", "they're not paying for the temperature quarter") and open a claim. This back-and-forth is the highest-value, lowest-volume work — and today it's buried under the 80% of routine matches that don't need any human attention.
5. **Team scaling is hard.** The user explicitly stated it has been "very hard to add people in that team as we grow because it's a lot of manual checking." *Source: `voice_recording_transcript` lines 4–6*

**The core problem:** AR clerks cannot see, at a glance, "100 checks came in — 80 matched cleanly, 15 were underpaid, 5 were overpaid, and here are the specific customers + invoices + amounts so I can pick up the phone." Today, producing that view is a multi-hour manual aggregation task. *Source: `interview_transcript.txt`*

---

## 4. KPIs & Business Justification

| KPI                                            | Baseline (Today)                | Target (Post-POC, illustrative) | Notes                                                       |
| :--------------------------------------------- | :------------------------------ | :------------------------------ | :---------------------------------------------------------- |
| Time per 100 checks to produce exception list  | Hours (manual aggregation)      | Minutes                         | ~80% reduction stated by customer in interview              |
| % of checks needing human review               | 100% (every check hand-keyed)   | ~20% (only exceptions)          | The 80% that match cleanly are auto-applied                 |
| Time to first follow-up call on a short-pay    | Hours-to-days (after manual sweep) | Same-day                     | Exceptions surface immediately after ingest                 |
| Cash-application accuracy                      | Human transcription error rate  | Higher (auto-extract + match)   | Removes hand-keying step                                    |
| AR headcount scalability                       | Linear with volume              | Sub-linear                      | Scaling pain explicitly called out                          |

**Business Justification:**

- **Why now:** Customer is actively struggling to scale the AR team with revenue growth; only ~25% of their revenue flows through their own OMS today, with the remainder coming through procurement partners (Kroger's system, retail chains, food-service distributors), each with different invoice formats. Manual reconciliation is the bottleneck. *Source: `interview_transcript.txt`*
- **Strategic fit:** The customer already has an Invoice Register (IR) system; adding a payment-capture + matching layer is a natural extension and a credible upsell from existing OMS/IR products.
- **Demo value:** A working POC that ingests a forwarded remittance email + a scanned check, matches both against sample invoices, and renders an exceptions dashboard is highly compelling for a 1-hour hackathon demo because it shows tangible time-savings on a real customer pain.

---

## 5. Success Criteria

For the **hackathon POC**, success means:

1. The customer (interview participant) watches the demo and confirms: "Yes — this is the direction we want; if it worked at full scale, it would cut our AR reconciliation time materially."
2. A live demo flow runs end-to-end in under 5 minutes:
   - Sample payment artifacts (1 remittance email PDF + 1 scanned check image) are ingested.
   - Payment data is extracted and matched against a sample invoice ledger (CSV / JSON seed).
   - The Exceptions Dashboard renders showing matched / underpaid / overpaid / unmatched buckets, with drill-down to customer + invoice + amount.
3. The demo correctly classifies at least one each of: clean match, underpayment, overpayment, multi-invoice check.
4. The customer signs off on the PRD direction (all 3 roles Approved).

**Out of scope for "success":** production-grade accuracy, full ERP integration, multi-tenant security, scale.

---

## 6. Users & Personas

> Note: This POC has not been validated against a published persona master list (the customer org's persona library was not provided). Personas below are derived from the interview transcript and flagged for confirmation by the customer's product team.

| Persona            | Role                       | Goals                                                                             | Pain Points (Today)                                                                              |
| :----------------- | :------------------------- | :-------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| AR Clerk (primary) | Processes incoming payments| Apply every payment to the right invoice quickly; flag short-pays for follow-up   | Hand-keys every stub; aggregates across email, lockbox, paper, ACH; no consolidated view         |
| Account Manager    | Owns customer relationship | Resolve short-pays with customers; recover claim amounts                          | Gets short-pays handed over with little context; has to re-investigate every claim from scratch  |
| AR Manager         | Owns AR team performance   | Scale reconciliation throughput without linear headcount growth                   | Cannot hire fast enough; team time is consumed by routine matching, not real exceptions          |
| ERP / OMS Admin    | System actor               | Keep invoice data in sync between OMS, IR, and CCRA                               | (Future state) needs a reliable feed from CCRA back into the ERP for cash application            |

*Persona list is provisional — flag for addition to the customer's master persona list during refinement.*

---

## 7. Scope

### In Scope (POC / MVP)

1. **AR cash collection demo flow** — ingest payment artifacts → extract → match → exceptions dashboard.
2. **Two ingest channels:**
   - **Email forwarding** (single inbox; user forwards remittance emails containing PDFs or inline body text).
   - **Mobile / file upload scan** of paper checks and stubs (image upload — frame-by-frame OCR or simulated extraction acceptable for POC).
3. **Invoice ledger** seeded from a CSV / JSON sample representing the consolidated invoice view that would normally come from the customer's data warehouse / ERP.
4. **Matching engine** with three outcomes per payment line: matched, underpaid (short-pay), overpaid, or unmatched.
5. **Exceptions Dashboard** showing summary counts (X matched / Y underpaid / Z overpaid / W unmatched) and drill-down rows with customer name, invoice number(s), invoiced amount, paid amount, delta.
6. **Email-draft preview** stub: when an exception is selected, show a pre-composed follow-up email body the AR clerk could send (no actual send in POC).

### Out of Scope (Deferred / Phase 2)

| Item                                                              | Rationale for Deferral                                                                       |
| :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| AP three-way matching (paper invoice → pending payable → release) | Customer confirmed this is a "flip" of the AR flow — valuable but explicitly out of POC scope|
| Post-recall recovery / chargeback reconciliation                  | Multi-party (grower-shipper → distributor → retailer), multi-year process; complex; deferred  |
| Direct lockbox API ingestion                                      | Email-forwarded lockbox PDFs cover the POC; native lockbox APIs are a later integration       |
| Direct bank ACH feed                                              | Email ACH notifications are sufficient for demo                                              |
| Live ERP write-back (auto cash application)                       | POC reads invoices from seed; doesn't post payments back                                     |
| Multi-tenant auth, SSO, role-based access                         | Single demo user / no auth for POC                                                           |
| Production accuracy targets (>99% extraction)                     | POC demo uses curated samples; production accuracy is a Phase-2 effort                       |
| Automated send of follow-up emails                                | POC shows draft preview only; no outbound mail                                               |
| Procurement-partner invoice ingestion (Kroger, etc.)              | POC uses the single consolidated ledger; multi-source invoice ingestion is Phase 2           |

---

## 8. Use Cases

> 5 use cases — MVP-scoped for the 1-hour demo. Identifiers are UC-NNN for downstream traceability.

### Phasing Summary

| ID     | Use Case                                            | Phase    |
| :----- | :-------------------------------------------------- | :------- |
| UC-001 | Ingest payment artifacts via forwarded email        | MVP      |
| UC-002 | Ingest payment artifacts via image/file upload      | MVP      |
| UC-003 | Auto-match payments against open invoices           | MVP      |
| UC-004 | View Exceptions Dashboard and drill into details    | MVP      |
| UC-005 | Preview follow-up email draft for an exception      | MVP      |
| UC-006 | AP three-way invoice matching                       | Phase 2  |
| UC-007 | Recall-recovery reconciliation                      | Phase 2  |

---

### UC-001 — Ingest Payment Artifacts via Forwarded Email

- **Actors:** AR Clerk (primary), Email Ingest Service (system).
- **Trigger:** AR Clerk forwards a remittance email (ACH notification, lockbox PDF, scanned-check email) to the dedicated CCRA inbox (e.g., `check-processing@<customer>.com`).
- **Steps:**
  1. Email arrives at the dedicated CCRA inbox.
  2. System parses the email body and any attachments (PDF, image).
  3. System extracts: payer name/ID, payment date, check or reference number, total amount, and a list of invoice-number + amount lines.
  4. System persists a Payment record + one Remittance Line per invoice-line on the stub.
  5. System hands off to the matching engine (UC-003).
- **Alt / Edge Flows:**
  - Email has no extractable payment data → record marked `EXTRACTION_FAILED`, surfaced in Exceptions Dashboard as "needs manual review."
  - Email contains multiple PDFs → each PDF processed as a separate payment artifact.
  - PDF text is unreadable (low-quality scan) → for POC, fall back to a manual "enter values" affordance OR use seeded sample data.
- **Acceptance Criteria:**
  - Given a forwarded email with a remittance PDF, when the system processes it, then a Payment record is created with at least: payer, total amount, at least one Remittance Line.
  - Given a multi-invoice stub, the system creates one Remittance Line per invoice referenced on the stub.

### UC-002 — Ingest Payment Artifacts via Image/File Upload

- **Actors:** AR Clerk (primary), Upload UI, Extraction Service.
- **Trigger:** AR Clerk opens the POC UI, drags or selects one or more check/stub images (or a PDF of scanned paper checks).
- **Steps:**
  1. User uploads file(s) via the UI.
  2. System runs OCR / extraction on each image.
  3. System produces Payment + Remittance Line records identical in shape to UC-001.
  4. Hands off to matching engine.
- **Alt / Edge Flows:**
  - File is not a check (e.g., random photo) → flagged `INVALID_ARTIFACT`.
  - For POC: a "use sample data" toggle allows skipping live OCR.
- **Acceptance Criteria:**
  - Given a check-image upload, when processed, then a Payment record with at least payer, amount, and a check/reference number is created.
  - User can upload 1–N files in a single action.

### UC-003 — Auto-Match Payments Against Open Invoices

- **Actors:** Matching Engine (system).
- **Trigger:** A Payment record with one or more Remittance Lines is persisted (from UC-001 or UC-002).
- **Steps:**
  1. For each Remittance Line, look up the referenced invoice number in the Invoice Ledger.
  2. Compare the line amount to the invoice's open balance.
  3. Classify the line as one of: `MATCHED` (line amount == open balance), `UNDERPAID` (line amount < open balance), `OVERPAID` (line amount > open balance), or `UNMATCHED` (invoice number not found).
  4. Persist a Match Result per Remittance Line.
- **Alt / Edge Flows:**
  - One check covers multiple invoices → each invoice line evaluated independently; the Payment as a whole shows a roll-up status.
  - Invoice exists but is already fully paid (zero open balance) → flagged `DUPLICATE_PAYMENT`.
  - Payer name on the check does not match the customer-of-record for the invoice → flagged `PAYER_MISMATCH` (warning, not blocking).
- **Business Rules:**
  - Tolerance threshold for a "clean match" is configurable (default: 0 cents — exact match for POC).
  - A single check may settle 1–N invoices.
- **Acceptance Criteria:**
  - Every Remittance Line has exactly one Match Result.
  - The four classifications (MATCHED / UNDERPAID / OVERPAID / UNMATCHED) are mutually exclusive.

### UC-004 — View Exceptions Dashboard and Drill Into Details

- **Actors:** AR Clerk (primary), AR Manager.
- **Trigger:** User opens the CCRA dashboard URL.
- **Steps:**
  1. Dashboard loads with summary tiles: Matched count, Underpaid count, Overpaid count, Unmatched count.
  2. User clicks the "Underpaid" tile (or any tile).
  3. System displays a list of all Remittance Lines in that bucket, columns: Customer, Invoice #, Invoiced Amount, Paid Amount, Delta, Source (email/upload), Received Date.
  4. User clicks a row → side panel shows full Payment context (the entire check + all its Remittance Lines), and a preview of the underlying artifact (PDF/image thumbnail when available).
- **Alt / Edge Flows:**
  - No exceptions exist → dashboard shows "All clear" state with the matched count only.
- **Acceptance Criteria:**
  - Summary counts equal the total Remittance Lines in each Match Result bucket.
  - Drill-down row shows customer name + invoice number + delta amount, matching the source artifact.
- **State Transitions:** Match Result → optional `RESOLVED` (out of scope for POC interactive resolution; surface-only).

### UC-005 — Preview Follow-Up Email Draft for an Exception

- **Actors:** AR Clerk.
- **Trigger:** From a drill-down row (UC-004), user clicks "Draft follow-up."
- **Steps:**
  1. System opens a side panel with a pre-composed email body: addressed to the payer's contact (mocked for POC), subject line referencing the invoice number, body explaining the underpayment/overpayment amount.
  2. User can copy the draft to clipboard (POC) — no live send.
- **Alt / Edge Flows:**
  - For OVERPAID exceptions, the draft acknowledges the overpayment and asks how to apply the surplus.
  - For UNMATCHED, the draft asks the payer to confirm which invoice(s) the payment was intended for.
- **Acceptance Criteria:**
  - Draft body includes: payer name, invoice number(s), invoiced vs paid amounts, delta.

---

## 9. Data, Entities & Information

### Core Entities

#### Invoice (read-only seed data for POC)

| Field            | Type      | Required | Notes                                                          |
| :--------------- | :-------- | :------- | :------------------------------------------------------------- |
| invoice_id       | string    | yes      | Primary key; e.g., "INV-2026-0001"                             |
| customer_id      | string    | yes      | Foreign key to Customer                                        |
| customer_name    | string    | yes      | Denormalized for POC display                                   |
| invoice_date     | date      | yes      |                                                                |
| due_date         | date      | yes      |                                                                |
| total_amount     | decimal   | yes      | Invoice face value                                             |
| open_balance     | decimal   | yes      | Remaining balance; decreases as payments apply                 |
| status           | enum      | yes      | `OPEN`, `PAID`, `PARTIALLY_PAID`                               |
| description      | string    | no       | Line-item summary (e.g., produce items)                        |
| source_system    | string    | no       | Which upstream system originated the invoice (ERP, OMS, etc.)  |

#### Payment (created from ingested artifact)

| Field             | Type       | Required | Notes                                                          |
| :---------------- | :--------- | :------- | :------------------------------------------------------------- |
| payment_id        | string     | yes      | Generated                                                      |
| source_channel    | enum       | yes      | `EMAIL`, `UPLOAD`, `LOCKBOX_EMAIL`, `ACH_EMAIL`                |
| received_at       | timestamp  | yes      | When CCRA ingested the artifact                                |
| payer_name        | string     | yes      | Extracted from check/stub/remittance                           |
| check_number      | string     | no       | Reference number for non-check payments                        |
| payment_date      | date       | no       |                                                                |
| total_amount      | decimal    | yes      | The full amount on the check / remittance                      |
| raw_artifact_ref  | string     | no       | Pointer to the stored PDF/image                                |
| extraction_status | enum       | yes      | `EXTRACTED`, `PARTIAL`, `FAILED`                               |

#### Remittance Line (one per invoice referenced on a stub)

| Field           | Type    | Required | Notes                                       |
| :-------------- | :------ | :------- | :------------------------------------------ |
| line_id         | string  | yes      |                                             |
| payment_id      | string  | yes      | FK → Payment                                |
| invoice_number  | string  | yes      | As written on the stub (may not match a known invoice) |
| line_amount     | decimal | yes      | Amount applied to that invoice              |
| description     | string  | no       |                                             |

#### Match Result (one per Remittance Line)

| Field           | Type    | Required | Notes                                                        |
| :-------------- | :------ | :------- | :----------------------------------------------------------- |
| match_id        | string  | yes      |                                                              |
| line_id         | string  | yes      | FK → Remittance Line                                         |
| invoice_id      | string  | no       | FK → Invoice (null when UNMATCHED)                           |
| classification  | enum    | yes      | `MATCHED`, `UNDERPAID`, `OVERPAID`, `UNMATCHED`, `DUPLICATE`, `PAYER_MISMATCH` |
| delta_amount    | decimal | yes      | line_amount − open_balance (sign indicates over/under)       |
| created_at      | timestamp | yes    |                                                              |

#### Customer (lightweight reference)

| Field          | Type   | Required | Notes                                  |
| :------------- | :----- | :------- | :------------------------------------- |
| customer_id    | string | yes      |                                        |
| customer_name  | string | yes      |                                        |
| contact_email  | string | no       | Used for draft follow-up emails        |

### Privacy & Sensitivity

- Customer payment data is **financially sensitive**. For POC, all data is synthetic / fixture-based — no real customer payment data is ingested.
- For production (Phase 2), payment artifacts would need encryption at rest, PII handling per the customer org's data policy, and audit logging of every match.

---

## 10. Integrations

### POC (In Scope)

| System                 | Direction     | Mechanism                                 | Notes                                          |
| :--------------------- | :------------ | :---------------------------------------- | :--------------------------------------------- |
| Email inbox            | Inbound       | IMAP poll OR webhook (POC: simulate via file upload OR a fixture inbox) | Forwarded remittance emails               |
| File upload UI         | Inbound       | Browser multipart upload                  | Mobile-camera flow can use the same endpoint   |
| Invoice ledger (seed)  | Inbound       | Static CSV or JSON fixture                | Represents the customer's consolidated invoice list from their data warehouse |

### Future / Deferred

| System                  | Direction      | Mechanism                                | Notes                                          |
| :---------------------- | :------------- | :--------------------------------------- | :--------------------------------------------- |
| Customer ERP / OMS      | Inbound (invoices) | API / scheduled extract              | Real consolidated invoice feed                 |
| Customer ERP            | Outbound (cash application) | API write-back                  | Auto-apply matched payments                    |
| Lockbox provider        | Inbound        | Lockbox API or SFTP                      | Native lockbox feed                            |
| Bank ACH feeds          | Inbound        | Bank API or BAI/CAMT files               | Direct ACH notifications                       |
| Outlook / Gmail (drafts)| Outbound       | Graph API / Gmail API                    | Place drafts directly in user's outbox         |
| Procurement partners (Kroger, retail chains, food-service) | Inbound | Partner-specific feeds | Multi-source invoice consolidation |

---

## 11. Error Handling & Edge Cases

| Condition                                                     | Behavior                                                                                |
| :------------------------------------------------------------ | :-------------------------------------------------------------------------------------- |
| Email arrives with no recognizable payment data               | Payment record created with `extraction_status=FAILED`; shown in dashboard as "needs review" |
| PDF/image extraction yields low confidence                    | `extraction_status=PARTIAL`; flagged in dashboard                                       |
| Invoice number on stub does not exist in ledger               | Match Result classified `UNMATCHED`                                                     |
| Invoice already fully paid (open_balance == 0)                | Match Result classified `DUPLICATE`                                                     |
| Payer on check ≠ customer-of-record on invoice                | Match Result tagged `PAYER_MISMATCH` (warning; still classified by amount)              |
| Stub line amounts do not sum to check total                   | Payment flagged; shown in dashboard with reconciliation discrepancy                     |
| Same Payment ingested twice (e.g., user forwards email twice) | Detect via check_number + amount + payer; second one flagged `DUPLICATE_ARTIFACT`       |
| Upload file is not an image/PDF                               | Reject with user-facing error message; do not create Payment                            |
| Negative or zero line amount                                  | Reject the line; flag Payment as `PARTIAL`                                              |

---

## 12. Non-Functional Expectations

> Calibrated for a 1-hour hackathon POC. Production targets would be set during refinement.

| Category          | POC Expectation                                                                          |
| :---------------- | :--------------------------------------------------------------------------------------- |
| Performance       | Demo flow completes end-to-end in < 30 seconds for a batch of ~10 artifacts              |
| Scalability       | POC handles ~100 invoices and ~30 payments in memory; no DB tuning required              |
| Availability      | Single-instance local dev server; no HA requirement                                       |
| Security          | No real PII; no authentication for the POC demo; local-only deployment                    |
| Accessibility     | Best-effort keyboard navigation on the dashboard; full WCAG conformance deferred         |
| Platform Support  | Modern desktop browser (Chrome/Edge/Safari latest); mobile-camera upload via standard `<input type="file" capture>` |
| Determinism       | Given the same input artifacts and the same invoice fixture, matching results must be identical across runs |
| Observability     | Console logging sufficient for POC; structured logs deferred                              |

---

## 13. UI/UX Requirements

### Key Screens

1. **Inbox / Upload Screen**
   - Drop zone for files (PDF / images) + "Use sample data" button for the demo.
   - List of recently-ingested artifacts with extraction status.
2. **Exceptions Dashboard (primary demo screen)**
   - Four summary tiles at the top: **Matched (count)**, **Underpaid (count)**, **Overpaid (count)**, **Unmatched (count)**.
   - Tile-click filters the row list below by classification.
   - Row list columns: Customer · Invoice # · Invoiced · Paid · Delta · Source · Received.
   - Sort + simple text filter on customer / invoice number.
3. **Drill-Down Side Panel**
   - Opens on row click.
   - Shows the full Payment (check details + all Remittance Lines, with per-line match status).
   - Thumbnail/preview of the source artifact (PDF/image) when available.
   - "Draft follow-up" button → opens email-draft side panel.
4. **Email Draft Panel**
   - Pre-composed body; "Copy to clipboard" button (no live send).

### Interaction Patterns

- Single-page app feel; no full page reloads between dashboard and drill-down.
- The dashboard is the landing screen — exception counts are the first thing the user sees (consistent with the customer's stated mental model: *"he wants to see 100 checks came in, 80 matched, 15 underpaid, 5 overpaid"*).

### Design Assets

```
Design Assets: None provided — UI will be planned during POC build using a lightweight, demo-friendly approach (e.g., a clean, default component library). No Figma, screenshots, or wireframes provided by the customer.
```

> Tech stack, framework, and component library choices are deferred to the build phase.

---

## 14. Constraints, Dependencies & Risks

### Constraints

- **Time-boxed:** 1-hour hackathon POC scaffold. Scope must remain demo-focused.
- **Data:** Customer's real invoice/payment data is not available for the demo. POC uses synthetic fixtures.
- **No production deployment:** Local dev / demo machine only.

### Dependencies

| Dependency                                                | Owner   | Status        |
| :-------------------------------------------------------- | :------ | :------------ |
| Synthetic invoice fixture (CSV/JSON of ~100 sample invoices) | Team | To create     |
| Synthetic payment artifacts (3–5 sample PDFs/images covering matched, underpaid, overpaid, unmatched, multi-invoice) | Team | To create |
| OCR / extraction approach (real OCR vs. simulated for POC) | Team   | To decide (see §15) |

### Risks

| Risk                                                                  | Mitigation                                                                  |
| :-------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| OCR accuracy is too low for live demo                                 | Have a "use sample data" path that bypasses live OCR and uses pre-extracted JSON |
| Demo data not representative of customer's real artifacts             | Build fixtures directly modeled on the patterns in the interview (multi-invoice stubs, multi-source channels) |
| Customer expects production polish in POC                             | Frame demo explicitly as a direction-validation POC, not a production system |
| Scope creep into AP matching or recall recovery                       | Both explicitly listed as Out of Scope in §7                                |

---

## 15. Open Questions

| #   | Question                                                                                                          | Impact if Unresolved                                          | Recommended Default for POC                                        |
| :-- | :---------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ | :----------------------------------------------------------------- |
| Q1  | For the POC demo, should extraction be real OCR or pre-extracted JSON tied to sample artifacts?                   | Affects build complexity and demo reliability                 | Pre-extracted JSON (with optional real OCR if time permits)        |
| Q2  | Is AP three-way matching needed as a secondary demo flow, or strictly Phase 2?                                    | Affects scope                                                 | Strictly Phase 2 (per scope decision in §7)                        |
| Q3  | Tolerance threshold for "MATCHED" — is exact-cents the right rule, or should small variances (e.g., $0.01) match? | Match classification ambiguity                                | Exact-match for POC; configurable in Phase 2                       |
| Q4  | Should `PAYER_MISMATCH` block a match or just warn?                                                               | Affects exception count and customer-call workflow            | Warn only for POC                                                  |
| Q5  | Are there persona definitions in the customer's master persona list that should be used instead of the provisional ones in §6? | Persona naming alignment with customer org           | Use provisional personas; flag for customer confirmation           |
| Q6  | For follow-up emails, should the POC integrate with Gmail/Outlook drafts, or stop at clipboard-copy?              | Demo polish                                                   | Clipboard-copy only for POC                                        |
| Q7  | Does the customer want the multi-invoice-per-check case demonstrated explicitly in the demo?                      | Affects fixture design                                        | Yes — include at least one multi-invoice fixture                   |
| Q8  | Are checks ever payment for invoices that originated in non-ERP systems (Kroger, retail chains)? If so, how does CCRA know the invoice exists? | Affects the "consolidated invoice ledger" assumption | POC assumes the seed CSV represents the consolidated view; Phase 2 handles multi-source ingestion |

---

## 16. Appendix

### Domain Glossary

| Term                  | Definition                                                                                                                                       | Example / Notes                                                          |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| AR (Accounts Receivable) | The function of collecting money owed to the company by its customers.                                                                          | The primary domain of this POC.                                          |
| AP (Accounts Payable) | The function of paying money owed by the company to its suppliers.                                                                                | Out of scope for POC; mentioned by customer as a future "flip" use case. |
| Invoice               | A bill issued by the company to a customer for goods/services. Has an open balance until fully paid.                                            | Originates in OMS / ERP / IR system.                                     |
| Open Invoice          | An invoice with a non-zero open balance — i.e., not yet fully paid.                                                                              |                                                                          |
| Check                 | A paper or electronic payment instrument from a customer; usually accompanied by a **stub** that itemizes which invoices the check is paying.    | May settle one or many invoices.                                         |
| Check Stub            | The paper or PDF document accompanying a check, listing invoice numbers and amounts.                                                             | Line amounts on a stub sum to the check total.                           |
| Remittance            | A notification from a payer specifying which invoices a payment is settling and the amount per invoice.                                          | Often arrives via email (PDF or inline) for ACH payments.                |
| Lockbox               | A bank-operated service that receives mailed checks on the company's behalf and provides scanned images + remittance data.                       | One of the ingest channels.                                              |
| ACH (Automated Clearing House) | An electronic funds-transfer system between banks; in this domain, ACH payments arrive with an email remittance notification.            |                                                                          |
| Short-Pay             | A payment that is less than the invoice's open balance.                                                                                          | Synonym for UNDERPAID.                                                   |
| Over-Pay              | A payment that is more than the invoice's open balance.                                                                                          |                                                                          |
| Match / Reconciliation| The process of associating a payment line with an invoice and determining if amounts agree.                                                      | The core action of CCRA.                                                 |
| Claim                 | A formal customer-side dispute about an invoice, typically triggered after a short-pay.                                                          | "Because either they're not paying for the broccoli..." — interview.     |
| Cash Application      | The act of recording a payment against an invoice in the ERP, reducing its open balance.                                                         | POC stops short of writing back to ERP.                                  |
| OMS                   | Order Management System — originates orders and invoices for ~25% of the customer's revenue.                                                     | Per interview.                                                           |
| IR System             | Invoice Register — the customer's existing internal system for tracking invoices.                                                                | Per interview: *"we have the invoice rate IR system"*.                   |
| ERP                   | Enterprise Resource Planning system — system of record for the customer's financials, including AR.                                              |                                                                          |
| Three-Way Matching    | (AP only — out of scope) Matching a paper invoice to a pending payable and a receipt before releasing payment.                                   | Phase 2 use case.                                                        |
| Exception             | A payment line whose match result is not `MATCHED` — i.e., UNDERPAID, OVERPAID, UNMATCHED, DUPLICATE, or PAYER_MISMATCH.                          | The 20% the AR clerk actually needs to handle.                           |
| Critical Path Journey | (POC) Ingest → Extract → Match → Exceptions Dashboard → Drill-Down → Draft Follow-Up.                                                            |                                                                          |

### References

- `interview_transcript.txt` — customer interview, primary requirements source. All major use cases, entities, and the exception-classification mental model are drawn from this document.
- `voice_recording_transcript` — supplementary context. Reinforces AR-team scaling pain (lines 4–6), introduces a mobile-video / phone-scan ingest pattern (lines 22–24), and mentions AP and recall-recovery as adjacent use cases (lines 9–10, 31–46) — both flagged Out of Scope in §7.
- Architecture-level content from source documents: none detected — both transcripts describe user needs and pain only; no design patterns, tech choices, or architectural prescriptions are present.

---

**PRD Complete (initial) — pending user review and refinement.**
