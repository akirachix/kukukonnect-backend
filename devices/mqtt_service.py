import json
import paho.mqtt.client as mqtt
from django.conf import settings
from devices.models import MCU
import ssl
from asgiref.sync import async_to_sync
from django.db import transaction
from decimal import Decimal
import os

from dotenv import load_dotenv
load_dotenv()

BROKER = os.getenv("MQTT_BROKER", "broker.emqx.io")
PORT = int(os.getenv("MQTT_PORT", 8883))
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", 60))
TOPIC_PREFIX = "esp32"

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        if USERNAME and PASSWORD:
            self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("MQTT Client connected successfully")
            self.client.subscribe(f"{TOPIC_PREFIX}/#")
        else:
            print(f"MQTT Client failed to connect with code {rc}")
    def on_disconnect(self, client, userdata, rc):
        print("MQTT Client disconnected")

    @transaction.atomic
    def save_or_update_mcu(self, device_id, data):
        mcu, created = MCU.objects.get_or_create(
            device_id=device_id,
            defaults={
                "temp_threshold_min": data["temp_min"],
                "temp_threshold_max": data["temp_max"],
                "humidity_threshold_min": data["humidity_min"],
                "humidity_threshold_max": data["humidity_max"],
            }
        )
        if not created:
            if "temp_min" in data:
                mcu.temp_threshold_min = data['temp_min']
            if "temp_max" in data:
                mcu.temp_threshold_max = data['temp_max']
            if "humidity_min" in data:
                mcu.humidity_threshold_min = data['humidity_min']
            if "humidity_max" in data:
                mcu.humidity_threshold_max = data['humidity_max']
            mcu.save()
        return(f"Saved MCU {device_id} thresholds to DB")

    def on_message(self, client, userdata, msg):
        print(f"Received MQTT message on topic {msg.topic}: {msg.payload}")
        try:
            payload = json.loads(msg.payload.decode())
            device_id = payload.get("device_id")
            temp_min = payload.get("temp_min")
            temp_max = payload.get("temp_max")
            humidity_min = payload.get("hum_min")
            humidity_max = payload.get("hum_max")
            if device_id and temp_min is not None and temp_max is not None and humidity_min is not None and humidity_max is not None:
                data = {
                    "temp_min": Decimal(temp_min),
                    "temp_max": Decimal(temp_max),
                    "humidity_min": Decimal(humidity_min),
                    "humidity_max": Decimal(humidity_max),
                }
                self.save_or_update_mcu(device_id, data)
                return(f"Updated MCU {device_id} from MQTT message")
            else:
                return("MQTT message missing device_id or one of the threshold values")
        except Exception as e:
            return("Error processing MQTT message:", e)
    def connect(self):
        self.client.connect(BROKER, PORT, KEEPALIVE)
        self.client.loop_start()
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
    def publish_thresholds(self, mcu_id, temp_min, temp_max, humidity_min=None, humidity_max=None):
        topic = f"{TOPIC_PREFIX}/sensor_data"
        payload = {
            "device_id": mcu_id,
            "thresholds": {
                "temp_min": temp_min,
                "temp_max": temp_max,
            }
        }
        if humidity_min is not None:
            payload["thresholds"]["humidity_min"] = humidity_min
        if humidity_max is not None:
            payload["thresholds"]["humidity_max"] = humidity_max
        json_payload = json.dumps(payload)
        result = self.client.publish(topic, json_payload, qos=1)
        status = result[0]
        if status == 0:
            return(f"Published thresholds to {topic}")
        else:
            return(f"Failed to publish to {topic}")
mqtt_client = MQTTClient()
mqtt_client.connect()
