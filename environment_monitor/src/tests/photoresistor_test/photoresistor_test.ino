/**
 * Benjamin Momoh, 2026
 * Environment Monitor Project
 * Photoresistor Test File
 *
 * Verifies the Arduino Mega2560 board, drivers, and IDE toolchain are
 * working correctly by blinking the onboard LED (pin 13).
 * No external wiring required.
 * Turns on an LED on for one second,
 * then off for one second, repeatedly.
 *
 * Reads ambient light level from a photoresistor wired as a voltage
 * divider with a 1kOhm resistor, and prints the raw analog value
 * (0-1023) to the Serial Monitor.
 *
 * Wiring:
 * Photoresistor: one leg -> 5V, other leg -> A0 + 1kOhm resistor
 * 1kOhm resistor: other leg -> GND
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