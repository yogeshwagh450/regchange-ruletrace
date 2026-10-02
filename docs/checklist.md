# RegChange Submission Checklist

**Hackathon:** Snowflake CoCo CLI Hackathon 2026 - GCC Edition
**Problem Statement:** 01 - Risk, Fraud and Regulatory Intelligence Copilot
**Submission Deadline:** October 4, 2026, 11:59 PM IST

---

## Submission Requirements (from Official Terms)

- [ ] **Complete profile** on hack2skill portal (name, email, phone, country)
- [ ] **Idea submission** on the contest portal
- [ ] **Prototype Deployed Link**: `https://app.snowflake.com/QGSNKWX/md84147/#/streamlit-apps/REGCHANGE_DB.REGCHANGE.REGCHANGE_APP`
- [ ] **GitHub Repository URL** - `https://github.com/yogeshwagh450/regchange-ruletrace`
- [ ] **Source code with documentation** in repo for judge review
- [ ] **Presentation deck** (PPT or similar) outlining idea, approach, and thought process
- [ ] **List all datasets used** (synthetic data, Snowflake Marketplace if any)

## Technical Deliverables

### Phase 1: Data Foundation (DONE)
- [x] Database `REGCHANGE_DB` created
- [x] Schema `REGCHANGE_DB.REGCHANGE` with tables
- [x] 10,000 synthetic INR transactions seeded
- [x] Baseline rule `AML_THRESHOLD_10L` at INR 1,000,000
- [x] `RUN_THRESHOLD_BACKTEST` procedure validated
- [x] Backtest metrics match expected values
- [x] DDL/DML reference saved

### Phase 2: Streamlit Prototype (DONE)
- [x] Streamlit in Snowflake app created and deployed (container runtime)
- [x] Policy change overview / proposal display
- [x] Backtest trigger with configurable proposed threshold
- [x] Impact metrics dashboard (alert counts, delta, % change, accounts)
- [x] Approval/reject workflow (human-in-the-loop, REVIEW_LOG table)
- [x] Prototype deployed link obtained from Snowflake

### Phase 2.5: Cortex Integration (DONE)
- [x] Cortex LLM (llama3.1-8b) policy text extraction tab
- [x] README updated with architecture, demo instructions
- [x] Project explainer doc for demo prep
- [x] Presentation outline created

### Phase 3: High-Impact Improvements (TODO — 48hr sprint)
Priority order by judge-scoring ROI:

- [x] **IMP-1: Close extraction→backtest loop** (Impact: 9/10)
  - Cortex extraction auto-populates sidebar threshold + dates
  - Turns two disconnected tabs into one coherent workflow
  - Effort: ~2 hrs | Risk: Low

- [x] **IMP-2: Executive summary generation** (Impact: 8/10)
  - Cortex generates a CISO-ready paragraph from backtest results
  - "This change adds 68 alerts, affects 47 new accounts, requires ~2 additional analysts"
  - Effort: ~2 hrs | Risk: Low

- [x] **IMP-3: SQL remediation preview** (Impact: 7/10)
  - Generate reviewable INSERT INTO REGULATORY_CONTROLS for new rule version
  - Makes system actionable, not just analytical
  - Effort: ~1 hr | Risk: Very low

- [x] **IMP-4: Semantic View + Cortex Analyst** (Impact: 8/10)
  - Created REGCHANGE_SEMANTIC with 10 metrics, 13 dimensions, 5 facts
  - "Ask Analyst" tab in Streamlit for natural language questions
  - Snowflake feature that gets "special consideration" from judges
  - Effort: ~3 hrs | Risk: Medium

- [x] **IMP-5: Data Metric Functions (DMFs)** — SKIPPED
  - DMFs not enabled on trial account ("feature is not enabled for this account")
  - Documented as production readiness item in presentation
  - No workaround available

### Phase 4: Final Polish (TODO)
- [ ] **IMP-6: Zero-Copy Clone isolation for backtest** (Impact: 7/10)
  - Clone TRANSACTIONS before backtest, run against clone, drop after
  - Shows data engineering best practice — never test on production
  - Uses signature Snowflake feature (zero additional storage)
  - Effort: ~30 min | Risk: Low
- [ ] Demo video (3 min screen recording of happy path) — optional but differentiating
- [ ] Final demo rehearsal (3 full run-throughs)
- [ ] Final git push
- [ ] Confirm hack2skill portal has all submissions
- [ ] PPT uploaded to portal

## Scoring Rubric Alignment

| Criterion | Weight | How We Address It |
|---|---|---|
| Real-World Relevance | 30% | AML threshold change is a real banking/NBFC workflow |
| Technical Execution | 40% | Snowflake-native: SQL procedures, Streamlit, versioned metadata, Cortex Code CLI usage |
| Solution Completeness | 30% | End-to-end: policy proposal -> control mapping -> backtest -> approval |

## Special Consideration Items (from Terms)
- [ ] Snowpark usage (procedure is SQL; consider Snowpark Python if adding Cortex)
- [x] Worksheets (Phase 1 SQL worksheet)
- [x] Streamlit (prototype app deployed)
- [ ] Snowflake Marketplace (optional: use if relevant dataset found)
- [x] Cortex Code CLI (development workflow throughout)

## Credit Budget
- Trial: $400 USD
- Monitor via: `SELECT SUM(CREDITS_USED) FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY`
- Keep warehouse XS, suspend when idle, avoid long-running queries

## Key Dates
- **Now - Oct 4:** Build and iterate
- **Oct 4, 11:59 PM IST:** Submission deadline (entry cannot be changed after)
- **Oct 5-22:** Evaluation round
- **Oct 23:** Finalist announcement
- **Oct 26:** Finalist induction
- **Oct 27-30:** Grand Finale (live demo if shortlisted)
