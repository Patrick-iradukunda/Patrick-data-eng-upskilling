from fastapi import APIRouter, Depends
from app.schemas.predict import PredictRequest, PredictResponse
from app.services.predict_service import PredictService
from app.dependencies import get_predict_service

router = APIRouter()


@router.post("/", summary="Predict Flight Fare", response_model=PredictResponse)
def predict_fare(
    payload: PredictRequest,
    service: PredictService = Depends(get_predict_service),
):
    return service.predict(payload.model_dump())