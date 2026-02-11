#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include "Max6675.h"

Adafruit_ADS1115 ads;
Max6675 ts(13, 12, 14); // (so, cs, sck)

// --- ตัวแปรสำหรับ Multitasking ---
unsigned long previousMillis = 0;  // เก็บเวลาล่าสุดที่อ่านอุณหภูมิ
const long interval = 300;         // ระยะห่างในการอ่านอุณหภูมิ (300 ms)

float currentTemp = 0.0;           // ตัวแปรเก็บค่าอุณหภูมิล่าสุดเอาไว้ส่ง

void setup(void) {
  Serial.begin(115200);
  ads.begin();
  ads.setDataRate(RATE_ADS1115_860SPS); // ตั้งให้ ADS อ่านไวที่สุดเท่าที่ทำได้
  ts.setOffset(0);
}

void loop(void) {
  unsigned long currentMillis = millis(); // ดูเวลาปัจจุบัน

  // -------------------------------------------------
  // TASK 1: อ่านเซนเซอร์ ADS1115 (ทำงานทุกรอบ ไม่มีการหน่วง)
  // -------------------------------------------------
  int16_t adc0 = ads.readADC_SingleEnded(0);
  int16_t adc1 = ads.readADC_SingleEnded(1);
  int16_t adc2 = ads.readADC_SingleEnded(2);

  double piezo_val = (adc0 * 0.1875 / 1000.0) * 100.0;
  
  double pressure_volt = adc1 * 0.1875 / 1000.0;
  double pressure = (pressure_volt - 0.5) * 12.5;
  
  double mic_volt = adc2 * 0.1875 / 1000.0;

  // -------------------------------------------------
  // TASK 2: อ่าน MAX6675 (ทำงานเฉพาะเมื่อครบ 300ms)
  // -------------------------------------------------
  if (currentMillis - previousMillis >= interval) {
    // บันทึกเวลาล่าสุดที่เข้ามาทำ
    previousMillis = currentMillis;

    // อ่านค่าอุณหภูมิใหม่ แล้วอัปเดตลงตัวแปร currentTemp
    currentTemp = ts.getCelsius();
  }

  // -------------------------------------------------
  // ส่วนแสดงผล (ส่งค่าออก Serial)
  // -------------------------------------------------
  Serial.print(piezo_val);
  Serial.print(",");
  Serial.print(pressure);
  Serial.print(",");
  Serial.print(mic_volt);
  Serial.print(",");
  
  // ส่งค่าอุณหภูมิล่าสุดออกไป (ถ้ายังไม่ถึง 300ms มันจะส่งค่าเดิมซ้ำไปเรื่อยๆ)
  Serial.println(currentTemp, 2); 

  // ไม่ต้องมี delay() ใหญ่ๆ ตรงนี้แล้ว 
  // อาจใส่ delay เล็กน้อยแค่ 5-10ms เพื่อป้องกัน Serial Buffer เต็ม ถ้าคอมพิวเตอร์รับไม่ทัน
//  delay(10); 
}
