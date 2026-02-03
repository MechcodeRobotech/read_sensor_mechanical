const int potPin = 34; // GPIO34 (ADC1_CH6)
int a1Value = 0;
double V_out = 0;
double Voltage_pressure_sensor = 0;

double voltage_divider(int adc_value){
  double V = ((adc_value*3.3)/4096 )*(3/2);
  return V;
  }

void setup() {
  Serial.begin(115200);
}

void loop() {
  a1Value = analogRead(potPin); // Read the ADC value
  Voltage_pressure_sensor = voltage_divider(a1Value);
  Serial.printf("Potvalue:{%d}",Voltage_pressure_sensor);
  Serial.println();
}
