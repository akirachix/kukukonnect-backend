import json
import paho.mqtt.client as mqtt
import ssl
import requests

TOPIC = "esp32/relay_status"

BROKER = settings.MQTT_BROKER
PORT = settings.MQTT_PORT
USERNAME = settings.MQTT_USERNAME
PASSWORD = settings.MQTT_PASSWORD
API_URL = settings.API_URL
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(TOPIC, qos=1)
    else:
        print(f"Connection failed with code {rc}")
def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode("utf-8", errors="ignore").strip()
        data = json.loads(payload_str)
        print(f"\nTopic: {msg.topic} QoS: {msg.qos}")
        if isinstance(data, dict): 
            def safe_get(key):
                val = data.get(key)
                return val if val is not None else "N/A"
            api_payload = {
                "device_id": safe_get('device_id'),
                "temperature": float(safe_get('temperature_celsius')) if safe_get('temperature_celsius') != "N/A" else None,
                "humidity": float(safe_get('humidity_percent')) if safe_get('humidity_percent') != "N/A" else None
            }
            
            api_payload = {k: v for k, v in api_payload.items() if v is not None}
            response = requests.post(API_URL, json=api_payload)
            if response.status_code == 201:
                print("Temperature and humidity data successfully sent to API")
            else:
                print(f"Failed to send data to API: {response.status_code} - {response.text}")
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
print("Connecting to broker...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()
