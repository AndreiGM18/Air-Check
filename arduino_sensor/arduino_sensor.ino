#include <SoftwareSerial.h>

// Pin for gas sensor (connected to A0 on Arduino Uno)
const int gasSensorPin = A0;
int sensorValue = 0;

// Setup SoftwareSerial communication for ESP-01
SoftwareSerial espSerial(2, 3);

void setup() {
  Serial.begin(9600);
  espSerial.begin(74880);

  Serial.println("Arduino Uno setup started...");
}

void loop() {
  sensorValue = analogRead(gasSensorPin);
  
  // Send the sensor data to the ESP-01 via serial
  espSerial.print("Sensor Value: ");
  espSerial.println(sensorValue);

  Serial.print("Sensor Value: ");
  Serial.println(sensorValue);

  delay(1000);
}
