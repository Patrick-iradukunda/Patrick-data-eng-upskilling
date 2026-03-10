from fastapi import APIRouter, Depends, Query
from app.services.data_service import DataService
from app.services.cleaning_service import CleaningService
from app.schemas.data import DataSummaryResponse, CleaningReportResponse
from app.dependencies import get_data_service, get_cleaning_service

router = APIRouter()


@router.get("/raw/summary", summary="Raw Dataset Summary")
def raw_summary(service: DataService = Depends(get_data_service)):
    return service.get_raw_summary()


@router.get("/raw/sample", summary="Raw Dataset Sample")
def raw_sample(
    n: int = Query(default=10, ge=1, le=100),
    service: DataService = Depends(get_data_service),
):
    return service.get_raw_sample(n)


@router.get("/cleaned/summary", summary="Cleaned Dataset Summary")
def cleaned_summary(service: DataService = Depends(get_data_service)):
    return service.get_cleaned_summary()


@router.get("/cleaned/sample", summary="Cleaned Dataset Sample")
def cleaned_sample(
    n: int = Query(default=10, ge=1, le=100),
    service: DataService = Depends(get_data_service),
):
    return service.get_cleaned_sample(n)


@router.get("/cleaning-report", summary="Data Cleaning Report")
def cleaning_report(service: CleaningService = Depends(get_cleaning_service)):
    return service.get_cleaning_report()