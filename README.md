# RegChange — Regulatory Change Impact & Control Intelligence

> Snowflake CoCo CLI Hackathon 2026 — Problem Statement 01: Risk, Fraud and Regulatory Intelligence Copilot

## What It Does

RegChange demonstrates an auditable regulatory-change workflow for banking/NBFC compliance teams. When a regulator proposes lowering an AML transaction-monitoring threshold, the system:

1. **Maps the change** to a versioned control record with typed metadata
2. **Replays history** — evaluates 10,000 synthetic transactions under both old and proposed thresholds
3. **Quantifies impact** — old/new alert counts, delta, percentage change, total and newly affected accounts
4. **Enables human approval** — a reviewer sees evidence and approves or rejects; the decision is logged for audit

The punchline: *"This proposed change adds 68 alerts and newly flags 47 accounts. Here is the control, evidence, and approval record."*

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit in Snowflake                    │
│   ┌──────────┐  ┌─────────────┐  ┌───────────────────────┐  │
│   │ Run      │  │ Run         │  │ Review &              │  │
│   │ Backtest │  │ History     │  │ Approve               │  │
│   └────┬─────┘  └──────┬──────┘  └───────────┬───────────┘  │
│        │               │                      │              │
├────────┼───────────────┼──────────────────────┼──────────────┤
│        ▼               ▼                      ▼              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              REGCHANGE_DB.REGCHANGE                   │   │
│  │                                                       │   │
│  │  TRANSACTIONS        10,000 synthetic INR txns        │   │
│  │  REGULATORY_CONTROLS Versioned rule metadata          │   │
│  │  BACKTEST_RUNS       Persisted run metrics            │   │
│  │  REVIEW_LOG          Approval/rejection audit trail   │   │
│  │                                                       │   │
│  │  RUN_THRESHOLD_BACKTEST()  SQL stored procedure       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  Runtime: Container (SYSTEM_COMPUTE_POOL_CPU)                │
│  Queries: COMPUTE_WH (XS)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Demo Scenario

A fictional regulator lowers the AML high-value transaction threshold from **₹10,00,000** (₹10 lakh) to **₹5,00,000** (₹5 lakh).

| Metric | Value | What It Means |
|---|---|---|
| Baseline alerts | 132 | Alerts under the current ₹10L rule |
| Proposed alerts | 200 | Alerts under the proposed ₹5L rule |
| Alert delta | +68 (+51.5%) | Additional operational workload |
| Accounts alerted | 50 | Total accounts flagged under the new rule |
| Newly alerted | 47 | Accounts flagged for the first time |

All data is synthetic. Nothing here constitutes production AML advice.

## Prototype

**Live app:** [Streamlit in Snowflake](https://app.snowflake.com/QGSNKWX/md84147/#/streamlit-apps/REGCHANGE_DB.REGCHANGE.REGCHANGE_APP)

## Project Structure

```
regchange-ruletrace/
├── README.md
├── docs/
│   ├── decision-brief.md          # Hackathon fit and architecture decisions
│   └── checklist.md               # Submission checklist
├── sql/
│   └── phase1/
│       ├── 01_initialize_regchange.sql   # Schema, tables, seed data, procedure
│       └── DDL_DML_REFERENCE.md          # Quick DDL/DML reference
├── streamlit/
│   ├── streamlit_app.py           # Streamlit app source
│   └── snowflake.yml              # Deployment manifest
└── .github/
    └── prompts/
        └── resume-regchange.prompt.md    # CoCo CLI resume prompt
```

## Setup and Run

### Prerequisites
- Snowflake account with `ACCOUNTADMIN` or a role with `CREATE SCHEMA/TABLE/PROCEDURE` privileges
- A warehouse (XS is sufficient)
- Snowflake CLI v3.14+ for Streamlit deployment (or deploy via Snowsight)

### Phase 1: Data Foundation
```sql
-- Connect to your target database, then:
CREATE DATABASE IF NOT EXISTS REGCHANGE_DB;
USE DATABASE REGCHANGE_DB;

-- Run the full Phase 1 script:
-- sql/phase1/01_initialize_regchange.sql

-- Verify with the sample backtest:
CALL REGCHANGE_DB.REGCHANGE.RUN_THRESHOLD_BACKTEST(
    500000.00,
    '2026-07-01 00:00:00'::TIMESTAMP_NTZ,
    '2026-10-01 00:00:00'::TIMESTAMP_NTZ
);
-- Expected: 132 baseline, 200 proposed, +68 delta, 50 accounts, 47 newly alerted
```

### Phase 2: Deploy Streamlit App
```bash
cd streamlit/
snow streamlit deploy --replace
```

The app deploys to `REGCHANGE_DB.REGCHANGE.REGCHANGE_APP` on the container runtime.

### Phase 3: Review Table (created separately)
```sql
CREATE TABLE IF NOT EXISTS REGCHANGE_DB.REGCHANGE.REVIEW_LOG (
    REVIEW_ID    VARCHAR(36)    NOT NULL,
    RUN_ID       VARCHAR(36)    NOT NULL,
    REVIEWER     VARCHAR(128)   NOT NULL,
    DECISION     VARCHAR(16)    NOT NULL,
    COMMENT      VARCHAR(500),
    REVIEWED_AT  TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP()
);
```

## How to Test

1. Open the Streamlit app URL
2. **Run Backtest tab** — keep defaults (₹5,00,000 proposed), click "Run Backtest", verify 6 metric cards appear
3. **Try different thresholds** — change to ₹3,00,000 or ₹7,50,000, run again, observe how impact scales
4. **Run History tab** — confirm all runs are persisted
5. **Review & Approve tab** — select a run, approve/reject with a comment, verify the Review Log table updates

## Technology Stack

| Component | Technology |
|---|---|
| Data platform | Snowflake |
| Schema & procedures | Snowflake SQL |
| App runtime | Streamlit in Snowflake (container runtime) |
| Compute | SYSTEM_COMPUTE_POOL_CPU + COMPUTE_WH (XS) |
| Development | Snowflake Cortex Code CLI (CoCo) |
| Deployment | Snowflake CLI (`snow streamlit deploy`) |

## Datasets

All data is **synthetic**, generated deterministically within the Phase 1 SQL script. No external datasets, APIs, or third-party data sources are used.

- 10,000 INR transactions across 2,500 accounts over a 90-day window (Jul-Sep 2026)
- 1 baseline regulatory control rule (`AML_THRESHOLD_10L` at ₹10,00,000)
- Transaction types: UPI, CARD, BANK_TRANSFER, CASH

## Scoring Rubric Alignment

| Criterion | Weight | How Addressed |
|---|---|---|
| Real-World Relevance | 30% | AML threshold changes are a real banking/NBFC compliance workflow |
| Technical Execution | 40% | Snowflake-native: SQL procedures, container-runtime Streamlit, versioned metadata, CoCo CLI development |
| Solution Completeness | 30% | End-to-end: policy proposal → control mapping → backtest → quantified impact → human approval with audit trail |

## Limitations and Future Work

- **Current scope:** Single threshold-change scenario with synthetic data
- **Not included:** Real regulatory document parsing, multi-regulator support, enterprise-wide lineage discovery, automatic rule promotion
- **Future:** Cortex-powered policy text extraction, Dynamic Tables for continuous impact monitoring, DMFs for data quality checks, transient clones for safe rule testing
