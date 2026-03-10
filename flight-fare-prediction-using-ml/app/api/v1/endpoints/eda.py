from fastapi import APIRouter, Depends
from app.services.eda_service import EDAService
from app.schemas.eda import (
    DescriptiveStatsResponse,
    FareDistributionResponse,
    KPIResponse,
    MonthlyTrendResponse,
)
from app.dependencies import get_eda_service

router = APIRouter()


@router.get("/stats", summary="Descriptive Statistics")
def descriptive_stats(service: EDAService = Depends(get_eda_service)):
    return service.get_descriptive_stats()


@router.get("/fare-distribution", summary="Total Fare Distribution")
def fare_distribution(service: EDAService = Depends(get_eda_service)):
    return service.get_fare_distribution()


@router.get("/kpis", summary="Key Performance Indicators")
def kpis(service: EDAService = Depends(get_eda_service)):
    return service.get_kpis()


@router.get("/correlation", summary="Feature Correlation Matrix")
def correlation(service: EDAService = Depends(get_eda_service)):
    return service.get_correlation()


@router.get("/fare-by-airline", summary="Fare Statistics by Airline")
def fare_by_airline(service: EDAService = Depends(get_eda_service)):
    return service.get_fare_by_airline()


@router.get("/fare-by-season", summary="Fare Statistics by Season")
def fare_by_season(service: EDAService = Depends(get_eda_service)):
    return service.get_fare_by_season()


@router.get("/fare-by-route", summary="Top 10 Routes by Average Fare")
def fare_by_route(service: EDAService = Depends(get_eda_service)):
    return service.get_fare_by_route()


@router.get("/monthly-trend", summary="Monthly Average Fare Trend")
def monthly_trend(service: EDAService = Depends(get_eda_service)):
    return service.get_monthly_trend()