import re
from datetime import datetime

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

_VALID_STATUSES = {"active", "inactive", "suspended"}
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_DATE_FMTS = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]
_PHONE_PATS = {
    "standard":     re.compile(r"^\d{3}-\d{3}-\d{4}$"),
    "parenthesis":  re.compile(r"^\(\d{3}\)\s?\d{3}-\d{4}$"),
    "dot-separated": re.compile(r"^\d{3}\.\d{3}\.\d{4}$"),
    "plain digits": re.compile(r"^\d{10}$"),
}
_EXPECTED_TYPES = {
    "customer_id": "INTEGER",   "first_name": "STRING",  "last_name": "STRING",
    "email": "STRING",          "phone": "STRING",       "date_of_birth": "DATE",
    "address": "STRING",        "income": "NUMERIC",     "account_status": "STRING (enum)",
    "created_date": "DATE",
}


def _parse_date(v: str) -> bool:
    for fmt in _DATE_FMTS:
        try: datetime.strptime(v, fmt); return True
        except ValueError: continue
    return False


def _classify_phone(phone: str) -> str:
    for label, pat in _PHONE_PATS.items():
        if pat.match(phone): return label
    return "unknown"


def _issue(col: str, text: str, sev: str, rows, examples) -> dict:
    return {"column": col, "issue": text, "severity": sev, "rows": list(rows), "examples": list(examples)}


def _quality_issues(df: pd.DataFrame) -> list[dict]:
    issues = []

    bad = df[~df["email"].fillna("").apply(lambda x: bool(_EMAIL_RE.match(x)))]
    if not bad.empty:
        issues.append(_issue("email", "Invalid or malformed email", "High", bad.index, bad["email"].head(3)))

    for col in ("date_of_birth", "created_date"):
        non_null = df[col].dropna().replace("", pd.NA).dropna()
        inv = non_null[~non_null.apply(_parse_date)]
        if not inv.empty:
            issues.append(_issue(col, "Unparseable or invalid date", "Critical", inv.index, inv.head(3)))

    fmt = df["phone"].fillna("").apply(_classify_phone)
    non_std = fmt != "standard"
    if non_std.any():
        issues.append(_issue("phone", f"Non-standard formats: {fmt.value_counts().to_dict()}", "Medium",
                             df[non_std].index, df.loc[non_std, "phone"].head(3)))

    bad_s = df[~df["account_status"].isin(_VALID_STATUSES) & df["account_status"].notna() & (df["account_status"] != "")]
    if not bad_s.empty:
        issues.append(_issue("account_status", f"Invalid values: {bad_s['account_status'].unique().tolist()}",
                             "High", bad_s.index, bad_s["account_status"].head(3)))

    def _bad_income(v: str) -> bool:
        try: f = float(v); return f < 0 or f > 10_000_000
        except (ValueError, TypeError): return bool(v and not pd.isna(v))

    bad_i = df[df["income"].fillna("").apply(_bad_income)]
    if not bad_i.empty:
        issues.append(_issue("income", "Out-of-range or non-numeric income", "High",
                             bad_i.index, bad_i["income"].head(3)))

    return issues


def profile(df: pd.DataFrame) -> dict:
    logger.info("Profiling %d rows...", len(df))
    total = len(df)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "shape": (total, len(df.columns)),
        "completeness": {
            col: {"missing": int(m), "pct": round((total - int(m)) / total * 100, 1)}
            for col in df.columns
            for m in [(df[col].isna() | (df[col] == "")).sum()]
        },
        "data_types": {col: str(df[col].dtype) for col in df.columns},
        "uniqueness": {
            "total": total,
            "unique": df["customer_id"].nunique(),
            "duplicates": int(df["customer_id"].duplicated().sum()),
        },
        "quality_issues": _quality_issues(df),
    }


def format_report(r: dict) -> str:
    H, D = "=" * 60, "-" * 40
    rows, cols = r["shape"]
    lines = [f"DATA QUALITY PROFILE REPORT\n{H}",
             f"Generated : {r['timestamp']}", f"Dataset   : {rows} rows × {cols} columns",
             f"\nCOMPLETENESS:\n{D}"]

    for col, s in r["completeness"].items():
        note = f"  ({s['missing']} missing)" if s["missing"] else ""
        lines.append(f"  {'✓' if not s['missing'] else '✗'} {col}: {s['pct']}%{note}")

    lines.append(f"\nDATA TYPES:\n{D}")
    for col, exp in _EXPECTED_TYPES.items():
        act = r["data_types"].get(col, "N/A")
        lines.append(f"  {'✗' if act == 'object' and exp != 'STRING' else '✓'} {col}: actual={act}  expected={exp}")

    u = r["uniqueness"]
    lines += [f"\nUNIQUENESS:\n{D}",
              f"  {'✓' if not u['duplicates'] else '✗'} customer_id: {u['unique']}/{u['total']} unique  ({u['duplicates']} duplicates)"]

    sev: dict[str, int] = {}
    lines.append(f"\nQUALITY ISSUES:\n{D}")
    for i, iss in enumerate(r["quality_issues"], 1):
        sev[iss["severity"]] = sev.get(iss["severity"], 0) + 1
        lines += [f"  {i}. [{iss['severity']}] {iss['column']}: {iss['issue']}",
                  f"       Rows: {iss['rows']}  Examples: {iss['examples']}"]

    lines += [f"\nSEVERITY SUMMARY:\n{D}",
              *[f"  {lv}: {sev.get(lv, 0)} issue(s)" for lv in ("Critical", "High", "Medium")],
              f"\nTOTAL ISSUES FOUND: {len(r['quality_issues'])}\n{H}"]
    return "\n".join(lines)
