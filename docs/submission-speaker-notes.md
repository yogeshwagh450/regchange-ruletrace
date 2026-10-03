# RegChange Submission: Speaker Notes and Validation

Reviewed on October 3, 2026 against the current 13-slide `RegChangeRuleTrace_Submission.pptx`, checked-in SQL, Streamlit source, deployment manifest, and README. This is a repository review, not a fresh Snowflake execution or deployment verification. Target delivery: approximately five minutes.

## Validation Findings

| Priority | Finding | Evidence and Required Action |
|---|---|---|
| High | Slide 7 incorrectly labels 47 accounts as newly alerted. | A local reproduction of the exact 10,000-row generator gives 132 baseline alerts, 200 proposed alerts, 50 baseline-alert accounts, 50 proposed-alert accounts, 47 accounts with transactions in the newly flagged amount band, and **0 truly new alerted accounts**. Fix the SQL using a proposed-account minus baseline-account comparison, rerun in Snowflake, and update the app, screenshot, slide, README and explainer together. Do not simply relabel a corrected result as 47. |
| High | Setup cannot reproduce Ask Analyst from the repo alone. | The app references `REGCHANGE_DB.REGCHANGE.REGCHANGE_SEMANTIC`; no Semantic View creation SQL is present among the checked-in implementation files. Export the actual deployed definition and grants. Verify the claimed 10 metrics and 13 dimensions against that definition. Create REVIEW_LOG before first app use; its DDL is currently in the README rather than the initialization script. |
| High | Policy evidence is not a persisted end-to-end audit chain. | The app holds policy input and extraction in UI/session state; no policy/extraction table or evidence ID linked to BACKTEST_RUNS is implemented. Describe the persisted audit trail as backtest-to-review, not circular-to-production-change. The displayed mapping does not validate an extracted rule identifier against the fixed AML control. |
| High | The remediation preview is not production-safe. | It retires the baseline immediately using CURRENT_DATE(), inserts the new rule with the replay end date as ACTIVE_FROM, and lacks an encompassing transaction. A future ACTIVE_FROM could leave no active baseline. Keep it preview-only; do not execute it during rehearsal. |
| Medium | Clone isolation is not concurrency-safe or retained for replay. | RUN_THRESHOLD_BACKTEST uses a shared TXN_BACKTEST_CLONE name and drops it after aggregation, with no exception cleanup. Concurrent runs can replace/drop each other's clone. The run stores metrics, not a durable snapshot reference. Use per-run isolation and record snapshot/lineage metadata before claiming reliable concurrent or historical replay. |
| Medium | Slides 2 and 12 do not provide a usable live app URL. | Slide 2 contains unfinished/combined link text; slide 12 says `Snowflake app: Snowflake`. Replace with the actual app URL from README and verify judge access. Retain the public GitHub URL as a separate hyperlink. |
| Medium | Some source slide text is unfinished. | Slides 10 and 11 contain fragments such as `SQL St`, `answerse`, and `IRDAI)ws`. These are actual stored strings, not just overflow. Restore intended wording from the authored source before upload. |
| Medium | Timing and architecture claims exceed available evidence. | Slide 12 claims under 60 seconds without a timed run record. Slide 10 says zero external dependencies although the app imports Streamlit and requests and calls Snowflake's Analyst REST API. Prefer `Snowflake-native services; no third-party data sources`. No claim that AI inference stays in one region is established by the repo. |
| Medium | README describes an earlier version. | README shows three tabs and lists Cortex extraction and clones as future work although the source has five tabs and clone replay. Update its architecture, setup order and limitations. The deployment YAML verifies declared configuration only, not deployed state. |
| Medium | Human verification is described more strongly than enforced. | Extraction writes threshold/date defaults after sidebar widgets have already rendered; there is no explicit confirmation gate. Test the next-rerun behavior with a different threshold, not only the default INR 500,000. Full numeric/date/JSON-shape validation and unrelated-policy rejection are not implemented. |
| Medium | Natural-language query governance needs careful wording. | Semantic View grounding helps define metrics, but the app directly executes returned SQL under its active session. It does not implement an independent SQL allowlist or read-only role restriction in source. Do not claim grounding alone guarantees safe execution. |
| Low | Git contains presentation artifacts needing review. | The current worktree has untracked presentation/template files and PowerPoint lock files, plus a tracked lock-file deletion and a modified checklist. Preserve user changes, exclude `~$*.pptx` lock files, and deliberately stage submission artifacts. No push was performed in this review. |

## Slide 1: Official Template Cover

**Say:**
Hello, I am Yogesh Wagh, presenting RegChange RuleTrace as a solo entry for Problem Statement 01: Risk, Fraud and Regulatory Intelligence Copilot. My focus is a specific compliance decision: understanding the impact of a proposed transaction-monitoring threshold change before a reviewer decides what to do.

**Evidence:** Cover fields match the selected project and challenge. The project uses Snowflake SQL and a Python Streamlit application.

**Presenter Check:** Confirm the saved cover matches your portal team details. Do not describe the prototype as a complete production compliance platform.

## Slide 2: RegChange RuleTrace

**Say:**
The product follows four ideas: trace the control, analyze the proposed change, validate the impact through replay, and govern the decision through human review. The demonstration uses fictional policy text and synthetic transactions. It is an engineering prototype, not legal interpretation or production AML advice.

**Evidence:** App caption labels policy and transactions fictional/synthetic; the source has extraction, replay and review paths.

**Presenter Check:** Repair the unfinished link text and add a clickable prototype URL. Verify access separately from your own authenticated Snowflake session.

## Slide 3: The Operational Decision

**Say:**
A lower threshold can increase the number of monitoring alerts even when the underlying transactions have not changed. Before implementing the change, a compliance team needs to know the workload impact, the affected control, and who reviewed the proposal. RegChange brings those questions into one reviewable workflow rather than treating policy extraction as the final answer.

**Evidence:** SQL compares baseline and proposed thresholds over the same filtered transaction snapshot; review records reference a run ID.

**Presenter Check:** Present the manual process as a motivating example, not a measured finding about all banks. The synthetic alerts do not establish fraud or suspicious activity.

## Slide 4: Five Stages

**Say:**
The workflow starts with Cortex proposing structured fields from the fictional circular. The demonstration targets the existing AML_THRESHOLD_10L control. A SQL procedure then evaluates the old and proposed thresholds, reports the impact, and stores the run. Finally, a reviewer records approval or rejection with a comment. Approval is a recorded decision, not automatic rule promotion.

**Evidence:** The app exposes five tabs; RUN_THRESHOLD_BACKTEST writes BACKTEST_RUNS; Submit Review writes REVIEW_LOG.

**Presenter Check:** Control selection is fixed to one AML rule, not general automated obligation-to-control discovery. Human review is expected but an extraction confirmation gate is not enforced. Confirm sidebar updates during rehearsal.

## Slide 5: Architecture

**Say:**
The UI is Streamlit in Snowflake. The deployment manifest targets REGCHANGE_DB.REGCHANGE.REGCHANGE_APP, with COMPUTE_WH for queries and a container runtime. SQL tables hold synthetic transactions, versioned control metadata and backtest results. The app also writes a review log and calls Cortex for extraction and summaries, plus Cortex Analyst for natural-language questions.

**Evidence:** streamlit/snowflake.yml declares the app, warehouse, container runtime and compute pool. The SQL and app define the stated interactions.

**Presenter Check:** This verifies declared configuration, not live deployment. Semantic View setup and grants are missing from the reproducible repo setup. Do not equate platform-native services with zero software dependencies or guaranteed region-local inference.

## Slide 6: Policy Extraction

**Say:**
The fictional sample proposes lowering the threshold from INR one million to INR five hundred thousand. Cortex is asked for a rule name, parameter, old and new thresholds, currency, effective date and summary. The proposed fields are displayed for review. The reviewer must check them against the source text; an LLM response is not authoritative regulation.

**Evidence:** SAMPLE_POLICY_TEXT and the extraction prompt enumerate these fields. Session state receives selected extracted values.

**Presenter Check:** There is no persisted source/evidence record or comprehensive schema-validation gate. Do not claim support for arbitrary regulators or reliable rejection of every ambiguous circular. The backtest covers all INR transaction types, not only cash.

## Slide 7: Impact Results

**Say:**
For the unmodified synthetic dataset and July-to-October replay window, the checked-in logic produces 132 baseline alerts and 200 proposed alerts. That is 68 additional alerts, approximately a 51.52 percent increase. Fifty accounts have proposed-rule alerts. An important distinction is that more alerted transactions do not necessarily mean new alerted accounts: the local account-set comparison shows the same fifty accounts already had baseline alerts.

**Evidence:** A fresh local reproduction of the generator and amount predicates confirms these values. It also confirms 47 accounts with transactions in the newly flagged amount band, but zero new accounts relative to the baseline-alert set.

**Presenter Check:** BLOCKER: the current slide and app call 47 `newly alerted accounts`; correct and rerun before presenting. Local arithmetic is not a fresh Snowflake result. Do not convert alert counts into hiring recommendations without explicit assumptions; the summary prompt's 30 alerts per analyst per quarter is illustrative.

## Slide 8: Human Review

**Say:**
A reviewer selects a successful run, chooses approved or rejected, and adds a comment. The app stores the current Snowflake user, decision, run ID and review time. The remediation SQL is displayed separately as a preview. Recording approval does not execute the SQL or change the active control.

**Evidence:** The Submit Review INSERT uses CURRENT_USER() and CURRENT_TIMESTAMP(); remediation is rendered through st.code, not executed by an approval button.

**Presenter Check:** Do not execute the migration preview. It needs effective-date and transaction fixes. Persisted traceability begins at the backtest run; source policy evidence and its relationship to the run are not stored.

## Slide 9: Ask Analyst

**Say:**
The Ask Analyst tab lets a reviewer ask questions about the modeled data in plain language. The app sends the question and the configured Semantic View name to Cortex Analyst. When SQL is returned, the app displays it and attempts to show query results. This complements deterministic backtesting; it does not replace the procedure that calculates impact.

**Evidence:** The source posts to /api/v2/cortex/analyst/message with REGCHANGE_SEMANTIC and displays returned text, SQL, results or suggestions.

**Presenter Check:** Verify a live answer before rehearsal. The actual Semantic View definition is absent from the repo, so metric counts and relationships are not independently verified here. Describe grounding as assistance, not a guarantee of correct or safe SQL.

## Slide 10: Differentiation

**Say:**
The distinction is connecting AI-assisted interpretation to explicit measurement and a recorded human decision. The alert calculation is deterministic, while Cortex supports interpretation and summarization. Versioned control metadata, persisted backtest runs and review records make the prototype more useful than an isolated policy-summary chatbot.

**Evidence:** Cortex calls, typed SQL comparisons, BASELINE_RULE_VERSION in BACKTEST_RUNS and REVIEW_LOG inserts are present in source.

**Presenter Check:** Restore truncated service text. Replace zero external dependencies with a narrower claim about Snowflake-native services and synthetic data. Verify Semantic View counts before quoting them. Do not describe session-only policy text as a complete persisted evidence chain.

## Slide 11: Scope and Roadmap

**Say:**
Today the prototype covers one fictional AML threshold scenario using ten thousand deterministic synthetic transactions. It provides extraction, replay, history, review and an Analyst integration path. Future work includes validated support for more rule types, persistent policy evidence, continuous data ingestion and quality checks, and stronger concurrency and promotion controls. These are roadmap items, not completed production capabilities.

**Evidence:** The seed generator uses ROWCOUNT 10000 and the baseline selection is hard-coded to AML_THRESHOLD_10L. No continuous ingestion, Dynamic Table or DMF setup is checked in.

**Presenter Check:** Repair the slide's unfinished strings. No external datasets are used; the app does use a Snowflake REST API. Zero-copy clone replay is already implemented in the SQL and should not be listed as entirely future work, although hardening remains necessary.

## Slide 12: Closing Message

**Say:**
RegChange RuleTrace demonstrates how a proposed threshold change can become a measured, reviewable decision. AI proposes the fields, deterministic replay quantifies the alert impact, and a human records the outcome. The next step is strengthening the evidence and validation controls so the workflow can be extended beyond this synthetic demonstration.

**Evidence:** Extraction, SQL replay and review logging are implemented; production promotion remains separate.

**Presenter Check:** Replace the unverified under-60-seconds headline with an untimed claim unless a repeatable timed run supports it. Replace `Snowflake app: Snowflake` with the actual prototype link.

## Slide 13: Template Closing

**Say:**
Thank you. I am happy to walk through the replay logic, the human-review boundary, or the roadmap for stronger data and governance controls.

**Evidence:** Official template closing retained; no additional product claims are made.

**Presenter Check:** Stop here or move to a rehearsed live demonstration. Do not run remediation SQL during questions.

## Final Rehearsal Checks

1. Correct the newly-alerted metric and related visuals before upload.
2. Ensure the app URL works under the organizer's accepted judge-access arrangement.
3. Export Semantic View setup and grants; make setup order reproducible.
4. Restore unfinished slide strings and qualify unsupported timing/dependency claims.
5. Rehearse extraction with a non-default valid threshold; verify the parameters actually used by the stored procedure.
6. Confirm an approval records REVIEW_LOG without changing the active baseline.
7. Avoid presenting generated staffing assumptions as business measurements.
8. Review and intentionally stage the deck and notes; do not publish PowerPoint lock files.