from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    timestamp: datetime
    x: float
    y: float
    z: float
    mode: str