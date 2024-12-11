#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Wi-Fi credentials
const char* ssid = "GabitzuPhone";
const char* password = "ukao4362";

// MQTT Broker settings
const char* mqttServer = "192.168.253.15";
const int mqttPort = 1883;
const char* mqttTopic = "air_quality/reading";

// Initialize SoftwareSerial for communication between Arduino and ESP-01
SoftwareSerial espSerial(2, 3);

// Pin for gas sensor (connected to A0 on Arduino Uno)
const int gasSensorPin = A0;
int sensorValue = 0;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(74880);
  espSerial.begin(74880);

  Serial.println("Arduino Uno setup started...");

  connectToWiFi();

  client.setServer(mqttServer, mqttPort);
  client.setCallback(mqttCallback);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  if (espSerial.available()) {
    String sensorData = espSerial.readString();
    Serial.println(sensorData);

    client.publish(mqttTopic, sensorData.c_str());
  }

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
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}
