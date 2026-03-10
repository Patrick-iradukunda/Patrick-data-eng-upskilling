from pydantic import BaseModel
from typing import Dict, Any, List


class ShapeInfo(BaseModel):
    rows: int
    columns: int


class DataSummaryResponse(BaseModel):
    shape: ShapeInfo
    columns: List[str]
    dtypes: Dict[str, str]
    missing_values: Dict[str, int]
    duplicate_rows: int
    descriptive_stats: Dict[str, Any]


class CleaningReportResponse(BaseModel):
    raw_shape: ShapeInfo
    cleaned_shape: ShapeInfo
    rows_removed: int
    columns_removed: int
    missing_values_before: int
    missing_values_after: int
    duplicate_rows_before: int
    duplicate_rows_after: int
    final_columns: List[str]
    dtypes: Dict[str, str]