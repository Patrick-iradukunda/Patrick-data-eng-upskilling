import os
from fastapi import APIRouter
from app.schemas.train import TrainingStatusResponse
from app.config import settings

router = APIRouter()


@router.get("/", summary="Health Check")
def health_check():
    model_exists = os.path.exists(
        os.path.join(settings.MODEL_DIR, "best_model.joblib")
    )
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model_trained": model_exists,
    }