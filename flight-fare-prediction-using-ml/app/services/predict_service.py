import os
import joblib
import logging
import pandas as pd
from app.config import settings
from app.core.exceptions import ModelNotTrainedError, InvalidInputError

logger = logging.getLogger(__name__)


class PredictService:

    def predict(self, payload: dict) -> dict:
        self._validate_trained()

        model = joblib.load(os.path.join(settings.MODEL_DIR, "best_model.joblib"))
        scaler = joblib.load(os.path.join(settings.MODEL_DIR, "scaler.joblib"))
        feature_columns = joblib.load(os.path.join(settings.MODEL_DIR, "feature_columns.joblib"))
        best_name = joblib.load(os.path.join(settings.MODEL_DIR, "best_model_name.joblib"))

        input_df = self._build_input(payload, feature_columns)

        scaled = scaler.transform(input_df)
        prediction = model.predict(scaled)[0]

        if prediction < 0:
            raise InvalidInputError("Predicted fare is negative. Please check your inputs.")

        logger.info(f"Prediction made: {prediction:.2f} using {best_name}")

        return {
            "predicted_fare": round(float(prediction), 2),
            "model_used": best_name,
            "inputs_received": payload,
            "note": "Prediction is based on the best performing trained model.",
        }

    def _build_input(self, payload: dict, feature_columns: list) -> pd.DataFrame:
        input_df = pd.DataFrame([{col: 0 for col in feature_columns}])

        direct_fields = ["base_fare", "tax_surcharge", "month", "day", "weekday"]
        for field in direct_fields:
            if field in payload and field in input_df.columns:
                input_df[field] = payload[field]

        one_hot_fields = {
            "airline":     "airline",
            "source":      "source",
            "destination": "destination",
            "season":      "season",
        }
        for payload_key, col_prefix in one_hot_fields.items():
            value = payload.get(payload_key)
            if value:
                col_name = f"{col_prefix}_{value}"
                if col_name in input_df.columns:
                    input_df[col_name] = 1
                else:
                    logger.warning(f"Column '{col_name}' not found in trained features. Skipping.")

        return input_df

    def _validate_trained(self):
        if not os.path.exists(os.path.join(settings.MODEL_DIR, "best_model.joblib")):
            raise ModelNotTrainedError()