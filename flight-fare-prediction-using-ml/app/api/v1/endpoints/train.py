import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from app.services.train_service import TrainService
from app.dependencies import get_train_service

router = APIRouter()

training_status = {"running": False, "done": False, "error": None}


def _run_training(service: TrainService):
    global training_status
    try:
        training_status["running"] = True
        training_status["done"]    = False
        training_status["error"]   = None
        service.train_all_models()
        training_status["done"]    = True
    except Exception as e:
        training_status["error"]   = str(e)
    finally:
        training_status["running"] = False


@router.get("/status", summary="Check Training Status")
def training_status_check(service: TrainService = Depends(get_train_service)):
    result = service.get_training_status()
    result["job"] = training_status
    return result


@router.post("/", summary="Train All Models")
def train_models(
    background_tasks: BackgroundTasks,
    service: TrainService = Depends(get_train_service),
):
    if training_status["running"]:
        return {"message": "Training already in progress. Check GET /api/v1/train/status"}

    background_tasks.add_task(_run_training, service)
    return {"message": "Training started in background. Poll GET /api/v1/train/status to check progress."}


@router.get("/comparison", summary="Model Comparison Table")
def model_comparison(service: TrainService = Depends(get_train_service)):
    return service.get_model_comparison()


@router.get("/feature-importance", summary="Feature Importance of Best Model")
def feature_importance(service: TrainService = Depends(get_train_service)):
    return service.get_feature_importance()