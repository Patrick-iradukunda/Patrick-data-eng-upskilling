from app.services.data_service import DataService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.train_service import TrainService
from app.services.predict_service import PredictService


def get_data_service() -> DataService:
    return DataService()


def get_cleaning_service() -> CleaningService:
    return CleaningService()


def get_eda_service() -> EDAService:
    return EDAService()


def get_train_service() -> TrainService:
    return TrainService()


def get_predict_service() -> PredictService:
    return PredictService()