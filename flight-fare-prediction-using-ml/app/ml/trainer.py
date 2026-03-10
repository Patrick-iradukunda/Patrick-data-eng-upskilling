import os
import joblib
import logging
import numpy as np

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV

from app.ml.cleaner import run_cleaning_pipeline
from app.ml.features import run_feature_pipeline
from app.ml.evaluator import evaluate_model, compare_models
from app.config import settings

logger = logging.getLogger(__name__)

MODELS = {
    "LinearRegression": LinearRegression(),
    "Ridge":            Ridge(),
    "Lasso":            Lasso(max_iter=10000),
    "DecisionTree":     DecisionTreeRegressor(random_state=42),
    "RandomForest":     RandomForestRegressor(random_state=42, n_jobs=-1, n_estimators=50, max_depth=10),
    "GradientBoosting": GradientBoostingRegressor(random_state=42, n_estimators=50, max_depth=3, subsample=0.5),
}

PARAM_GRIDS = {
    "Ridge":        {"alpha": [1.0, 10.0]},
    "Lasso":        {"alpha": [1.0, 10.0]},
    "DecisionTree": {"max_depth": [10, 20], "min_samples_split": [2, 5]},
    "RandomForest": {"max_depth": [10, 15]},
    "GradientBoosting": {"learning_rate": [0.1, 0.2], "max_depth": [3, 5]},
}

TUNING_SAMPLE_SIZE = 5000
TRAINING_SAMPLE_SIZE = 20000


def _sample(X, y, size):
    size = min(size, len(X))
    idx  = np.random.RandomState(42).choice(len(X), size=size, replace=False)
    return X[idx], y.iloc[idx]


def _tune_model(name, model, X_train, y_train):
    if name not in PARAM_GRIDS:
        logger.info(f"Training {name}...")
        X_s, y_s = _sample(X_train, y_train, TRAINING_SAMPLE_SIZE)
        model.fit(X_s, y_s)
        return model

    logger.info(f"Tuning {name} on {TUNING_SAMPLE_SIZE} samples...")
    X_tune, y_tune = _sample(X_train, y_train, TUNING_SAMPLE_SIZE)

    gs = GridSearchCV(
        model,
        PARAM_GRIDS[name],
        cv=3,
        scoring="r2",
        n_jobs=-1,
        verbose=0,
    )
    gs.fit(X_tune, y_tune)
    logger.info(f"{name} best params: {gs.best_params_}")

    final_model = gs.best_estimator_.__class__(**gs.best_estimator_.get_params())
    X_s, y_s = _sample(X_train, y_train, TRAINING_SAMPLE_SIZE)
    final_model.fit(X_s, y_s)
    logger.info(f"{name} retrained on {TRAINING_SAMPLE_SIZE} samples.")
    return final_model


def run_training_pipeline():
    os.makedirs(settings.MODEL_DIR, exist_ok=True)

    df = run_cleaning_pipeline(settings.DATA_PATH)
    X_train, X_test, y_train, y_test, scaler, feature_columns = run_feature_pipeline(df)

    joblib.dump(scaler,           os.path.join(settings.MODEL_DIR, "scaler.joblib"))
    joblib.dump(feature_columns,  os.path.join(settings.MODEL_DIR, "feature_columns.joblib"))
    logger.info("Saved scaler and feature columns.")

    results = []

    for name, model in MODELS.items():
        trained_model = _tune_model(name, model, X_train, y_train)
        metrics       = evaluate_model(trained_model, X_test, y_test)
        metrics["model"] = name
        results.append(metrics)
        joblib.dump(trained_model, os.path.join(settings.MODEL_DIR, f"{name}.joblib"))
        logger.info(f"{name} — R²: {metrics['r2']} | MAE: {metrics['mae']} | RMSE: {metrics['rmse']}")

    best       = compare_models(results)
    best_model = joblib.load(os.path.join(settings.MODEL_DIR, f"{best['model']}.joblib"))

    joblib.dump(best_model,       os.path.join(settings.MODEL_DIR, "best_model.joblib"))
    joblib.dump(best["model"],    os.path.join(settings.MODEL_DIR, "best_model_name.joblib"))

    logger.info(f"Best model: {best['model']} with R²={best['r2']}")
    return results, best["model"]