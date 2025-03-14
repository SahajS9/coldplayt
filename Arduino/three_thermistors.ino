void setup()
{
    Serial.begin(9600);
}

void loop()
{
    int sensorValue1 = analogRead(A0); // Read thermistor 1
    int sensorValue2 = analogRead(A1); // Read thermistor 2
    int sensorValue3 = analogRead(A2); // Read thermistor 3

    // Convert analog readings to voltage (if using 5V)
    float voltage1 = sensorValue1 * (5.0 / 1023.0);
    float voltage2 = sensorValue2 * (5.0 / 1023.0);
    float voltage3 = sensorValue3 * (5.0 / 1023.0);

    // Calculate thermistor resistance using the voltage divider equation
    float R_fixed = 5100.0; // 5.1kΩ fixed resistor
    float R_thermistor1 = R_fixed * (5.0 / voltage1 - 1.0);
    float R_thermistor2 = R_fixed * (5.0 / voltage2 - 1.0);
    float R_thermistor3 = R_fixed * (5.0 / voltage3 - 1.0);

    // Calculate temperature using the Steinhart-Hart equation or a lookup table
    // Example: Steinhart-Hart equation for NTC thermistors
    float T1 = calculateTemperature(R_thermistor1);
    float T2 = calculateTemperature(R_thermistor2);
    float T3 = calculateTemperature(R_thermistor3);

    // Print temperatures
    Serial.print("Thermistor 1 Temperature: ");
    Serial.println(T1);
    Serial.print("Thermistor 2 Temperature: ");
    Serial.println(T2);
    Serial.print("Thermistor 3 Temperature: ");
    Serial.println(T3);

    delay(1000);
}

// Helper function to calculate temperature from thermistor resistance
float calculateTemperature(float R_thermistor)
{
    // Steinhart-Hart equation coefficients (replace with your thermistor's values)
    float A = 1.009249522e-03;
    float B = 2.378405444e-04;
    float C = 2.019202697e-07;

    float logR = log(R_thermistor);
    float T = 1.0 / (A + B * logR + C * logR * logR * logR); // Temperature in Kelvin
    T = T - 273.15;                                          // Convert to Celsius
    return T;
}