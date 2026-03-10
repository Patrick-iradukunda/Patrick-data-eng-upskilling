import os
import joblib
import logging
from app.ml.trainer import run_training_pipeline
from app.ml.evaluator import get_feature_importance
from app.config import settings
from app.core.exceptions import ModelNotTrainedError

logger = logging.getLogger(__name__)


class TrainService:

    def train_all_models(self) -> dict:
        logger.info("Training pipeline started...")
        results, best_model_name = run_training_pipeline()
        best = next(r for r in results if r["model"] == best_model_name)
        return {
            "message": "Training complete. All models saved.",
            "best_model": best_model_name,
            "best_metrics": {
                "r2":   best["r2"],
                "mae":  best["mae"],
                "rmse": best["rmse"],
            },
            "all_results": results,
        }

    def get_model_comparison(self) -> dict:
        self._validate_trained()
        model_names = [
            "LinearRegression",
            "Ridge",
            "Lasso",
            "DecisionTree",
            "RandomForest",
            "GradientBoosting",
        ]
        results = []
        for name in model_names:
            path = os.path.join(settings.MODEL_DIR, f"{name}.joblib")
            if os.path.exists(path):
                model = joblib.load(path)
                results.append({
                    "model": name,
                    "type":  type(model).__name__,
                })
        best_name = joblib.load(os.path.join(settings.MODEL_DIR, "best_model_name.joblib"))
        return {
            "trained_models": results,
            "best_model":     best_name,
        }

    def get_feature_importance(self) -> dict:
        self._validate_trained()
        model           = joblib.load(os.path.join(settings.MODEL_DIR, "best_model.joblib"))
        feature_columns = joblib.load(os.path.join(settings.MODEL_DIR, "feature_columns.joblib"))
        best_name       = joblib.load(os.path.join(settings.MODEL_DIR, "best_model_name.joblib"))
        importance      = get_feature_importance(model, feature_columns)
        return {
            "model":              best_name,
            "feature_importance": importance,
        }

    def get_training_status(self) -> dict:
        model_path = os.path.join(settings.MODEL_DIR, "best_model.joblib")
        trained    = os.path.exists(model_path)
        result     = {"trained": trained}
        if trained:
            best_name        = joblib.load(os.path.join(settings.MODEL_DIR, "best_model_name.joblib"))
            result["best_model"] = best_name
        return result

    def _validate_trained(self):
        if not os.path.exists(os.path.join(settings.MODEL_DIR, "best_model.joblib")):
            raise ModelNotTrainedError()