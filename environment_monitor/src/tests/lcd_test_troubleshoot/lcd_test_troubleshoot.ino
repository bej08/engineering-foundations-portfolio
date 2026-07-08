/*
 * Benjamin Momoh, 2026
 * Environment Monitor Project
 * LCD Test Troubleshoot File
 * -------------
 * Verifies the LCD1602 display is wired and initialising correctly by
 * printing a static test message 'Hello World. Used to confirm problem 
 * with potentiometer by directing VO->2k Resistor->5V for contrast. 
 * Note that this isnt a perminant fix.
 *
 * Wiring:
 * RS->D12, E->D11, D4->D8, D5->D7, D6->D6, D7->D5
 * VO->2k Resistor->5V, R/W->GND
 * VDD->5V, VSS->GND, backlight A->5V, K->GND
 */#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 8, 7, 6, 5);

void setup() {
  lcd.begin(16, 2);
  lcd.print("Hello World!");
}

void loop() {
 
}