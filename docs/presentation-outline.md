# RegChange — Presentation Deck Outline

Use this outline to create the required PPT. Aim for 8-10 slides, ~5 min presentation.

---

## Slide 1: Title
- **RegChange — Regulatory Change Impact & Control Intelligence**
- Snowflake CoCo CLI Hackathon 2026 | Problem Statement 01
- Yogesh Wagh | Solo Entry
- GitHub: github.com/yogeshwagh450/regchange-ruletrace

---

## Slide 2: The Problem
- Banking/NBFC compliance teams handle regulatory threshold changes manually
- When a regulator lowers an AML monitoring threshold, teams must:
  - Understand what changed in the circular
  - Estimate how many new alerts will be generated
  - Assess operational and customer impact
  - Get approval before updating systems
- Today: spreadsheets, guesswork, weeks of effort, no audit trail

---

## Slide 3: Our Solution
- RegChange automates the regulatory change impact workflow:
  1. **Extract** — Cortex LLM reads the policy circular and extracts structured change fields
  2. **Map** — Links the change to a versioned control record with typed metadata
  3. **Replay** — Backtests 10,000 historical transactions under old and new thresholds
  4. **Quantify** — Reports exact alert counts, delta, percentage change, affected accounts
  5. **Approve** — Human reviewer approves/rejects with an auditable record
- Key: LLM output is a *proposal*; a human approves any control change

---

## Slide 4: Architecture
- (Use the ASCII diagram from README or redraw as a visual)
- Streamlit in Snowflake (container runtime) → 4 tabs
- REGCHANGE_DB.REGCHANGE schema with 4 tables + 1 stored procedure
- Snowflake Cortex (llama3.1-8b) for policy extraction
- Developed entirely using Snowflake CoCo CLI

---

## Slide 5: Demo Scenario
- Fictional circular: AML threshold lowered from ₹10,00,000 → ₹5,00,000
- Show the 4-tab workflow:
  - Tab 1: Paste policy text → Cortex extracts fields
  - Tab 2: Run backtest → see 6 metric cards + distribution chart
  - Tab 3: Run history shows all past backtests
  - Tab 4: Approve/reject with comment → audit log

---

## Slide 6: Impact Results (Screenshot)
- (Screenshot of the Run Backtest tab with metrics)
- 132 baseline alerts → 200 proposed alerts (+68, +51.5%)
- 50 accounts flagged, 47 newly flagged
- "This proposed change adds 68 alerts and newly flags 47 accounts"

---

## Slide 7: Technical Execution
- **Snowflake-native:** SQL stored procedures, Streamlit, Cortex AI
- **Deterministic:** Same inputs always produce same outputs (demo-safe)
- **Auditable:** Every backtest run and review decision is persisted
- **Safe:** LLM extracts a proposal, human approves, no auto-promotion
- **Developed with CoCo CLI** throughout (Phase 1 SQL, Streamlit, deployment)

---

## Slide 8: Scoring Rubric Fit
| Criterion | Weight | How We Address It |
|---|---|---|
| Real-World Relevance (30%) | AML threshold changes are a real banking compliance workflow |
| Technical Execution (40%) | Snowflake SQL + Streamlit + Cortex + CoCo CLI |
| Solution Completeness (30%) | End-to-end: circular → extraction → backtest → approval |

---

## Slide 9: Limitations & Future Work
- **Current:** Single threshold scenario, synthetic data, one rule type
- **Future:**
  - Multi-regulator support (RBI, SEBI, etc.)
  - Dynamic Tables for continuous impact monitoring
  - DMFs for data quality checks on the control catalog
  - Transient clones for safe rule testing before production
  - Cortex-powered regulatory document parsing at scale

---

## Slide 10: Thank You
- **Live prototype:** (Streamlit URL)
- **GitHub:** github.com/yogeshwagh450/regchange-ruletrace
- **Built with:** Snowflake CoCo CLI, Streamlit in Snowflake, Cortex AI
- Questions?

---

## Presentation Tips
- Lead with the problem (compliance pain), not the tech
- Demo the happy path live: paste text → extract → backtest → approve
- Emphasize the audit trail — judges care about governance
- Keep it under 5 minutes; leave time for questions
- Have the Streamlit app open and ready before presenting
