import os
import time
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_from_directory
import paho.mqtt.client as mqtt
from threading import Thread

# Setup Flask app
app = Flask(__name__)

# MQTT Broker details
mqtt_broker = "192.168.253.15"
mqtt_port = 1883
mqtt_topic = "air_quality/reading"

timestamps = []
sensor_data = []

# Plot image path
plot_image_path = os.path.join(os.getcwd(), "static", "plot.png")

# Initialize MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received message: {message}")

    timestamps.append(len(timestamps))
    sensor_data.append(float(message))

    # Create the plot and save it as an image
    plt.clf()
    plt.plot(timestamps, sensor_data, label="Air Quality Index")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Air Quality Index (sensor value)")
    plt.title("Air Quality over Time")
    plt.legend()
    plt.savefig(plot_image_path)  # Save the plot as an image

    # Close the plot after saving
    plt.close()

def mqtt_thread():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/plot.png')
def plot_image():
    return send_from_directory(os.path.join(os.getcwd(), 'static'), 'plot.png')

if __name__ == "__main__":
    # Start the MQTT client in a separate thread
    mqtt_thread_instance = Thread(target=mqtt_thread)
    mqtt_thread_instance.daemon = True
    mqtt_thread_instance.start()

    # Run Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
