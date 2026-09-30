# RegChange

RegChange is the selected project for the Snowflake CoCo CLI Hackathon, Problem Statement 01. It will demonstrate a reviewable regulatory-change workflow: policy evidence, mapped control metadata, historical replay, quantified impact, and approval-ready remediation.

## Phase 1: Synthetic Data and Backtest

Run [`sql/phase1/01_initialize_regchange.sql`](sql/phase1/01_initialize_regchange.sql) in a Snowflake worksheet while connected to the database where you want the `REGCHANGE` schema created. The active role needs permission to create a schema, tables, and procedures; select an available small warehouse before executing the backtest call.

The script is designed to be re-runnable:

- It creates 10,000 deterministic synthetic transactions dated in a fixed 90-day window beginning July 1, 2026.
- It seeds the active `AML_THRESHOLD_10L` rule at INR 1,000,000 (₹10 lakh). The `SQL_PREDICATE` field is descriptive metadata and is never dynamically executed.
- It creates `RUN_THRESHOLD_BACKTEST`, which compares the current active baseline with a proposed threshold for a half-open timestamp range (`start <= TXN_TIMESTAMP < end`).
- The sample call tests INR 500,000 (₹5 lakh) for July 1 through October 1, 2026. Each successful run is returned as a `VARIANT` and saved to `BACKTEST_RUNS`.

Metrics distinguish total accounts alerted under the proposed rule from accounts newly alerted relative to the baseline. Percentage alert change is `(new alert count - old alert count) / old alert count * 100`; it is `NULL` when the old count is zero, with an explicit status in the returned object.

For the unmodified generated dataset and sample replay window, the expected results are 132 baseline alerts, 200 proposed alerts, a delta of 68 alerts (51.5152%), 50 accounts alerted under the proposed rule, and 47 newly alerted accounts. Treat these as a quick smoke-test target; changing source data, the replay window, or the baseline will change the figures.

All values are synthetic and for demonstration only. This phase does not parse real regulations, call Cortex, apply a control change, or represent production AML advice. No third-party Python packages are needed for Phase 1.

## Resume in Copilot

In a new Copilot Chat opened on this workspace, run `/resume-regchange` to restore the project context and continue from the next unverified step. The prompt is stored at [`.github/prompts/resume-regchange.prompt.md`](.github/prompts/resume-regchange.prompt.md).