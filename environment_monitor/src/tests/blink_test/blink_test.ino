/**
 * Benjamin Momoh, 2026
 * Environment Monitor Project
 * Blink Test File
 * Verifies the Arduino Mega2560 board, drivers, and IDE toolchain are
 * working correctly by blinking the onboard LED (pin 13).
 * No external wiring required.
 * Turns on an LED on for one second,
 * then off for one second, repeatedly.
 */
 int lightPin = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int reading = analogRead(lightPin);
  Serial.print("Light level: ");
  Serial.println(reading);
  delay(500);
}
