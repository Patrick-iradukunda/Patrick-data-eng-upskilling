import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import logging

logger = logging.getLogger(__name__)


def evaluate_model(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)

    r2 = round(r2_score(y_test, y_pred), 4)
    mae = round(mean_absolute_error(y_test, y_pred), 4)
    rmse = round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)

    logger.info(f"Evaluation — R²: {r2} | MAE: {mae} | RMSE: {rmse}")
    return {"r2": r2, "mae": mae, "rmse": rmse}


def compare_models(results: list[dict]) -> dict:
    if not results:
        raise ValueError("No model results to compare.")

    best = max(results, key=lambda x: x["r2"])
    logger.info(f"Best model: {best['model']} with R²={best['r2']}")
    return best


def get_feature_importance(model, feature_columns: list) -> list[dict]:
    importance = []

    if hasattr(model, "feature_importances_"):
        scores = model.feature_importances_
        importance = [
            {"feature": col, "importance": round(float(score), 6)}
            for col, score in zip(feature_columns, scores)
        ]
    elif hasattr(model, "coef_"):
        scores = np.abs(model.coef_)
        importance = [
            {"feature": col, "importance": round(float(score), 6)}
            for col, score in zip(feature_columns, scores)
        ]
    else:
        logger.warning("Model does not support feature importance extraction.")

    importance.sort(key=lambda x: x["importance"], reverse=True)
    return importance