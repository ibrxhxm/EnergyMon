
#include "EmonLib.h"
#include <LiquidCrystal_PCF8574.h> //LCD_I2C library by Matthias Hertel (https://github.com/mathertel/LiquidCrystal_PCF8574)
#include <Wire.h>

EnergyMonitor emon1;
LiquidCrystal_PCF8574 lcd(0x27); // set the LCD address to 0x27 for a 16 chars and 2 line display


#define CURRENT_CAL 52.51 // 60.6 before calibration
#define VOLTAGE_CAL 670.62
#define PHASE_SHIFT 1.7
#define CURRENT_PIN 1
#define VOLTAGE_PIN 3
#define HALF_WAVELENGTHS 20
#define TIME_OUT 2000

struct Power {
  float rmsCurrent;
  float rmsVoltage;
  float realPower;
  float apparentPower;
  float powerFactor;
};

int error;

void setup() {
  Serial.begin(9600);

  emon1.current(CURRENT_PIN, CURRENT_CAL);             // Current: input pin, calibration.
  emon1.voltage(VOLTAGE_PIN, VOLTAGE_CAL, PHASE_SHIFT);  // Voltage: input pin, calibration, phase_shift

  Wire.begin();
  Wire.beginTransmission(0x27);
  lcd.setBacklight(255);
} // end setup

void sendPayloadToSerial(Power payload) {
  String payloadString = "";

  payloadString.concat(payload.rmsCurrent);
  payloadString.concat("|");
  payloadString.concat(payload.rmsVoltage);
  payloadString.concat("|");
  payloadString.concat(payload.realPower);
  payloadString.concat("|");
  payloadString.concat(payload.apparentPower);
  payloadString.concat("|");
  payloadString.concat(payload.powerFactor);

  Serial.println(payloadString);
} // end sendPayloadToSerial

void sendPayloadToLCD(Power payload) {
  error = Wire.endTransmission();

  if (error == 0) {
    lcd.begin(16, 2); // initialize the lcd
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("Vrms: ");
    lcd.print(payload.rmsVoltage);
    lcd.print("V");

    lcd.setCursor(0, 1);
    lcd.print("Irms: ");
    lcd.print(payload.rmsCurrent);
    lcd.print("A");

    delay(3000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("P: ");
    lcd.print(payload.realPower);
    lcd.print("kW");

    lcd.setCursor(0, 1);
    lcd.print("Q: ");
    lcd.print(payload.apparentPower);
    lcd.print("kVAr");

    delay(3000);
    lcd.clear();

    lcd.setCursor(0, 0);
    lcd.print("PF: ");
    lcd.print(payload.powerFactor);
    
  } else {
    Serial.println("error: LCD not found.");
  }
}

void loop() {
  Power payload;
  emon1.calcVI(HALF_WAVELENGTHS, TIME_OUT);        // Calculate all. No.of half wavelengths (crossings), time-out

  payload.realPower = emon1.realPower/1000.00;        //extract Real Power into variable
  payload.apparentPower = emon1.apparentPower/1000.00;    //extract Apparent Power into variable
  payload.powerFactor = emon1.powerFactor;      //extract Power Factor into Variable
  payload.rmsVoltage = emon1.Vrms;             //extract Vrms into Variable
  payload.rmsCurrent = emon1.Irms;             //extract Irms into Variable

  sendPayloadToSerial(payload);
  //sendPayloadToLCD(payload);

  delay(3000);
} // end loop
