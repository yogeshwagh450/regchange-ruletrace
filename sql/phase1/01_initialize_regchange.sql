-- RegChange Phase 1: deterministic synthetic data and threshold backtesting.
-- Run in a Snowflake worksheet using a role with CREATE SCHEMA/TABLE/PROCEDURE
-- privileges in the current database and an available warehouse for the call.

CREATE SCHEMA IF NOT EXISTS REGCHANGE;
USE SCHEMA REGCHANGE;

CREATE TABLE IF NOT EXISTS TRANSACTIONS (
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

-- Stable IDs and deterministic values make setup re-runnable and demos repeatable.
MERGE INTO TRANSACTIONS AS target
USING (
    WITH numbered AS (
        SELECT ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1 AS N
        FROM TABLE(GENERATOR(ROWCOUNT => 10000))
    )
    SELECT
        'TXN-' || LPAD(TO_VARCHAR(N + 1), 8, '0') AS TXN_ID,
        'ACCT-' || LPAD(TO_VARCHAR(MOD(N * 37 + 11, 2500) + 1), 6, '0') AS ACCOUNT_ID,
        CASE
            WHEN MOD(N, 100) < 2
                THEN 500000 + MOD(N * 7919 + 104729, 1500001)
            WHEN MOD(N, 100) < 15
                THEN 10000 + MOD(N * 3571 + 7919, 490001)
            ELSE 100 + MOD(N * 1877 + 101, 99900)
        END::NUMBER(18, 2) AS TXN_AMOUNT,
        'INR' AS CURRENCY_CODE,
        DATEADD(
            'second',
            MOD(N * 104729 + 17, 7776000),
            '2026-07-01 00:00:00'::TIMESTAMP_NTZ
        ) AS TXN_TIMESTAMP,
        CASE MOD(N, 4)
            WHEN 0 THEN 'UPI'
            WHEN 1 THEN 'CARD'
            WHEN 2 THEN 'BANK_TRANSFER'
            ELSE 'CASH'
        END AS TXN_TYPE,
        CASE
            WHEN MOD(N, 4) = 3 THEN NULL
            ELSE 'BEN-' || LPAD(TO_VARCHAR(MOD(N * 31 + 7, 1400) + 1), 5, '0')
        END AS BENEFICIARY_ID,
        'SYNTHETIC-2026-09' AS SOURCE_BATCH_ID
    FROM numbered
) AS source
    ON target.TXN_ID = source.TXN_ID
WHEN NOT MATCHED THEN INSERT (
    TXN_ID,
    ACCOUNT_ID,
    TXN_AMOUNT,
    CURRENCY_CODE,
    TXN_TIMESTAMP,
    TXN_TYPE,
    BENEFICIARY_ID,
    SOURCE_BATCH_ID
)
VALUES (
    source.TXN_ID,
    source.ACCOUNT_ID,
    source.TXN_AMOUNT,
    source.CURRENCY_CODE,
    source.TXN_TIMESTAMP,
    source.TXN_TYPE,
    source.BENEFICIARY_ID,
    source.SOURCE_BATCH_ID
);

CREATE TABLE IF NOT EXISTS REGULATORY_CONTROLS (
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

-- SQL_PREDICATE is descriptive metadata only; the procedure uses typed fields.
MERGE INTO REGULATORY_CONTROLS AS target
USING (
    SELECT
        'AML_THRESHOLD_10L' AS RULE_ID,
        'AML high-value transaction threshold' AS RULE_NAME,
        1 AS RULE_VERSION,
        'TXN_AMOUNT_THRESHOLD_INR' AS PARAMETER_NAME,
        1000000.00::NUMBER(18, 2) AS THRESHOLD_VALUE,
        'INR' AS CURRENCY_CODE,
        'TXN_AMOUNT > :THRESHOLD_VALUE' AS SQL_PREDICATE,
        'ACTIVE' AS STATUS,
        '2026-01-01'::DATE AS ACTIVE_FROM,
        NULL::DATE AS ACTIVE_TO,
        'SYNTHETIC_BASELINE_FOR_HACKATHON' AS SOURCE_REFERENCE
) AS source
    ON target.RULE_ID = source.RULE_ID
    AND target.RULE_VERSION = source.RULE_VERSION
WHEN NOT MATCHED THEN INSERT (
    RULE_ID,
    RULE_NAME,
    RULE_VERSION,
    PARAMETER_NAME,
    THRESHOLD_VALUE,
    CURRENCY_CODE,
    SQL_PREDICATE,
    STATUS,
    ACTIVE_FROM,
    ACTIVE_TO,
    SOURCE_REFERENCE
)
VALUES (
    source.RULE_ID,
    source.RULE_NAME,
    source.RULE_VERSION,
    source.PARAMETER_NAME,
    source.THRESHOLD_VALUE,
    source.CURRENCY_CODE,
    source.SQL_PREDICATE,
    source.STATUS,
    source.ACTIVE_FROM,
    source.ACTIVE_TO,
    source.SOURCE_REFERENCE
);

CREATE TABLE IF NOT EXISTS BACKTEST_RUNS (
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

CREATE OR REPLACE PROCEDURE RUN_THRESHOLD_BACKTEST(
    PROPOSED_THRESHOLD_INR NUMBER(18, 2),
    PERIOD_START_NTZ TIMESTAMP_NTZ,
    PERIOD_END_NTZ TIMESTAMP_NTZ
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    v_control_count NUMBER(10, 0);
    v_rule_version NUMBER(10, 0);
    v_old_threshold NUMBER(18, 2);
    v_old_alert_count NUMBER(18, 0);
    v_new_alert_count NUMBER(18, 0);
    v_accounts_alerted_new_rule NUMBER(18, 0);
    v_newly_alerted_accounts NUMBER(18, 0);
    v_alert_count_delta NUMBER(18, 0);
    v_percent_alert_change NUMBER(18, 4);
    v_run_id VARCHAR(36);
BEGIN
    IF (PROPOSED_THRESHOLD_INR IS NULL OR PROPOSED_THRESHOLD_INR <= 0) THEN
        RETURN OBJECT_CONSTRUCT(
            'status', 'ERROR',
            'message', 'Proposed threshold must be greater than zero.'
        );
    END IF;

    IF (PERIOD_START_NTZ IS NULL OR PERIOD_END_NTZ IS NULL
        OR PERIOD_START_NTZ >= PERIOD_END_NTZ) THEN
        RETURN OBJECT_CONSTRUCT(
            'status', 'ERROR',
            'message', 'Replay period must have a start timestamp before its end timestamp.'
        );
    END IF;

    SELECT COUNT(*)
      INTO :v_control_count
      FROM REGULATORY_CONTROLS
     WHERE RULE_ID = 'AML_THRESHOLD_10L'
       AND STATUS = 'ACTIVE'
       AND ACTIVE_FROM <= CURRENT_DATE()
       AND (ACTIVE_TO IS NULL OR ACTIVE_TO >= CURRENT_DATE());

    IF (v_control_count <> 1) THEN
        RETURN OBJECT_CONSTRUCT(
            'status', 'ERROR',
            'message', 'Expected exactly one currently active AML_THRESHOLD_10L baseline rule.'
        );
    END IF;

    SELECT RULE_VERSION, THRESHOLD_VALUE
      INTO :v_rule_version, :v_old_threshold
      FROM REGULATORY_CONTROLS
     WHERE RULE_ID = 'AML_THRESHOLD_10L'
       AND STATUS = 'ACTIVE'
       AND ACTIVE_FROM <= CURRENT_DATE()
       AND (ACTIVE_TO IS NULL OR ACTIVE_TO >= CURRENT_DATE());

    SELECT
        COALESCE(COUNT_IF(TXN_AMOUNT > :v_old_threshold), 0),
        COALESCE(COUNT_IF(TXN_AMOUNT > :PROPOSED_THRESHOLD_INR), 0),
        COUNT(DISTINCT IFF(
            TXN_AMOUNT > :PROPOSED_THRESHOLD_INR,
            ACCOUNT_ID,
            NULL
        )),
        COUNT(DISTINCT IFF(
            TXN_AMOUNT > :PROPOSED_THRESHOLD_INR
            AND TXN_AMOUNT <= :v_old_threshold,
            ACCOUNT_ID,
            NULL
        ))
      INTO
        :v_old_alert_count,
        :v_new_alert_count,
        :v_accounts_alerted_new_rule,
        :v_newly_alerted_accounts
      FROM TRANSACTIONS
     WHERE CURRENCY_CODE = 'INR'
       AND TXN_TIMESTAMP >= :PERIOD_START_NTZ
       AND TXN_TIMESTAMP < :PERIOD_END_NTZ;

    v_alert_count_delta := v_new_alert_count - v_old_alert_count;
    v_percent_alert_change := IFF(
        v_old_alert_count = 0,
        NULL,
        (v_alert_count_delta * 100.0) / v_old_alert_count
    );
    v_run_id := UUID_STRING();

    INSERT INTO BACKTEST_RUNS (
        RUN_ID,
        RULE_ID,
        BASELINE_RULE_VERSION,
        OLD_THRESHOLD_INR,
        PROPOSED_THRESHOLD_INR,
        PERIOD_START_NTZ,
        PERIOD_END_NTZ,
        OLD_ALERT_COUNT,
        NEW_ALERT_COUNT,
        ALERT_COUNT_DELTA,
        PERCENT_ALERT_CHANGE,
        ACCOUNTS_ALERTED_NEW_RULE,
        NEWLY_ALERTED_ACCOUNTS,
        RUN_STATUS
    )
    VALUES (
        :v_run_id,
        'AML_THRESHOLD_10L',
        :v_rule_version,
        :v_old_threshold,
        :PROPOSED_THRESHOLD_INR,
        :PERIOD_START_NTZ,
        :PERIOD_END_NTZ,
        :v_old_alert_count,
        :v_new_alert_count,
        :v_alert_count_delta,
        :v_percent_alert_change,
        :v_accounts_alerted_new_rule,
        :v_newly_alerted_accounts,
        'SUCCESS'
    );

    RETURN OBJECT_CONSTRUCT_KEEP_NULL(
        'status', 'SUCCESS',
        'run_id', v_run_id,
        'rule_id', 'AML_THRESHOLD_10L',
        'baseline_rule_version', v_rule_version,
        'currency', 'INR',
        'old_threshold', v_old_threshold,
        'proposed_threshold', PROPOSED_THRESHOLD_INR,
        'period_start_inclusive', PERIOD_START_NTZ,
        'period_end_exclusive', PERIOD_END_NTZ,
        'old_alert_count', v_old_alert_count,
        'new_alert_count', v_new_alert_count,
        'alert_count_delta', v_alert_count_delta,
        'percentage_alert_change', v_percent_alert_change,
        'percentage_change_status', IFF(
            v_old_alert_count = 0,
            'UNDEFINED_ZERO_BASELINE',
            'DEFINED'
        ),
        'accounts_alerted_under_new_rule', v_accounts_alerted_new_rule,
        'newly_alerted_accounts', v_newly_alerted_accounts
    );
END;
$$;

-- Example: compare the active ₹10 lakh baseline with a proposed ₹5 lakh rule.
CALL RUN_THRESHOLD_BACKTEST(
    500000.00,
    '2026-07-01 00:00:00'::TIMESTAMP_NTZ,
    '2026-10-01 00:00:00'::TIMESTAMP_NTZ
);

-- The result row is also persisted for review and repeatable demos.
SELECT *
FROM BACKTEST_RUNS
ORDER BY CREATED_AT DESC
LIMIT 5;