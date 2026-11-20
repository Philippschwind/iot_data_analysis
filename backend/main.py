import logging
import time

from backend.mqtt_subscriber import MQTTSubscriber
from backend.database.connection import Base, engine
from backend.database.models import SensorReading
from backend.database.repository import save_sensor_reading


def main():
    logging.basicConfig(level=logging.INFO)

    # Create tables if necessary
    Base.metadata.create_all(bind=engine)

    # Initialize MQTT subscriber
    subscriber = MQTTSubscriber(
        message_handler=save_sensor_reading,
    )

    try:
        subscriber.connect()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:
        subscriber.disconnect()


if __name__ == "__main__":
    main()