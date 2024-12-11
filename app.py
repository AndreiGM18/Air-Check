import os
import time
import subprocess
import socket
import requests
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_from_directory
import paho.mqtt.client as mqtt
from threading import Thread

app = Flask(__name__)

# Get the local IP address of the server (MQTT Broker)
def get_local_ip():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print(f"Local IP address (server) is: {ip_address}")
    return ip_address

# MQTT Broker details
mqtt_broker = get_local_ip()  # Automatically get the local IP address
mqtt_port = 1883
mqtt_topic = "air_quality/reading"

timestamps = []
sensor_data = []

# Plot image path
plot_image_path = os.path.join(os.getcwd(), "static", "plot.png")

# Initialize MQTT client
client = mqtt.Client()

# Check if Mosquitto is running, if not, start it
def check_mosquitto():
    try:
        # Check if Mosquitto is running
        result = subprocess.run(["tasklist"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()

        if "mosquitto.exe" in output:
            print("Mosquitto is already running!")
        else:
            print("Mosquitto is not running. Starting Mosquitto now...")
            start_mosquitto()
    except Exception as e:
        print(f"Error checking Mosquitto: {e}")

# Start Mosquitto if it is not running
def start_mosquitto():
    try:
        # Command to start Mosquitto
        command = r'"C:\Program Files\mosquitto\mosquitto.exe" -v -c "C:\Program Files\mosquitto\mosquitto.conf"'
        subprocess.Popen(command, shell=True)
        print("Mosquitto has been started successfully.")
    except Exception as e:
        print(f"Error starting Mosquitto: {e}")

# MQTT client callbacks
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
    # Check if Mosquitto is running before starting the Flask app
    check_mosquitto()

    # Start the MQTT client in a separate thread
    mqtt_thread_instance = Thread(target=mqtt_thread)
    mqtt_thread_instance.daemon = True
    mqtt_thread_instance.start()

    # Run Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)
