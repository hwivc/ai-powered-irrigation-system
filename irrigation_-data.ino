#include <DHT.h>

#define DHTTYPE DHT11

const int DHT_PIN = 2;
const int SOIL_PIN = A1;

DHT dht(DHT_PIN, DHTTYPE);

const int DRY_VALUE = 1020;
const int WET_VALUE = 400;

void setup() {
  Serial.begin(9600);
  dht.begin();

  Serial.println("Soil_Moisture,Temperature_C,Humidity");

  delay(2000);
}

void loop() {

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  int rawSoil = analogRead(SOIL_PIN);

  if (isnan(humidity) || isnan(temperature)) {
    delay(2000);
    return;
  }

  // Convert raw reading to percentage
  float soilMoisture =
    ((float)(DRY_VALUE - rawSoil) /
    (DRY_VALUE - WET_VALUE)) * 100.0;

  // Keep percentage between 0 and 100
  soilMoisture = constrain(soilMoisture, 0, 100);

  // CSV output
  Serial.print(soilMoisture, 1);
  Serial.print(",");
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.println(humidity, 1);

  delay(2000);
}