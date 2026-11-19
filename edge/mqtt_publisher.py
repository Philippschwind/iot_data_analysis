
import json
import logging
import os
import time
from datetime import datetime, timezone
from threading import Event

import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


class MQTTPublisher:

    def __init__(
        self,
        host: str,
        port: int = 1883,
        device_id: str = "raspberry01",
        qos: int = 0,
    ):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.qos = qos
        self.topic = f"devices/{device_id}/acceleration"
        self.connected = Event()

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"{device_id}-publisher",
        )

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def _on_connect(
        self, client, userdata, flags, reason_code, properties
    ):
        if reason_code == 0:
            self.connected.set()
            logger.info("Connected to MQTT broker")
        else:
            logger.error("Connection failed: %s", reason_code)

    def _on_disconnect(
        self, client, userdata, flags, reason_code, properties
    ):
        self.connected.clear()
        logger.info("Disconnected from MQTT broker: %s", reason_code)

    def connect(self, timeout: float = 10.0):
        self.client.connect_async(self.host, self.port, keepalive=60)
        self.client.loop_start()

        if not self.connected.wait(timeout):
            self.disconnect()
            raise TimeoutError("Could not connect to MQTT broker")

    def publish(self, x: float, y: float, z: float) -> bool:
        if not self.connected.is_set():
            logger.warning("Not connected. Measurement dropped.")
            return False

        data = {
            "device_id": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "x": float(x),
            "y": float(y),
            "z": float(z),
        }

        payload = json.dumps(data)

        result = self.client.publish(
            topic=self.topic,
            payload=payload,
            qos=self.qos,
            retain=False,
        )

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error("Failed to publish message")
            return False

        logger.debug("Queued for publishing: %s", payload)

        return True

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        self.connected.clear()


# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    publisher = MQTTPublisher(
        host=os.environ["MQTT_HOST"],
        port=int(os.getenv("MQTT_PORT", "1883")),
    )

    try:
        publisher.connect()

        while True:
            publisher.publish(x=0.12, y=-0.03, z=0.85)
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:
        publisher.disconnect()
