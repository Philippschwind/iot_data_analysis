
import logging
import os
import time

from mqtt_publisher import MQTTPublisher
from data_simulation import DataSimulation

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
# Configuration
SAMPLE_RATE = 20           # Hz
MODE_DURATION = 10         # Seconds per mode
MODES = ["idle", "walking", "shaking"]

MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_DEVICE_ID = os.getenv("MQTT_DEVICE_ID", "raspberry01")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    publisher = MQTTPublisher(
        host=MQTT_HOST,
        port=MQTT_PORT,
        device_id=MQTT_DEVICE_ID,
    )

    publisher.connect()

    sample_interval = 1.0 / SAMPLE_RATE

    simulator = DataSimulation()

    try:
        while True:
            for mode in MODES:
                logger.info("Starting mode: %s", mode)

                start_time = time.monotonic()
                next_sample = start_time

                while time.monotonic() - start_time < MODE_DURATION:
                    data = simulator.generate_sample(mode)

                    publisher.publish(
                        x=data["x"],
                        y=data["y"],
                        z=data["z"],
                        mode=mode
                    )

                    next_sample += sample_interval
                    sleep_time = next_sample - time.monotonic()

                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        next_sample = time.monotonic()

    except KeyboardInterrupt:
        logger.info("Stopping simulation")

    finally:
        publisher.disconnect()


if __name__ == "__main__":
    main()
