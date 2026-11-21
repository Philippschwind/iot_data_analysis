
import logging
import threading
import time
from datetime import datetime, timezone
from math import isfinite

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.database.models import SensorReading

logger = logging.getLogger(__name__)


class SensorRepository:
    """Database operations for sensor readings."""

    @staticmethod
    def _parse_reading(data: dict) -> SensorReading:
        """Validate MQTT payload and create a database model."""

        timestamp = datetime.fromisoformat(data["timestamp"])

        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must include timezone")

        x = float(data["x"])
        y = float(data["y"])
        z = float(data["z"])

        if not all(isfinite(v) for v in (x, y, z)):
            raise ValueError("Acceleration values must be finite")

        device_id = data["device_id"]
        mode = data["mode"]

        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("Invalid device_id")

        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("Invalid mode")

        return SensorReading(
            device_id=device_id,
            timestamp=timestamp,
            acceleration_x=x,
            acceleration_y=y,
            acceleration_z=z,
            activity=mode,
        )

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------

    def save(self, data: dict) -> int:
        """Save one sensor reading and return its ID."""

        reading = self._parse_reading(data)

        with SessionLocal() as session:
            session.add(reading)
            session.commit()
            return reading.id

    def save_batch(self, data_list: list[dict]) -> int:
        """Save multiple readings in one transaction."""

        if not data_list:
            return 0

        readings = [
            self._parse_reading(data)
            for data in data_list
        ]

        with SessionLocal() as session:
            session.add_all(readings)
            session.commit()

        logger.info("Saved batch of %d readings", len(readings))
        return len(readings)

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    def get_readings(
        self,
        device_id: str | None = None,
        activity: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[dict]:
        """Retrieve sensor readings with optional filters."""

        if limit < 1 or limit > 10000:
            raise ValueError("limit must be between 1 and 10000")

        if offset < 0:
            raise ValueError("offset must not be negative")

        stmt = select(SensorReading)

        if device_id is not None:
            stmt = stmt.where(
                SensorReading.device_id == device_id
            )

        if activity is not None:
            stmt = stmt.where(
                SensorReading.activity == activity
            )

        if start_time is not None:
            stmt = stmt.where(
                SensorReading.timestamp >= start_time
            )

        if end_time is not None:
            stmt = stmt.where(
                SensorReading.timestamp <= end_time
            )

        stmt = (
            stmt.order_by(
                SensorReading.timestamp.desc(),
                SensorReading.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        with SessionLocal() as session:
            readings = session.scalars(stmt).all()
            return [self._to_dict(r) for r in readings]

    def get_latest(
        self,
        device_id: str | None = None,
    ) -> dict | None:
        """Retrieve the latest reading."""

        results = self.get_readings(
            device_id=device_id,
            limit=1,
        )

        return results[0] if results else None

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    def delete_by_id(self, reading_id: int) -> bool:
        """Delete one reading by primary key."""

        with SessionLocal() as session:
            result = session.execute(
                delete(SensorReading).where(
                    SensorReading.id == reading_id
                )
            )
            session.commit()
            return result.rowcount > 0

    def delete_before(self, timestamp: datetime) -> int:
        """Delete all readings older than timestamp."""

        with SessionLocal() as session:
            result = session.execute(
                delete(SensorReading).where(
                    SensorReading.timestamp < timestamp
                )
            )
            session.commit()
            return result.rowcount

    # --------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------

    @staticmethod
    def _to_dict(reading: SensorReading) -> dict:
        """Convert ORM object to serializable dictionary."""

        return {
            "id": reading.id,
            "device_id": reading.device_id,
            "timestamp": reading.timestamp.isoformat(),
            "x": reading.acceleration_x,
            "y": reading.acceleration_y,
            "z": reading.acceleration_z,
            "mode": reading.activity,
        }


class SensorBatchWriter:
    """
    Buffered sensor writer.

    Flushes when:
    - batch_size is reached
    - flush_interval seconds have elapsed
    - stop() is called
    """

    def __init__(
        self,
        repository: SensorRepository,
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ):
        if batch_size < 1 or flush_interval <= 0:
            raise ValueError("Invalid batch configuration")

        self.repository = repository
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._flush_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        """Start periodic background flushing."""

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._flush_loop,
            daemon=True,
            name="sensor-batch-writer",
        )
        self._thread.start()

    def add(self, data: dict):
        """Validate and add a reading to the buffer."""

        # Validate before buffering
        self.repository._parse_reading(data)

        with self._lock:
            self._buffer.append(data.copy())
            should_flush = len(self._buffer) >= self.batch_size

        if should_flush:
            self.flush()

    def flush(self) -> int:
        """Write buffered readings to the database."""

        with self._flush_lock:
            with self._lock:
                if not self._buffer:
                    return 0

                batch = self._buffer
                self._buffer = []

            try:
                return self.repository.save_batch(batch)

            except Exception:
                # Restore failed batch without losing newer data
                with self._lock:
                    self._buffer = batch + self._buffer

                logger.exception("Batch write failed")
                raise

    def _flush_loop(self):
        """Periodically flush pending readings."""

        while not self._stop_event.wait(self.flush_interval):
            try:
                self.flush()
            except Exception:
                logger.exception("Periodic flush failed")

    def stop(self):
        """Stop background thread and flush remaining data."""

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()
            self._thread = None

        self.flush()
