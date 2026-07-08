/**
 * Benjamin Momoh, 2026
 * Environment Monitor Project
 * LCD Test File
 * 
 * Verifies the LCD1602 display is wired and initialising correctly by
 * printing a static test message. Used to confirm contrast, backlight,
 * and all six data/control pin connections before combining with
 * sensor readings.
 *
 * Wiring:
 * RS->D7, E->D8, D4->D9, D5->D10, D6->D11, D7->D12
 * VO->potentiometer wiper (contrast), R/W->GND
 * VDD->5V, VSS->GND, backlight A->5V, K->GND
 */


#include <LiquidCrystal.h>

LiquidCrystal lcd(7, 8, 9, 10, 11, 12);
int lightPin = A0;

void setup() {
  lcd.begin(16, 2);
  lcd.print("Light level:");
}

void loop() {
  int reading = analogRead(lightPin);
  lcd.setCursor(0, 1);
  lcd.print("            "); // clear the previous number
  lcd.setCursor(0, 1);
  lcd.print(reading);
  delay(500);
}