import re
from datetime import datetime

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

_PII_CATEGORIES = {
    "first_name": "Name",   "last_name": "Name",      "email": "Email",
    "phone": "Phone",       "date_of_birth": "DOB",   "address": "Address",
    "income": "Financial",
}

PII_PATTERNS: dict[str, re.Pattern] = {
    "EMAIL":       re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "PHONE":       re.compile(r"(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})"),
    "SSN":         re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b"),
    "IP_ADDRESS":  re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}


def _scan_column(series: pd.Series) -> dict[str, int]:
    text = series.dropna().astype(str)
    return {
        ptype: int(count)
        for ptype, pat in PII_PATTERNS.items()
        if (count := text.apply(lambda v: bool(pat.search(v))).sum())
    }


def detect(df: pd.DataFrame) -> dict:
    logger.info("Running PII detection...")
    findings = {}
    for col in df.columns:
        non_empty = df[col].replace("", pd.NA).dropna()
        if not len(non_empty): continue
        category = _PII_CATEGORIES.get(col)
        hits = _scan_column(df[col])
        if category or hits:
            findings[col] = {"category": category or "Pattern Match",
                             "total_non_null": len(non_empty), "pattern_hits": hits}
    return {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows": len(df), "pii_columns": findings}


def format_report(report: dict) -> str:
    H, D = "=" * 60, "-" * 40
    total = report["total_rows"]
    lines = [f"PII DETECTION REPORT\n{H}", f"Generated  : {report['timestamp']}",
             f"Total rows : {total}", f"\nRISK ASSESSMENT:\n{D}",
             "  HIGH   : first_name, last_name, email, phone, date_of_birth, address",
             "  MEDIUM : income (financial sensitivity)",
             f"\nDETECTED PII BY COLUMN:\n{D}"]

    for col, info in report["pii_columns"].items():
        pct = round(info["total_non_null"] / total * 100, 1)
        lines.append(f"  {col} [{info['category']}]: {info['total_non_null']}/{total} rows ({pct}%)")
        for ptype, count in info["pattern_hits"].items():
            lines.append(f"    └─ {ptype} matched: {count} value(s)")

    lines += [f"\nEXPOSURE RISK:\n{D}",
              "  - Phish customers (emails exposed)",
              "  - Spoof identities (names + DOB + address exposed)",
              "  - Social engineer (phone numbers exposed)",
              f"\nMITIGATION:\n{D}",
              "  Mask PII before sharing. Apply RBAC on raw tables.",
              f"\n{H}"]
    return "\n".join(lines)
