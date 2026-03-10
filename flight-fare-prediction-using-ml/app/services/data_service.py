import os
import logging
import pandas as pd
from app.ml.cleaner import run_cleaning_pipeline
from app.config import settings
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class DataService:

    def get_raw_summary(self) -> dict:
        self._validate_data_path()
        df = pd.read_csv(settings.DATA_PATH)

        return {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "descriptive_stats": df.describe(include="all").fillna("").round(2).to_dict(),
        }

    def get_cleaned_summary(self) -> dict:
        self._validate_data_path()
        df = run_cleaning_pipeline(settings.DATA_PATH)

        return {
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "descriptive_stats": df.describe().fillna("").round(2).to_dict(),
        }

    def get_raw_sample(self, n: int = 10) -> list[dict]:
        self._validate_data_path()
        df = pd.read_csv(settings.DATA_PATH)
        return df.head(n).fillna("").to_dict(orient="records")

    def get_cleaned_sample(self, n: int = 10) -> list[dict]:
        self._validate_data_path()
        df = run_cleaning_pipeline(settings.DATA_PATH)
        return df.head(n).fillna("").to_dict(orient="records")

    def _validate_data_path(self):
        if not os.path.exists(settings.DATA_PATH):
            raise DataNotFoundError(f"Dataset not found at: {settings.DATA_PATH}")