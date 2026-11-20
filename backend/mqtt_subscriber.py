
from email.mime import message
import json
import logging
import os
import time
from typing import Callable

import paho.mqtt.client as mqtt

from pathlib import Path
from dotenv import load_dotenv

# Path to project root
BASE_DIR = Path(__file__).resolve().parents[1]

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_DEVICE_ID = os.getenv("MQTT_DEVICE_ID", "raspberry01")

logger = logging.getLogger(__name__)


class MQTTSubscriber:

    def __init__(
        self,
        host: str = MQTT_HOST,
        port: int = MQTT_PORT,
        topic: str = "devices/#",
        qos: int = 0,
        message_handler: Callable[[dict], None] | None = None,
    ):
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.message_handler = message_handler

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="backend-subscriber",
        )

        self.client.enable_logger(logger)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.on_subscribe = self._on_subscribe
    
    def _on_connect(
        self, client, userdata, flags, reason_code, properties
        ):
        if reason_code == 0:
            logger.info("Connected to MQTT broker")

            result, mid = client.subscribe(self.topic, qos=self.qos)

            logger.info(
                "Subscription request: topic=%s, result=%s, mid=%s",
                self.topic,
                result,
                mid,
            )
        else:
            logger.error("Connection failed: %s", reason_code)

    def _on_disconnect(
        self, client, userdata, flags, reason_code, properties
    ):
        logger.info("Disconnected from MQTT broker: %s", reason_code)

    def _on_message(self, client, userdata, message):
        logger.debug(
            "Raw message: topic=%s, payload=%s",
            message.topic,
            message.payload,
        )
        try:
            payload = message.payload.decode("utf-8")
            data = json.loads(payload)

            if not isinstance(data, dict):
                logger.warning("Expected a JSON object")
                return

        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("Invalid message received")
            return

        if self.message_handler is not None:
            try:
                self.message_handler(data)
            except Exception:
                logger.exception("Message processing failed")
        else:
            logger.info("Received: %s", data)

    def _on_subscribe(
        self, client, userdata, mid, reason_code_list, properties
    ):
        logger.info(
            "Subscription acknowledged: mid=%s, reason_codes=%s",
            mid,
            reason_code_list,
        )

    def connect(self):
        self.client.connect_async(self.host, self.port, keepalive=60)
        self.client.loop_start()

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()


# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    subscriber = MQTTSubscriber(
        host=MQTT_HOST,
        port=MQTT_PORT,
    )

    try:
        subscriber.connect()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:
        subscriber.disconnect()
