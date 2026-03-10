from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Flight Fare Prediction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATA_PATH: str = "data/Flight_Price_Dataset_of_Bangladesh.csv"
    MODEL_DIR: str = "saved_models"

    class Config:
        env_file = ".env"

settings = Settings()