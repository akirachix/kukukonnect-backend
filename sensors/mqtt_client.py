import json
import paho.mqtt.client as mqtt
import ssl
import requests
from django.conf import settings

BROKER = settings.MQTT_BROKER
PORT = settings.MQTT_PORT
USERNAME = settings.MQTT_USERNAME
PASSWORD = settings.MQTT_PASSWORD
RELAY_TOPIC = settings.RELAY_TOPIC
API_URL = settings.API_URL


latest_message = None

def safe_get(data, key):
    return data.get(key, "N/A")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(RELAY_TOPIC, qos=1)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    global latest_message
    try:
        payload_str = msg.payload.decode("utf-8", errors="ignore").strip()
        latest_message = payload_str 
        data = json.loads(payload_str)
        print(f"\nTopic: {msg.topic} QoS: {msg.qos}")

        if isinstance(data, dict):
            api_payload = {
                "device_id": safe_get(data, "device_id"),
                "timestamp": safe_get(data, "timestamp"),
                "heater_relay": data.get("heater_relay"),
                "fan_relay": data.get("fan_relay"),
                "system_mode": data.get("system_mode"),
                "temperature": data.get("temperature"),
            }
           
            api_payload = {k: v for k, v in api_payload.items() if v is not None}

            if API_URL and api_payload.get("device_id"):
                response = requests.post(API_URL, json=api_payload)
                if response.status_code == 201:
                    print("Relay status data successfully sent to API")
                else:
                    print(f"Failed to send relay status to API: {response.status_code} - {response.text}")
            else:
                print("Missing API_URL or device_id, skipping API post...")
        else:
            print(data)
    except json.JSONDecodeError:
        print(f"\nRaw message received on topic {msg.topic}: {payload_str}")
    except Exception as e:
        print(f"\nError decoding message on topic {msg.topic}: {e}")

client = mqtt.Client(client_id="", protocol=mqtt.MQTTv5)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    print("Connecting to broker...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()