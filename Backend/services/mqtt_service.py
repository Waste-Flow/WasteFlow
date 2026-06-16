import json
import httpx
import paho.mqtt.client as mqtt
from loguru import logger
from core.config import settings

BACKEND_URL = "http://localhost:8000"

def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT connected with code {rc}")
    client.subscribe(settings.MQTT_TOPIC)

def on_message(client, userdata, msg):
    """
    ESP8266 should publish JSON to topic: dustbin/sensors/<bin_code>
    Payload format: {"bin_code": "BIN-001", "distance_cm": 35.5}
    """
    try:
        payload = json.loads(msg.payload.decode())
        logger.info(f"MQTT received: {payload}")

        # Forward data to the FastAPI sensor endpoint
        response = httpx.post(f"{BACKEND_URL}/dustbins/sensor-data", json=payload)
        logger.info(f"Sensor data forwarded: {response.status_code}")
    except Exception as e:
        logger.error(f"MQTT message error: {e}")

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)
        client.loop_start()
        logger.info("MQTT client started")
    except Exception as e:
        logger.warning(f"MQTT not available: {e}. Sensor data can still be sent via HTTP.")
