# RegChange RuleTrace — Presentation Deck (Judge-Optimized)

**Tagline:** Trace. Analyze. Validate. Govern.

Each slide answers: "Why should the judges care?"

---

## SLIDE 1: Title

**RegChange RuleTrace**
*Regulatory Change Impact & Control Intelligence*

Trace. Analyze. Validate. Govern.

Snowflake CoCo CLI Hackathon 2026 | Problem Statement 01
Yogesh Wagh | Solo Entry

GitHub: github.com/yogeshwagh450/regchange-ruletrace
Live Prototype: [Streamlit URL]

**Speaker Notes:**
"RegChange RuleTrace — one system that takes a regulatory circular and turns it into a governed, auditable compliance decision in under 60 seconds."

---

## SLIDE 2: The Compliance Challenge

**Title:** The Compliance Challenge

**Show the current manual process (use arrow flow):**

```
Regulatory Circular → Manual Reading → Spreadsheet Analysis → Ad-hoc SQL → Email Approvals → Rule Change
```

**Pain points (use red/warning icons):**

| Pain Point | Business Risk |
|---|---|
| Manual interpretation | Wrong thresholds applied, missed deadlines |
| No impact visibility | Unknown alert volume increase, understaffed teams |
| Weak auditability | Regulators ask "who approved this?" — no answer |
| Slow response | Days to weeks per threshold change |

**Bold callout:**
"A single threshold change can flood compliance teams with hundreds of unexpected alerts — but today, they don't know until it's too late."

**Speaker Notes:**
"When RBI issues a circular changing an AML threshold, banks today read it manually, estimate impact in spreadsheets, and approve via email. There's no reproducibility, no audit trail, and no way to know the real operational impact before it hits."

---

## SLIDE 3: Introducing RegChange RuleTrace

**Title:** Introducing RegChange RuleTrace

**5-step workflow (horizontal arrow flow — use icons for each step):**

**EXTRACT** → **MAP** → **BACKTEST** → **QUANTIFY** → **APPROVE**

| Step | What Happens | Snowflake Service |
|---|---|---|
| EXTRACT | AI reads circular, extracts threshold change | Cortex COMPLETE |
| MAP | Links to versioned control record, auto-fills parameters | Regulatory Controls table |
| BACKTEST | Replays 10K transactions under old vs new threshold | SQL Stored Procedure |
| QUANTIFY | Shows exact alert counts, delta, affected accounts | Streamlit Dashboard |
| APPROVE | Human reviews evidence, approves/rejects with comment | Review Log (audit trail) |

**Key message (large, centered):**
*"AI proposes. Humans approve."*

**Speaker Notes:**
"Five steps, fully automated except for the final approval. The AI extracts the change, the system quantifies the impact, and a human makes the decision with full evidence. This is the design principle: the LLM proposes, the compliance officer decides."

---

## SLIDE 4: Snowflake-Native Architecture

**Title:** Built Entirely on Snowflake

**(Use architecture diagram PNG here)**

**Call out these Snowflake services (use badges/pills):**

- Cortex COMPLETE (llama3.1-8b)
- Cortex Analyst REST API
- Semantic View (10 metrics, 13 dimensions)
- Streamlit in Snowflake (container runtime)
- SQL Stored Procedures
- CoCo CLI (development workflow)

**Key message:**
"Zero external dependencies. Everything runs inside Snowflake's governance boundary."

**Speaker Notes:**
"Every component runs inside Snowflake. Cortex handles AI. Streamlit provides the UI. Semantic Views govern the business definitions. SQL procedures ensure deterministic replay. And the entire project was built using CoCo CLI. No data leaves Snowflake."

---

## SLIDE 5: AI-Powered Policy Extraction

**Title:** AI Reads the Regulation

**(Screenshot: Policy Extraction tab with Cortex results)**

**Flow:**
```
Regulatory Circular (text) → Cortex LLM → Structured JSON
```

**Extracted fields shown:**
- rule_name: "Revision of Threshold..."
- old_threshold: 1,000,000
- new_threshold: 500,000
- effective_date: 2026-10-01

**Key callouts:**
- Extracted values auto-populate the backtest sidebar
- Human verifies before proceeding — extraction is a *proposal*
- Handles markdown fences, JSON arrays, format variations

**Key message:**
*"Cortex converts unstructured regulation into actionable metadata."*

**Speaker Notes:**
"I paste the circular. Cortex extracts the key fields: what rule is changing, from what to what, and when. The sidebar auto-fills with 500,000. But notice — the compliance officer must verify before proceeding. We never auto-apply AI output in a regulatory system."

---

## SLIDE 6: Quantified Impact Analysis

**Title:** The Numbers That Matter

**(Screenshot: Run Backtest tab with metric cards)**

**Make these numbers LARGE and prominent:**

```
     132                    200
  Baseline Alerts    →    Proposed Alerts

        +68 Additional Alerts
        +51.5% Impact Increase

     50 Accounts Flagged
     47 Newly Flagged Customers
```

**Business translation (below the numbers):**
- +68 alerts = ~2 additional analysts needed per quarter
- 47 new customers = potential complaints if not communicated
- The bank now has evidence to plan BEFORE the regulation takes effect

**Key message:**
*"From guesswork to precision — compliance teams know the exact impact before it happens."*

**Speaker Notes:**
"One click, three seconds. The compliance team now knows: 68 more alerts, 47 customers flagged for the first time. Do we have capacity? Do we need to hire? This is the difference between reacting to a regulatory change and planning for it."

---

## SLIDE 7: Governance-Ready Remediation

**Title:** Every Change Is Traceable and Auditable

**Two panels:**

**Left — SQL Remediation Preview:**
- (Screenshot: generated UPDATE + INSERT SQL)
- Retires current rule version (v1 → SUPERSEDED)
- Creates new version (v2 at INR 500,000)
- Source reference links to backtest run ID

**Right — Approval Audit Trail:**
- (Screenshot: Review & Approve tab with Review Log)
- Who approved: reviewer name
- When: timestamp
- Why: comment
- Decision: APPROVED / REJECTED

**Key message:**
*"Every regulatory change becomes fully traceable and auditable."*

**Speaker Notes:**
"The system generates the exact SQL to implement the change — copy, review, execute. And every approval is logged: who, when, why. When the regulator audits, you have the complete chain: circular, extraction, impact analysis, approval, and the rule change itself."

---

## SLIDE 8: Natural Language Compliance Analytics

**Title:** Ask Questions, Get Governed Answers

**(Screenshot: Ask Analyst tab showing "How many high value transactions exceed 10 lakh?" → 132)**

**How it works:**
```
Compliance Officer asks → Cortex Analyst REST API → Semantic View → Governed SQL → Result
```

**Why this matters:**
- Answers are grounded in the Semantic View's defined metrics
- Not LLM guessing at SQL — governed, consistent definitions
- "high_value_transaction_count" always means COUNT_IF(amount > 1,000,000)

**Example questions a compliance officer could ask:**
- "How many accounts were newly alerted?"
- "What is the average alert increase across all backtests?"
- "How many proposals have been approved?"

**Key message:**
*"Business users ask in plain English. The Semantic View ensures every answer is consistent and governed."*

**Speaker Notes:**
"A compliance officer types a question in plain English. Cortex Analyst generates SQL grounded in our Semantic View — not guessing, but using the exact metric definitions we defined. '132' matches our baseline alert count because the Semantic View knows what 'high value' means."

---

## SLIDE 9: Why RegChange RuleTrace Stands Out

**Title:** Why RegChange RuleTrace Stands Out

**Four pillars (use large icons or colored cards):**

| | Pillar | What It Means |
|---|---|---|
| 🧠 | **AI-Powered** | Cortex extracts policy changes and generates executive summaries — no manual reading |
| ⚠️ | **Risk-Aware** | Quantifies exact alert and customer impact BEFORE a rule change takes effect |
| 🔒 | **Governed** | Semantic Views, versioned controls, human approval, full audit trail |
| ❄️ | **Snowflake-Native** | 6 Snowflake services, zero external dependencies, everything in the governance boundary |

**Rubric alignment (small table below):**

| Real-World Relevance (30%) | Technical Execution (40%) | Solution Completeness (30%) |
|---|---|---|
| AML threshold changes are a real banking workflow | 6 Snowflake-native services + CoCo CLI | End-to-end: circular → approval with audit trail |

**Speaker Notes:**
"Four reasons this solution stands out. It's AI-powered — Cortex reads the circular. Risk-aware — you see exact impact before anything changes. Governed — every step is auditable. And fully Snowflake-native — nothing leaves the platform."

---

## SLIDE 10: Business Impact & Future Roadmap

**Title:** Immediate Value & Enterprise Roadmap

**Left — Immediate Value (green checkmarks):**
- Faster regulatory response (days → seconds)
- Reduced compliance risk (quantified impact, not guesswork)
- Lower analyst effort (auto-extraction, auto-summary)
- Audit readiness (every decision logged)
- Consistent answers (Semantic View governs definitions)

**Right — Future Enhancements (roadmap arrows):**
- Dynamic Tables — continuous impact monitoring
- Data Metric Functions — automated quality gates
- Zero-Copy Clone Validation — test rule changes safely
- Cortex Search Service — search across policy document library
- Multi-Regulator Support — RBI, SEBI, IRDAI thresholds

**Datasets declaration (small footer):**
"All data is synthetic, generated deterministically. No external datasets or APIs used. Tested at 500K rows with no code changes."

**Speaker Notes:**
"Today, RegChange handles one threshold scenario end-to-end. In production, this extends to any regulatory parameter change across multiple regulators. Dynamic Tables would keep impact views always fresh. DMFs would add quality gates. The architecture is designed for enterprise scale."

---

## SLIDE 11: Closing

**Title:**

*"From Regulatory Circular to Governed Compliance Decision in Under 60 Seconds."*

**Show:**
- Live Prototype: [Streamlit URL]
- GitHub: github.com/yogeshwagh450/regchange-ruletrace
- Solo Builder: Yogesh Wagh
- Built with: Snowflake CoCo CLI

**Final message (centered, bold):**

*"RegChange RuleTrace transforms regulatory change management from a manual process into a repeatable, measurable, and auditable workflow."*

Questions?

**Speaker Notes:**
"RegChange RuleTrace — from a regulatory circular to a governed compliance decision in under 60 seconds. Fully Snowflake-native, AI-powered, and built solo with CoCo CLI. Thank you. I'm happy to take questions."

---

## DESIGN TIPS FOR THE PPT

1. **Use dark backgrounds** for title and closing slides (Snowflake dark blue #1A1A2E)
2. **White backgrounds** for content slides with accent colors
3. **Make numbers HUGE** on Slide 6 — this is the demo moment
4. **One key message per slide** — centered, bold, in a contrasting color
5. **Minimize bullet points** — use icons, cards, and visual flows instead
6. **Screenshots should be full-width** with subtle borders
7. **Four-pillar slide (9)** — use 4 equal-width colored cards
8. **Add the Snowflake logo** to every slide footer (small, right-aligned)
9. **Total: 11 slides, aim for 5-minute delivery**
10. **Practice the speaker notes** — they're written as natural speech, not read-aloud text
