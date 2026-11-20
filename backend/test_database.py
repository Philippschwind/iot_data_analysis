from sqlalchemy import select, text

from backend.database.connection import (
    Base,
    engine,
    SessionLocal,
)
from backend.database.models import SensorReading


def main():
    print("Starting database test...", flush=True)

    print("Connecting to PostgreSQL...", flush=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful:", result.scalar(), flush=True)

    print("Creating tables...", flush=True)
    Base.metadata.create_all(bind=engine)

    print("Database tables created.")

    # Insert test data
    with SessionLocal() as session:
        reading = SensorReading(
            device_id="raspberry-01",
            acceleration_x=0.1,
            acceleration_y=0.2,
            acceleration_z=0.3,
            activity="walking",
        )

        session.add(reading)
        session.commit()

        print(f"Saved reading with ID: {reading.id}")

    # Read data
    with SessionLocal() as session:
        statement = select(SensorReading).order_by(
            SensorReading.id.desc()
        ).limit(5)

        readings = session.scalars(statement).all()

        for reading in readings:
            print(
                reading.id,
                reading.device_id,
                reading.acceleration_x,
                reading.acceleration_y,
                reading.acceleration_z,
                reading.activity,
            )


if __name__ == "__main__":
    main()