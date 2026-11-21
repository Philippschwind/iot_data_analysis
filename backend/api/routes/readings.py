
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas import SensorReadingResponse
from backend.database.repository import SensorRepository


router = APIRouter(
    prefix="/readings",
    tags=["Sensor Readings"],
)

repository = SensorRepository()


@router.get(
    "",
    response_model=list[SensorReadingResponse],
)
def get_readings(
    device_id: str | None = None,
    activity: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
):
    return repository.get_readings(
        device_id=device_id,
        activity=activity,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/latest",
    response_model=SensorReadingResponse,
)
def get_latest(device_id: str | None = None):
    reading = repository.get_latest(device_id)

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="No sensor readings found",
        )

    return reading
