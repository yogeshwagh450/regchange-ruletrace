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
- Implementation decisions: [engineering log](../../docs/challenges-and-decisions.md)
- Phase 1 worksheet: [initialization and backtest SQL](../../sql/phase1/01_initialize_regchange.sql)
- The local Git repository is on `main`, with `origin` set to `https://github.com/yogeshwagh450/regchange-ruletrace.git`. Remote and local commit `6dad93e` were verified on 2026-10-03 before subsequent local presentation/documentation corrections. Check current status before committing; do not assume later edits are published.
- Phase 1 SQL creates schema `REGCHANGE`, 10,000 deterministic synthetic INR transactions, the active `AML_THRESHOLD_10L` baseline at INR 1,000,000, and `RUN_THRESHOLD_BACKTEST` with persisted run metrics.
- The unchanged synthetic fixture gives 132 baseline alerts, 200 proposed alerts at INR 500,000, 68 additional alerts (51.5152%), 50 proposed-alert accounts and 47 accounts with transactions in the newly monitored amount band. These 47 are not first-time accounts; local account-set comparison gives zero first-time accounts. The legacy SQL field name remains NEWLY_ALERTED_ACCOUNTS.
- The user reports a deployed five-tab app and prior successful tests; DDL_DML_REFERENCE records earlier validation. This editing session did not execute Snowflake or revalidate deployment. Source now contains Semantic View setup, clone replay and a corrected summary prompt. Verify deployed behavior before recording, rather than rebuilding or reseeding.

## Journey Handoff

- This is a solo hackathon project. The personal public GitHub repository is `https://github.com/yogeshwagh450/regchange-ruletrace`; the submission challenge is **Risk, Fraud and Regulatory Intelligence Copilot**.
- The portal requires repository/app links, a 3-5 minute demo video showing CoCo CLI execution, an MVP brief and a PDF deck no larger than 5 MB. The app URL is in README; judge access must be checked separately from the user's authenticated session.
- Current priority: deploy the focused summary-prompt correction if needed, verify one sequential workflow, record the video, export/submit the final PDF and confirm portal completeness. Do not add new features, run expensive exploratory AI calls or execute the remediation preview.
- The user has enabled Snowflake CoCo in this workspace and wants to continue the project there. CoCo usage is token-billed for an existing Snowflake account; SQL/warehouse compute is billed separately. Be economical with prompts and warehouse runtime, and do not claim CoCo saves trial credits.
- Never read, print, or ask the user to share passwords, tokens, or other secrets from `C:\Users\YogeshWagh\.snowflake\connections.toml`. Do not include account-specific connection details in public project files.

## Constraints and Engineering Direction

- Center the work on Snowflake data engineering: schemas, metadata, lineage, deterministic replay, governance, quality, and auditability. No custom model training.
- Prefer Snowflake-native SQL, Snowpark Python, Cortex, Dynamic Tables, DMFs, and Streamlit in Snowflake when they serve the demonstrated workflow.
- Verify current Snowflake product/API syntax in official documentation before adding features. Avoid unverified packages, third-party vector databases, and executing arbitrary LLM-generated SQL.
- Keep all policy and transaction data synthetic or appropriately licensed. Label illustrative circular text as fictional; never imply demo outputs are production AML advice.
- Freeze feature scope for submission. Cortex extraction, clone replay and Analyst are in source; ingestion/CDC, persisted policy evidence and production promotion hardening remain limitations, not completed capabilities.
- The published prototype submission deadline was October 4, 2026, 11:59 PM IST. Treat the date as urgent and verify the current portal/event terms if schedule or requirements matter.
- Use the user's Snowflake CoCo/Cortex Code CLI workflow where required, but do not spend effort regenerating large amounts of code when a focused local or worksheet check will answer the question.

## How to Continue

Read README and the relevant implementation before editing. Continue with final submission preparation, not project initialization. In a new CoCo session use: `Read @.github/prompts/resume-regchange.prompt.md and README. Help verify one sequential demo workflow and prepare submission. Do not reseed, redeploy, change controls, run additional queries or push without explicit approval.` Report local checks separately from actual account execution. Prefer the published README and presentation over ignored local planning documents.