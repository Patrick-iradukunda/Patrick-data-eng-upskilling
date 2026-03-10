from pydantic import BaseModel
from typing import List


class ModelMetrics(BaseModel):
    r2: float
    mae: float
    rmse: float


class ModelResult(BaseModel):
    model: str
    r2: float
    mae: float
    rmse: float


class TrainResponse(BaseModel):
    message: str
    best_model: str
    best_metrics: ModelMetrics
    all_results: List[ModelResult]


class ModelComparisonItem(BaseModel):
    model: str
    type: str


class ModelComparisonResponse(BaseModel):
    trained_models: List[ModelComparisonItem]
    best_model: str


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    model: str
    feature_importance: List[FeatureImportanceItem]


class TrainingStatusResponse(BaseModel):
    trained: bool
    best_model: str = None