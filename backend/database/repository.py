import logging
from datetime import datetime
from math import isfinite

from backend.database.connection import SessionLocal
from backend.database.models import SensorReading

logger = logging.getLogger(__name__)


def save_sensor_reading(data: dict):
    try:
        timestamp = datetime.fromisoformat(
            data["timestamp"]
        )

        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must include timezone")

        x = float(data["x"])
        y = float(data["y"])
        z = float(data["z"])

        if not all(isfinite(v) for v in (x, y, z)):
            raise ValueError("Acceleration values must be finite")

        reading = SensorReading(
            device_id=str(data["device_id"]),
            timestamp=timestamp,
            acceleration_x=x,
            acceleration_y=y,
            acceleration_z=z,
            activity=str(data["mode"]),
        )

    except (KeyError, ValueError, TypeError) as error:
        logger.warning("Invalid sensor data: %s", error)
        return

    try:
        with SessionLocal() as session:
            session.add(reading)
            session.commit()

            logger.info(
                "Saved reading: id=%s, activity=%s",
                reading.id,
                reading.activity,
            )

    except Exception:
        logger.exception("Failed to save sensor reading")