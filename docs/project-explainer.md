# RegChange — Project Explainer (Demo Prep Guide)

This document explains every concept in the project from scratch. Read this before demoing. No ML/DS background required — this is written for a data engineer.

---

## Part 1: The Business Problem (Why This Exists)

### What is AML?

**AML = Anti-Money Laundering.** It's a set of rules that banks and financial companies (called NBFCs in India) must follow to detect and report suspicious money movement. Every country has these rules. In India, the key law is the **Prevention of Money Laundering Act (PMLA)**.

### What is a "threshold" in AML?

Banks monitor every transaction. If a transaction exceeds a certain amount (the **threshold**), it gets **flagged as an alert** for manual investigation by a compliance officer.

**Example:**
- Current rule: Flag any single transaction above **₹10,00,000** (₹10 lakh = INR 1,000,000)
- If you transfer ₹12,00,000, it gets flagged
- If you transfer ₹8,00,000, it does NOT get flagged

### What happens when a regulator changes the threshold?

The regulator (like RBI in India) periodically issues **circulars** — official letters that say "we're changing the rules." For example:

> "The threshold for flagging high-value transactions is being lowered from ₹10 lakh to ₹5 lakh, effective October 1, 2026."

This means: starting October 1, ANY transaction above ₹5 lakh must be flagged. This is a **much lower bar**, so many more transactions will trigger alerts.

### Why is this a problem for banks?

When the threshold drops, the bank gets **flooded with new alerts**. Each alert needs a human to review it. The compliance team needs to know:

1. **How many more alerts will we get?** (to plan staffing)
2. **How many new customers will be affected?** (customers who were never flagged before)
3. **Can we handle the volume?** (operational capacity)
4. **Who approved this assessment?** (audit trail for regulators)

**Today, banks do this manually** — spreadsheets, SQL queries on production data, emails for approval. It takes days to weeks with no audit trail.

### What does RegChange do?

RegChange automates this entire workflow in one app:

```
Regulatory circular arrives
        ↓
AI extracts: "threshold changing from ₹10L to ₹5L"
        ↓
System replays historical transactions under both rules
        ↓
Dashboard shows: "68 more alerts, 47 new customers affected"
        ↓
Compliance officer approves with a comment
        ↓
Everything is logged for audit
```

---

## Part 2: Key Terms Dictionary

### Banking / Compliance Terms

| Term | Plain English |
|---|---|
| **AML** | Anti-Money Laundering — rules to catch suspicious money transfers |
| **Threshold** | The amount above which a transaction gets flagged for review |
| **Alert** | A flagged transaction that needs human investigation |
| **Circular** | An official letter from a regulator announcing a rule change |
| **NBFC** | Non-Banking Financial Company (e.g., Bajaj Finance, Muthoot) — they follow similar AML rules as banks |
| **Compliance officer** | Person responsible for ensuring the bank follows regulations |
| **Audit trail** | A record of who did what and when — regulators demand this |
| **Baseline** | The current/existing rule (₹10 lakh in our demo) |
| **Proposed** | The new rule being evaluated (₹5 lakh in our demo) |
| **Backtest** | Running old data through a new rule to see what would have happened |
| **Remediation** | The actual change you make to fix/update a system |

### Technical Terms (Snowflake / Project)

| Term | Plain English |
|---|---|
| **Deterministic data** | Same script always produces the same data — no randomness. Good for demos because results are reproducible |
| **MERGE** | A SQL command that inserts data only if it doesn't already exist. Makes the script re-runnable |
| **Stored procedure** | A saved SQL program you can call with parameters, like a function |
| **VARIANT** | A Snowflake data type that holds JSON — used to return the backtest results as a structured object |
| **Container runtime** | The Streamlit app runs inside a Docker-like container in Snowflake (not on a warehouse). More modern approach |
| **Compute pool** | A set of machines in Snowflake that run containers. Ours is `SYSTEM_COMPUTE_POOL_CPU` |
| **Cortex** | Snowflake's built-in AI service. We use it to call an LLM (llama3.1-8b) directly from SQL |
| **Cortex COMPLETE** | A Snowflake function that sends text to an LLM and gets a response back. Like calling ChatGPT but inside Snowflake |
| **DMF** | Data Metric Function — a Snowflake feature that continuously checks data quality on a table |
| **Dynamic Table** | A Snowflake table that automatically refreshes based on a query — like a materialized view that stays fresh |
| **Semantic View** | A Snowflake object that describes your data in business terms so an AI (Cortex Analyst) can answer natural language questions about it |
| **Cortex Analyst** | A Snowflake service that converts natural language questions into SQL using a Semantic View |
| **Cortex Search Service** | A Snowflake service that lets you search through text documents (like policy circulars) using AI |
| **CoCo CLI** | Cortex Code CLI — the Snowflake AI coding assistant (what we're using right now) |

---

## Part 3: What Each Table Does

### TRANSACTIONS (10,000 rows)
The fake bank transaction data. Each row is one transaction.

| Column | What it is | Example |
|---|---|---|
| TXN_ID | Unique transaction ID | TXN-00000001 |
| ACCOUNT_ID | Which customer account | ACCT-000042 |
| TXN_AMOUNT | How much money (INR) | 750000.00 |
| CURRENCY_CODE | Always INR in our demo | INR |
| TXN_TIMESTAMP | When it happened | 2026-08-15 14:30:00 |
| TXN_TYPE | How the money moved | UPI, CARD, BANK_TRANSFER, CASH |
| BENEFICIARY_ID | Who received the money | BEN-00123 (NULL for CASH) |

**Data distribution:**
- ~2% of transactions are high-value (₹5L - ₹20L) — these trigger alerts
- ~13% are medium (₹10K - ₹5L)
- ~85% are small daily transactions (₹100 - ₹1L)
- 2,500 unique accounts across 90 days (Jul-Sep 2026)

### REGULATORY_CONTROLS (1 row)
The current rule. Think of this as the "rule catalog."

| Column | What it is | Our value |
|---|---|---|
| RULE_ID | Short name | AML_THRESHOLD_10L |
| RULE_VERSION | Version number | 1 |
| THRESHOLD_VALUE | The amount that triggers an alert | 1000000.00 (₹10 lakh) |
| STATUS | Is this rule active? | ACTIVE |
| ACTIVE_FROM | When did this rule start? | 2026-01-01 |

### BACKTEST_RUNS (grows with each test)
Every time you click "Run Backtest," a row is saved here.

| Key columns | Meaning |
|---|---|
| OLD_ALERT_COUNT | How many alerts under the current rule (132) |
| NEW_ALERT_COUNT | How many alerts under the proposed rule (200) |
| ALERT_COUNT_DELTA | The difference (68 more alerts) |
| PERCENT_ALERT_CHANGE | Percentage increase (51.5%) |
| ACCOUNTS_ALERTED_NEW_RULE | Total accounts with at least one alert under new rule (50) |
| NEWLY_ALERTED_ACCOUNTS | Accounts that were NEVER flagged before but will be now (47) |

### REVIEW_LOG (grows with each approval)
The audit trail. Every approval or rejection is recorded.

| Column | Meaning |
|---|---|
| REVIEWER | Who approved (Snowflake username) |
| DECISION | APPROVED or REJECTED |
| COMMENT | Why they made that decision |
| REVIEWED_AT | Timestamp |

---

## Part 4: What the Numbers Mean (Demo Talking Points)

When you run the backtest with threshold = ₹5,00,000:

**"132 baseline alerts"**
→ Under the current ₹10 lakh rule, 132 transactions in our 90-day window exceed the threshold. This is the current workload for the compliance team.

**"200 proposed alerts"**
→ Under the proposed ₹5 lakh rule, 200 transactions exceed the threshold. This is the new workload.

**"+68 alerts (+51.5%)"**
→ The compliance team will get 68 additional alerts per quarter — a 51.5% increase. Do they have enough people to review them?

**"50 accounts alerted under new rule"**
→ 50 distinct customer accounts have at least one transaction above ₹5 lakh. These accounts will appear in the alert queue.

**"47 newly alerted accounts"**
→ This is the most important number. 47 accounts that were NEVER flagged before (all their transactions were between ₹5L and ₹10L) will now start getting flagged. These customers may receive calls or letters from the bank for the first time.

**Why this matters to a bank:**
- 68 more alerts = need to hire or reassign ~2 analysts (each analyst reviews ~30 alerts/quarter)
- 47 new customers = potential complaints if not communicated properly
- The bank has evidence to plan for this BEFORE the regulation takes effect

---

## Part 5: The Demo Flow (What to Say)

### Opening (30 seconds)
"Banks spend weeks manually estimating the impact of regulatory changes. RegChange does it in 60 seconds using Snowflake."

### Tab 1: Policy Extraction (1 minute)
"Here's a regulatory circular — I paste it in, and Snowflake Cortex extracts the key fields: what rule is changing, from what to what, and when. This is AI reading the regulation for me."

### Tab 2: Run Backtest (1.5 minutes)
"Now I click Run Backtest. The system replays 10,000 historical transactions under both the old and new thresholds. In 3 seconds, I know: 68 more alerts, 47 customers affected for the first time. I can try different thresholds too."

### Tab 3: Run History (30 seconds)
"Every backtest is saved. I can compare what happens at ₹5 lakh versus ₹3 lakh versus ₹7.5 lakh — the compliance team can evaluate multiple scenarios."

### Tab 4: Review & Approve (1 minute)
"Finally, the compliance officer approves or rejects with a comment. This is logged for audit — the regulator can see exactly who approved what change, when, and why. No more email chains."

### Closing (30 seconds)
"Built entirely on Snowflake: Cortex for AI extraction, SQL procedures for deterministic replay, Streamlit for the UI, all developed with CoCo CLI."

---

## Part 6: Data Scale and Why It Matters

### Current demo scale
- 10,000 transactions, 2,500 accounts, 90-day window
- Backtest runs in <1 second on XS warehouse

### Tested scale
- 500,000 transactions, 50,000 accounts — backtest runs in <2 seconds
- Same XS warehouse, no code changes needed

### Why we chose 10K for demo
- **Deterministic:** same data every time = same results every time = reliable demo
- **Cost efficient:** trial account has $400; we've used ~$22 so far
- **Honest:** we're not pretending 10K is production-scale. We're showing the ARCHITECTURE works

### Production scale comparison
| | Demo | Real bank |
|---|---|---|
| Transactions | 10K / quarter | 10M-100M+ / quarter |
| Accounts | 2,500 | 500K-10M |
| Backtest time | <1 sec | 5-30 sec on Medium warehouse |
| The SQL is the same | Yes | Yes — COUNT_IF scales linearly |

### What to say if judges ask about scale
"We deliberately chose 10K rows for demo reproducibility. The backtest is a COUNT_IF aggregation — we tested it at 500K rows with the same code, under 2 seconds. Snowflake's architecture handles the rest."

---

## Part 7: Anticipated Judge Questions and Answers

**Q: Is this real regulatory data?**
A: No, everything is synthetic — the circular, the transactions, and the thresholds. In production, the circular would come from RBI/SEBI and the transactions from the core banking system.

**Q: Why not just use a spreadsheet?**
A: Three reasons: (1) reproducibility — same inputs always give same outputs, (2) audit trail — every decision is logged, (3) scale — this handles 10K transactions in seconds, production would be millions.

**Q: What if the threshold change affects multiple rules?**
A: The REGULATORY_CONTROLS table supports multiple rules with versioning. In the demo we show one rule, but the architecture supports many.

**Q: Why is the LLM output a "proposal" and not automatically applied?**
A: Safety. LLMs can hallucinate. A human must verify the extracted values before they're used. This is a regulatory system — auto-applying AI output would be irresponsible.

**Q: Could this work with real RBI circulars?**
A: Yes. The Cortex extraction prompt would need tuning for the actual format, and the rule catalog would expand, but the architecture is the same.

**Q: What Snowflake features are you using?**
A: SQL stored procedures, Streamlit in Snowflake (container runtime), Cortex COMPLETE (LLM), deterministic data generation, and the CoCo CLI development workflow. [If we add more: Semantic Views, Cortex Analyst, DMFs.]
