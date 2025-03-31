// Constants for the thermistors
const float R_FIXED = 51000.0;             // 10kΩ fixed resistor
const float THERMISTOR_NOMINAL = 100000.0; // Thermistor nominal resistance at 25°C (100kΩ)
const float TEMPERATURE_NOMINAL = 25.0;    // Nominal temperature (25°C)
const float BETA = 3950.0;                 // Beta coefficient of the thermistor
const int THERMISTOR_PIN = A0;             // Analog pin connected to thermistor 1
const int THERMISTOR_PIN2 = A1;            // Analog pin connected to thermistor 2
const int THERMISTOR_PIN3 = A2;            // Analog pin connected to thermistor 3

void setup()
{
    Serial.begin(19200); // Initialize serial communication
    // Serial.println("Running three_thermistors.ino");
}

void loop()
{
    readThermistor(THERMISTOR_PIN);
    // Serial.print("\n");
    readThermistor(THERMISTOR_PIN2);
    // Serial.print("\n");
    readThermistor(THERMISTOR_PIN3);
    Serial.print("\n");

    delay(200); // Wait 1 second before the next reading
}

// Thermistor read function, calls Steinhart function
float readThermistor(int THERMISTOR)
{
    // Read the analog value from the thermistor
    int sensorValue = analogRead(THERMISTOR);
    // Convert the analog reading to resistance
    float resistance = R_FIXED / (1023.0 / sensorValue - 1.0);
    // Calculate temperature using the Steinhart-Hart equation
    float temperature = calculateTemperature(resistance);

    // Outputs for serial monitor
    // // Output the temperature to the Serial Monitor
    // // Serial.print("Raw value: ");
    // // Serial.print(sensorValue);
    // // Serial.print(" Temperature for ");
    // Serial.print("Temperature for ");
    // Serial.print(THERMISTOR);
    // Serial.print(": ");
    // Serial.print(temperature);
    // Serial.println(" °C");

    // Outputs for serial plotter
    Serial.print(temperature);
    Serial.print(" ");
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
