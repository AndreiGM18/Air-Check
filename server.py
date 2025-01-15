import os
import time
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread
import queue

app = Flask(__name__)
socketio = SocketIO(app)

# MQTT Broker details
mqtt_broker = '192.168.69.15'
mqtt_port = 1883

# MQTT client initialization
client = mqtt.Client()

# Dictionary to store data for each topic
data_sources = {}

# Store threshold and alert trigger value
current_threshold = 40
alert_trigger_value = 100

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe('air_quality/reading')
    client.subscribe('air_quality/reading2')
    client.subscribe('LED')  # Subscribe to the LED topic

def on_message(client, userdata, msg):
    global current_threshold, alert_trigger_value
    topic = msg.topic
    message = msg.payload.decode()
    
    print(f"Received message from {topic}: {message}")

    if topic == "LED":
        if message == "ON":
            print("Turning LED ON from Flask!")
        elif message == "OFF":
            print("Turning LED OFF from Flask!")
        return

    try:
        sensor_value = float(message)
    except ValueError:
        print(f"Error: Unable to convert {message} to float")
        return
    
    timestamp = int(time.time())  # Use the current timestamp as the x-axis value
    if topic not in data_sources:
        data_sources[topic] = {'timestamps': [], 'sensor_data': []}

    # Add data to the corresponding source
    data_sources[topic]['timestamps'].append(timestamp)
    data_sources[topic]['sensor_data'].append(sensor_value)

    # Count how many points exceed the threshold
    threshold_exceeded_count = sum(1 for value in data_sources[topic]['sensor_data'] if value > current_threshold)

    print(f"Threshold exceeded count: {threshold_exceeded_count}")

    # If threshold exceeded, control LED based on alert trigger value
    if threshold_exceeded_count >= alert_trigger_value:
        print("Threshold exceeded the alert trigger value! Sending signal to turn LED ON!")
        client.publish('LED', 'ON')  # Send signal to turn LED on
    else:
        print("Threshold not exceeded the alert trigger value! Sending signal to turn LED OFF!")
        client.publish('LED', 'OFF')  # Send signal to turn LED off

    # Emit the data to the frontend
    socketio.emit('new_data', {
        'topic': topic,
        'timestamps': data_sources[topic]['timestamps'],
        'sensor_data': data_sources[topic]['sensor_data']
    })

# Start MQTT client in a thread
def mqtt_thread():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_forever()

@app.route('/')
def index():
    return render_template('index.html')

# Handle threshold change from frontend
@socketio.on('update_threshold')
def update_threshold(data):
    global current_threshold, alert_trigger_value
    current_threshold = data.get('threshold', 40)  # Default to 40 if not specified
    alert_trigger_value = data.get('alert_trigger', 100)  # Default to 100 if not specified
    print(f"Threshold updated to: {current_threshold}, Alert trigger set to: {alert_trigger_value}")

if __name__ == "__main__":
    # Start the MQTT client in a separate thread
    mqtt_thread_instance = Thread(target=mqtt_thread)
    mqtt_thread_instance.daemon = True
    mqtt_thread_instance.start()

    # Run Flask app
    socketio.run(app, host='0.0.0.0', port=5000, 
                 ssl_context=('server.crt', 'server.key'))  # Enable SSL
