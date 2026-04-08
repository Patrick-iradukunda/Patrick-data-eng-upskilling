# PII Detection & Data Quality Pipeline

A production-style Python pipeline for fintech customer data. Profiles raw records, detects PII, validates schema, cleans and normalises fields, masks sensitive data, and produces audit reports — end to end in a single command.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| pandas | Data processing |
| pandera | Declarative schema validation |
| pytest + pytest-cov | Unit testing & coverage |

---

## Project Structure

```
├── data/
│   ├── raw/customers_raw.csv       ← input
│   └── processed/                  ← pipeline outputs (git-ignored)
│       ├── customers_cleaned.csv
│       └── customers_masked.csv
│
├── src/
│   ├── utils.py          shared logger & file helpers
│   ├── profiler.py       Stage 1 — completeness, types, format issues
│   ├── pii_detector.py   Stage 2 — regex-based PII scanning
│   ├── validator.py      Stage 3 — raw checks + Pandera schema
│   ├── cleaner.py        Stage 4 — normalisation & missing value fill
│   └── masker.py         Stage 5 — field-level PII masking
│
├── pipeline.py           entry point — orchestrates all stages
├── tests/                unit tests (in-memory DataFrames, no file I/O)
├── docs/reflection.md    governance write-up
└── requirements.txt
```

---

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python pipeline.py
```

---

## Data Flow

```
customers_raw.csv
       │
       ▼
  [1] PROFILE     →  data_quality_report.txt
       │
       ▼
  [2] DETECT PII  →  pii_detection_report.txt
       │
       ▼
  [3] VALIDATE    →  validation_results.txt        (raw failures captured)
       │
       ▼
  [4] CLEAN       →  cleaning_log.txt
       │
       ▼
  [3] VALIDATE    →  validation_results.txt        (post-clean — must pass)
       │
       ▼
  [5] MASK        →  masked_sample.txt
       │
       ▼
  customers_cleaned.csv  +  customers_masked.csv
```

All reports are written to `reports/`. The pipeline also generates `reports/pipeline_execution_report.txt` with per-stage timing and a final status.

---

## Running Tests

```bash
pytest tests/ -v --cov=src
```

Tests use in-memory DataFrames only — no file I/O, no fixtures on disk.

---

## Pipeline Stages

| # | Module | Responsibility |
|---|--------|---------------|
| 1 | `profiler.py` | Completeness %, detected type mismatches, format issues, severity classification |
| 2 | `pii_detector.py` | Regex pattern scanning across all string columns, exposure risk summary |
| 3 | `validator.py` | Custom row-level checks on raw data; Pandera schema validation on cleaned data |
| 4 | `cleaner.py` | Phone → `XXX-XXX-XXXX`, dates → `YYYY-MM-DD`, title case, missing value fill |
| 5 | `masker.py` | `J***`, `j***@gmail.com`, `***-***-4567`, `1985-**-**`, `[MASKED ADDRESS]` |
| 6 | `pipeline.py` | Orchestration, stage timing, execution report |
