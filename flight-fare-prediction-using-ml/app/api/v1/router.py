from fastapi import APIRouter
from app.api.v1.endpoints import health, data, eda, train, predict

api_router = APIRouter()

api_router.include_router(health.router,   prefix="/health",  tags=["Health"])
api_router.include_router(data.router,     prefix="/data",    tags=["Data"])
api_router.include_router(eda.router,      prefix="/eda",     tags=["EDA"])
api_router.include_router(train.router,    prefix="/train",   tags=["Training"])
api_router.include_router(predict.router,  prefix="/predict", tags=["Prediction"])