CCRA Demo Script
  
  1 · The Pain (15 sec — set the scene)

"When we last spoke, you told me your AR team has two big time sucks. First — you get checks and ACH remittances 
from lockbox, email, and paper mail, and someone has to manually type each one into the ERP. Second — when a 
customer short-pays, your account manager has to dig through invoices to figure out why they short-paid before they 
can call the customer.
What we built is a small POC that tackles both."

  2 · The Setup (10 sec — opening shot)

[Open the Streamlit URL on your phone or laptop]

"The idea is simple — you forward your ACH emails, your lockbox notifications, and your scanned paper checks to a 
single inbox. Today I'm using sample data so we can see it end-to-end in 60 seconds."

  3 · Ingest (20 sec — go to Inbox)

[Click "Use sample data" on the Inbox page]
"Behind the scenes the system extracted the payer, the check number, every invoice on the stub, and every amount. 
Some are single-invoice ACHs, some are multi-invoice lockbox checks, one is a scanned paper cheque."
[Optional, if on phone] [Tap the + button → Open camera] "And here's how a paper check would come in from the field 
— phone camera, snap, done."

  4 · The "Wow" — Exception Dashboard (30 sec — the core moment)

[Click into Dashboard]
"Here's where the time savings come from. The system processed every payment and bucketed them: 12 matched cleanly, 
2 underpaid, 2 overpaid, 1 unmatched. Your team's job just collapsed from 17 things to look at, down to 5."
[Click the Underpaid tile]
"Now I can see exactly who short-paid and by how much — Whole Foods short-paid invoice 0020 by 50 dollars. That's 
the call my account manager makes next."

  5 · The Drilldown + Source PDF (25 sec — earn trust)

[Click "Open" on the Whole Foods row]
"Drilling in — full payment, every line, and on the right, the actual source artifact. This is the lockbox 
remittance PDF the system extracted from. So if my AM ever doubts the data, they see the original document right 
next to it."
  
  6 · The Escalation Email (20 sec — close the loop)

[Click "Draft account-manager escalation"]
"Last step — the system drafts an internal note to the right person. We talked about this — your AR person doesn't 
want to email the customer directly, they want to escalate to the AM who owns that relationship. So it's addressed 
to Sarah Chen, the AM for Whole Foods. She copies it, calls the customer, problem solved."
  
  7 · Close (15 sec — anchor the value)

"So in production, you'd hook this to a real inbox and to your ERP for the invoice ledger — that's straightforward. 
What's unique here is the cross-matching engine and the exception triage. Today your AR team spends 100% of their 
time. After this, they're spending 20% of their time on the exceptions and zero on the matched ones.
What did this look like to you?"
