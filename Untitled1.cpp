#include "max6675.h"
#include <Arduino.h>

#define THRESHOLD_HUMIDITY 0.9 // High humidity threshold (h2)
#define THRESHOLD_DRYNESS 0.1  // Dryness threshold (h2)
#define ADC_MAX_VOLTAGE 5.0    // Maximum voltage the ADC can measure (e.g., 5V)
#define ADC_RESOLUTION 1023    // Maximum value of a 10-bit ADC (0~1023)

int pin[20];
int thermo1DO = 12, thermo1CS = 13, thermo1CLK = 14;
int thermo2DO = 15, thermo2CS = 16, thermo2CLK = 17;

int adcValues[10];
float voltages[3];
float current[3];
float humidity[2];
float temp_of_humidity_sensor[2];

MAX6675 thermocouple1(thermo1CLK, thermo1CS, thermo1DO);
MAX6675 thermocouple2(thermo2CLK, thermo2CS, thermo2DO);

unsigned long startTime;
unsigned long exitTime;
bool isHigh = false;
bool isExitHigh = false;

void initialization();
void controlSolenoid(int state1, int state2, bool heaterState, bool seawaterPump);
int level(int t);
void exit_phase(int phase);

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 20; i++)
    pin[i] = i + 1;
  for (int i = 0; i < 11; i++)
    pinMode(pin[i], OUTPUT);
  for (int i = 11; i < 20; i++)
    pinMode(pin[i], INPUT);
  Serial.println("INITIALIZATION");
  initialization();
}

void loop() {
  for (int i = 0; i < 10; i++)
    adcValues[i] = analogRead(A0 + i);
    
  for (int i = 0; i < 3; i++) {
    voltages[i] = (adcValues[i] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION;
    current[i] = (adcValues[i + 3] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION;
  }

  humidity[0] = ((adcValues[6] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION) / 5; // O_2 Humidity
  humidity[1] = ((adcValues[7] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION) / 5; // H_2 Humidity
  temp_of_humidity_sensor[0] = (adcValues[8] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION; // O_2 Temperature
  temp_of_humidity_sensor[1] = (adcValues[9] * ADC_MAX_VOLTAGE) / ADC_RESOLUTION; // H_2 Temperature

  int t1 = thermocouple1.readCelsius();
  int t2 = thermocouple2.readCelsius();

  Serial.print("T1(Stack out) = ");
  Serial.println(t1);
  Serial.print("T2(Stack in) = ");
  Serial.println(t2);
  Serial.print("O2 Humidity: ");
  Serial.println(humidity[0]);
  Serial.print("H2 Humidity: ");
  Serial.println(humidity[1]);
  Serial.print("O2 Temp(%): ");
  Serial.println(temp_of_humidity_sensor[0] * 100);
  Serial.print("H2 Temp(%): ");
  Serial.println(temp_of_humidity_sensor[1] * 100);

  Serial.println("\n[1  2  3  4  5  6  7  8  9  10 11]");
  for (int i = 0; i < 11; i++) {
    int pinState = digitalRead(pin[i]);
    Serial.print(pinState == HIGH ? " 1 " : " 0 ");
  }
  Serial.println();

  if (isHigh && millis() - startTime >= 15000) {
    digitalWrite(pin[10], LOW);
    digitalWrite(pin[11], LOW);
    isHigh = false;
  }

  if (isExitHigh && millis() - exitTime >= 15000) {
    digitalWrite(pin[10], LOW);
    digitalWrite(pin[11], LOW);
    isExitHigh = false;
  }

  int m = level(t1) * level(t2);
  if (m <= 2)
    controlSolenoid(LOW, LOW, true, false); // loop3: cold
  else if (m < 6)
    controlSolenoid(LOW, HIGH, true, false); // loop2: moderate
  else if (m >= 6)
    controlSolenoid(HIGH, HIGH, false, true); // loop1: hot

  if (t1 > 100 || t2 > 100) {
    exit_phase(1);
    delay(5000);
    exit_phase(2);
    return;
  }

  if (humidity[1] > THRESHOLD_HUMIDITY)
    digitalWrite(pin[7], HIGH);
  else if (humidity[1] < THRESHOLD_DRYNESS)
    digitalWrite(pin[7], LOW);

  delay(1000);
}

void initialization() {
  Serial.println("3 way Solenoid ");
  digitalWrite(pin[3], HIGH);
  digitalWrite(pin[4], LOW);
  digitalWrite(pin[5], HIGH);
  digitalWrite(pin[6], LOW);
  digitalWrite(pin[7], LOW);
  digitalWrite(pin[8], HIGH);
  digitalWrite(pin[9], HIGH);
  controlSolenoid(LOW, LOW, true, false);
}

void controlSolenoid(int state1, int state2, bool heaterState, bool seawaterPump) {
  digitalWrite(pin[1], state1);
  digitalWrite(pin[2], state2);
  digitalWrite(pin[10], HIGH);
  digitalWrite(pin[11], HIGH);
  startTime = millis();
  isHigh = true;
  digitalWrite(pin[3], HIGH);
  digitalWrite(pin[4], seawaterPump ? HIGH : LOW);
  digitalWrite(pin[9], heaterState ? HIGH : LOW);
}

void exit_phase(int phase) {
  Serial.println("exiting...");
  for (int i = 0; i < 20; i++)
    digitalWrite(pin[i], LOW);
  if (phase == 1) {
    controlSolenoid(HIGH, HIGH, false, true); // cooling at exit mode
    exitTime = millis();
    isExitHigh = true;
  }
}

int level(int t) {
  if (t < 65)
    return 1;
  else if (t <= 80)
    return 2;
  else
    return 3;
}
