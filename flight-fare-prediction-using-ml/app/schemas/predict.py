from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    airline: str = Field(..., example="Us-Bangla Airlines")
    source: str = Field(..., example="Dhaka")
    destination: str = Field(..., example="Chittagong")
    base_fare: float = Field(..., gt=0, example=3500.0)
    tax_surcharge: float = Field(..., ge=0, example=800.0)
    month: int = Field(..., ge=1, le=12, example=6)
    day: int = Field(..., ge=1, le=31, example=15)
    weekday: int = Field(..., ge=0, le=6, example=2)
    season: str = Field(..., example="summer")

    class Config:
        json_schema_extra = {
            "example": {
                "airline": "Us-Bangla Airlines",
                "source": "Dhaka",
                "destination": "Chittagong",
                "base_fare": 3500.0,
                "tax_surcharge": 800.0,
                "month": 6,
                "day": 15,
                "weekday": 2,
                "season": "summer",
            }
        }


class PredictResponse(BaseModel):
    model_config = {'protected_namespaces': ()}
    predicted_fare: float
    model_used: str
    inputs_received: dict
    note: str