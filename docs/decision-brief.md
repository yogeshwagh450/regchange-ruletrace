# RegChange Hackathon Decision Brief

**Status:** RegChange selected; Phase 1 implementation underway  
**Decision:** Conditional go for Problem Statement 01, subject to a sharply scoped prototype and a confirmed CoCo CLI workflow.

## Executive View

RegChange is a strong fit for the Risk, Fraud and Regulatory Intelligence Copilot challenge. The useful distinction is not simply asking an LLM to summarize a circular: it is connecting a proposed policy change to governed control metadata, replaying the same historical data under old and proposed parameters, and producing evidence that a compliance or risk owner can review.

That makes the concept especially credible for a solo Data Engineer. Its core value is data architecture and execution: versioned rule metadata, lineage to the affected data, reproducible backtesting, quality checks, and an auditable approval artifact. The main risk is scope. Parsing many regulators' documents, discovering all enterprise dependencies, creating transient clones, and generating production migrations would be too much to build and verify in the submission window.

**Recommendation:** Proceed with a single AML threshold-change scenario, synthetic transactions, one Snowflake-native end-to-end workflow, and explicit human approval. Keep clone orchestration and broad multi-regulator coverage as future roadmap items, not MVP promises.

## Hackathon Fit and Timing

The event page describes Problem Statement 01 as surfacing risk/fraud signals and producing audit-ready regulatory outputs from natural-language questions. Its published rubric is Real-World Relevance (30%), Technical Execution (40%), and Solution Completeness (30%). Individual participation is allowed; teams may have one to four members.

The official terms add important implementation constraints: the entry should respond to a designated problem statement and include use of Cortex Code CLI; Snowflake use is required; Python, Java, and/or Scala are listed; and Snowpark, Worksheets, Streamlit, and/or Snowflake Marketplace receive special consideration. The prototype submission period is September 13 through October 4, 2026, 11:59 PM IST. The terms state that a trial account is provided with USD 400 in credits. Confirm the current submission portal instructions and the exact CLI workflow before relying on any detail, since event materials may change.

The project is maintained separately from the earlier IHUB-style pipeline portfolio so that its hackathon workflow, documentation, and demo artifacts have a focused home. Reuse relevant Snowflake experience, but present a coherent product workflow rather than a collection of pipeline examples.

## Proposed MVP Story

**Scenario:** A fictional regulator-issued policy update lowers a transaction-monitoring threshold from ₹10 lakh to ₹5 lakh. The demo uses synthetic data and clearly labels the policy text as illustrative, not an actual legal circular.

1. Submit the policy text and ask what changed. Cortex extracts a small, typed proposal: rule identifier, parameter, old/new thresholds, effective date if present, and the supporting text excerpt. Save the source and extraction result for audit. Require a human to confirm the extracted change.
2. Resolve the approved proposal against a versioned `REGULATORY_CONTROLS` record. Show the mapped control and affected data object(s), with the relationship stored as metadata rather than inferred from free-form SQL alone.
3. Run old and proposed rule versions over the same fixed historical transaction snapshot. Show old/new alert counts, count and percentage delta, and distinct accounts alerted under the proposed rule. Define the percentage denominator as the old alert count, with an explicit zero-baseline result.
4. Produce a review package containing the proposal, evidence excerpt, affected-control mapping, backtest metrics, DQ results, generated migration preview, and approval status. Do not automatically apply a production change.

The punchline for the demo is a quantified decision: “This proposed change adds N alerts and affects M accounts on the selected historical period; here is the control, evidence, and migration preview for approval.”

## Architecture Direction

- **Input and evidence:** a staged, versioned policy excerpt plus an extraction record. Use synthetic or properly licensed materials; list all datasets in the submission.
- **Control catalog:** typed fields for rule name, parameter, numeric threshold, status, effective dates, owner, source/evidence reference, and version. Avoid treating `SQL_PREDICATE` as executable arbitrary text.
- **Backtest:** parameterized Snowflake SQL or Snowpark Python evaluates both versions against the same immutable time-bounded input. Persist run ID, source period, rule versions, results, and timestamp.
- **Governance:** validate the input data and result shape; record human approval separately from LLM output; make every generated DDL a preview until approved.
- **Experience:** use a small Streamlit in Snowflake surface for the change review and results, with Snowflake worksheets/Snowpark for execution. Keep the workflow operable and explainable from the required CoCo/Cortex Code CLI development workflow; verify what the judges expect to see for CLI usage.
- **Optional later:** Dynamic Tables for continuously maintained impact views, DMFs for table-level quality monitoring, and transient clones where the account permissions, credit budget, and demo reliability justify them. These are supporting options, not requirements for proving the core value.

## Accuracy and Safety Notes

- ₹10 lakh is **₹1,000,000**, and ₹5 lakh is **₹500,000**. Keep the currency unit explicit in the UI and data model; do not encode ₹10 lakh as ₹100,000.
- LLM output is a proposal, not a policy decision. Validate required fields and numeric values, retain the source excerpt, and require a reviewer before a rule version is promoted.
- Prefer a constrained operator/column/threshold representation over executing model-generated SQL. Generate a parameterized, reviewable SQL preview from validated metadata.
- Define the backtest period and comparison grain. “Unique accounts impacted” should mean distinct accounts with an alert under the proposed rule; also consider showing newly alerted accounts separately so the delta is not confused with the total.
- Do not claim enterprise-wide lineage discovery unless the prototype can demonstrate it. Show explicit metadata mapping for the modeled pipeline and make its limits visible.
- Use a fixed data snapshot so repeated demos produce stable results. Report the old alert count, new alert count, alert-count increase, percentage increase, and proposed-rule distinct-account count with unambiguous definitions.

## Differentiation and Alternatives

Within Problem Statement 01, a focused regulatory-change lifecycle is a more defensible solo build than a broad fraud/risk chatbot: it has a concrete user, a before/after outcome, a natural audit trail, and a compact live demo. Its distinguishing feature should be the evidence-to-control-to-backtest-to-approval chain, not the use of Cortex by itself.

The event publishes five challenge categories. Compared against your data-engineering background and solo build constraints:

| Problem statement | Fit and opportunity | Main solo-build risk |
|---|---|---|
| **01 Risk, Fraud and Regulatory Intelligence** | Strong banking/NBFC fit; RegChange can demonstrate lineage, governed rule metadata, replay, and an auditable impact decision. | Regulatory parsing and enterprise-wide impact discovery can balloon; keep it to one threshold change and explicit mappings. |
| **02 Customer 360 and Next Best Action** | Relevant to lenders and insurers; a Snowflake-native unified view is feasible. | Broad structured/unstructured integration plus recommendation quality can feel generic and needs credible business outcomes. |
| **03 Predictive Maintenance and OEE** | Clear operational value from joining OT sensor, ERP, and maintenance data. | Requires time-series/industrial context and convincing failure prediction; weaker match to your stated strengths and risks becoming an ML project. |
| **04 Patient/Member 360 and Clinical or Regulatory Document Copilot** | Strong evidence-grounded document workflow; the page explicitly requires synthetic or de-identified data. | Crowded copilot pattern, sensitive domain, and less natural emphasis on pipeline/control backtesting than RegChange. |
| **05 Supply Chain Ontology and Governed Conversational Analytics** | Closest alternative for your data-engineering profile: canonical entities, semantic views, governance, and consistent metrics map directly to Snowflake modeling. | Needs an unmistakable demo proving that shared definitions resolve conflicting answers; otherwise it can look like a generic text-to-SQL assistant. |

**Recommendation:** Stay with RegChange unless the regulatory use case is not personally compelling or Cortex/CLI access blocks the workflow. It is sufficiently differentiated for a hackathon when the demo proves a quantified impact and a safe approval path; the concept alone is not a guarantee of uniqueness. Problem Statement 05 is the best fallback on role fit, but its differentiation is harder to show in a short demo. Since the terms allow only one entry per participant, make the final choice after a short prototype-risk check rather than splitting effort across both.

## Decision Gates Before Building

1. Confirm registration/eligibility and the submission portal requirements; the published submission deadline is October 4, 2026, 11:59 PM IST, only a few days after the current date.
2. Confirm access to the Snowflake trial, Cortex capability/model availability, required roles, and the CoCo/Cortex Code CLI workflow. The terms use “Cortex Code CLI,” while the event is branded “CoCo CLI”; establish the exact judge-facing expectation.
3. Freeze the demo to one synthetic threshold change and one input dataset. Make the entire happy path runnable twice with repeatable results.
4. Reserve time for the required source-code repository, documentation, presentation deck, and a live-demo rehearsal; these are explicit submission/final requirements in the terms.

## Sources

- [Hackathon event page](https://hack2skill.com/event/cococlihack-gccedition/) — problem statement, published scoring rubric, event dates, workshops, and team format.
- [Official terms and conditions](https://docs.google.com/document/d/e/2PACX-1vTrXSK6v7T9tP3-Ab8LuFCDOuuW90debariK5I3PsIF0TrQ4A6q5RSC2B2wA4WM7Qif16AgynvdA4XL/pub) — submission period, entry requirements, trial credits, technology criteria, and presentation/demo expectations.
- Project setup and Phase 1 run guide: [README.md](../README.md).