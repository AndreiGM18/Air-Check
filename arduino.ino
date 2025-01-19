#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "GabitzuPhone";
const char* password = "ukao4362";

const char* mqttServer = "192.168.30.15";
const int mqttPort = 1883;
const char* mqttTopic = "air_quality/reading";
const char* ledTopic = "LED";

const int gasSensorPin = A0; 
int sensorValue = 0;

const int ledPin = D2;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
	Serial.begin(9600);
	pinMode(ledPin, OUTPUT);

	Serial.println("ESP setup started...");

	connectToWiFi();

	client.setServer(mqttServer, mqttPort);
	client.setCallback(mqttCallback);

	client.subscribe(ledTopic);
}

void loop() {
	if (!client.connected()) {
		reconnectMQTT();
	}
	client.loop();

	sensorValue = analogRead(gasSensorPin);

	client.publish(mqttTopic, String(sensorValue).c_str());

	Serial.print("Sensor Value: ");
	Serial.println(sensorValue);

	delay(1000);
}

void connectToWiFi() {
	Serial.print("Connecting to Wi-Fi...");
	WiFi.begin(ssid, password);

	while (WiFi.status() != WL_CONNECTED) {
		delay(1000);
		Serial.print(".");
	}

	Serial.println();
	Serial.println("Connected to Wi-Fi");
	Serial.print("IP Address: ");
	Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
	while (!client.connected()) {
		Serial.print("Attempting MQTT connection...");
		if (client.connect("ESP8266Client")) {
			Serial.println("Connected to MQTT broker");
			client.subscribe(ledTopic);
		} else {
			Serial.print("Failed, rc=");
			Serial.print(client.state());
			delay(5000);
		}
	}
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
	String message = "";
	for (int i = 0; i < length; i++) {
		message += (char)payload[i];
	}

	Serial.print("Message arrived [");
	Serial.print(topic);
	Serial.print("] ");
	Serial.println(message);

	if (String(topic) == ledTopic) {
		if (message == "ON") {
			digitalWrite(ledPin, HIGH);
			Serial.println("LED is ON");
		} else if (message == "OFF") {
			digitalWrite(ledPin, LOW);
			Serial.println("LED is OFF");
		}
	}
}