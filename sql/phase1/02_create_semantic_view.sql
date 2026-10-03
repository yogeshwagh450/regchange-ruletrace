-- RegChange: Semantic View creation for Cortex Analyst
-- Run after Phase 1 tables are created

CREATE OR REPLACE SEMANTIC VIEW REGCHANGE_DB.REGCHANGE.REGCHANGE_SEMANTIC

  TABLES (
    txn AS REGCHANGE_DB.REGCHANGE.TRANSACTIONS
      PRIMARY KEY (TXN_ID)
      WITH SYNONYMS = ('transactions', 'bank transactions', 'payments')
      COMMENT = 'Synthetic INR transactions for AML monitoring',
    backtest AS REGCHANGE_DB.REGCHANGE.BACKTEST_RUNS
      PRIMARY KEY (RUN_ID)
      WITH SYNONYMS = ('backtest runs', 'threshold tests', 'impact analysis')
      COMMENT = 'Persisted results from threshold backtest runs',
    controls AS REGCHANGE_DB.REGCHANGE.REGULATORY_CONTROLS
      PRIMARY KEY (RULE_ID, RULE_VERSION)
      WITH SYNONYMS = ('rules', 'AML rules', 'regulatory rules', 'thresholds')
      COMMENT = 'Versioned AML regulatory control rules',
    reviews AS REGCHANGE_DB.REGCHANGE.REVIEW_LOG
      PRIMARY KEY (REVIEW_ID)
      WITH SYNONYMS = ('approvals', 'review decisions', 'audit log')
      COMMENT = 'Approval and rejection audit trail for backtest proposals'
  )

  RELATIONSHIPS (
    review_to_backtest AS
      reviews (RUN_ID) REFERENCES backtest
  )

  FACTS (
    txn.txn_amount_value AS TXN_AMOUNT
      COMMENT = 'Transaction amount in INR',
    backtest.old_alerts AS OLD_ALERT_COUNT
      COMMENT = 'Number of alerts under the current baseline rule',
    backtest.new_alerts AS NEW_ALERT_COUNT
      COMMENT = 'Number of alerts under the proposed rule',
    backtest.alert_delta AS ALERT_COUNT_DELTA
      COMMENT = 'Difference between proposed and baseline alert counts',
    backtest.pct_change AS PERCENT_ALERT_CHANGE
      COMMENT = 'Percentage increase in alerts from baseline to proposed'
  )

  DIMENSIONS (
    txn.account AS ACCOUNT_ID
      WITH SYNONYMS = ('customer', 'customer account')
      COMMENT = 'Customer account identifier',
    txn.transaction_type AS TXN_TYPE
      WITH SYNONYMS = ('payment method', 'channel')
      COMMENT = 'Transaction channel: UPI, CARD, BANK_TRANSFER, or CASH',
    txn.transaction_date AS TXN_TIMESTAMP
      COMMENT = 'Timestamp when the transaction occurred',
    txn.currency AS CURRENCY_CODE
      COMMENT = 'Currency code, always INR in this dataset',
    backtest.proposed_threshold AS PROPOSED_THRESHOLD_INR
      WITH SYNONYMS = ('new threshold', 'proposed limit')
      COMMENT = 'The proposed AML threshold in INR for this backtest run',
    backtest.run_status AS RUN_STATUS
      COMMENT = 'Backtest run status: SUCCESS or ERROR',
    backtest.run_date AS CREATED_AT
      WITH SYNONYMS = ('backtest date', 'run date')
      COMMENT = 'When the backtest was executed',
    controls.rule_name AS RULE_NAME
      COMMENT = 'Human-readable name of the AML rule',
    controls.rule_status AS STATUS
      COMMENT = 'Rule lifecycle status: ACTIVE, SUPERSEDED',
    controls.threshold AS THRESHOLD_VALUE
      WITH SYNONYMS = ('current threshold', 'baseline threshold')
      COMMENT = 'Current active threshold value in INR',
    reviews.decision AS DECISION
      WITH SYNONYMS = ('approval status', 'review outcome')
      COMMENT = 'APPROVED or REJECTED',
    reviews.reviewer_name AS REVIEWER
      COMMENT = 'Snowflake username of the reviewer',
    reviews.review_date AS REVIEWED_AT
      COMMENT = 'When the review decision was recorded'
  )

  METRICS (
    txn.total_transactions AS COUNT(TXN_ID)
      COMMENT = 'Total number of transactions',
    txn.total_transaction_value AS SUM(txn_amount_value)
      COMMENT = 'Sum of all transaction amounts in INR',
    txn.average_transaction_value AS AVG(txn_amount_value)
      COMMENT = 'Average transaction amount in INR',
    txn.high_value_transaction_count AS COUNT_IF(txn_amount_value > 1000000)
      COMMENT = 'Transactions exceeding INR 10 lakh (current AML threshold)',
    txn.unique_accounts AS COUNT(DISTINCT account)
      COMMENT = 'Number of distinct customer accounts',
    backtest.total_backtest_runs AS COUNT(RUN_ID)
      COMMENT = 'Total number of backtest runs performed',
    backtest.avg_alert_increase AS AVG(pct_change)
      COMMENT = 'Average percentage increase in alerts across all backtests',
    backtest.max_alert_delta AS MAX(alert_delta)
      COMMENT = 'Largest alert count increase from any single backtest',
    reviews.total_reviews AS COUNT(REVIEW_ID)
      COMMENT = 'Total number of review decisions recorded',
    reviews.approval_count AS COUNT_IF(decision = 'APPROVED')
      COMMENT = 'Number of approved proposals'
  )

  COMMENT = 'RegChange: AML threshold impact analysis semantic view for Cortex Analyst'
  AI_SQL_GENERATION 'This semantic view covers AML regulatory change impact analysis for a fictional bank. Transactions are in INR. The backtest compares alert counts under a current threshold versus a proposed lower threshold. Always filter transactions by CURRENCY_CODE = ''INR'' unless asked otherwise.';
