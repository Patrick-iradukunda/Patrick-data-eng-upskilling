from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ModelNotTrainedError(Exception):
    pass


class DataNotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ModelNotTrainedError)
    async def model_not_trained_handler(request: Request, exc: ModelNotTrainedError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Model not trained yet. Call POST /api/v1/train first."
            },
        )

    @app.exception_handler(DataNotFoundError)
    async def data_not_found_handler(request: Request, exc: DataNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )