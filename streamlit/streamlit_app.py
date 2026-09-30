import streamlit as st
import json

st.set_page_config(
    page_title="RegChange: AML Threshold Impact",
    page_icon="⚖️",
    layout="wide",
)

conn = st.connection("snowflake")
session = conn.session()
session.use_database("REGCHANGE_DB")
session.use_schema("REGCHANGE")

# ── Session state defaults ──────────────────────────────────────────────────
if "extracted_threshold" not in st.session_state:
    st.session_state.extracted_threshold = None
if "extracted_date" not in st.session_state:
    st.session_state.extracted_date = None
if "last_backtest" not in st.session_state:
    st.session_state.last_backtest = None

# ── Header ──────────────────────────────────────────────────────────────────
st.title("RegChange — Regulatory Change Impact & Control Intelligence")
st.caption(
    "All policy text, transactions and thresholds shown here are **synthetic / fictional** "
    "and for hackathon demonstration only. Nothing on this page constitutes production AML advice."
)

# ── Sidebar: active rule & backtest parameters ──────────────────────────────
with st.sidebar:
    st.header("Active Baseline Rule")
    rule_df = conn.query(
        """
        SELECT RULE_ID, RULE_NAME, THRESHOLD_VALUE, CURRENCY_CODE,
               STATUS, ACTIVE_FROM, RULE_VERSION
          FROM REGCHANGE_DB.REGCHANGE.REGULATORY_CONTROLS
         WHERE RULE_ID = 'AML_THRESHOLD_10L'
           AND STATUS = 'ACTIVE'
           AND ACTIVE_FROM <= CURRENT_DATE()
           AND (ACTIVE_TO IS NULL OR ACTIVE_TO >= CURRENT_DATE())
        """,
        ttl=300,
    )
    if rule_df.empty:
        st.error("No active AML_THRESHOLD_10L rule found.")
        st.stop()

    rule = rule_df.iloc[0]
    st.metric("Current Threshold (INR)", f"₹{rule['THRESHOLD_VALUE']:,.0f}")
    st.caption(f"Rule: {rule['RULE_ID']} v{rule['RULE_VERSION']}")
    st.caption(f"Active from: {rule['ACTIVE_FROM']}")

    st.divider()
    st.header("Backtest Parameters")

    # IMP-1: If Cortex extracted a threshold, use it as default
    default_threshold = st.session_state.extracted_threshold or 500_000
    if st.session_state.extracted_threshold:
        st.success(f"Auto-filled from Cortex extraction")

    proposed = st.number_input(
        "Proposed threshold (INR)",
        min_value=50_000,
        max_value=5_000_000,
        value=int(default_threshold),
        step=50_000,
        format="%d",
    )
    period_start = st.date_input("Period start", value="2026-07-01")
    period_end = st.date_input(
        "Period end",
        value=st.session_state.extracted_date or "2026-10-01",
    )

# ── Sample policy text for demo ─────────────────────────────────────────────
SAMPLE_POLICY_TEXT = """FICTIONAL REGULATORY CIRCULAR — FOR DEMONSTRATION ONLY

Circular No. AML/2026-07/DEMO
Date: July 15, 2026
Subject: Revision of Threshold for Reporting of Cash and Suspicious Transactions

In exercise of powers conferred under the Prevention of Money Laundering Act, the threshold \
for reporting high-value transactions under the AML framework is hereby revised.

Current threshold: INR 10,00,000 (Rupees Ten Lakh)
Revised threshold: INR 5,00,000 (Rupees Five Lakh)
Effective date: October 1, 2026

All regulated entities shall update their transaction monitoring systems to flag transactions \
exceeding INR 5,00,000 with effect from the above date. Entities are advised to assess \
operational impact and ensure adequate resources for the expected increase in alert volumes.

This circular is purely fictional and created for hackathon demonstration purposes."""

# ── Main area: tabs ─────────────────────────────────────────────────────────
tab_extract, tab_backtest, tab_history, tab_approve, tab_analyst = st.tabs(
    ["Policy Extraction", "Run Backtest", "Run History", "Review & Approve", "Ask Analyst"]
)

# ── Tab 0: Cortex Policy Extraction ─────────────────────────────────────────
with tab_extract:
    st.subheader("AI-Powered Policy Change Extraction")
    st.markdown(
        "Paste a regulatory circular below. Snowflake Cortex extracts the structured "
        "change proposal (rule, thresholds, effective date) for review before backtesting."
    )

    policy_text = st.text_area(
        "Policy text (fictional)",
        value=SAMPLE_POLICY_TEXT,
        height=250,
    )

    if st.button("Extract with Cortex", type="primary", use_container_width=True):
        if not policy_text.strip():
            st.warning("Please enter policy text.")
        else:
            with st.spinner("Calling Snowflake Cortex LLM..."):
                safe_text = policy_text.replace("'", "''").replace("\\", "\\\\")
                prompt = f"""Extract the following fields from this regulatory policy text as JSON only, no other text:
- rule_name: short name for the rule
- parameter: what is being changed
- old_threshold: current threshold as a number
- new_threshold: revised threshold as a number
- currency: currency code (e.g. INR)
- effective_date: when the change takes effect (YYYY-MM-DD or null)
- summary: one sentence summary of the change

Policy text:
{safe_text}"""
                safe_prompt = prompt.replace("'", "''")
                rows = session.sql(
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{safe_prompt}') AS result"
                ).collect()
                raw_result = rows[0][0]

            st.subheader("Cortex Extraction Result")

            try:
                cleaned = raw_result.strip()
                if "```" in cleaned:
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                    cleaned = cleaned.strip()
                extracted = json.loads(cleaned)
                if isinstance(extracted, list) and len(extracted) > 0:
                    extracted = extracted[0]

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Extracted Fields**")
                    st.json(extracted)
                with col2:
                    st.markdown("**Mapped to Control**")
                    st.info(
                        f"**Rule:** {extracted.get('rule_name', 'N/A')}\n\n"
                        f"**Parameter:** {extracted.get('parameter', 'N/A')}\n\n"
                        f"**Current:** {extracted.get('currency', '')} "
                        f"{extracted.get('old_threshold', 'N/A'):,}\n\n"
                        f"**Proposed:** {extracted.get('currency', '')} "
                        f"{extracted.get('new_threshold', 'N/A'):,}\n\n"
                        f"**Effective:** {extracted.get('effective_date', 'N/A')}"
                    )

                # IMP-1: Store extracted values to auto-populate sidebar
                new_thresh = extracted.get("new_threshold")
                eff_date = extracted.get("effective_date")
                if new_thresh and isinstance(new_thresh, (int, float)) and new_thresh > 0:
                    st.session_state.extracted_threshold = int(new_thresh)
                if eff_date and eff_date != "null":
                    st.session_state.extracted_date = eff_date

                st.divider()
                st.success(
                    "Extracted values have been applied to the **Backtest Parameters** "
                    "in the sidebar. Review them, then switch to the **Run Backtest** tab."
                )
                st.caption(
                    "This extraction is an LLM proposal — a human must confirm before "
                    "the values are used for backtesting or control updates."
                )
            except (json.JSONDecodeError, ValueError):
                st.markdown("**Raw LLM response** (could not parse structured JSON):")
                st.code(raw_result)
                st.caption("Review the output manually and enter values in the sidebar.")

# ── Tab 1: Run Backtest ─────────────────────────────────────────────────────
with tab_backtest:
    st.subheader("Threshold Change Impact Analysis")
    col_old, col_arrow, col_new = st.columns([2, 1, 2])
    with col_old:
        st.markdown(f"**Current threshold:** ₹{rule['THRESHOLD_VALUE']:,.0f}")
    with col_arrow:
        st.markdown("<h2 style='text-align:center'>→</h2>", unsafe_allow_html=True)
    with col_new:
        st.markdown(f"**Proposed threshold:** ₹{proposed:,.0f}")

    if st.button("Run Backtest", type="primary", use_container_width=True):
        with st.spinner("Running threshold backtest..."):
            rows = session.sql(
                f"""
                CALL REGCHANGE_DB.REGCHANGE.RUN_THRESHOLD_BACKTEST(
                    {proposed}::NUMBER(18,2),
                    '{period_start} 00:00:00'::TIMESTAMP_NTZ,
                    '{period_end} 00:00:00'::TIMESTAMP_NTZ
                )
                """
            ).collect()
            raw = rows[0][0]
            r = json.loads(raw) if isinstance(raw, str) else raw

        if r.get("status") == "ERROR":
            st.error(r.get("message", "Unknown error"))
        else:
            st.session_state.last_backtest = r
            st.success(f"Backtest complete — Run ID: `{r['run_id']}`")

            m1, m2, m3 = st.columns(3)
            m1.metric("Baseline Alerts", f"{r['old_alert_count']:,}")
            m2.metric(
                "Proposed Alerts",
                f"{r['new_alert_count']:,}",
                delta=f"+{r['alert_count_delta']:,}",
                delta_color="inverse",
            )
            pct = r.get("percentage_alert_change")
            pct_str = f"{pct:.2f}%" if pct is not None else "N/A (zero baseline)"
            m3.metric("Alert Increase", pct_str)

            m4, m5, m6 = st.columns(3)
            m4.metric("Accounts Alerted (new rule)", f"{r['accounts_alerted_under_new_rule']:,}")
            m5.metric("Newly Alerted Accounts", f"{r['newly_alerted_accounts']:,}")
            m6.metric(
                "Replay Period",
                f"{str(r['period_start_inclusive'])[:10]} to {str(r['period_end_exclusive'])[:10]}",
            )

            # ── IMP-2: Executive Summary ────────────────────────────────────
            st.divider()
            st.subheader("Executive Summary")
            with st.spinner("Generating executive summary with Cortex..."):
                summary_prompt = f"""You are a compliance analyst. Write a concise 3-4 sentence executive summary for a Chief Compliance Officer based on these AML threshold backtest results. Be specific with numbers. Do not use markdown formatting.

Results:
- Current threshold: INR {r['old_threshold']:,.0f}
- Proposed threshold: INR {r['proposed_threshold']:,.0f}
- Period: {str(r['period_start_inclusive'])[:10]} to {str(r['period_end_exclusive'])[:10]}
- Baseline alerts: {r['old_alert_count']}
- Proposed alerts: {r['new_alert_count']}
- Additional alerts: {r['alert_count_delta']} ({pct_str} increase)
- Total accounts flagged under new rule: {r['accounts_alerted_under_new_rule']}
- Accounts flagged for the first time: {r['newly_alerted_accounts']}

Assume each analyst reviews approximately 30 alerts per quarter."""
                safe_summary_prompt = summary_prompt.replace("'", "''")
                summary_rows = session.sql(
                    f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-8b', '{safe_summary_prompt}') AS result"
                ).collect()
                exec_summary = summary_rows[0][0].strip()

            st.info(exec_summary)
            st.caption("Generated by Snowflake Cortex (llama3.1-8b) — review before sharing.")

            # ── IMP-3: SQL Remediation Preview ──────────────────────────────
            st.divider()
            st.subheader("SQL Remediation Preview")
            st.markdown(
                "The following SQL would create the new rule version in the control catalog. "
                "**This is a preview only** — copy and execute after approval."
            )
            new_version = int(rule["RULE_VERSION"]) + 1
            remediation_sql = f"""-- Step 1: Retire the current rule version
UPDATE REGCHANGE_DB.REGCHANGE.REGULATORY_CONTROLS
   SET STATUS = 'SUPERSEDED',
       ACTIVE_TO = CURRENT_DATE()
 WHERE RULE_ID = 'AML_THRESHOLD_10L'
   AND RULE_VERSION = {int(rule['RULE_VERSION'])}
   AND STATUS = 'ACTIVE';

-- Step 2: Insert the new rule version
INSERT INTO REGCHANGE_DB.REGCHANGE.REGULATORY_CONTROLS (
    RULE_ID, RULE_NAME, RULE_VERSION, PARAMETER_NAME,
    THRESHOLD_VALUE, CURRENCY_CODE, SQL_PREDICATE,
    STATUS, ACTIVE_FROM, SOURCE_REFERENCE
)
VALUES (
    'AML_THRESHOLD_10L',
    'AML high-value transaction threshold',
    {new_version},
    'TXN_AMOUNT_THRESHOLD_INR',
    {proposed}.00,
    'INR',
    'TXN_AMOUNT > :THRESHOLD_VALUE',
    'ACTIVE',
    '{period_end}',
    'BACKTEST_RUN:{r["run_id"]}'
);"""
            st.code(remediation_sql, language="sql")
            st.caption(
                f"This creates version {new_version} of AML_THRESHOLD_10L at "
                f"INR {proposed:,} and retires version {int(rule['RULE_VERSION'])}. "
                f"Source reference links back to backtest run `{r['run_id'][:8]}...`"
            )

            # ── Transaction Distribution Chart ──────────────────────────────
            st.divider()
            st.subheader("Transaction Distribution")
            dist_df = conn.query(
                f"""
                SELECT
                    CASE
                        WHEN TXN_AMOUNT > {float(rule['THRESHOLD_VALUE'])} THEN 'Above current (₹{rule["THRESHOLD_VALUE"]:,.0f})'
                        WHEN TXN_AMOUNT > {proposed} THEN 'New alerts (₹{proposed:,} – ₹{rule["THRESHOLD_VALUE"]:,.0f})'
                        ELSE 'Below proposed (≤ ₹{proposed:,})'
                    END AS BAND,
                    COUNT(*) AS TXN_COUNT
                  FROM REGCHANGE_DB.REGCHANGE.TRANSACTIONS
                 WHERE CURRENCY_CODE = 'INR'
                   AND TXN_TIMESTAMP >= '{period_start} 00:00:00'::TIMESTAMP_NTZ
                   AND TXN_TIMESTAMP <  '{period_end} 00:00:00'::TIMESTAMP_NTZ
                 GROUP BY 1
                 ORDER BY 2 DESC
                """
            )
            st.bar_chart(dist_df, x="BAND", y="TXN_COUNT", horizontal=True)

# ── Tab 2: Run History ──────────────────────────────────────────────────────
with tab_history:
    st.subheader("Previous Backtest Runs")
    history_df = conn.query(
        """
        SELECT RUN_ID, PROPOSED_THRESHOLD_INR, OLD_ALERT_COUNT,
               NEW_ALERT_COUNT, ALERT_COUNT_DELTA, PERCENT_ALERT_CHANGE,
               ACCOUNTS_ALERTED_NEW_RULE, NEWLY_ALERTED_ACCOUNTS,
               RUN_STATUS, CREATED_AT
          FROM REGCHANGE_DB.REGCHANGE.BACKTEST_RUNS
         ORDER BY CREATED_AT DESC
         LIMIT 20
        """,
        ttl=0,
    )
    if history_df.empty:
        st.info("No backtest runs yet. Use the **Run Backtest** tab to create one.")
    else:
        st.dataframe(history_df, use_container_width=True, hide_index=True)

# ── Tab 3: Review & Approve ─────────────────────────────────────────────────
with tab_approve:
    st.subheader("Approve or Reject a Backtest Proposal")
    st.markdown(
        "Select a completed backtest run and record your review decision. "
        "This action is logged for audit; it does **not** automatically promote the rule."
    )

    runs_df = conn.query(
        """
        SELECT RUN_ID,
               'INR ' || TO_VARCHAR(PROPOSED_THRESHOLD_INR, '999,999,999') ||
               ' | Δ ' || TO_VARCHAR(ALERT_COUNT_DELTA) ||
               ' alerts | ' || TO_VARCHAR(CREATED_AT, 'YYYY-MM-DD HH24:MI') AS LABEL
          FROM REGCHANGE_DB.REGCHANGE.BACKTEST_RUNS
         WHERE RUN_STATUS = 'SUCCESS'
         ORDER BY CREATED_AT DESC
         LIMIT 10
        """,
        ttl=0,
    )

    if runs_df.empty:
        st.info("No successful backtest runs available for review.")
    else:
        options = dict(zip(runs_df["LABEL"], runs_df["RUN_ID"]))
        selected_label = st.selectbox("Select backtest run", list(options.keys()))
        selected_run_id = options[selected_label]

        decision = st.radio("Decision", ["APPROVED", "REJECTED"], horizontal=True)
        comment = st.text_area("Reviewer comment", max_chars=500)

        if st.button("Submit Review", type="primary"):
            if not comment.strip():
                st.warning("Please add a comment before submitting.")
            else:
                safe_comment = comment.replace("'", "''")
                session.sql(
                    f"""
                    INSERT INTO REGCHANGE_DB.REGCHANGE.REVIEW_LOG
                        (REVIEW_ID, RUN_ID, REVIEWER, DECISION, COMMENT, REVIEWED_AT)
                    SELECT
                        UUID_STRING(),
                        '{selected_run_id}',
                        CURRENT_USER(),
                        '{decision}',
                        '{safe_comment}',
                        CURRENT_TIMESTAMP()
                    """
                ).collect()
                st.success(f"Review recorded: **{decision}** for run `{selected_run_id[:8]}…`")
                st.balloons()

    st.divider()
    st.subheader("Review Log")
    review_df = conn.query(
        """
        SELECT R.REVIEW_ID, R.RUN_ID, R.REVIEWER, R.DECISION, R.COMMENT,
               R.REVIEWED_AT, B.PROPOSED_THRESHOLD_INR
          FROM REGCHANGE_DB.REGCHANGE.REVIEW_LOG R
          JOIN REGCHANGE_DB.REGCHANGE.BACKTEST_RUNS B ON R.RUN_ID = B.RUN_ID
         ORDER BY R.REVIEWED_AT DESC
         LIMIT 20
        """,
        ttl=0,
    )
    if review_df.empty:
        st.info("No reviews recorded yet.")
    else:
        st.dataframe(review_df, use_container_width=True, hide_index=True)

# ── Tab 4: Ask Analyst (Cortex Analyst + Semantic View) ─────────────────────
with tab_analyst:
    st.subheader("Natural Language Query — Cortex Analyst")
    st.markdown(
        "Ask questions about transactions, backtests, or approvals in plain English. "
        "Powered by a **Semantic View** over the RegChange data and **Cortex Analyst**."
    )

    SAMPLE_QUESTIONS = [
        "How many total transactions are there?",
        "What is the average transaction amount?",
        "How many backtest runs have been performed?",
        "How many high value transactions exceed 10 lakh?",
        "How many unique accounts are there?",
        "What is the maximum alert delta from any backtest?",
        "How many proposals have been approved?",
    ]

    selected_q = st.selectbox("Sample questions", ["(type your own)"] + SAMPLE_QUESTIONS)
    user_question = st.text_input(
        "Your question",
        value="" if selected_q == "(type your own)" else selected_q,
    )

    if st.button("Ask Cortex Analyst", type="primary", use_container_width=True):
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Cortex Analyst is generating SQL..."):
                import requests

                # Get connection details from the active Snowpark session
                sf_conn = session._conn._conn
                token = sf_conn.rest.token
                host = sf_conn.host

                resp = requests.post(
                    url=f"https://{host}/api/v2/cortex/analyst/message",
                    json={
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_question}
                                ],
                            }
                        ],
                        "semantic_view": "REGCHANGE_DB.REGCHANGE.REGCHANGE_SEMANTIC",
                    },
                    headers={
                        "Authorization": f'Snowflake Token="{token}"',
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )

                if resp.status_code >= 400:
                    st.error(f"Cortex Analyst API error ({resp.status_code}): {resp.text[:500]}")
                    st.stop()

                resp_json = resp.json()

            # Parse the Cortex Analyst response
            analyst_sql = None
            analyst_text = None
            suggestions = None

            for content_block in resp_json.get("message", {}).get("content", []):
                if content_block.get("type") == "sql":
                    analyst_sql = content_block.get("statement", "")
                elif content_block.get("type") == "text":
                    analyst_text = content_block.get("text", "")
                elif content_block.get("type") == "suggestions":
                    suggestions = content_block.get("suggestions", [])

            if analyst_text:
                st.markdown(f"**Analyst:** {analyst_text}")

            if analyst_sql:
                st.markdown("**Generated SQL (grounded in Semantic View):**")
                st.code(analyst_sql, language="sql")

                try:
                    with st.spinner("Executing query..."):
                        result_df = conn.query(analyst_sql)
                    st.markdown("**Result:**")
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Query execution failed: {e}")

            if suggestions:
                st.markdown("**Suggested questions:**")
                for s in suggestions:
                    st.markdown(f"- {s}")

            if not analyst_sql and not analyst_text and not suggestions:
                st.warning("Cortex Analyst returned an empty response. Try a different question.")

    st.divider()
    st.caption(
        "This tab uses the **Cortex Analyst REST API** with the RegChange **Semantic View**. "
        "Unlike generic LLM SQL generation, Cortex Analyst generates queries grounded in "
        "defined metrics, dimensions, and relationships — ensuring consistent, governed results."
    )
