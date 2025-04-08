#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "<WifiName>";
const char* password = "<WifiPassword>";

// Server URL
const char* serverName = "http://<ServerIP>:5000/api/data";

// DHT sensor config
#define DHTPIN D2       // GPIO4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// LED pin
#define LEDPIN D1       // GPIO5

void setup() {
  Serial.begin(115200);
  pinMode(LEDPIN, OUTPUT);
  dht.begin();

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connected!");
}

void loop() {
  // Read temperature and humidity
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if reading failed
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    delay(5000);
    return;
  }

  // Prepare JSON payload
  StaticJsonDocument<200> doc;
  doc["timestamp"] = ""; // Leave empty, server fills it
  doc["userid"] = "esp_user_1";
  doc["sensorid"] = "dht11_temp";
  doc["value"] = temperature;

  String payload;
  serializeJson(doc, payload);

  // Blink LED for 5 seconds
  digitalWrite(LEDPIN, HIGH);
  delay(5000);
  digitalWrite(LEDPIN, LOW);

  // Send HTTP POST request
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(15000); // Send every 15 seconds
}
