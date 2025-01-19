import time
import paho.mqtt.client as mqtt
from flask import Flask, get_flashed_messages, render_template, redirect, url_for, flash, request, session
from flask_socketio import SocketIO
from threading import Thread
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
socketio = SocketIO(app)

# Database configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_USERNAME'] = 'priotmitran@gmail.com'
app.config['MAIL_PASSWORD'] = 'hyvo utrf kwqm gdrn'

db = SQLAlchemy(app)

# MQTT Broker details
mqtt_broker = '192.168.30.15'
mqtt_port = 1883

# MQTT client initialization
client = mqtt.Client()

# Dictionary to store data for each topic
data_sources = {}

# Store threshold and alert trigger value
current_threshold = 40
alert_trigger_value = 100

# Store previous LED state to detect change
previous_led_state = "OFF"

# SQLAlchemy User Model
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)

# Create the database tables
with app.app_context():
	db.create_all()

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
	print(f"Connected to MQTT Broker with result code {rc}")
	client.subscribe('air_quality/reading')
	client.subscribe('LED')

def on_message(client, userdata, msg):
	global current_threshold, alert_trigger_value, previous_led_state
	topic = msg.topic
	message = msg.payload.decode()

	print(f"Received message from {topic}: {message}")

	if topic == "LED":
		if message == "ON" and previous_led_state == "OFF":
			print("LED turned ON, sending email warning...")
			send_led_warning_email(userdata['email'])

		previous_led_state = message

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

	timestamp = int(time.time())
	if topic not in data_sources:
		data_sources[topic] = {'timestamps': [], 'sensor_data': []}

	data_sources[topic]['timestamps'].append(timestamp)
	data_sources[topic]['sensor_data'].append(sensor_value)

	if len(data_sources[topic]['timestamps']) > 100:
		data_sources[topic]['timestamps'].pop(0)
		data_sources[topic]['sensor_data'].pop(0)

	threshold_exceeded_count = sum(1 for value in data_sources[topic]['sensor_data'] if value > current_threshold)

	print(f"Threshold exceeded count: {threshold_exceeded_count}")

	if threshold_exceeded_count >= alert_trigger_value:
		print("Threshold exceeded the alert trigger value! Sending signal to turn LED ON!")
		client.publish('LED', 'ON')
	else:
		print("Threshold not exceeded the alert trigger value! Sending signal to turn LED OFF!")
		client.publish('LED', 'OFF')

	socketio.emit('new_data', {
		'topic': topic,
		'timestamps': data_sources[topic]['timestamps'],
		'sensor_data': data_sources[topic]['sensor_data']
	})

# Start MQTT client in a thread
def mqtt_thread(email):
	client.on_connect = on_connect
	client.on_message = on_message
	client.user_data_set({'email': email})
	client.connect(mqtt_broker, mqtt_port, 60)
	client.loop_forever()

@app.route('/')
def index():
	if 'username' not in session:
		return redirect(url_for('login'))
	return render_template('index.html')

# Handle threshold change from frontend
@socketio.on('update_threshold')
def update_threshold(data):
	global current_threshold, alert_trigger_value
	current_threshold = data.get('threshold', 40)
	alert_trigger_value = data.get('alert_trigger', 100)
	print(f"Threshold updated to: {current_threshold}, Alert trigger set to: {alert_trigger_value}")

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']

		user_exists = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
		if user_exists:
			flash("Username or Email already exists!", "danger")
			return redirect(url_for('register'))

		password_hash = generate_password_hash(password)

		new_user = User(username=username, email=email, password=password_hash)
		db.session.add(new_user)
		db.session.commit()

		send_confirmation_email(email)

		flash("Registration successful! Please log in.", "success")
		return redirect(url_for('login'))
	
	return render_template('register.html')

# Function to send confirmation email
def send_confirmation_email(user_email):
	subject = "Registration Confirmation"
	body = "Thank you for registering with our service. You can now log in to your account."
	msg = MIMEMultipart()
	msg['From'] = app.config['MAIL_USERNAME']
	msg['To'] = user_email
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		server.sendmail(app.config['MAIL_USERNAME'], user_email, msg.as_string())
		server.quit()
		print("Confirmation email sent successfully!")
	except Exception as e:
		print(f"Error sending confirmation email: {e}")

# Function to send LED warning email using smtplib
def send_led_warning_email(user_email):
	subject = "Warning: Air Quality is Poor"
	body = "Warning: The air quality has exceeded the threshold value. Please take necessary precautions."
	msg = MIMEMultipart()
	msg['From'] = app.config['MAIL_USERNAME']
	msg['To'] = user_email
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		server.sendmail(app.config['MAIL_USERNAME'], user_email, msg.as_string())
		server.quit()
		print("Warning email sent successfully!")
	except Exception as e:
		print(f"Error sending warning email: {e}")

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		user = User.query.filter_by(username=username).first()
		if user and check_password_hash(user.password, password):
			session['username'] = username
			session['email'] = user.email
			flash("Login successful!", "success")
			get_flashed_messages()

			mqtt_thread_instance = Thread(target=mqtt_thread, args=(user.email,))
			mqtt_thread_instance.daemon = True
			mqtt_thread_instance.start()

			return redirect(url_for('index'))
		else:
			flash("Invalid username or password.", "danger")

	return render_template('login.html')

# Logout route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session.pop('username', None)
	session.pop('email', None)
	flash("You have been logged out!", "success")
	return redirect(url_for('login'))

if __name__ == "__main__":
	socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('self_signed_certificate.crt', 'private_key.pem'))
