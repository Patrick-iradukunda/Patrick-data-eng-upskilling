import logging
import os
from app.ml.cleaner import run_cleaning_pipeline
from app.config import settings
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)


class CleaningService:

    def get_cleaning_report(self) -> dict:
        self._validate_data_path()

        import pandas as pd
        raw_df = pd.read_csv(settings.DATA_PATH)
        cleaned_df = run_cleaning_pipeline(settings.DATA_PATH)

        report = {
            "raw_shape": {
                "rows": raw_df.shape[0],
                "columns": raw_df.shape[1],
            },
            "cleaned_shape": {
                "rows": cleaned_df.shape[0],
                "columns": cleaned_df.shape[1],
            },
            "rows_removed": raw_df.shape[0] - cleaned_df.shape[0],
            "columns_removed": raw_df.shape[1] - cleaned_df.shape[1],
            "missing_values_before": raw_df.isnull().sum().sum(),
            "missing_values_after": cleaned_df.isnull().sum().sum(),
            "duplicate_rows_before": raw_df.duplicated().sum(),
            "duplicate_rows_after": cleaned_df.duplicated().sum(),
            "final_columns": list(cleaned_df.columns),
            "dtypes": cleaned_df.dtypes.astype(str).to_dict(),
        }

        logger.info("Cleaning report generated.")
        return report

    def get_cleaned_sample(self, n: int = 10) -> list[dict]:
        self._validate_data_path()
        cleaned_df = run_cleaning_pipeline(settings.DATA_PATH)
        return cleaned_df.head(n).to_dict(orient="records")

    def _validate_data_path(self):
        if not os.path.exists(settings.DATA_PATH):
            raise DataNotFoundError(f"Dataset not found at: {settings.DATA_PATH}")