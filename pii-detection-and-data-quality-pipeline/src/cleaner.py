import re
from datetime import datetime

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

_DATE_FMTS = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]
_DIGITS_RE = re.compile(r"[^\d]")


def _normalize_phone(v: str) -> str:
    if pd.isna(v) or not str(v).strip(): return v
    d = _DIGITS_RE.sub("", str(v))
    if len(d) == 10: return f"{d[:3]}-{d[3:6]}-{d[6:]}"
    if len(d) == 11 and d[0] == "1": return f"{d[1:4]}-{d[4:7]}-{d[7:]}"
    return v


def _normalize_date(v: str) -> str:
    if pd.isna(v) or not str(v).strip(): return v
    for fmt in _DATE_FMTS:
        try: return datetime.strptime(str(v).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError: continue
    return pd.NA


def _track(result: pd.DataFrame, col: str, fn, log: list, label: str) -> None:
    before = result[col].copy()
    result[col] = result[col].apply(fn)
    log.append(f"{col:<14} | {label:<42} | {(before != result[col]).sum()} row(s) affected")


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    logger.info("Cleaning %d rows...", len(df))
    result, log = df.copy(), []

    _track(result, "phone", _normalize_phone, log, "Normalized to XXX-XXX-XXXX")
    for col in ("date_of_birth", "created_date"):
        _track(result, col, _normalize_date, log, "Normalized to YYYY-MM-DD")
    _track(result, "email", lambda v: str(v).strip().lower() if not pd.isna(v) else v, log, "Lowercased")
    for col in ("first_name", "last_name"):
        _track(result, col, lambda v: str(v).strip().title() if not pd.isna(v) and str(v).strip() else v, log, "Applied title case")

    for col, fill in {"first_name": "[UNKNOWN]", "last_name": "[UNKNOWN]",
                      "address": "[UNKNOWN]", "account_status": "[UNKNOWN]"}.items():
        mask = result[col].isna() | (result[col] == "")
        if mask.any():
            result.loc[mask, col] = fill
            log.append(f"{col:<14} | Filled missing with '{fill}'                  | {mask.sum()} row(s)")

    income_mask = result["income"].isna() | (result["income"] == "")
    if income_mask.any():
        result.loc[income_mask, "income"] = "0"
        log.append(f"{'income':<14} | Filled missing with 0                         | {income_mask.sum()} row(s)")

    result["customer_id"] = pd.to_numeric(result["customer_id"], errors="coerce").astype("Int64")
    result["income"] = pd.to_numeric(result["income"], errors="coerce").astype(float)

    logger.info("Cleaning complete — %d transformation(s) applied.", len(log))
    return result, log


def format_log(log_entries: list[str], before_failures: int, after_passed: bool) -> str:
    H, D = "=" * 60, "-" * 40
    lines = [f"DATA CLEANING LOG\n{H}", f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             f"\nACTIONS TAKEN:\n{D}",
             f"  {'Column':<14}   {'Action':<42}   Impact",
             f"  {'-'*14}   {'-'*42}   {'-'*20}",
             *[f"  {e}" for e in log_entries],
             f"\nMISSING VALUE STRATEGY:\n{D}",
             "  first_name, last_name, address, account_status → '[UNKNOWN]' (preserve row, flag for review)",
             "  income → 0  (unreported, not confirmed zero income)",
             f"\nVALIDATION SUMMARY:\n{D}",
             f"  Before cleaning : {before_failures} row(s) failed",
             f"  After cleaning  : {'✓ PASS — 0 failures' if after_passed else '✗ Some issues remain'}",
             f"\n{H}"]
    return "\n".join(lines)
