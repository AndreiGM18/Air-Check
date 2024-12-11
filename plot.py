import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from time import sleep

mqtt_broker = "192.168.253.15"
mqtt_port = 1883
mqtt_topic = "air_quality/reading"

timestamps = []
sensor_data = []

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message}")

    timestamps.append(len(timestamps))
    sensor_data.append(float(message))

    plt.clf()
    plt.plot(timestamps, sensor_data, label="Air Quality Index")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Air Quality Index (sensor value)")
    plt.title("Air Quality over Time")
    plt.legend()
    plt.pause(1)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

plt.ion()
plt.figure(figsize=(10, 5))
plt.xlabel("Time (seconds)")
plt.ylabel("Air Quality Index")
plt.title("Air Quality over Time")

try:
    while True:
        client.loop() 
        sleep(1)
except KeyboardInterrupt:
    print("Disconnected from MQTT Broker.")
    client.disconnect()
