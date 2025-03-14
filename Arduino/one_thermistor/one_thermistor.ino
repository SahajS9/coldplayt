// Constants for the thermistor
const float R_FIXED = 51000.0;             // 10kΩ fixed resistor
const float THERMISTOR_NOMINAL = 100000.0; // Thermistor nominal resistance at 25°C (100kΩ)
const float TEMPERATURE_NOMINAL = 25.0;    // Nominal temperature (25°C)
const float BETA = 3950.0;                 // Beta coefficient of the thermistor
const int THERMISTOR_PIN = A0;             // Analog pin connected to the thermistor

void setup()
{
    Serial.begin(19200); // Initialize serial communication
}

void loop()
{
    // Read the analog value from the thermistor
    int sensorValue = analogRead(THERMISTOR_PIN);

    // Convert the analog reading to resistance
    float resistance = R_FIXED / (1023.0 / sensorValue - 1.0);

    // Calculate temperature using the Steinhart-Hart equation
    float temperature = calculateTemperature(resistance);

    // Output the temperature to the Serial Monitor
    // Serial.print("Raw value: ");
    // Serial.print(sensorValue);
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    delay(1000); // Wait 1 second before the next reading
}

// Function to calculate temperature from resistance using the Steinhart-Hart equation
float calculateTemperature(float resistance)
{
    // Convert resistance to temperature in Kelvin
    float steinhart;
    steinhart = resistance / THERMISTOR_NOMINAL;       // (R/Ro)
    steinhart = log(steinhart);                        // ln(R/Ro)
    steinhart /= BETA;                                 // 1/B * ln(R/Ro)
    steinhart += 1.0 / (TEMPERATURE_NOMINAL + 273.15); // + (1/To)
    steinhart = 1.0 / steinhart;                       // Invert
    steinhart -= 273.15;                               // Convert to Celsius

    return steinhart;
}
