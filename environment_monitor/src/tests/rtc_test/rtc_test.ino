/*
 * Benjamin Momoh, 2026
 * Environment Monitor Project
 * RTC Test File
 * 
 * Verifies the DS1307 real-time clock module is wired correctly and
 * keeping time, printing the current date/time to the Serial Monitor
 * once per second. Sets the clock to the sketch's compile time on
 * first run if the RTC isn't already running.
 *
 * Wiring (Mega2560 I2C pins):
 * VCC->5V, GND->GND, SDA->D20, SCL->D21
 */
#include <Wire.h>
#include <RTClib.h>

RTC_DS1307 rtc;

void setup() {
  Serial.begin(9600);
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  if (!rtc.isrunning()) {
    // Sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
}

void loop() {
  DateTime now = rtc.now();
  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(' ');
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.println(now.second(), DEC);
  delay(1000);
}