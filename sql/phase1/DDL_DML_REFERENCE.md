# Phase 1 DDL/DML Reference

Executed on **2026-09-30** against account `II85874`, role `ACCOUNTADMIN`, warehouse `COMPUTE_WH`.

## 1. Database and Schema

```sql
CREATE DATABASE IF NOT EXISTS REGCHANGE_DB COMMENT = 'RegChange hackathon project';
USE DATABASE REGCHANGE_DB;
CREATE SCHEMA IF NOT EXISTS REGCHANGE;
USE SCHEMA REGCHANGE_DB.REGCHANGE;
```

## 2. Tables Created

### TRANSACTIONS
```sql
CREATE TABLE IF NOT EXISTS REGCHANGE_DB.REGCHANGE.TRANSACTIONS (
    TXN_ID           VARCHAR(32)      NOT NULL,
    ACCOUNT_ID       VARCHAR(32)      NOT NULL,
    TXN_AMOUNT       NUMBER(18, 2)    NOT NULL,
    CURRENCY_CODE    VARCHAR(3)       NOT NULL,
    TXN_TIMESTAMP    TIMESTAMP_NTZ    NOT NULL,
    TXN_TYPE         VARCHAR(24)      NOT NULL,
    BENEFICIARY_ID   VARCHAR(32),
    SOURCE_BATCH_ID  VARCHAR(32)      NOT NULL,
    CREATED_AT       TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP()
);
```

### REGULATORY_CONTROLS
```sql
CREATE TABLE IF NOT EXISTS REGCHANGE_DB.REGCHANGE.REGULATORY_CONTROLS (
    RULE_ID             VARCHAR(64)      NOT NULL,
    RULE_NAME           VARCHAR(200)     NOT NULL,
    RULE_VERSION        NUMBER(10, 0)    NOT NULL,
    PARAMETER_NAME      VARCHAR(100)     NOT NULL,
    THRESHOLD_VALUE     NUMBER(18, 2)    NOT NULL,
    CURRENCY_CODE       VARCHAR(3)       NOT NULL,
    SQL_PREDICATE       VARCHAR(500)     NOT NULL,
    STATUS              VARCHAR(16)      NOT NULL,
    ACTIVE_FROM         DATE             NOT NULL,
    ACTIVE_TO           DATE,
    SOURCE_REFERENCE    VARCHAR(500),
    CREATED_AT          TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP()
);
```

### BACKTEST_RUNS
```sql
CREATE TABLE IF NOT EXISTS REGCHANGE_DB.REGCHANGE.BACKTEST_RUNS (
    RUN_ID                       VARCHAR(36)      NOT NULL,
    RULE_ID                      VARCHAR(64)      NOT NULL,
    BASELINE_RULE_VERSION        NUMBER(10, 0)    NOT NULL,
    OLD_THRESHOLD_INR            NUMBER(18, 2)    NOT NULL,
    PROPOSED_THRESHOLD_INR       NUMBER(18, 2)    NOT NULL,
    PERIOD_START_NTZ             TIMESTAMP_NTZ    NOT NULL,
    PERIOD_END_NTZ               TIMESTAMP_NTZ    NOT NULL,
    OLD_ALERT_COUNT              NUMBER(18, 0)    NOT NULL,
    NEW_ALERT_COUNT              NUMBER(18, 0)    NOT NULL,
    ALERT_COUNT_DELTA            NUMBER(18, 0)    NOT NULL,
    PERCENT_ALERT_CHANGE         NUMBER(18, 4),
    ACCOUNTS_ALERTED_NEW_RULE    NUMBER(18, 0)    NOT NULL,
    NEWLY_ALERTED_ACCOUNTS       NUMBER(18, 0)    NOT NULL,
    RUN_STATUS                   VARCHAR(24)      NOT NULL,
    CREATED_AT                   TIMESTAMP_NTZ    DEFAULT CURRENT_TIMESTAMP()
);
```

## 3. Data Seeded

### 10,000 Synthetic Transactions (MERGE)
- Source: deterministic generator using `TABLE(GENERATOR(ROWCOUNT => 10000))`
- 2,500 unique accounts, 90-day window from 2026-07-01, all INR
- Transaction types: UPI, CARD, BANK_TRANSFER, CASH
- Amount distribution: ~2% high-value (500K-2M), ~13% medium (10K-500K), ~85% low (100-100K)
- Batch ID: `SYNTHETIC-2026-09`
- Full MERGE SQL in `01_initialize_regchange.sql`

### Baseline Rule (MERGE)
- `AML_THRESHOLD_10L`, version 1, threshold INR 1,000,000, status ACTIVE, from 2026-01-01

## 4. Stored Procedure

### RUN_THRESHOLD_BACKTEST
```
CALL REGCHANGE_DB.REGCHANGE.RUN_THRESHOLD_BACKTEST(
    proposed_threshold_inr,   -- NUMBER(18,2)
    period_start_ntz,         -- TIMESTAMP_NTZ
    period_end_ntz            -- TIMESTAMP_NTZ
);
```
Returns VARIANT with backtest metrics. Persists each run to BACKTEST_RUNS.

## 5. Validated Results (Smoke Test)

```sql
CALL REGCHANGE_DB.REGCHANGE.RUN_THRESHOLD_BACKTEST(
    500000.00,
    '2026-07-01 00:00:00'::TIMESTAMP_NTZ,
    '2026-10-01 00:00:00'::TIMESTAMP_NTZ
);
```

| Metric | Value |
|---|---|
| Old alert count (baseline INR 10L) | 132 |
| New alert count (proposed INR 5L) | 200 |
| Alert count delta | 68 |
| Percentage alert change | 51.5152% |
| Accounts alerted under new rule | 50 |
| Accounts with transactions in the newly monitored amount band | 47 |

The legacy `NEWLY_ALERTED_ACCOUNTS` column holds this band-account measure, not first-time alerted accounts. Some already have baseline alerts. In the unchanged seed, the baseline and proposed rules alert the same 50 accounts; local account-set comparison gives zero first-time accounts.
