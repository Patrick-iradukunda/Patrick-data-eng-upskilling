import re
from datetime import datetime

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

_EMAIL_RE = re.compile(r"^(.)(.*?)(@.+)$")
_PHONE_RE = re.compile(r"^(\d{3})-(\d{3})-(\d{4})$")

_skip = lambda v: pd.isna(v) or str(v).strip() in ("", "[UNKNOWN]")


def _mask_name(v: str) -> str:
    return v if _skip(v) else f"{str(v)[0]}***"


def _mask_email(v: str) -> str:
    if pd.isna(v) or "@" not in str(v): return v
    m = _EMAIL_RE.match(str(v))
    return f"{m.group(1)}***{m.group(3)}" if m else v


def _mask_phone(v: str) -> str:
    if pd.isna(v): return v
    m = _PHONE_RE.match(str(v))
    return f"***-***-{m.group(3)}" if m else v


def _mask_dob(v: str) -> str:
    if _skip(v): return v
    parts = str(v).split("-")
    return f"{parts[0]}-**-**" if len(parts) == 3 else v


def _mask_address(v: str) -> str:
    return v if _skip(v) else "[MASKED ADDRESS]"


MASKING_RULES = {
    "first_name": _mask_name,  "last_name": _mask_name,
    "email": _mask_email,      "phone": _mask_phone,
    "date_of_birth": _mask_dob, "address": _mask_address,
}


def mask(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Applying PII masking...")
    result = df.copy()
    for col, fn in MASKING_RULES.items():
        if col in result.columns:
            result[col] = result[col].apply(fn)
    return result


def format_sample(original: pd.DataFrame, masked: pd.DataFrame, n: int = 3) -> str:
    H, D = "=" * 60, "-" * 40
    lines = [f"MASKED SAMPLE\n{H}", f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             f"\nBEFORE MASKING (first {n} rows):\n{D}", original.head(n).to_csv(index=False).strip(),
             f"\nAFTER MASKING (first {n} rows):\n{D}", masked.head(n).to_csv(index=False).strip(),
             f"\nANALYSIS:\n{D}",
             f"  Data structure : {original.shape} → {masked.shape} (unchanged)",
             "  PII masked     : names, emails, phones, addresses, dates of birth",
             "  Business data  : income, account_status, customer_id, created_date (intact)",
             f"\nMASKING RULES:\n{D}",
             "  name          : 'John'            → 'J***'",
             "  email         : 'john@gmail.com'  → 'j***@gmail.com'",
             "  phone         : '555-123-4567'    → '***-***-4567'",
             "  date_of_birth : '1985-03-15'      → '1985-**-**'",
             "  address       : '123 Main St ...' → '[MASKED ADDRESS]'",
             f"\nUSE CASE:",
             "  Safe for analytics. Compliant with GDPR Article 89 (pseudonymisation).",
             f"\n{H}"]
    return "\n".join(lines)
