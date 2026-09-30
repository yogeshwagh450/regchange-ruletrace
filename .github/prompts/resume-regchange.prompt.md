---
name: resume-regchange
description: "Resume RegChange hackathon development from the current project state"
argument-hint: "Optional: describe the next RegChange task"
agent: "agent"
---

Resume work on **RegChange: Regulatory Change Impact & Control Intelligence Agent** in this workspace. This is the selected solo project for Snowflake CoCo CLI Hackathon 2026, Problem Statement 01: Risk, Fraud and Regulatory Intelligence Copilot. Do not return to or modify the separate IHUB pipeline repository unless explicitly asked.

## Project Goal

Demonstrate an auditable regulatory-change workflow for a fictional AML transaction threshold update: preserve policy evidence, map the change to governed control metadata, replay a fixed transaction history with old and proposed thresholds, quantify alert/customer impact, and prepare an approval-ready remediation preview. LLM output is a proposal; a human approves any control promotion. This must solve a concrete banking/NBFC workflow, not be a generic regulatory chatbot.

## Current Workspace and State

- Workspace root: `C:\Users\YogeshWagh\Projects\snowflake-coco-project`
- Project overview and Phase 1 run steps: [README](../../README.md)
- Hackathon fit, MVP, and architecture decision: [decision brief](../../docs/decision-brief.md)
- Phase 1 worksheet: [initialization and backtest SQL](../../sql/phase1/01_initialize_regchange.sql)
- The local Git repository is on `main`, with `origin` set to `https://github.com/yogeshwagh450/regchange-ruletrace.git`. Commit `e26a115` (`Initialize RegChange RuleTrace`) was verified on both `main` and `origin/main` on 2026-09-30. The working tree had an untracked `.github/` directory at that check; do not assume this prompt is published.
- Phase 1 SQL creates schema `REGCHANGE`, 10,000 deterministic synthetic INR transactions, the active `AML_THRESHOLD_10L` baseline at INR 1,000,000, and `RUN_THRESHOLD_BACKTEST` with persisted run metrics.
- A local arithmetic sanity check predicts 132 baseline alerts, 200 proposed alerts at INR 500,000, 68 additional alerts (51.5152%), 50 accounts alerted under the proposed rule, and 47 newly alerted accounts.
- The SQL has not yet been executed or compiled in the user's Snowflake trial. The user has opened Snowsight for the trial and believes the VS Code Snowflake extension is now connected, but that connection has not been independently verified. First confirm the active account/session, role, database, and warehouse, then run the worksheet and compare results. Do not claim successful execution until confirmed.

## Journey Handoff

- This is a solo hackathon project. The personal public GitHub repository is `https://github.com/yogeshwagh450/regchange-ruletrace`; the submission challenge is **Risk, Fraud and Regulatory Intelligence Copilot**.
- The submission form requires both the GitHub repository URL and a separate **Prototype Deployed Link**. No prototype has been built or deployed yet; do not put the repository URL in both fields or claim a deployment.
- The immediate blocker is validating `sql/phase1/01_initialize_regchange.sql` in Snowflake. Once it succeeds, build the smallest usable demo, preferably a Snowflake Streamlit app, and deploy it to obtain the prototype link.
- The user has enabled Snowflake CoCo in this workspace and wants to continue the project there. CoCo usage is token-billed for an existing Snowflake account; SQL/warehouse compute is billed separately. Be economical with prompts and warehouse runtime, and do not claim CoCo saves trial credits.
- Never read, print, or ask the user to share passwords, tokens, or other secrets from `C:\Users\YogeshWagh\.snowflake\connections.toml`. Do not include account-specific connection details in public project files.

## Constraints and Engineering Direction

- Center the work on Snowflake data engineering: schemas, metadata, lineage, deterministic replay, governance, quality, and auditability. No custom model training.
- Prefer Snowflake-native SQL, Snowpark Python, Cortex, Dynamic Tables, DMFs, and Streamlit in Snowflake when they serve the demonstrated workflow.
- Verify current Snowflake product/API syntax in official documentation before adding features. Avoid unverified packages, third-party vector databases, and executing arbitrary LLM-generated SQL.
- Keep all policy and transaction data synthetic or appropriately licensed. Label illustrative circular text as fictional; never imply demo outputs are production AML advice.
- Keep the scope solo-buildable and changes small. Do not add Cortex parsing, clones, DMFs, Dynamic Tables, UI, or deployment claims before the core Phase 1 worksheet is validated.
- The published prototype submission deadline was October 4, 2026, 11:59 PM IST. Treat the date as urgent and verify the current portal/event terms if schedule or requirements matter.
- Use the user's Snowflake CoCo/Cortex Code CLI workflow where required, but do not spend effort regenerating large amounts of code when a focused local or worksheet check will answer the question.

## How to Continue

Read the README, decision brief, and Phase 1 SQL before changing code. Pick up from the next unverified step: verify the Snowflake extension session and run the Phase 1 worksheet, resolve any compile/runtime issues in that same slice, and compare the output to the expected metrics above. Then report what was actually tested and proceed to a minimal deployed prototype. If using CoCo in a new session, start with: `Read @.github/prompts/resume-regchange.prompt.md and the linked project files. Continue from the next unverified step; first verify the Snowflake connection, then validate the Phase 1 worksheet. Keep all actions within this repository and ask before any destructive or externally visible action.` If the user supplies a specific next task, prioritize it while preserving these project constraints.