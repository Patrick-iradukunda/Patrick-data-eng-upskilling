# Governance & Engineering Reflection

---

## Data Quality Issues Found

| # | Issue | Fix | Impact |
|---|-------|-----|--------|
| 1 | **Inconsistent date formats** — `1975/05/10`, `01/15/2024`, `invalid_date` mixed in same column | Iterative `strptime` across known formats; unrecoverable values set to `NaN` | 5 rows. Unresolved values block age calculations and compliance date checks |
| 2 | **Non-standard phone formats** — parenthesis, dot-separated, plain digits all present | Strip non-digits, reformat to `XXX-XXX-XXXX` | 3 rows. Would break CRM integration and phone validation rules |
| 3 | **Missing required fields** — `first_name`, `last_name`, `address`, `income` had gaps | `[UNKNOWN]` placeholder; income defaulted to `0` with manual review flag | 4 rows. Missing names corrupt identity resolution; missing income breaks credit scoring |
| 4 | **Invalid categorical value** — `account_status` empty for one row | Filled with `[UNKNOWN]`, flagged for review | 1 row. Downstream status-filtered queries silently exclude or misclassify the record |
| 5 | **Mixed-case emails** — `PATRICIA.DAVIS@GMAIL.COM` alongside lowercase values | Lowercased all emails during normalisation | 1 row. Deduplication and matching fail without case normalisation |

---

## PII Risk Assessment

| Column | Type | Sensitivity | Risk if Leaked |
|--------|------|-------------|----------------|
| `first_name`, `last_name` | Direct identifier | HIGH | Enables identity linkage across datasets |
| `email` | Direct identifier | HIGH | Targeted phishing; account takeover |
| `phone` | Direct identifier | HIGH | Direct contact; SIM-swapping attacks |
| `date_of_birth` | Quasi-identifier | HIGH | Combined with name/address, sufficient to pass identity verification |
| `address` | Direct identifier | HIGH | Physical location exposure; mail fraud |
| `income` | Financial | MEDIUM | Reveals wealth bracket; enables social engineering |

At 10 rows the blast radius is contained. At 10 million rows, the same dataset becomes a GDPR Article 83 liability — fines up to €20M or 4% of global annual turnover. The exposure profile does not change with scale, only the consequence does.

---

## Masking Trade-offs

Masking reduces data utility. Capabilities lost after masking:

- **Customer outreach** — emails and phones are masked; the dataset cannot drive campaigns
- **Age segmentation** — DOB reduced to year only (`1985-**-**`); exact age unavailable
- **Geographic analytics** — full address replaced; zip-code clustering eliminated
- **Identity joins** — masked names cannot be joined to credit bureaus or external registries

**When masking is the right call:**
- Sharing with analytics teams, data scientists, or third-party vendors who need patterns, not identities
- Populating non-production environments (dev, staging, QA)
- GDPR Article 89 compliance for research and statistics use cases

**When masking is the wrong call:**
- CRM, billing, or support systems that must contact customers
- Fraud investigation workflows requiring exact identity linkage
- KYC / AML flows comparing against source-of-truth records
- Audit trails where legal traceability to a specific individual is mandated

The guiding principle: **mask at the consumption layer, not the storage layer.** Keep the full dataset encrypted in access-controlled storage; serve masked views to consumers who don't need PII.

---

## Validation Strategy

**What the validators caught:**

- Missing required fields across 4 rows
- Two unparseable date values (`invalid_date`)
- Three non-standard phone formats
- One invalid `account_status` value
- One malformed email (uppercase, non-standard)

**Gaps identified:**

| Gap | Example | Consequence |
|----|---------|-------------|
| Semantic validity | `date_of_birth: 2005-12-25` parses correctly but implies a minor | Age-of-service policy violation passes validation undetected |
| Cross-field consistency | No check that `created_date` ≥ `date_of_birth` | Logically impossible records enter the system |
| Referential integrity | `customer_id` uniqueness checked locally, not against registry | Silent collision with existing IDs in an external system |
| Statistical anomalies | `income: 0` after fill is schema-valid but suspicious | Outlier passes without review; skews income-based models |

**Production improvements:**

1. Cross-field rules — DOB before `created_date`, age ≥ 18
2. Statistical anomaly detection on numeric columns (IQR, z-score)
3. Data contract versioning (Great Expectations) to detect schema drift over time
4. Row-level quarantine — route invalid rows to a dead-letter table instead of filling in-place

---

## Production Operations

**Trigger model:** Event-driven — pipeline fires on file arrival (S3 `PutObject` or Kafka message). A daily reprocessing job at 02:00 UTC catches late-arriving or previously failed records.

**Failure handling:**

| Scenario | Response |
|----------|----------|
| Partial failure (<20% rows) | Quarantine failing rows to `customers_rejected`; continue processing valid rows; alert DE team |
| Total failure (≥20% rows) | Halt pipeline; write no output; page on-call engineer |
| Unrecoverable field (e.g. `invalid_date`) | Route to manual review queue; data steward resolves before record enters production |

**Observability:**
- Structured logs per stage: name, row counts, elapsed time, pass/fail
- Input vs. output row count compared; >5% drop triggers alert
- Execution reports archived as audit artifacts alongside processed data
- Validation failures posted to `#data-quality-alerts` on every run; weekly trend digest for missing-value rate drift

---

## Lessons Learned

**What surprised me:**
A 10-row dataset produced every phone format, three date formats, missing values across five columns, and a case inconsistency — simultaneously. Real-world ingestion from a mobile app, web form, and third-party API produces exactly this at scale. The small dataset was not a simplification; it was representative.

Pandera's `lazy=True` mode proved essential. Halting on the first schema failure gives you one error per run, which is unhelpful for writing a remediation plan. Collecting all failures in a single pass made the validation report genuinely useful.

**What was harder than expected:**
Phone normalisation. Handling parentheses, dots, spaces, plain digits, and an optional country prefix without introducing regressions on already-valid formats required careful regex and a test case for each variant.

Missing value strategy is a product decision, not a technical one. Dropping rows is clean but loses data. Filling with placeholders preserves row count but adds noise. The right answer depends on downstream consumers — which the pipeline cannot know. That decision belongs in a data contract agreed between producer and consumer teams.

**What I would do differently:**
- **Schema versioning from day one.** When upstream adds a column or changes a date format, the pipeline should detect the drift and alert rather than silently fail or produce garbage output.
- **Dead-letter table over in-place filling.** Filling invalid values in the output obscures what the original data looked like. A dead-letter table preserves source values for audit and enables clean reprocessing once the upstream issue is fixed.
- **Configurable masking rules.** Hardcoding masking logic in `masker.py` means every consumer gets the same mask. In practice, a fraud analyst needs more fields unmasked than an analytics engineer. Externalising masking rules to a config file makes the pipeline serve both without code changes.
