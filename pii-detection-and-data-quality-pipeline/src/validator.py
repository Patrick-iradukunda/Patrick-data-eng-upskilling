import re
from datetime import datetime

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check, DataFrameSchema

from src.utils import get_logger

logger = get_logger(__name__)

_VALID_STATUSES = ["active", "inactive", "suspended", "[UNKNOWN]"]
_EMAIL_RE = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
_PHONE_RE = r"^\d{3}-\d{3}-\d{4}$"
_DATE_RE = r"^\d{4}-\d{2}-\d{2}$"

CLEANED_SCHEMA = DataFrameSchema(
    {
        "customer_id":    Column(int,   Check.greater_than(0),                                 nullable=False),
        "first_name":     Column(str,   Check.str_length(min_value=1, max_value=50),            nullable=False),
        "last_name":      Column(str,   Check.str_length(min_value=1, max_value=50),            nullable=False),
        "email":          Column(str,   Check.str_matches(_EMAIL_RE),                          nullable=False),
        "phone":          Column(str,   Check.str_matches(_PHONE_RE),                          nullable=False),
        "date_of_birth":  Column(str,   Check.str_matches(_DATE_RE),                           nullable=True),
        "address":        Column(str,   Check.str_length(min_value=5),                         nullable=True),
        "income":         Column(float, Check.in_range(min_value=0, max_value=10_000_000),      nullable=False),
        "account_status": Column(str,   Check.isin(_VALID_STATUSES),                           nullable=False),
        "created_date":   Column(str,   Check.str_matches(_DATE_RE),                           nullable=True),
    },
    checks=[pa.Check(lambda df: ~df["customer_id"].duplicated().any(), error="Duplicate customer_id")],
    coerce=False,
)


def _fail(row: int, col: str, val, reason: str) -> dict:
    return {"row": row, "column": col, "value": val, "reason": reason}


def _try_parse_date(v: str) -> bool:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try: datetime.strptime(v, fmt); return True
        except ValueError: continue
    return False


def _validate_raw(df: pd.DataFrame) -> list[dict]:
    failures = []
    for idx, row in df.iterrows():
        n = idx + 2
        for col in ("first_name", "last_name", "address"):
            if pd.isna(row[col]) or str(row[col]).strip() == "":
                failures.append(_fail(n, col, row[col], "Missing value"))
        if not re.match(_EMAIL_RE, str(row.get("email", ""))):
            failures.append(_fail(n, "email", row["email"], "Invalid email format"))
        if not re.match(_PHONE_RE, str(row.get("phone", ""))):
            failures.append(_fail(n, "phone", row["phone"], "Non-standard phone format"))
        for col in ("date_of_birth", "created_date"):
            v = str(row.get(col, ""))
            if v and not pd.isna(row.get(col)) and not _try_parse_date(v):
                failures.append(_fail(n, col, v, "Invalid date value"))
        status = str(row.get("account_status", ""))
        if status and status not in ("active", "inactive", "suspended"):
            failures.append(_fail(n, "account_status", status, "Invalid status value"))
        if pd.isna(row.get("income")) or str(row.get("income", "")).strip() == "":
            failures.append(_fail(n, "income", row.get("income"), "Missing value"))
    return failures


def validate_raw(df: pd.DataFrame) -> tuple[bool, list[dict]]:
    logger.info("Validating raw data...")
    failures = _validate_raw(df)
    logger.info("Raw validation: %d failure(s)", len(failures))
    return len(failures) == 0, failures


def validate_cleaned(df: pd.DataFrame) -> tuple[bool, list[str]]:
    logger.info("Validating cleaned data...")
    try:
        CLEANED_SCHEMA.validate(df, lazy=True)
        logger.info("Cleaned data passed all schema checks")
        return True, []
    except pa.errors.SchemaErrors as exc:
        msgs = [
            f"  Row {(e['index'] or 0) + 2} | {e['column']}: {e['failure_case']}"
            for e in exc.failure_cases[["column", "failure_case", "index"]].to_dict("records")
        ]
        logger.warning("Cleaned validation: %d failure(s)", len(msgs))
        return False, msgs


def format_report(raw_failures: list[dict], cleaned_passed: bool, cleaned_errors: list[str]) -> str:
    by_col: dict[str, list] = {}
    for f in raw_failures:
        by_col.setdefault(f["column"], []).append(f)

    H, D = "=" * 60, "-" * 40
    lines = [f"VALIDATION RESULTS\n{H}", f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             f"\nRAW DATA VALIDATION:\n{D}",
             f"  Total failures : {len(raw_failures)}",
             f"  Status         : {'✓ PASS' if not raw_failures else '✗ FAIL'}",
             f"\nFAILURES BY COLUMN:\n{D}"]

    if not raw_failures:
        lines.append("  None — raw data passed all checks.")
    else:
        for col, items in by_col.items():
            lines.append(f"  {col}:")
            for item in items:
                lines.append(f"    - Row {item['row']}: {repr(item['value'])}  →  {item['reason']}")

    status = "✓ PASS — all schema checks passed" if cleaned_passed else "✗ FAIL"
    lines += [f"\nCLEANED DATA VALIDATION:\n{D}", f"  Status : {status}"]
    lines.extend(cleaned_errors)
    lines.append(f"\n{H}")
    return "\n".join(lines)
