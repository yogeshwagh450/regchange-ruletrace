# RegChange — Presentation Deck (Copy-Paste Ready)

Use this to create your PPT. Each section = one slide. Copy the content directly.

---

## SLIDE 1: Title Slide

**Title:** RegChange — Regulatory Change Impact & Control Intelligence

**Subtitle:** Snowflake CoCo CLI Hackathon 2026 | Problem Statement 01
Risk, Fraud and Regulatory Intelligence Copilot

**Author:** Yogesh Wagh | Solo Entry

**Links:**
- GitHub: github.com/yogeshwagh450/regchange-ruletrace
- Prototype: [Streamlit in Snowflake App URL]

**Speaker Notes:**
"Good [morning/afternoon]. I'm Yogesh Wagh, a data engineer, and I built RegChange — a regulatory change impact intelligence system for banking compliance teams. Let me show you what it does."

---

## SLIDE 2: The Problem

**Title:** The Problem: Regulatory Threshold Changes Are Manual and Unauditable

**Bullet points:**
- Banks and NBFCs must comply with AML (Anti-Money Laundering) regulations
- Regulators periodically change monitoring thresholds via official circulars
- Example: "Lower the high-value transaction alert threshold from INR 10 lakh to INR 5 lakh"
- Today's process is manual:
  - Read the circular, interpret what changed
  - Estimate impact with spreadsheets and ad-hoc SQL on production data
  - Email chains for approval — no audit trail
  - Takes days to weeks, error-prone, not reproducible

**Key stat (bold this):**
"A single threshold change can affect thousands of accounts and generate hundreds of new alerts — but compliance teams often don't know the exact impact until it's too late."

**Speaker Notes:**
"When a regulator issues a circular changing an AML threshold, banks today spend days estimating the impact manually. There's no reproducibility, no audit trail, and no way to compare scenarios. RegChange solves this."

---

## SLIDE 3: Our Solution

**Title:** RegChange: End-to-End Regulatory Change Workflow

**5-step flow (use arrows or numbered boxes):**

1. **EXTRACT** — Paste the regulatory circular → Snowflake Cortex LLM extracts structured fields (rule name, old/new threshold, effective date)

2. **MAP** — Extracted values auto-populate into the backtest parameters → linked to a versioned control record in REGULATORY_CONTROLS

3. **REPLAY** — Run the backtest: same 10,000 historical transactions evaluated under both old and proposed thresholds

4. **QUANTIFY** — Dashboard shows: 132 → 200 alerts (+68, +51.5%), 50 accounts flagged, 47 newly flagged

5. **APPROVE** — Compliance officer reviews evidence, approves/rejects with a comment → logged for audit

**Footer:** "LLM output is a proposal — a human approves every control change."

**Speaker Notes:**
"RegChange is a 5-step workflow. The AI reads the circular and extracts the change. It maps to a versioned control record. The system replays history under both rules. You see exact impact numbers. And a human approves with a full audit trail. The key design principle: the LLM proposes, the human decides."

---

## SLIDE 4: Architecture

**Title:** Architecture — Built Entirely on Snowflake

**Use the Draw.io diagram here (see ARCHITECTURE DIAGRAM section below)**

**Text labels for the diagram:**

Left side — "Streamlit in Snowflake (Container Runtime)":
- Tab 1: Policy Extraction (Cortex LLM)
- Tab 2: Run Backtest (SQL Procedure + Cortex Summary)
- Tab 3: Run History
- Tab 4: Review & Approve
- Tab 5: Ask Analyst (Cortex Analyst + Semantic View)

Right side — "REGCHANGE_DB.REGCHANGE":
- TRANSACTIONS (10K synthetic INR txns)
- REGULATORY_CONTROLS (versioned rule metadata)
- BACKTEST_RUNS (persisted metrics)
- REVIEW_LOG (approval audit trail)
- RUN_THRESHOLD_BACKTEST() (SQL stored procedure)
- REGCHANGE_SEMANTIC (Semantic View: 10 metrics, 13 dimensions)

Bottom — "Snowflake Services":
- Cortex COMPLETE (llama3.1-8b) — policy extraction + executive summary
- Cortex Analyst REST API — natural language queries
- Compute Pool (SYSTEM_COMPUTE_POOL_CPU) — Streamlit container
- COMPUTE_WH (XS) — SQL queries
- CoCo CLI — development workflow

**Speaker Notes:**
"Everything runs inside Snowflake. The Streamlit app uses container runtime. Cortex handles both the policy extraction and the natural language query interface. The semantic view defines business metrics so Cortex Analyst generates governed, accurate SQL — not guesswork."

---

## SLIDE 5: Live Demo — Policy Extraction

**Title:** Demo: AI Reads the Regulatory Circular

**Screenshot:** Policy Extraction tab showing the fictional circular and Cortex extraction result (extracted fields + mapped to control panel)

**Call out these elements:**
- Paste any circular text → Cortex extracts structured fields
- JSON output: rule_name, old_threshold (1000000), new_threshold (500000), effective_date
- "Auto-filled from Cortex extraction" badge in sidebar
- "This is an LLM proposal — human must confirm"

**Speaker Notes:**
"I paste the regulatory circular. Cortex reads it and extracts: the threshold is changing from 10 lakh to 5 lakh, effective October 1. Notice the sidebar automatically populated with 500,000. The compliance officer reviews these values before proceeding."

---

## SLIDE 6: Live Demo — Backtest Results

**Title:** Demo: Quantified Impact in 3 Seconds

**Screenshot:** Run Backtest tab showing the 6 metric cards + executive summary

**Highlight these numbers (make them large):**
- 132 → 200 alerts (+68, +51.5%)
- 50 accounts flagged, 47 newly flagged
- Executive summary: "This would require our analysts to review an additional 17 alerts per quarter..."

**Speaker Notes:**
"One click — 3 seconds — and the compliance team knows exactly what this change means. 68 more alerts, 47 customers flagged for the first time. The executive summary is auto-generated by Cortex — ready to send to the Chief Compliance Officer. Below this, the system also generates the exact SQL to implement the new rule version."

---

## SLIDE 7: Live Demo — SQL Remediation + Approval

**Title:** Demo: Actionable Output + Auditable Approval

**Two sections on this slide:**

Left — "SQL Remediation Preview":
- Screenshot of the generated UPDATE + INSERT SQL
- "Step 1: Retire current rule version"
- "Step 2: Insert new rule at INR 500,000"
- "Source reference links back to backtest run ID"

Right — "Review & Approve":
- Screenshot of the approval tab with APPROVED decision and Review Log
- "Who approved, when, why — full audit trail"
- "Does NOT auto-promote the rule"

**Speaker Notes:**
"The system generates the exact SQL to implement the change — copy, review, execute. And the approval is logged: who approved, when, with what justification. This is what regulators want to see in an audit."

---

## SLIDE 8: Live Demo — Ask Analyst

**Title:** Demo: Natural Language Queries with Cortex Analyst

**Screenshot:** Ask Analyst tab showing "How many high value transactions exceed 10 lakh" → Generated SQL → Result: 132

**Key points:**
- Powered by a Semantic View (10 metrics, 13 dimensions, 5 facts)
- Cortex Analyst REST API generates grounded SQL — not LLM guessing
- Compliance officer asks in plain English, gets governed answers
- "How many high value transactions exceed 10 lakh?" → 132 (matches baseline alerts exactly)

**Speaker Notes:**
"A compliance officer can ask questions in plain English. The system uses Cortex Analyst with our Semantic View — it doesn't guess at SQL, it generates queries grounded in our defined business metrics. 'How many high value transactions exceed 10 lakh' returns exactly 132, matching our baseline alert count."

---

## SLIDE 9: Technical Depth + Scoring Rubric

**Title:** Technical Execution & Rubric Alignment

**Left column — Snowflake Features Used:**
- SQL Stored Procedures (deterministic backtest)
- Streamlit in Snowflake (container runtime)
- Cortex COMPLETE (policy extraction + executive summary)
- Cortex Analyst REST API (natural language queries)
- Semantic View (governed business metrics)
- Cortex Code CLI (entire development workflow)

**Right column — Rubric Fit:**

| Criterion | Weight | How Addressed |
|---|---|---|
| Real-World Relevance | 30% | AML threshold changes are a real banking compliance workflow |
| Technical Execution | 40% | 6 Snowflake-native services, Semantic View, deterministic replay |
| Solution Completeness | 30% | End-to-end: circular → extraction → backtest → summary → remediation → approval |

**Speaker Notes:**
"We use six Snowflake-native services. The Semantic View is particularly important — it defines business metrics once, and both the dashboard and the natural language interface use those same definitions. This ensures consistency, which is critical in a compliance system."

---

## SLIDE 10: Datasets Declaration

**Title:** Data Sources & Limitations

**Datasets:**
- ALL data is synthetic, generated deterministically within the Phase 1 SQL script
- No external datasets, APIs, or third-party data sources used
- 10,000 INR transactions across 2,500 accounts over 90 days (Jul–Sep 2026)
- 1 baseline regulatory control rule (AML_THRESHOLD_10L at INR 10,00,000)
- Transaction types: UPI, CARD, BANK_TRANSFER, CASH
- Tested at 500K rows — same code, under 2 seconds on XS warehouse

**Limitations & Future Work:**
- Current: single threshold scenario, synthetic data, one rule type
- DMFs planned but not available on trial account
- Future: multi-regulator support, Dynamic Tables for continuous monitoring, Cortex Search for policy document library, transient clones for safe rule testing

**Speaker Notes:**
"All data is synthetic and generated deterministically — the same script always produces the same results. We tested at 50x scale with no code changes. In production, this would connect to core banking data. We planned Data Metric Functions for quality monitoring but the feature isn't enabled on trial accounts."

---

## SLIDE 11: Thank You

**Title:** Thank You

**Content:**
- **Live Prototype:** [Streamlit URL]
- **GitHub:** github.com/yogeshwagh450/regchange-ruletrace
- **Built with:** Snowflake CoCo CLI, Streamlit, Cortex AI, Semantic Views, Cortex Analyst
- **Solo entry by:** Yogesh Wagh

"RegChange turns a weeks-long manual process into a 60-second auditable workflow."

Questions?

**Speaker Notes:**
"Thank you. RegChange turns a weeks-long manual compliance process into a 60-second workflow with full audit trail. Everything you saw runs inside Snowflake, built with CoCo CLI. I'm happy to take questions."

---

# ARCHITECTURE DIAGRAM — Draw.io Instructions

Create a Draw.io diagram with these exact boxes and connections:

**Top banner (full width, light blue):**
"RegChange — Regulatory Change Impact & Control Intelligence"

**Left section — "Streamlit in Snowflake (Container Runtime)":**
Draw a large rounded rectangle containing 5 smaller boxes stacked vertically:
1. "Policy Extraction" — with icon: document
2. "Run Backtest" — with icon: play
3. "Run History" — with icon: table
4. "Review & Approve" — with icon: checkmark
5. "Ask Analyst" — with icon: chat bubble

**Right section — "REGCHANGE_DB.REGCHANGE":**
Draw a large rounded rectangle (database shape) containing:
- 4 table icons labeled:
  - TRANSACTIONS (10K rows)
  - REGULATORY_CONTROLS
  - BACKTEST_RUNS
  - REVIEW_LOG
- 1 procedure icon: RUN_THRESHOLD_BACKTEST()
- 1 semantic view icon: REGCHANGE_SEMANTIC

**Arrows from left to right:**
- "Policy Extraction" → arrow labeled "Cortex COMPLETE (llama3.1-8b)" → REGULATORY_CONTROLS
- "Run Backtest" → arrow labeled "CALL procedure" → RUN_THRESHOLD_BACKTEST() → TRANSACTIONS + BACKTEST_RUNS
- "Run Backtest" → arrow labeled "Cortex COMPLETE" → "Executive Summary"
- "Review & Approve" → arrow → REVIEW_LOG
- "Ask Analyst" → arrow labeled "Cortex Analyst REST API" → REGCHANGE_SEMANTIC

**Bottom bar (full width, dark):**
"Snowflake Platform: COMPUTE_WH (XS) | SYSTEM_COMPUTE_POOL_CPU | Cortex AI | CoCo CLI"

**Color scheme:**
- Streamlit tabs: light blue (#29B5E8)
- Database tables: light green
- Cortex services: orange
- Arrows: dark gray
- Background: white
