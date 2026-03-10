from pydantic import BaseModel
from typing import Dict, Any, List


class DescriptiveStatsResponse(BaseModel):
    stats: Dict[str, Any]
    skewness: Dict[str, float]
    kurtosis: Dict[str, float]


class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int


class FareDistributionResponse(BaseModel):
    min: float
    max: float
    mean: float
    median: float
    std: float
    histogram: List[HistogramBin]


class KPIResponse(BaseModel):
    average_fare_by_airline: Dict[str, float] = {}
    most_popular_routes: Dict[str, int] = {}
    top_5_expensive_routes: Dict[str, float] = {}
    average_fare_by_season: Dict[str, float] = {}
    average_fare_by_month: Dict[str, float] = {}


class CorrelationResponse(BaseModel):
    correlation_matrix: Dict[str, Dict[str, float]]


class MonthlyTrendResponse(BaseModel):
    monthly_average_fare: Dict[str, float]