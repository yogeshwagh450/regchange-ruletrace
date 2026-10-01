# RegChange — Challenges, Decisions & Engineering Log

A running log of issues encountered, decisions made, and trade-offs chosen during development. Written in plain language for demo prep and judge Q&A.

---

## Decision 1: Data Scale — 10K vs Production Scale

### What we chose
10,000 transactions across 2,500 accounts for the demo.

### Why
- Demo stability: deterministic data means every run produces exactly the same numbers (132 alerts, 200 proposed, etc.)
- Fast iteration: backtest completes in <1 second on XS warehouse
- Cost: trial account has $400 budget; keeping data small preserves credits for the entire hackathon

### Does it scale?
**Yes.** We tested the backtest query on 500,000 rows (50x the demo) and it completed in under 2 seconds on the same XS warehouse. The query uses `COUNT_IF` and `COUNT(DISTINCT IFF(...))` — these are simple aggregations that Snowflake handles efficiently at any scale.

At 500K rows: 6,662 baseline alerts, 10,000 proposed alerts, 3,338 delta, 1,000 accounts, 632 newly alerted. The proportions hold because the data generation formula is the same.

### What a production system would look like
| Aspect | Our demo | Production |
|---|---|---|
| Transaction volume | 10,000 (90 days) | 10M-100M+ per quarter |
| Accounts | 2,500 | 500K-10M+ |
| Warehouse size | XS (1 credit/hr) | Medium to Large |
| Backtest time | <1 second | 5-30 seconds at 100M rows |
| Data source | Deterministic SQL generator | Core banking system (real-time or batch) |

### What to say to judges
"We use 10K rows for demo stability, but the architecture is the same COUNT_IF aggregation that scales linearly. We tested at 500K rows with no change needed — Snowflake handles it."

---

## Decision 2: Cortex LLM for Policy Extraction — Hallucination Risk

### The problem
When an LLM reads a regulatory circular and extracts "new threshold = ₹5,00,000", it could hallucinate a wrong number. In production AML compliance, a wrong threshold means either:
- Missing real suspicious transactions (dangerous)
- Flooding the team with false alerts (wasteful)

### How we handle it
**The LLM output is a PROPOSAL, never auto-applied.** Our architecture has three safeguards:

1. **Human review gate:** The extracted fields are displayed for the compliance officer to verify before any backtest runs. The sidebar values must be explicitly confirmed.
2. **Structured extraction prompt:** We ask the LLM to return specific JSON fields (rule_name, old_threshold, new_threshold, currency, effective_date). This constrains the output space vs. free-form generation.
3. **Typed validation:** The `REGULATORY_CONTROLS` table has `NUMBER(18,2)` for threshold values. If the LLM hallucinates text instead of a number, it won't pass SQL type checks.

### At scale (many circulars)
If processing 50+ circulars, additional safeguards would be:
- Cross-reference extracted thresholds against a known range (e.g., AML thresholds are always between ₹1 lakh and ₹1 crore)
- Use Cortex Search Service to find similar historical circulars and compare extractions
- Run extraction with two different models and flag disagreements for human review
- Log every extraction with the source text for audit

### What to say to judges
"We intentionally do NOT auto-apply LLM output. This is a regulatory system — the extraction is a proposal that a human must confirm. The architecture enforces this: extracted values go to the UI for review, and the approval step is separate from the extraction step."

---

## Decision 3: No dbt/Schemachange — Manual Deployment

### What we chose
Direct SQL for schema creation (`01_initialize_regchange.sql`) and `snow streamlit deploy` for the app.

### Why NOT dbt
1. **The hackathon terms do not mention dbt.** The rubric gives "special consideration" to Snowpark, Worksheets, Streamlit, and Marketplace — not dbt.
2. **Adding dbt adds complexity without scoring benefit.** The judges evaluate the solution, not the CI/CD pipeline.
3. **Our SQL is already idempotent.** Every CREATE is `IF NOT EXISTS`, every data load is `MERGE` (only inserts if not already present). The script IS re-runnable.
4. **Time trade-off.** Setting up dbt profiles, writing models, testing `dbt run` would cost 4-6 hours that are better spent on improvements that judges can SEE in the demo.

### What a production version would use
| Tool | Purpose |
|---|---|
| **Schemachange** or **dbt** | Versioned migrations for REGULATORY_CONTROLS schema evolution |
| **Snowflake Tasks** | Scheduled data loads from core banking into TRANSACTIONS |
| **CI/CD (GitHub Actions)** | `snow streamlit deploy` on merge to main |
| **Terraform** | Infrastructure as code for compute pools, warehouses, roles |

### What to say to judges
"For the hackathon, I focused on the solution workflow rather than CI/CD scaffolding. The SQL scripts are idempotent — you can run them multiple times safely. In production, I'd add schemachange for migrations and GitHub Actions for automated deployment. I'm a data engineer, so I know the gap — I made a deliberate time trade-off to maximize the demo."

---

## Decision 4: Container Runtime vs Warehouse Runtime for Streamlit

### What we chose
Container runtime on `SYSTEM_COMPUTE_POOL_CPU`.

### Why
- Modern approach: Snowflake docs recommend container runtime
- Shared instance: all viewers see the same app (better for demo day — judge opens the link, it's already running)
- Caching: container runtime supports `st.cache_data` between sessions
- Cost: compute pool auto-suspends after 5 min idle

### Trade-off
- First load takes 1-2 minutes (container startup) if the pool was suspended
- Warehouse runtime would start faster per session but doesn't share state

### What to say to judges
"I chose container runtime because it provides a shared, always-ready instance and supports Streamlit caching natively."

---

## Challenge 1: `conn.query()` Fails on CALL Statements

### What happened
When the Streamlit app called `conn.query("CALL RUN_THRESHOLD_BACKTEST(...)")`, it crashed with `NotSupportedError: Unknown error`.

### Root cause
`conn.query()` uses `fetch_pandas_all()` internally, which expects Arrow-format results. Snowflake CALL statements return JSON-format results. The formats are incompatible.

### Fix
Switched from `conn.query()` to `session.sql().collect()` for CALL and INSERT statements. `session.sql()` handles all result formats correctly.

### Lesson
Use `conn.query()` only for SELECT statements. Use `session.sql().collect()` for CALL, INSERT, UPDATE, DELETE.

---

## Challenge 2: `UUID_STRING()` in VALUES Clause

### What happened
The INSERT for REVIEW_LOG used `VALUES (UUID_STRING(), ...)` which failed with "Invalid expression in VALUES clause."

### Root cause
Snowflake does not allow function calls inside a `VALUES` clause. Only literals and parameters are valid.

### Fix
Changed `INSERT...VALUES (UUID_STRING(), ...)` to `INSERT...SELECT UUID_STRING(), ...`. Same result, different SQL syntax.

### Lesson
In Snowflake SQL, if you need to call a function in an INSERT, use `INSERT INTO ... SELECT` instead of `INSERT INTO ... VALUES`.

---

## Challenge 3: No Python or `snow` CLI on the Machine

### What happened
The development machine had no Python installed, so `pip install snowflake-cli` and `snow streamlit deploy` were unavailable.

### Fix
1. Installed `uv` (a standalone Rust binary, no Python dependency)
2. Used `uvx --python 3.11 --from snowflake-cli snow streamlit deploy` — this downloads Python 3.11 on the fly, installs the Snowflake CLI in an isolated environment, and runs the deploy
3. First attempt with Python 3.14 failed because PyYAML needed a C compiler. Pinning to Python 3.11 provided pre-built wheels.

### Lesson
`uv`/`uvx` is a lifesaver on machines without Python. Always pin to a stable Python version (3.11) for Snowflake tooling.

---

## Challenge 4: `sql_execute` Context Not Persisting

### What happened
Running `USE SCHEMA REGCHANGE` followed by `MERGE INTO TRANSACTIONS` in separate `sql_execute` calls failed because the schema context from `USE` didn't carry over.

### Fix
Used fully qualified table names everywhere: `REGCHANGE_DB.REGCHANGE.TRANSACTIONS` instead of just `TRANSACTIONS`.

### Lesson
In the VS Code extension, each `sql_execute` may run in a different session context. Always use fully qualified names (database.schema.table).

---

## Challenge 5: Cortex Model Availability

### What happened
First tried `mistral-large2` for policy extraction. Got: "The model mistral-large2 has been in legacy state."

### Fix
Switched to `llama3.1-8b` which is available on the trial account. Tested with a simple prompt first (`"Return only the word YES"`) before using it in the app.

### Lesson
Always test Cortex model availability on your specific account before building features around it. Model availability varies by region and account type.

---

## Challenge 6: Cortex LLM Returns JSON Array Instead of Object

### What happened
The Cortex extraction prompt asks the LLM to return a JSON object with fields like `rule_name`, `new_threshold`, etc. The `llama3.1-8b` model sometimes wraps the result in a JSON array: `[{"rule_name": ...}]` instead of `{"rule_name": ...}`. Our code called `extracted.get('rule_name')` which failed with `AttributeError: 'list' object has no attribute 'get'`.

### Root cause
LLM output is non-deterministic. Even with "return JSON only" in the prompt, the model may return an array, add markdown fences, or include extra text. You cannot assume a fixed output shape.

### Fix
Added a defensive check after JSON parsing:
```python
extracted = json.loads(cleaned)
if isinstance(extracted, list) and len(extracted) > 0:
    extracted = extracted[0]
```

### Lesson
When parsing LLM-generated JSON, always handle: (1) arrays wrapping a single object, (2) markdown code fences around JSON, (3) extra text before/after the JSON. Our code now handles all three. This is why the LLM output is a "proposal" — the format is unpredictable, so a human must verify.

---

## Challenge 7: OAuth Token Expiry During `snow` CLI Deploy

### What happened
The `snow streamlit deploy --replace` command failed with "OAuth access token expired" after the session had been running for a while. The VS Code extension auto-refreshes its token, but the `snow` CLI uses a snapshot from `connections.toml` that doesn't auto-refresh.

### Fix
Bypassed the `snow` CLI entirely. Used SQL `PUT` to upload the file directly to the Streamlit live version URI:
```sql
PUT 'file://local/path/streamlit_app.py'
    'snow://streamlit/DB.SCHEMA.APP/versions/live/'
    AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

### Lesson
For quick updates, `PUT` directly to the Streamlit `snow://` URI is faster and doesn't depend on CLI token freshness. For full redeploys (new manifest, new dependencies), refresh the connection token first or re-authenticate.

---

## Challenge 8: DMFs Not Available on Trial Account

### What happened
Attempted to use Snowflake Data Metric Functions (DMFs) to add data quality checks on the TRANSACTIONS table. Got: "Data quality monitoring feature is not enabled for this account."

### Root cause
DMFs require a specific account-level feature flag that is not enabled on the hackathon trial accounts.

### Decision
Skip IMP-5 (DMFs). The feature physically cannot be enabled by the user. Document it as a "production readiness" item in the presentation.

### What to say to judges
"We planned to add DMFs for data quality monitoring on the transactions table — null checks, amount range validation — but the feature isn't enabled on the trial account. In production, this would be a critical governance layer before any backtest runs."

---

## Decision 5: Semantic View + Cortex Analyst Instead of Direct SQL

### What we chose
Created a Semantic View (`REGCHANGE_SEMANTIC`) over all 4 tables with defined facts, dimensions, metrics, relationships, and synonyms. Added an "Ask Analyst" tab in Streamlit where users can ask natural language questions.

### Why
- The hackathon terms give "special consideration" to entries using Snowflake-native features
- Semantic Views demonstrate governed data access — metrics are defined once, consistently
- It's a natural extension of the AML compliance use case: a compliance officer asks "how many accounts were newly alerted?" and gets a governed answer
- Shows depth beyond basic SQL + Streamlit

### What the Semantic View defines
- **10 metrics:** total transactions, avg/sum amounts, high-value count, unique accounts, backtest run count, avg alert increase, max alert delta, review count, approval count
- **13 dimensions:** account, transaction type, date, currency, proposed threshold, run status, rule name, rule status, decision, reviewer, etc.
- **5 facts:** amount, old alerts, new alerts, alert delta, percentage change
- **AI_SQL_GENERATION instructions** for Cortex Analyst to understand the AML context

---

## Challenge 9: `_snowflake` Module Not Available in Container Runtime

### What happened
The Ask Analyst tab called `import _snowflake` to use `send_snow_api_request` for the Cortex Analyst REST API. Failed with `ModuleNotFoundError: No module named '_snowflake'`.

### Root cause
The `_snowflake` module is only available in **warehouse runtime** Streamlit apps. Our app uses **container runtime** (`SYSTEM_COMPUTE_POOL_CPU`), which runs in a Docker container where `_snowflake` doesn't exist.

### Fix
Used `requests.post` to call the Cortex Analyst REST API directly, authenticating with the session token from the Snowpark connection:
```python
sf_conn = session._conn._conn
token = sf_conn.rest.token
host = sf_conn.host
resp = requests.post(
    url=f"https://{host}/api/v2/cortex/analyst/message",
    headers={"Authorization": f'Snowflake Token="{token}"'},
    json={...}
)
```

### Lesson
Container runtime and warehouse runtime have different available modules. Container runtime has `requests` and full PyPI access but no `_snowflake`. Warehouse runtime has `_snowflake` but limited packages. Always test API calls in the actual runtime environment.

### Why this matters for accuracy
The first attempt used `Cortex COMPLETE` (generic LLM) to generate SQL — it guessed at joins and returned wrong results (0 instead of 132). The Cortex Analyst REST API uses the Semantic View's defined metrics and dimensions to generate grounded SQL (`COUNT_IF(txn_amount_value > 1000000) WHERE currency = 'INR'`), returning the correct answer (132). This is the difference between "LLM guessing at SQL" and "governed text-to-SQL."

---

## Credit Usage Tracking

| Date | Activity | Credits Used | Running Total |
|---|---|---|---|
| Sep 30 | Phase 1 setup + backtest | ~2 | ~2 |
| Sep 30 | Streamlit deploys (4x) | ~3 | ~5 |
| Sep 30 | Cortex calls + misc queries | ~0.5 | ~5.5 |
| Sep 30 | 500K scale test | ~0.1 | ~5.6 |
| | | | |
| **Budget remaining** | | | **~$378 of $400** |

---

## Open Risks

1. **Compute pool cold start:** If judges open the app when the pool is suspended, they'll wait 1-2 minutes. Mitigation: keep the app "warm" before demo day by opening it 5 minutes before the scheduled slot.
2. **Cortex extraction quality:** The llama3.1-8b model sometimes returns extra text around the JSON. The app handles this with fallback parsing, but a cleaner model (mistral-large2 if it comes back) would be better.
3. **Single rule scenario:** We only demo one AML threshold rule. Judges might ask about multi-rule support. Answer: the REGULATORY_CONTROLS table supports multiple rules; the procedure is parameterized by RULE_ID.
