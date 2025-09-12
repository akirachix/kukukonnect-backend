import json
import paho.mqtt.client as mqtt
import ssl
import requests
from django.conf import settings

BROKER = settings.MQTT_BROKER
PORT = settings.MQTT_PORT
USERNAME = settings.MQTT_USERNAME
PASSWORD = settings.MQTT_PASSWORD
SENSOR_TOPIC = settings.SENSOR_TOPIC

API_URL_SENSOR = settings.API_URL_SENSOR

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        return("Connected to MQTT Broker")
        client.subscribe(SENSOR_TOPIC, qos=1)
        return(f"Subscribed to: {SENSOR_TOPIC}")
    else:
        return(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", errors="ignore").strip()
        data = json.loads(payload_str)

        if msg.topic == SENSOR_TOPIC and isinstance(data, dict):
            api_payload = {
                "temperature": data.get("avg_temp"),
                "humidity": data.get("avg_humidity"),
                "timestamp": data.get("timestamp"), 
                "device_id": data.get("device_id") 
            }

            api_payload = {k: v for k, v in api_payload.items() if v is not None}

            if API_URL_SENSOR:
                try:
                    response = requests.post(API_URL_SENSOR, json=api_payload, timeout=5)
                    if response.status_code in [200, 201]:
                        return("Sensor data successfully saved to Django!")
                    else:
                        return(f"API Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    return(f"Failed to reach API: {e}")
            else:
                return("API_URL_SENSOR is not defined.")
    except json.JSONDecodeError:
        return(f"Invalid JSON on topic '{msg.topic}': {payload_str}")
    except Exception as e:
        return(f"Error processing message: {e}")

client = mqtt.Client(client_id="", protocol=mqtt.MQTTv5)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)

if USERNAME and PASSWORD:
    client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    if not BROKER:
        return("MQTT_BROKER not configured in settings.")
        

    print(f"Connecting to {BROKER}:{PORT}...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
        return("MQTT client is running and listening for sensor data.")
    except Exception as e:
        return(f"Connection error: {e}")
