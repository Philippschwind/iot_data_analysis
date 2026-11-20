from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Identity,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.connection import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    device_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    acceleration_x: Mapped[float] = mapped_column(Float)
    acceleration_y: Mapped[float] = mapped_column(Float)
    acceleration_z: Mapped[float] = mapped_column(Float)

    activity: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )