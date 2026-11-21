
from fastapi import FastAPI

from backend.api.routes.readings import router as readings_router


app = FastAPI(
    title="IoT Motion Analysis API",
    description=(
        "REST API for storing, retrieving and analyzing "
        "motion sensor data from Raspberry Pi devices."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "iot-motion-api",
    }


app.include_router(readings_router)
