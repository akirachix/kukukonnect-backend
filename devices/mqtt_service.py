import json
import paho.mqtt.client as mqtt
from django.conf import settings
import ssl
from asgiref.sync import async_to_sync
from django.db import transaction
from decimal import Decimal
import requests
from devices.models import MCU


KEEPALIVE = getattr(settings, "MQTT_KEEPALIVE", 60)
BROKER = settings.MQTT_BROKER
PORT = settings.MQTT_PORT
USERNAME = settings.MQTT_USERNAME
PASSWORD = settings.MQTT_PASSWORD
SENSOR_TOPIC = settings.SENSOR_TOPIC

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
            self.client.subscribe(f"{SENSOR_TOPIC}/#")
        else:
            print(f"MQTT Client failed to connect with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("MQTT Client disconnected")

    @transaction.atomic
    def save_or_update_mcu(self, device_id, data):
        mcu, created = MCU.objects.get_or_create(pk=device_id)
        if "temp_min" in data:
            mcu.temp_threshold_min = data['temp_min']
        if "temp_max" in data:
            mcu.temp_threshold_max = data['temp_max']
        if "humidity_min" in data:
            mcu.humidity_threshold_min = data['humidity_min']
        if "humidity_max" in data:
            mcu.humidity_threshold_max = data['humidity_max']
        mcu.save()
        print(f"Saved MCU {device_id} thresholds to DB")

    def on_message(self, client, userdata, msg):
        print(f"Received MQTT message on topic {msg.topic}: {msg.payload}")
        try:
            payload = json.loads(msg.payload.decode())
            device_id = payload.get("device_id")
            thresholds = payload.get("thresholds", {})
            if device_id and thresholds:
                data = {
                    "temp_min": Decimal(thresholds.get("temp_min", 0.00)),
                    "temp_max": Decimal(thresholds.get("temp_max", 0.00)),
                    "humidity_min": Decimal(thresholds.get("humidity_min", 0.00)),
                    "humidity_max": Decimal(thresholds.get("humidity_max", 0.00)),
                }
                async_to_sync(self.save_or_update_mcu)(device_id, data)
                print(f"Updated MCU {device_id} from MQTT message")

                api_payload = {
                    "device_id": device_id,
                    "temp_min": float(data["temp_min"]),
                    "temp_max": float(data["temp_max"]),
                    "humidity_min": float(data["humidity_min"]),
                    "humidity_max": float(data["humidity_max"]),
                }

                if API_URL_THRESHOLDS:
                    try:
                        response = requests.post(API_URL_THRESHOLDS, json=api_payload, timeout=5)
                        if response.status_code in [200, 201]:
                            print("Thresholds successfully posted to external API")
                        else:
                            print(f"API error: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to post thresholds to API: {e}")
                else:
                    print("API_URL_THRESHOLDS not configured in settings.")
            else:
                print("MQTT message missing device_id or thresholds")
        except Exception as e:
            print("Error processing MQTT message:", e)

    def connect(self):
        self.client.connect(BROKER, PORT, KEEPALIVE)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish_thresholds(self, mcu_id, temp_min, temp_max, humidity_min=None, humidity_max=None):
        topic = f"{SENSOR_TOPIC}"
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
            print(f"Published thresholds to {topic}")
        else:
            print(f"Failed to publish to {topic}")


mqtt_client = MQTTClient()
mqtt_client.connect()
