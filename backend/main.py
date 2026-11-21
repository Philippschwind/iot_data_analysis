
import logging
import time

from backend.mqtt_subscriber import MQTTSubscriber
from backend.database.connection import Base, engine
from backend.database.models import SensorReading
from backend.database.repository import (
    SensorRepository,
    SensorBatchWriter,
)


def main():
    logging.basicConfig(level=logging.INFO)

    Base.metadata.create_all(bind=engine)

    repository = SensorRepository()

    batch_writer = SensorBatchWriter(
        repository=repository,
        batch_size=100,
        flush_interval=5.0,
    )

    batch_writer.start()

    subscriber = MQTTSubscriber(
        message_handler=batch_writer.add,
    )

    try:
        subscriber.connect()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down...")

    finally:
        subscriber.disconnect()
        batch_writer.stop()


if __name__ == "__main__":
    main()
